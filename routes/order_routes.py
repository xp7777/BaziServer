from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from models.order_model import OrderModel, orders_collection
from models.bazi_result_model import BaziResultModel
from utils.payment_service import create_wechat_payment, create_alipay_payment, verify_wechat_payment, verify_alipay_payment
from datetime import datetime

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
    # 验证支付结果
    result = verify_wechat_payment(request.data)
    
    if result and result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
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
                    from routes.bazi_routes_fixed import calculate_bazi, generate_ai_analysis
                    
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
            except Exception as e:
                # 记录错误但不影响支付成功响应
                import logging
                logging.error(f"生成八字分析时出错: {str(e)}")
            
            return "<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"
    
    return "<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[签名失败]]></return_msg></xml>"

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
                    from routes.bazi_routes_fixed import calculate_bazi, generate_ai_analysis
                    
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
            except Exception as e:
                # 记录错误但不影响支付成功响应
                import logging
                logging.error(f"生成八字分析时出错: {str(e)}")
            
            return "success"
    
    return "fail"

@order_bp.route('/mock/pay/<order_id>', methods=['POST'])
# 暂时移除JWT验证，用于测试
# @jwt_required()
def mock_payment(order_id):
    """
    模拟支付完成(仅用于开发测试)
    实际生产环境中应该禁用此接口
    """
    # 测试环境：不检查用户身份
    # user_id = get_jwt_identity()
    
    import logging
    logging.info(f"正在处理模拟支付请求，订单ID: {order_id}")
    
    try:
        # 获取请求中的出生日期和时间数据（如果有）
        data = request.get_json() or {}
        requested_birth_date = data.get('birthDate')
        requested_birth_time = data.get('birthTime')
        requested_gender = data.get('gender')
        
        # 详细记录收到的数据
        logging.info(f"请求体数据: {data}")
        
        # 如果请求中没有数据，尝试从URL查询参数中获取
        if not requested_birth_date or not requested_birth_time:
            requested_birth_date = request.args.get('birthDate')
            requested_birth_time = request.args.get('birthTime')
            requested_gender = request.args.get('gender')
            if requested_birth_date:
                logging.info(f"从URL参数获取日期时间: {requested_birth_date} {requested_birth_time}")
        
        # 详细记录URL参数
        logging.info(f"URL查询参数: {dict(request.args)}")
        
        # 如果请求中没有数据，尝试从RES前缀中提取
        if (not requested_birth_date or not requested_birth_time) and order_id.startswith("RES"):
            try:
                # 尝试从数据库查找
                existing_result = BaziResultModel.find_by_id(order_id)
                if existing_result and 'birthDate' in existing_result and 'birthTime' in existing_result:
                    requested_birth_date = existing_result.get('birthDate')
                    requested_birth_time = existing_result.get('birthTime')
                    requested_gender = existing_result.get('gender', 'male')
                    logging.info(f"从现有记录获取日期时间: {requested_birth_date} {requested_birth_time}")
            except Exception as e:
                logging.warning(f"从RES记录获取数据失败: {str(e)}")
        
        # 如果所有尝试都失败，尝试使用默认值
        if not requested_birth_date:
            requested_birth_date = "2022-06-21"  # 默认日期
            logging.warning(f"未能获取出生日期，使用默认值: {requested_birth_date}")
        
        if not requested_birth_time:
            requested_birth_time = "午时 (11:00-13:00)"  # 默认时间
            logging.warning(f"未能获取出生时间，使用默认值: {requested_birth_time}")
        
        if not requested_gender:
            requested_gender = "male"  # 默认性别
            logging.warning(f"未能获取性别，使用默认值: {requested_gender}")
        
        # 验证日期格式
        birth_year = int(requested_birth_date.split('-')[0])
        if birth_year < 1900 or birth_year > 2100:
            logging.warning(f"出生年份超出合理范围: {birth_year}，可能导致计算错误")
        
        logging.info(f"确认使用的出生信息: 日期={requested_birth_date}, 时间={requested_birth_time}, 性别={requested_gender}")
        
        # 查找订单
        order = OrderModel.find_by_id(order_id)
        
        if not order:
            # 如果找不到订单，创建一个临时订单
            import random
            mock_user_id = "test_user_" + str(random.randint(1000, 9999))
            
            # 对于数字ID，直接使用该ID作为订单ID
            if order_id.isdigit() or (order_id.startswith("RES") and order_id[3:].isdigit()):
                # 直接创建一个使用该ID的文档
                logging.info(f"创建使用指定ID的测试订单: {order_id}")
                order = {
                    "_id": order_id,  # 使用传入的ID
                    "userId": mock_user_id,
                    "amount": 9.9,
                    "status": "pending",
                    "paymentMethod": "test",
                    "createTime": datetime.now(),
                    "payTime": None,
                    "resultId": None
                }
                try:
                    # 尝试插入文档
                    orders_collection.insert_one(order)
                except Exception as e:
                    logging.error(f"创建订单失败: {str(e)}")
                    # 如果插入失败，使用普通方法创建
                    order = OrderModel.create_order(mock_user_id, 9.9)
                    order_id = order['_id']
            else:
                # 使用常规方法创建随机ID的订单
                order = OrderModel.create_order(mock_user_id, 9.9)
                order_id = order['_id']
            
            # 使用请求中的日期时间，如果没有则使用默认值
            birth_date = requested_birth_date
            birth_time = requested_birth_time
            gender = requested_gender
            focus_areas = ["health", "wealth", "career", "relationship"]
            
            # 记录使用的日期和时间
            logging.info(f"使用出生日期: {birth_date}, 出生时间: {birth_time}, 性别: {gender}")
            
            # 创建一个临时的八字结果记录
            try:
                bazi_result = BaziResultModel.create_result(
                    user_id=mock_user_id,
                    order_id=order_id,
                    gender=gender,
                    birth_time=f"{birth_date} {birth_time}",
                    focus_areas=focus_areas
                )
                
                # 添加birthDate字段
                try:
                    from models.bazi_result_model import results_collection
                    results_collection.update_one(
                        {"_id": bazi_result["_id"]},
                        {"$set": {"birthDate": birth_date}}
                    )
                    logging.info(f"更新了birthDate字段: {birth_date}")
                except Exception as e:
                    logging.error(f"更新birthDate字段失败: {str(e)}")
                
                # 更新订单状态
                OrderModel.update_status(order_id, 'paid')
                
                # 启动八字分析任务
                try:
                    # 调用分析API
                    from routes.bazi_routes_fixed import calculate_bazi, generate_ai_analysis
                    
                    # 计算八字
                    bazi_chart = calculate_bazi(
                        birth_date,
                        birth_time,
                        gender
                    )
                    
                    if not bazi_chart:
                        return jsonify(code=500, message=f"八字计算失败，请检查出生日期和时间: {birth_date} {birth_time}"), 500
                    
                    # 生成AI分析
                    ai_analysis = generate_ai_analysis(
                        bazi_chart,
                        focus_areas,
                        gender
                    )
                    
                    # 更新分析结果
                    BaziResultModel.update_analysis(
                        bazi_result['_id'],
                        bazi_chart,
                        ai_analysis
                    )
                    
                    return jsonify(
                        code=200,
                        message="支付成功",
                        data={
                            "orderId": order_id,
                            "resultId": bazi_result['_id']
                        }
                    )
                except Exception as e:
                    # 记录错误
                    logging.error(f"生成八字分析时出错: {str(e)}")
                    return jsonify(code=500, message=f"分析生成失败: {str(e)}"), 500
            except Exception as e:
                logging.error(f"创建八字结果记录失败: {str(e)}")
                return jsonify(code=500, message=f"创建分析记录失败: {str(e)}"), 500
        
        # 不检查用户权限
        # if order['userId'] != user_id:
        #    return jsonify(code=403, message="无权访问此订单"), 403
        
        if order['status'] == 'paid':
            # 查找对应的八字结果记录
            bazi_result = BaziResultModel.find_by_order_id(order_id)
            if bazi_result:
                return jsonify(
                    code=200,
                    message="订单已支付",
                    data={
                        "orderId": order_id,
                        "resultId": bazi_result['_id']
                    }
                )
            else:
                return jsonify(code=400, message="订单已支付但未找到分析结果"), 400
        
        # 更新订单状态
        OrderModel.update_status(order_id, 'paid')
        
        # 启动八字分析任务
        try:
            # 查找对应的八字结果记录
            bazi_result = BaziResultModel.find_by_order_id(order_id)
            if bazi_result:
                # 调用分析API (实际项目中应该使用异步任务)
                from routes.bazi_routes_fixed import calculate_bazi, generate_ai_analysis
                
                # 提取出生日期和时间
                if 'birthDate' in bazi_result and bazi_result['birthDate']:
                    birth_date = bazi_result['birthDate']
                    birth_time = bazi_result['birthTime']
                else:
                    # 尝试从birthTime字段分离日期和时间
                    birth_parts = bazi_result['birthTime'].split(' ')
                    if len(birth_parts) >= 2 and len(birth_parts[0].split('-')) == 3:
                        birth_date = birth_parts[0]
                        birth_time = ' '.join(birth_parts[1:])
                    else:
                        # 使用请求中提供的日期或默认值
                        birth_date = requested_birth_date
                        birth_time = requested_birth_time
                        
                        # 更新记录中的日期
                        try:
                            from models.bazi_result_model import results_collection
                            results_collection.update_one(
                                {"_id": bazi_result["_id"]},
                                {"$set": {
                                    "birthDate": birth_date,
                                    "birthTime": birth_time
                                }}
                            )
                            logging.info(f"更新了birthDate和birthTime字段: {birth_date} {birth_time}")
                        except Exception as e:
                            logging.error(f"更新birth字段失败: {str(e)}")
                
                logging.info(f"分析使用的日期时间: {birth_date}, {birth_time}")
                
                # 计算八字
                bazi_chart = calculate_bazi(
                    birth_date,
                    birth_time,
                    bazi_result['gender']
                )
                
                if not bazi_chart:
                    return jsonify(code=500, message=f"八字计算失败，请检查出生日期和时间: {birth_date} {birth_time}"), 500
                
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
                
                return jsonify(
                    code=200,
                    message="支付成功",
                    data={
                        "orderId": order_id,
                        "resultId": bazi_result['_id']
                    }
                )
            else:
                # 创建一个临时的八字结果记录并分析
                # 使用请求中的日期时间，如果没有则使用默认值
                birth_date = requested_birth_date
                birth_time = requested_birth_time
                gender = requested_gender or "male"
                focus_areas = ["health", "wealth", "career", "relationship"]
                
                logging.info(f"创建新结果记录使用: {birth_date} {birth_time}")
                
                try:
                    bazi_result = BaziResultModel.create_result(
                        user_id=order.get('userId', 'test_user'),
                        order_id=order_id,
                        gender=gender,
                        birth_time=f"{birth_date} {birth_time}",
                        focus_areas=focus_areas
                    )
                    
                    # 添加birthDate字段
                    try:
                        from models.bazi_result_model import results_collection
                        results_collection.update_one(
                            {"_id": bazi_result["_id"]},
                            {"$set": {"birthDate": birth_date}}
                        )
                        logging.info(f"更新了birthDate字段: {birth_date}")
                    except Exception as e:
                        logging.error(f"更新birthDate字段失败: {str(e)}")
                    
                    # 计算八字
                    bazi_chart = calculate_bazi(
                        birth_date,
                        birth_time,
                        gender
                    )
                    
                    if not bazi_chart:
                        return jsonify(code=500, message=f"八字计算失败，请检查出生日期和时间: {birth_date} {birth_time}"), 500
                    
                    # 生成AI分析
                    ai_analysis = generate_ai_analysis(
                        bazi_chart,
                        focus_areas,
                        gender
                    )
                    
                    # 更新分析结果
                    BaziResultModel.update_analysis(
                        bazi_result['_id'],
                        bazi_chart,
                        ai_analysis
                    )
                    
                    return jsonify(
                        code=200,
                        message="支付成功",
                        data={
                            "orderId": order_id,
                            "resultId": bazi_result['_id']
                        }
                    )
                except Exception as e:
                    logging.error(f"创建新结果记录失败: {str(e)}")
                    return jsonify(code=500, message=f"创建分析记录失败: {str(e)}"), 500
        except Exception as e:
            # 记录错误
            logging.error(f"生成八字分析时出错: {str(e)}")
            return jsonify(code=500, message=f"分析生成失败: {str(e)}"), 500
    except Exception as e:
        # 记录错误
        logging.error(f"模拟支付处理过程中发生未捕获的错误: {str(e)}")
        return jsonify(code=500, message=f"服务器处理错误: {str(e)}"), 500 