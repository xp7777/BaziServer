from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from models.order_model import OrderModel, orders_collection
from models.bazi_result_model import BaziResultModel
from utils.payment_service import create_wechat_payment, create_alipay_payment, verify_wechat_payment, verify_alipay_payment
from datetime import datetime
import traceback
import time
import logging
from utils.bazi_calculator import calculate_bazi
from utils.ai_service import analyze_bazi_with_ai, extract_analysis_from_text, generate_bazi_analysis, generate_followup_analysis
import threading
from pymongo import MongoClient
from utils.wechat_pay_v3 import wechat_pay_v3
import json

order_bp = Blueprint('order', __name__)

@order_bp.route('/create', methods=['POST'])
@jwt_required()
def create_order():
    """创建订单"""
    user_id = get_jwt_identity()
    data = request.json
    
    gender = data.get('gender')
    birth_time = data.get('birthTime')
    focus_areas = data.get('focusAreas', [])
    
    if not gender or not birth_time:
        return jsonify(code=400, message="请提供性别和出生时间信息"), 400
    
    # 计算订单金额: 基础费用9.9元 + 每个侧重点9.9元
    base_price = 9.9
    focus_price = 9.9 * len(focus_areas)
    total_amount = base_price + focus_price
    
    # 创建订单
    order = OrderModel.create_order(user_id, total_amount)
    
    # 创建八字结果记录
    result = BaziResultModel.create_result(
        user_id=user_id,
        order_id=order['_id'],
        gender=gender,
        birth_time=birth_time,
        focus_areas=focus_areas
    )
    
    return jsonify(
        code=200,
        message="订单创建成功",
        data={
            "orderId": order['_id'],
            "amount": order['amount']
        }
    )

@order_bp.route('/payment', methods=['POST'])
@jwt_required()
def get_payment():
    """获取支付信息"""
    user_id = get_jwt_identity()
    data = request.json
    
    order_id = data.get('orderId')
    payment_method = data.get('paymentMethod')
    device_type = data.get('deviceType', 'pc')  # 新增设备类型参数
    return_qr = data.get('returnQrCode', False)  # 是否返回二维码图片
    
    if not order_id or not payment_method:
        return jsonify(code=400, message="请提供订单ID和支付方式"), 400
    
    # 检查支付方式
    if payment_method not in ['wechat', 'alipay']:
        return jsonify(code=400, message="不支持的支付方式"), 400
    
    # 查找订单
    order = OrderModel.find_by_id(order_id)
    
    if not order:
        return jsonify(code=404, message="订单不存在"), 404
    
    if order['userId'] != user_id:
        return jsonify(code=403, message="无权访问此订单"), 403
    
    if order['status'] == 'paid':
        return jsonify(code=400, message="订单已支付"), 400
    
    # 更新支付方式
    OrderModel.update_payment(order_id, payment_method)
    
    # 生成支付参数
    payment_data = None
    if payment_method == 'wechat':
        payment_data = create_wechat_payment(order_id, order['amount'], return_qr=return_qr)
    elif payment_method == 'alipay':
        is_mobile = device_type.lower() in ['mobile', 'h5', 'app']
        payment_data = create_alipay_payment(order_id, order['amount'], is_mobile=is_mobile)
    
    if not payment_data:
        return jsonify(code=500, message="生成支付参数失败"), 500
    
    response_data = {
        "orderId": order_id,
        **payment_data
    }
    
    return jsonify(
        code=200,
        message="成功",
        data=response_data
    )

@order_bp.route('/status/<order_id>', methods=['GET'])
@jwt_required()
def check_status(order_id):
    """查询订单状态"""
    user_id = get_jwt_identity()
    
    order = OrderModel.find_by_id(order_id)
    
    if not order:
        return jsonify(code=404, message="订单不存在"), 404
    
    if order['userId'] != user_id:
        return jsonify(code=403, message="无权访问此订单"), 403
    
    return jsonify(
        code=200,
        message="成功",
        data={
            "orderId": order['_id'],
            "status": order['status'],
            "resultId": order.get('resultId')
        }
    )

@order_bp.route('/wechat/notify', methods=['POST'])
def wechat_notify():
    """微信支付回调"""
    logging.info("收到微信支付回调")
    logging.debug(f"回调数据: {request.data}")
    
    # 验证支付结果
    try:
        result = verify_wechat_payment(request.data)
        
        if result and result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
            order_id = result['out_trade_no']
            logging.info(f"微信支付成功: {order_id}")
            
            # 获取支付金额
            total_fee = int(result.get('total_fee', 0))  # 单位: 分
            transaction_id = result.get('transaction_id', '')
            logging.info(f"订单ID: {order_id}, 微信支付单号: {transaction_id}, 支付金额: {total_fee / 100}元")
            
            # 更新订单状态
            order = OrderModel.find_by_id(order_id)
            if order and order['status'] != 'paid':
                logging.info(f"更新订单状态为已支付: {order_id}")
                OrderModel.update_status(order_id, 'paid')
                
                # 将支付信息添加到订单
                payment_info = {
                    'paymentTime': datetime.now(),
                    'transactionId': transaction_id,
                    'paymentMethod': 'wechat',
                    'totalFee': total_fee / 100
                }
                OrderModel.update_payment_info(order_id, payment_info)
                
                # 启动八字分析任务
                try:
                    # 查找对应的八字结果记录
                    bazi_result = BaziResultModel.find_by_order_id(order_id)
                    if bazi_result:
                        logging.info(f"启动八字分析任务: {order_id}")
                        
                        # 获取订单类型
                        order_type = order.get('orderType', 'analysis')
                        
                        # 如果是基础八字分析订单
                        if order_type == 'analysis':
                            # 调用分析API
                            from routes.bazi_routes_fixed_new import calculate_bazi, generate_ai_analysis
                            
                            # 计算八字
                            bazi_chart = calculate_bazi(
                                bazi_result['birthTime'].split(' ')[0],
                                bazi_result['birthTime'].split(' ')[1],
                                bazi_result['gender']
                            )
                            
                            # 生成AI分析
                            ai_analysis = generate_ai_analysis(
                                bazi_chart,
                                bazi_result['focusAreas'],
                                bazi_result['gender']
                            )
                            
                            # 更新分析结果
                            BaziResultModel.update_analysis(
                                bazi_result['_id'],
                                bazi_chart,
                                ai_analysis
                            )
                        # 如果是追问分析订单
                        elif order_type == 'followup':
                            area = order.get('area')
                            result_id = order.get('resultId')
                            
                            if area and result_id:
                                logging.info(f"启动追问分析任务: {result_id}, 领域: {area}")
                                
                                # 异步生成追问分析
                                async_task(
                                    async_generate_followup,
                                    result_id,
                                    area
                                )
                except Exception as e:
                    # 记录错误但不影响支付成功响应
                    logging.error(f"生成八字分析时出错: {str(e)}")
                    logging.error(traceback.format_exc())
                
                logging.info("微信支付回调处理成功，返回成功响应")
                return "<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"
            else:
                logging.warning(f"订单不存在或已支付: {order_id}")
        else:
            # 支付验证失败
            error_msg = "未知错误"
            if result:
                error_msg = result.get('return_msg', '未知错误')
            logging.error(f"微信支付验证失败: {error_msg}")
            
        # 如果没有成功处理，返回失败
        logging.warning("微信支付回调处理失败，返回失败响应")
        return "<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[签名失败]]></return_msg></xml>"
    except Exception as e:
        logging.error(f"处理微信支付回调异常: {str(e)}")
        logging.error(traceback.format_exc())
        return "<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[系统错误]]></return_msg></xml>"

@order_bp.route('/alipay/notify', methods=['POST'])
def alipay_notify():
    """支付宝回调"""
    # 验证支付结果
    result = verify_alipay_payment(request.form.to_dict())
    
    if result and result['trade_status'] in ('TRADE_SUCCESS', 'TRADE_FINISHED'):
        order_id = result['out_trade_no']
        
        # 更新订单状态
        order = OrderModel.find_by_id(order_id)
        if order and order['status'] != 'paid':
            OrderModel.update_status(order_id, 'paid')
            
            # 启动八字分析任务
            try:
                # 查找对应的八字结果记录
                bazi_result = BaziResultModel.find_by_order_id(order_id)
                if bazi_result:
                    # 调用分析API
                    from routes.bazi_routes_fixed_new import calculate_bazi, generate_ai_analysis
                    
                    # 计算八字
                    bazi_chart = calculate_bazi(
                        bazi_result['birthTime'],
                        bazi_result['gender']
                    )
                    
                    # 生成AI分析
                    ai_analysis = generate_ai_analysis(
                        bazi_chart,
                        bazi_result['focusAreas'],
                        bazi_result['gender']
                    )
                    
                    # 更新分析结果
                    BaziResultModel.update_analysis(
                        bazi_result['_id'],
                        bazi_chart,
                        ai_analysis
                    )
            except Exception as e:
                # 记录错误但不影响支付成功响应
                logging.error(f"生成八字分析时出错: {str(e)}")
            
            return "success"
    
    return "fail"

@order_bp.route('/create/followup', methods=['POST'])
def create_followup_order():
    """
    创建追问订单
    """
    data = request.json
    result_id = data.get('resultId')
    area = data.get('area')
    
    if not result_id or not area:
        return jsonify({
            "code": 400,
            "message": "缺少必要参数"
        }), 400
    
    current_app.logger.info(f"创建追问订单，结果ID: {result_id}，领域: {area}")
    
    # 查找结果记录
    result = BaziResultModel.find_by_id(result_id)
    if not result:
        return jsonify({
            "code": 404,
            "message": "找不到对应的结果记录"
        }), 404
    
    # 创建订单ID
    order_id = "FQ" + str(int(time.time() * 1000))
    
    # 创建订单
    order = {
        "_id": order_id,
        "userId": result.get('userId', 'anonymous'),
        "amount": 9.9,
        "status": "pending",
        "orderType": "followup",
        "resultId": result_id,
        "area": area,
        "createTime": datetime.now()
    }
    
    # 保存订单
    OrderModel.insert(order)
    
    return jsonify({
        "code": 200,
        "message": "创建追问订单成功",
        "data": {
                            "orderId": order_id,
            "amount": 9.9
        }
    })

# 新增异步任务处理函数
def async_task(func, *args, **kwargs):
    """
    创建异步任务
    
    Args:
        func: 要异步执行的函数
        *args, **kwargs: 函数参数
    """
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread

# 异步生成八字分析
def async_generate_analysis(result_id, bazi_chart, gender):
    """
    异步生成八字分析
    
    Args:
        result_id: 结果ID
        bazi_chart: 八字命盘数据
        gender: 性别
    """
    try:
        logging.info(f"开始异步生成八字分析: {result_id}")
        # 生成AI分析
        ai_analysis = generate_bazi_analysis(bazi_chart, gender)
        
        # 更新AI分析结果
        BaziResultModel.update_ai_analysis(result_id, ai_analysis)
        logging.info(f"八字分析异步生成完成: {result_id}")
    except Exception as e:
        logging.error(f"异步生成八字分析失败: {str(e)}")
        logging.error(traceback.format_exc())

# 异步生成追问分析
def async_generate_followup(result_id, area, birth_date=None, birth_time=None, gender=None):
    """
    异步生成追问分析
    
    Args:
        result_id: 结果ID
        area: 追问领域
        birth_date: 出生日期（可选）
        birth_time: 出生时间（可选）
        gender: 性别（可选）
    """
    try:
        logging.info(f"开始异步生成追问分析: {result_id}, 领域: {area}")
        
        # 获取完整的结果记录，包括八字命盘和AI分析结果
        full_result = BaziResultModel.get_result(result_id)
        if not full_result:
            logging.error(f"找不到结果记录: {result_id}")
            error_message = f"找不到{result_id}的分析结果"
            BaziResultModel.update_followup(result_id, area, error_message)
            return
            
        # 获取八字命盘数据
        bazi_chart = full_result.get('baziChart')
        if not bazi_chart:
            logging.error(f"结果记录中没有八字命盘数据: {result_id}")
            error_message = f"八字命盘数据不完整，无法生成{area}分析"
            BaziResultModel.update_followup(result_id, area, error_message)
            return
            
        # 获取性别信息，优先使用参数传入的，其次是八字命盘中的
        if not gender:
            gender = bazi_chart.get('gender')
            if not gender:
                logging.warning(f"未提供性别信息，使用默认值'male'")
                gender = 'male'
                
        # 将AI分析结果添加到命盘数据中，作为上下文
        ai_analysis = full_result.get('aiAnalysis')
        if ai_analysis:
            bazi_chart['aiAnalysis'] = ai_analysis
            logging.info(f"已添加AI分析结果作为上下文")
        else:
            logging.warning(f"没有找到AI分析结果作为上下文")
        
        # 生成追问分析
        from utils.ai_service import generate_followup_analysis
        analysis = generate_followup_analysis(bazi_chart, area, gender)
        
        # 更新追问分析结果
        BaziResultModel.update_followup(result_id, area, analysis)
        logging.info(f"追问分析异步生成完成: {result_id}, 领域: {area}")
    except Exception as e:
        logging.error(f"异步生成追问分析失败: {str(e)}")
        logging.error(traceback.format_exc())
        # 确保即使出错也有友好的错误消息保存到数据库
        error_message = f"生成{area}分析时出错: {str(e)}"
        try:
            BaziResultModel.update_followup(result_id, area, error_message)
        except Exception as save_error:
            logging.error(f"保存错误消息到数据库失败: {str(save_error)}")

@order_bp.route('/mock/pay/<order_id>', methods=['POST'])
def mock_pay(order_id):
    """模拟支付接口"""
    try:
        logging.info(f"模拟支付请求: {order_id}")
        data = request.json
        logging.info(f"请求数据: {data}")

        # 查询订单
        order = OrderModel.get_order(order_id)
        if not order:
            logging.error(f"未找到订单: {order_id}")
            return jsonify(code=404, message="未找到订单"), 404
        
        # 检查订单状态
        if order.get('status') == 'paid':
            logging.info(f"订单已支付: {order_id}")
            # 返回该订单对应的结果ID
            result_id = order.get('resultId')
            
            # 如果订单没有关联的resultId，创建一个新的
            if not result_id:
                logging.warning(f"已支付订单没有resultId，创建新的resultId: {order_id}")
                
                # 使用一个固定的算法生成resultId，确保多次调用返回相同的ID
                # 使用订单ID的哈希值，更加稳定
                import hashlib
                hash_obj = hashlib.md5(order_id.encode())
                hash_hex = hash_obj.hexdigest()
                result_id = f"RESBZ{hash_hex[:8]}"
                
                logging.info(f"为已支付订单创建固定的resultId: {result_id}")
                OrderModel.update_order_result_id(order_id, result_id)
                
                # 从请求数据中获取必要的参数
                birth_date = data.get('birthDate')
                birth_time = data.get('birthTime')
                gender = data.get('gender')
                focus_areas = data.get('focusAreas', [])
                
                # 构建八字命盘数据
                bazi_chart = {
                    'birthDate': birth_date,
                    'birthTime': birth_time,
                    'gender': gender
                }
                
                # 创建初始的八字分析结果记录
                initial_result = {
                    "_id": result_id,
                    "orderId": order_id,
                    "gender": gender,
                    "birthTime": birth_time,
                    "birthDate": birth_date, 
                    "focusAreas": focus_areas,
                    "baziChart": {
                        'yearPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'monthPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'dayPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'hourPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'fiveElements': {'metal': 0, 'wood': 0, 'water': 0, 'fire': 0, 'earth': 0},
                        'gender': gender,
                        'birthDate': birth_date,
                        'birthTime': birth_time
                    },
                    "aiAnalysis": {
                        'overall': '正在分析整体运势...',
                        'health': '正在分析健康运势...',
                        'wealth': '正在分析财运...',
                        'career': '正在分析事业运势...',
                        'relationship': '正在分析感情运势...',
                        'children': '正在分析子女运势...'
                    },
                    "status": "processing",
                    "createTime": datetime.now()
                }
                
                # 首先检查该结果ID是否已存在
                existing = BaziResultModel.find_by_id(result_id)
                if existing:
                    logging.info(f"结果ID {result_id} 已存在，无需重复创建")
                else:
                    # 创建结果记录
                    try:
                        # 直接使用insert_one而不是create方法，确保_id字段被正确使用
                        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
                        client = MongoClient(mongo_uri)
                        db = client.get_database()
                        results_collection = db.bazi_results
                        
                        results_collection.insert_one(initial_result)
                        logging.info(f"成功直接插入初始八字分析记录: {result_id}")
                        
                        # 异步生成分析
                        threading.Thread(
                            target=async_generate_analysis, 
                            args=(result_id, bazi_chart, gender)
                        ).start()
                    except Exception as e:
                        logging.error(f"创建初始八字分析记录失败: {str(e)}")
                        logging.error(traceback.format_exc())
                
            # 确认结果记录存在
            bazi_result = BaziResultModel.find_by_id(result_id)
            if not bazi_result:
                logging.warning(f"结果记录 {result_id} 不存在，创建一个基本记录")
                
                # 从请求数据中获取必要的参数
                birth_date = data.get('birthDate')
                birth_time = data.get('birthTime')
                gender = data.get('gender')
                focus_areas = data.get('focusAreas', [])
                
                # 创建初始的八字分析结果记录
                initial_result = {
                    "_id": result_id,
                    "orderId": order_id,
                    "gender": gender,
                    "birthTime": birth_time,
                    "birthDate": birth_date, 
                    "focusAreas": focus_areas,
                    "baziChart": {
                        'yearPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'monthPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'dayPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'hourPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'fiveElements': {'metal': 0, 'wood': 0, 'water': 0, 'fire': 0, 'earth': 0},
                        'gender': gender,
                        'birthDate': birth_date,
                        'birthTime': birth_time
                    },
                    "aiAnalysis": {
                        'overall': '正在分析整体运势...',
                        'health': '正在分析健康运势...',
                        'wealth': '正在分析财运...',
                        'career': '正在分析事业运势...',
                        'relationship': '正在分析感情运势...',
                        'children': '正在分析子女运势...'
                    },
                    "status": "processing",
                    "createTime": datetime.now()
                }
                
                # 直接使用insert_one插入记录
                mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
                client = MongoClient(mongo_uri)
                db = client.get_database()
                results_collection = db.bazi_results
                
                try:
                    results_collection.insert_one(initial_result)
                    logging.info(f"紧急创建了初始八字分析记录: {result_id}")
                except Exception as e:
                    logging.error(f"紧急创建八字分析记录失败: {str(e)}")
                    
            return jsonify(code=200, message="订单已支付", data={"resultId": result_id})
            
        # 更新订单状态为已支付
        OrderModel.update_order_status(order_id, 'paid')
        
        # 获取订单类型
        order_type = order.get('orderType', 'analysis')
        
        # 如果是基础八字分析订单
        if order_type == 'analysis':
            # 异步生成八字分析
            result_id = order.get('resultId')
            if not result_id:
                # 创建新的结果记录
                result_id = f"RESBZ{int(time.time())}"
                OrderModel.update_order_result_id(order_id, result_id)
            
            # 准备生成参数
            birth_date = data.get('birthDate')
            birth_time = data.get('birthTime')
            gender = data.get('gender')
            
            # 构建八字命盘数据
            bazi_chart = {
                'birthDate': birth_date,
                'birthTime': birth_time,
                'gender': gender
            }
            
            # 异步生成分析
            threading.Thread(
                target=async_generate_analysis, 
                args=(result_id, bazi_chart, gender)
            ).start()
            
            return jsonify(code=200, message="支付成功，正在生成分析", data={"resultId": result_id})
        
        # 如果是追问分析订单
        elif order_type == 'followup':
            result_id = order.get('resultId')
            area = order.get('area')
            
            if not result_id or not area:
                logging.error(f"缺少必要参数: resultId={result_id}, area={area}")
                return jsonify(code=400, message="缺少必要参数"), 400
            
            logging.info(f"准备生成追问分析: resultId={result_id}, area={area}")
            
            # 先立即更新数据库中的标记，表示该领域已支付
            # 这样前端轮询时可以立即看到已支付状态
            try:
                # 获取当前的追问列表
                result = BaziResultModel.get_result(result_id)
                if result:
                    # 确保followups字段存在
                    if 'followupPaid' not in result:
                        BaziResultModel.update_field(result_id, 'followupPaid', [area])
                    else:
                        # 添加到已付费领域列表中
                        paid_areas = result.get('followupPaid', [])
                        if area not in paid_areas:
                            paid_areas.append(area)
                            BaziResultModel.update_field(result_id, 'followupPaid', paid_areas)
                    
                    logging.info(f"已将 {area} 标记为已支付")
                else:
                    logging.warning(f"找不到结果记录: {result_id}")
            except Exception as e:
                logging.error(f"更新已支付追问状态失败: {str(e)}")
            
            # 异步生成追问分析
            threading.Thread(
                target=async_generate_followup,
                args=(result_id, area, data.get('birthDate'), data.get('birthTime'), data.get('gender'))
            ).start()
            
            return jsonify(code=200, message="支付成功，正在生成分析", data={"resultId": result_id})
        
        else:
            logging.error(f"未知订单类型: {order_type}")
            return jsonify(code=400, message="未知订单类型"), 400
            
    except Exception as e:
        logging.error(f"模拟支付失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=str(e)), 500 

# 添加订单查询API
@order_bp.route('/query/<order_id>', methods=['GET'])
def query_order(order_id):
    """查询订单状态，用于前端轮询支付结果"""
    # 先从数据库查询订单
    order = OrderModel.find_by_id(order_id)
    
    if not order:
        return jsonify(code=404, message="订单不存在"), 404
    
    # 如果订单已支付，直接返回
    if order['status'] == 'paid':
        return jsonify(
            code=200,
            message="订单已支付",
            data={
                "orderId": order['_id'],
                "status": order['status'],
                "resultId": order.get('resultId'),
                "paymentMethod": order.get('paymentMethod'),
                "paymentTime": order.get('paymentTime', "").isoformat() if order.get('paymentTime') else None
            }
        )
    
    # 如果订单未支付，尝试从微信支付查询最新状态
    payment_method = order.get('paymentMethod')
    
    if payment_method == 'wechat':
        # 尝试使用V3接口查询
        if wechat_pay_v3 is not None:
            try:
                query_result = wechat_pay_v3.query_order(order_id)
                
                if query_result.get('code') == 'SUCCESS' and query_result.get('is_paid'):
                    # 订单已支付，更新状态
                    OrderModel.update_status(order_id, 'paid')
                    
                    # 添加支付信息
                    payment_info = {
                        'paymentTime': datetime.now(),
                        'transactionId': query_result.get('transaction_id'),
                        'paymentMethod': 'wechat',
                        'apiVersion': 'v3'
                    }
                    OrderModel.update_payment_info(order_id, payment_info)
                    
                    # 返回更新后的状态
                    return jsonify(
                        code=200,
                        message="订单已支付",
                        data={
                            "orderId": order['_id'],
                            "status": 'paid',
                            "resultId": order.get('resultId'),
                            "paymentMethod": 'wechat'
                        }
                    )
            except Exception as e:
                logging.error(f"微信支付V3查询订单异常: {str(e)}")
                # 查询失败时继续返回数据库中的状态
    
    # 返回数据库中的订单状态
    return jsonify(
        code=200,
        message="成功",
        data={
            "orderId": order['_id'],
            "status": order['status'],
            "resultId": order.get('resultId'),
            "paymentMethod": order.get('paymentMethod'),
            "paymentTime": order.get('paymentTime', "").isoformat() if order.get('paymentTime') else None
        }
    )

# 创建支付订单API（不需要JWT认证）
@order_bp.route('/create/payment/<order_id>', methods=['POST'])
def create_payment(order_id):
    """创建支付订单并返回支付二维码"""
    data = request.json
    
    payment_method = data.get('paymentMethod')
    device_type = data.get('deviceType', 'pc')
    
    if not payment_method:
        return jsonify(code=400, message="请提供支付方式"), 400
    
    # 检查支付方式
    if payment_method not in ['wechat', 'alipay']:
        return jsonify(code=400, message="不支持的支付方式"), 400
    
    # 查找订单
    order = OrderModel.find_by_id(order_id)
    
    if not order:
        return jsonify(code=404, message="订单不存在"), 404
    
    if order['status'] == 'paid':
        return jsonify(code=400, message="订单已支付"), 400
    
    # 记录订单相关信息（出生日期等）用于后续处理
    if data.get('birthDate') and data.get('birthTime') and data.get('gender'):
        orders_collection.update_one(
            {"_id": order_id},
            {"$set": {
                "birthDate": data.get('birthDate'),
                "birthTime": data.get('birthTime'),
                "gender": data.get('gender'),
                "focusAreas": data.get('focusAreas', []),
                "birthPlace": data.get('birthPlace', ""),
                "livingPlace": data.get('livingPlace', ""),
                "calendarType": data.get('calendarType', "solar")
            }}
        )
    
    # 更新支付方式
    OrderModel.update_payment(order_id, payment_method)
    
    # 生成支付参数
    payment_data = None
    try:
        if payment_method == 'wechat':
            # 设置return_qr=True返回二维码图片的base64编码
            payment_data = create_wechat_payment(order_id, order['amount'], return_qr_image=True)
            
            # 检查支付结果是否包含错误信息
            if payment_data and "error" in payment_data:
                logging.error(f"微信支付创建失败: {payment_data['error']}")
                # 如果包含错误但同时也有code_url（测试模式），仍然返回code_url
                if "code_url" not in payment_data:
                    return jsonify(code=500, message=f"微信支付创建失败: {payment_data['error']}"), 500
        elif payment_method == 'alipay':
            is_mobile = device_type.lower() in ['mobile', 'h5', 'app']
            payment_data = create_alipay_payment(order_id, order['amount'], is_mobile=is_mobile)
        
        if not payment_data:
            return jsonify(code=500, message="生成支付参数失败"), 500
        
        logging.info(f"创建{payment_method}支付订单成功: {order_id}")
        
        response_data = {
            "orderId": order_id,
            **payment_data
        }
        
        return jsonify(
            code=200,
            message="成功",
            data=response_data
        )
    except Exception as e:
        logging.error(f"创建支付订单失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=f"创建支付订单失败: {str(e)}"), 500 

# 简化版订单创建API (不需要JWT认证)
@order_bp.route('/create/simple', methods=['POST'])
def create_simple_order():
    """创建简化版订单，不需要用户登录"""
    data = request.json
    
    gender = data.get('gender')
    birth_date = data.get('birthDate')
    birth_time = data.get('birthTime')
    focus_areas = data.get('focusAreas', [])
    
    if not gender or not birth_date or not birth_time:
        return jsonify(code=400, message="请提供性别和出生日期时间信息"), 400
    
    # 计算订单金额: 基础费用9.9元
    total_amount = 9.9
    
    try:
        # 生成订单ID
        timestamp = int(time.time() * 1000)
        order_id = f"BZ{timestamp}"
        
        # 构造订单数据
        order = {
            "_id": order_id,  # 使用字符串ID
            "userId": "guest",  # 游客用户
            "amount": total_amount,
            "status": "pending",  # pending, paid, failed
            "paymentMethod": None,  # wechat, alipay
            "createTime": datetime.now(),
            "payTime": None,
            "resultId": None,
            "birthDate": birth_date,
            "birthTime": birth_time,
            "gender": gender,
            "focusAreas": focus_areas,
            "birthPlace": data.get('birthPlace', ""),
            "livingPlace": data.get('livingPlace', ""),
            "calendarType": data.get('calendarType', "solar")
        }
        
        # 直接插入订单
        OrderModel.insert(order)
        
        logging.info(f"简化版订单创建成功: {order_id}")
        
        return jsonify(
            code=200,
            message="订单创建成功",
            data={
                "orderId": order_id,
                "amount": total_amount
            }
        )
    except Exception as e:
        logging.error(f"创建订单失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=f"创建订单失败: {str(e)}"), 500 

# 微信支付V3回调处理
@order_bp.route('/wechat/notify/v3', methods=['POST'])
def wechat_notify_v3():
    """微信支付V3回调"""
    if wechat_pay_v3 is None:
        logging.error("微信支付V3接口未初始化")
        return jsonify(code="FAIL", message="支付接口未初始化"), 500
    
    logging.info("收到微信支付V3回调")
    
    # 获取请求头和请求体
    headers = request.headers
    body = request.data.decode('utf-8')
    
    logging.debug(f"微信支付V3回调头部: {dict(headers)}")
    logging.debug(f"微信支付V3回调数据: {body}")
    
    # 验证回调
    try:
        # 验证回调通知
        notify_data = wechat_pay_v3.verify_notify(headers, body)
        
        if not notify_data:
            # 如果验证失败，尝试直接解析JSON
            try:
                notify_data = json.loads(body)
                logging.warning("微信支付V3回调验证失败，使用直接解析JSON")
            except:
                logging.error("微信支付V3回调验证失败且无法解析JSON")
                return jsonify(code="FAIL", message="回调验证失败"), 400
        
        # 解析回调数据
        event_type = notify_data.get("event_type")
        
        # 记录回调数据
        logging.info(f"微信支付V3回调事件类型: {event_type}")
        logging.info(f"微信支付V3回调数据: {notify_data}")
        
        # 处理支付成功通知
        if event_type == "TRANSACTION.SUCCESS":
            resource = notify_data.get("resource", {})
            # 如果V3 API密钥存在，尝试解密resource数据
            api_v3_key = os.getenv('WECHAT_API_V3_KEY')
            
            # 以下为处理逻辑示例
            # 实际情况中，如果有API V3密钥，可以解密resource数据获取订单详情
            # 如果没有API V3密钥，这里只记录回调但不处理支付结果
            out_trade_no = "订单号"  # 从解密后的数据获取
            transaction_id = "微信支付单号"  # 从解密后的数据获取
            
            # 输出一个成功响应，即使不处理支付结果
            # 微信支付平台期望收到http状态码200和{}作为应答
            return "{}"
        
        logging.warning(f"未处理的微信支付V3事件类型: {event_type}")
        return "{}"  # 返回空JSON
        
    except Exception as e:
        logging.error(f"处理微信支付V3回调异常: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code="FAIL", message="处理异常"), 500 