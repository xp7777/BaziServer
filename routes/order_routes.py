from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
import os
import uuid
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
    base_price = 1
    focus_price = 0.00000000001 * len(focus_areas)
    total_amount = base_price + focus_price
    
    # 创建订单
    order = OrderModel.create_order(user_id, base_price)
    
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
        "amount": 1, #追问支付金额设置
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
            "amount": 0.00001
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
                    
                    # 生成结果ID (如果没有)
                    result_id = order.get('resultId')
                    if not result_id:
                        result_id = f"RES{order_id.replace('BZ', '')}"
                        OrderModel.update_order_result_id(order_id, result_id)
                    else:
                        result_id = order.get('resultId')
                    
                    # 添加支付信息
                    payment_info = {
                        'paymentTime': datetime.now(),
                        'transactionId': query_result.get('transaction_id'),
                        'paymentMethod': 'wechat',
                        'apiVersion': 'v3'
                    }
                    OrderModel.update_payment_info(order_id, payment_info)
                    
                    # 创建八字分析记录（如果不存在）
                    bazi_result = BaziResultModel.find_by_id(result_id)
                    if not bazi_result:
                        logging.info(f"创建八字分析记录: {result_id}")
                        # 从订单中获取必要的参数
                        birth_date = order.get('birthDate')
                        birth_time = order.get('birthTime')
                        gender = order.get('gender')
                        focus_areas = order.get('focusAreas', [])
                        
                        if birth_date and birth_time and gender:
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
                            
                            try:
                                # 直接使用insert_one插入记录
                                mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
                                client = MongoClient(mongo_uri)
                                db = client.get_database()
                                results_collection = db.bazi_results
                                results_collection.insert_one(initial_result)
                                logging.info(f"成功创建初始八字分析记录: {result_id}")
                            except Exception as e:
                                logging.error(f"创建初始八字分析记录失败: {str(e)}")
                                logging.error(traceback.format_exc())
                        else:
                            logging.error(f"订单缺少必要的出生信息，无法创建八字分析记录: {order_id}")
                    
                    # 返回更新后的状态
                    return jsonify(
                        code=200,
                        message="订单已支付",
                        data={
                            "orderId": order['_id'],
                            "status": 'paid',
                            "resultId": result_id,
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
    """创建支付订单并返回支付参数"""
    data = request.json
    
    payment_method = data.get('paymentMethod')
    device_type = data.get('deviceType', 'pc')
    
    # 查找订单
    order = OrderModel.find_by_id(order_id)
    if not order:
        return jsonify(code=404, message="订单不存在"), 404
    
    # 获取用户openid（用于JSAPI支付）
    user_openid = order.get('openid') or order.get('userId')
    
    # 生成支付参数
    if payment_method == 'wechat':
        payment_data = create_wechat_payment(
            order_id, 
            order['amount'], 
            return_qr_image=True,
            device_type=device_type,
            openid=user_openid
        )
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

# 简化版订单创建API (不需要JWT认证)
@order_bp.route('/create/simple', methods=['POST'])
@jwt_required()
def create_simple_order():
    """创建简单订单"""
    try:
        user_id = get_jwt_identity()
        logging.info(f"创建订单，用户ID: {user_id}")
        
        data = request.json
        
        # 创建订单数据
        order_data = {
            'userId': user_id,  # 使用JWT中的用户ID
            'openid': user_id,  # 同时保存openid字段，确保兼容性
            'orderType': 'bazi_analysis',
            'amount': 1,  #八字支付金额设置
            'status': 'pending',
            'gender': data.get('gender'),
            'birthDate': data.get('birthDate'),
            'birthTime': data.get('birthTime'),
            'birthPlace': data.get('birthPlace'),
            'livingPlace': data.get('livingPlace'),
            'focusAreas': data.get('focusAreas', []),
            'calendarType': data.get('calendarType', 'solar'),
            'createdAt': datetime.utcnow(),
            'createTime': datetime.utcnow()
        }
        
        # 生成结果ID
        result_id = str(uuid.uuid4())
        order_data['resultId'] = result_id
        
        # 插入订单到数据库
        result = orders_collection.insert_one(order_data)
        order_id = str(result.inserted_id)
        
        logging.info(f"订单创建成功: {order_id}, 用户ID: {user_id}, 结果ID: {result_id}")
        
        return jsonify({
            'code': 200,
            'message': '订单创建成功',
            'data': {
                'orderId': order_id,
                'resultId': result_id,
                'amount': 9.9
            }
        })
        
    except Exception as e:
        logging.error(f"创建订单失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'创建订单失败: {str(e)}'}), 500

# 微信支付V3回调处理
@order_bp.route('/wechat/notify/v3', methods=['POST'])
def wechat_notify_v3():
    """微信支付V3回调处理"""
    if wechat_pay_v3 is None:
        logging.error("微信支付V3接口未初始化")
        return jsonify(code="FAIL", message="支付接口未初始化"), 500
    
    logging.info("收到微信支付V3回调")
    
    # 获取请求头和请求体
    headers = request.headers
    body = request.data.decode('utf-8')
    
    logging.debug(f"微信支付V3回调头部: {dict(headers)}")
    logging.debug(f"微信支付V3回调数据: {body}")
    
    # 处理回调
    try:
        # 验证并解析回调通知
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
            # 获取解密后的数据
            decrypted_data = notify_data.get("decrypted_resource")
            
            if not decrypted_data:
                logging.warning("未解密资源数据，可能缺少API V3密钥")
                # 尝试从原始数据中获取订单号
                resource = notify_data.get("resource", {})
                if isinstance(resource, dict) and resource.get("original_type") == "transaction":
                    # 可能包含订单号信息
                    out_trade_no = resource.get("out_trade_no", "unknown")
                else:
                    logging.error("无法获取订单号，回调处理终止")
                    return "{}"  # 返回空JSON表示接收成功
            else:
                # 从解密数据中获取订单信息
                out_trade_no = decrypted_data.get("out_trade_no")
                transaction_id = decrypted_data.get("transaction_id")
                trade_state = decrypted_data.get("trade_state")
                amount = decrypted_data.get("amount", {}).get("total")
                
                logging.info(f"支付成功: 订单={out_trade_no}, 微信订单号={transaction_id}, 金额={amount}分")
                
                # 更新订单状态
                if out_trade_no:
                    order = OrderModel.find_by_id(out_trade_no)
                    if order and order['status'] != 'paid':
                        # 更新订单状态
                        OrderModel.update_status(out_trade_no, 'paid')
                        
                        # 生成结果ID (如果没有)
                        result_id = order.get('resultId')
                        if not result_id:
                            result_id = f"RES{out_trade_no.replace('BZ', '')}"
                            OrderModel.update_order_result_id(out_trade_no, result_id)
                        
                        # 添加支付信息
                        payment_info = {
                            'paymentTime': datetime.now(),
                            'transactionId': transaction_id,
                            'paymentMethod': 'wechat',
                            'apiVersion': 'v3',
                            'amount': amount
                        }
                        OrderModel.update_payment_info(out_trade_no, payment_info)
                        
                        logging.info(f"已更新订单状态为已支付: {out_trade_no}")
                        
                        # 创建八字分析记录（如果不存在）
                        bazi_result = BaziResultModel.find_by_id(result_id)
                        if not bazi_result:
                            logging.info(f"微信支付回调时创建八字分析记录: {result_id}")
                            # 从订单中获取必要的参数
                            birth_date = order.get('birthDate')
                            birth_time = order.get('birthTime')
                            gender = order.get('gender')
                            focus_areas = order.get('focusAreas', [])
                            
                            if birth_date and birth_time and gender:
                                # 创建初始的八字分析结果记录
                                initial_result = {
                                    "_id": result_id,
                                    "orderId": out_trade_no,
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
                                
                                try:
                                    # 直接使用insert_one插入记录
                                    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
                                    client = MongoClient(mongo_uri)
                                    db = client.get_database()
                                    results_collection = db.bazi_results
                                    results_collection.insert_one(initial_result)
                                    logging.info(f"成功创建初始八字分析记录: {result_id}")
                                except Exception as e:
                                    logging.error(f"创建初始八字分析记录失败: {str(e)}")
                                    logging.error(traceback.format_exc())
                            else:
                                logging.error(f"订单缺少必要的出生信息，无法创建八字分析记录: {out_trade_no}")
                        
                        # 处理后续业务逻辑（可以添加任务队列处理八字分析等）
                        # 这里可以添加类似onPaymentSuccess的逻辑
                    else:
                        logging.info(f"订单已处理或不存在: {out_trade_no}")
                else:
                    logging.error("回调数据中未找到订单号")
            
        # 微信支付平台期望收到http状态码200和返回体{}，表示成功接收通知
        return "{}", 200, {"Content-Type": "application/json"}
        
    except Exception as e:
        logging.error(f"处理微信支付V3回调异常: {str(e)}")
        logging.error(traceback.format_exc())
        
        # 即使出错，仍需返回200和{}，避免微信平台重复通知
        return "{}", 200, {"Content-Type": "application/json"}

# 添加手动更新支付状态API
@order_bp.route('/manual_update/<order_id>', methods=['GET'])
def manual_update_order(order_id):
    """手动更新订单状态并生成分析结果"""
    try:
        logging.info(f"手动更新订单: {order_id}")
        
        # 查找订单 - 使用模型的正确查询方法
        order = OrderModel.find_by_id(order_id)
        if not order:
            logging.warning(f"订单不存在: {order_id}")
            return jsonify(code=404, message="订单不存在"), 404
        
        logging.info(f"订单状态: {order.get('status')}, 结果ID: {order.get('resultId')}")
        logging.info(f"订单数据: {order}")
        
        # 如果订单已支付但没有结果ID，生成结果ID
        if order.get('status') == 'paid' and not order.get('resultId'):
            # 生成结果ID
            result_id = 'RES' + order_id[2:] if order_id.startswith('BZ') else 'RES' + order_id
            
            # 更新订单的结果ID - 使用正确的ObjectId
            try:
                orders_collection.update_one(
                    {'_id': ObjectId(order_id)},
                    {'$set': {'resultId': result_id}}
                )
            except:
                # 如果ObjectId失败，尝试字符串ID
                orders_collection.update_one(
                    {'_id': order_id},
                    {'$set': {'resultId': result_id}}
                )
            
            # 创建分析结果记录
            result_data = {
                '_id': result_id,
                'orderId': order_id,
                'userId': order.get('userId', ''),
                'gender': order.get('gender', 'male'),
                'birthTime': order.get('birthTime', ''),
                'birthDate': order.get('birthDate', ''),
                'birthPlace': order.get('birthPlace', ''),
                'livingPlace': order.get('livingPlace', ''),
                'focusAreas': order.get('focusAreas', []),
                'calendarType': order.get('calendarType', 'solar'),
                'createdAt': datetime.utcnow(),
                'baziChart': {},  # 初始为空，后续分析填充
                'aiAnalysis': {}  # 初始为空，后续分析填充
            }
            
            logging.info(f"准备创建分析结果记录: {result_data}")
            
            # 使用BaziResultModel创建结果记录
            try:
                from models.bazi_result_model import bazi_results_collection
                bazi_results_collection.insert_one(result_data)
                logging.info(f"已创建分析结果记录: {result_id}")
            except Exception as e:
                logging.error(f"创建结果记录失败: {str(e)}")
            
            return jsonify({
                'code': 200,
                'message': '订单已支付',
                'data': {
                    'resultId': result_id,
                    'status': 'paid'
                }
            })
        
        # 如果订单已有结果ID
        elif order.get('resultId'):
            result_id = order.get('resultId')
            
            # 检查结果记录是否存在
            try:
                from models.bazi_result_model import bazi_results_collection
                result = bazi_results_collection.find_one({'_id': result_id})
            except Exception as e:
                logging.error(f"查询结果记录失败: {str(e)}")
                result = None
                
            if not result:
                # 创建分析结果记录
                result_data = {
                    '_id': result_id,
                    'orderId': order_id,
                    'userId': order.get('userId', ''),
                    'gender': order.get('gender', 'male'),
                    'birthTime': order.get('birthTime', ''),
                    'birthDate': order.get('birthDate', ''),
                    'birthPlace': order.get('birthPlace', ''),
                    'livingPlace': order.get('livingPlace', ''),
                    'focusAreas': order.get('focusAreas', []),
                    'calendarType': order.get('calendarType', 'solar'),
                    'createdAt': datetime.utcnow(),
                    'baziChart': {},  # 初始为空，后续分析填充
                    'aiAnalysis': {}  # 初始为空，后续分析填充
                }
                
                # 插入结果记录
                try:
                    bazi_results_collection.insert_one(result_data)
                    logging.info(f"已创建缺失的分析结果记录: {result_id}")
                except Exception as e:
                    logging.error(f"创建结果记录失败: {str(e)}")
            
            return jsonify({
                'code': 200,
                'message': '订单已支付',
                'data': {
                    'resultId': result_id,
                    'status': order.get('status', 'paid')
                }
            })
        
        # 其他情况
        return jsonify({
            'code': 200,
            'message': f'订单状态: {order.get("status", "unknown")}',
            'data': {
                'orderId': order_id,
                'status': order.get('status', 'unknown')
            }
        })
    
    except Exception as e:
        logging.error(f"手动更新订单错误: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500

@order_bp.route('/my', methods=['GET'])
@jwt_required()
def get_user_orders():
    """获取用户的订单列表"""
    try:
        user_id = get_jwt_identity()
        logging.info(f"获取用户订单列表，用户ID: {user_id}")
        
        # 获取查询参数
        status = request.args.get('status')
        
        # 构建查询条件
        query = {
            '$or': [
                {'userId': user_id},  # 兼容旧的userId字段
                {'openid': user_id}   # 新的openid字段
            ]
        }
        if status:
            query['status'] = status
        
        logging.info(f"查询条件: {query}")
        
        # 从数据库获取用户的订单，包含更多字段
        orders = list(orders_collection.find(
            query,
            {
                '_id': 1, 
                'orderType': 1, 
                'amount': 1, 
                'status': 1, 
                'createdAt': 1,
                'createTime': 1,
                'payTime': 1,
                'resultId': 1,
                'userId': 1,
                'openid': 1
            }
        ).sort('createdAt', -1))
        
        logging.info(f"找到 {len(orders)} 条订单记录")
        logging.info(f"订单详情: {[{'_id': str(order['_id']), 'userId': order.get('userId'), 'openid': order.get('openid'), 'status': order.get('status')} for order in orders]}")
        
        # 格式化返回数据
        order_data = []
        for order in orders:
            order_data.append({
                '_id': str(order['_id']),
                'orderType': order.get('orderType', ''),
                'amount': order.get('amount', 0),
                'status': order.get('status', ''),
                'createdAt': order.get('createdAt') or order.get('createTime'),
                'payTime': order.get('payTime'),
                'resultId': order.get('resultId')
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': order_data
        })
        
    except Exception as e:
        logging.error(f"获取用户订单列表错误: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500
