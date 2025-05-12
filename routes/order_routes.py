from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from models.order_model import OrderModel
from models.bazi_result_model import BaziResultModel
from utils.payment_service import create_wechat_payment, create_alipay_payment, verify_wechat_payment, verify_alipay_payment

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
    payment_url = None
    if payment_method == 'wechat':
        payment_url = create_wechat_payment(order_id, order['amount'])
    elif payment_method == 'alipay':
        payment_url = create_alipay_payment(order_id, order['amount'])
    
    return jsonify(
        code=200,
        message="成功",
        data={
            "paymentUrl": payment_url,
            "orderId": order_id
        }
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
                    # 调用分析API (实际项目中应该使用异步任务)
                    from routes.bazi_routes import calculate_bazi, generate_ai_analysis
                    
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
                    # 调用分析API (实际项目中应该使用异步任务)
                    from routes.bazi_routes import calculate_bazi, generate_ai_analysis
                    
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
@jwt_required()
def mock_payment(order_id):
    """
    模拟支付完成(仅用于开发测试)
    实际生产环境中应该禁用此接口
    """
    user_id = get_jwt_identity()
    
    # 查找订单
    order = OrderModel.find_by_id(order_id)
    
    if not order:
        return jsonify(code=404, message="订单不存在"), 404
    
    if order['userId'] != user_id:
        return jsonify(code=403, message="无权访问此订单"), 403
    
    if order['status'] == 'paid':
        return jsonify(code=400, message="订单已支付"), 400
    
    # 更新订单状态
    OrderModel.update_status(order_id, 'paid')
    
    # 启动八字分析任务
    try:
        # 查找对应的八字结果记录
        bazi_result = BaziResultModel.find_by_order_id(order_id)
        if bazi_result:
            # 调用分析API (实际项目中应该使用异步任务)
            from routes.bazi_routes import calculate_bazi, generate_ai_analysis
            
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
        import logging
        logging.error(f"生成八字分析时出错: {str(e)}")
        return jsonify(code=500, message=f"分析生成失败: {str(e)}"), 500
    
    return jsonify(
        code=200,
        message="支付成功",
        data={
            "orderId": order_id
        }
    ) 