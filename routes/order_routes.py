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
            except Exception as e:
                # 记录错误但不影响支付成功响应
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

@order_bp.route('/mock/pay/<order_id>', methods=['POST'])
def mock_payment(order_id):
    """模拟支付接口，用于测试和开发"""
    try:
        data = request.json
        birth_date = data.get('birthDate')
        birth_time = data.get('birthTime')
        gender = data.get('gender')
        area = data.get('area')
        result_id = data.get('resultId')
        
        logging.info(f"模拟支付请求: order_id={order_id}, birth_date={birth_date}, birth_time={birth_time}, gender={gender}, area={area}, result_id={result_id}")
        
        # 如果是追问订单
        if area and result_id:
            # 更新订单状态
            OrderModel.update_status(order_id, 'paid')
            
            # 生成追问分析
            try:
                # 获取原始八字数据
                bazi_result = BaziResultModel.find_by_id(result_id)
                if not bazi_result:
                    return jsonify(code=404, message="未找到原始分析结果"), 404
                
                # 生成追问分析
                analysis = generate_followup_analysis(
                    bazi_result['baziChart'],
                    area,
                    bazi_result.get('gender', gender)
                )
                
                # 更新追问分析结果
                BaziResultModel.update_followup(result_id, area, analysis)
                
                return jsonify(
                    code=200,
                    message="追问分析已生成",
                    data={
                        "orderId": order_id,
                        "resultId": result_id,
                        "area": area
                    }
                )
            except Exception as e:
                logging.error(f"生成追问分析失败: {str(e)}")
                logging.error(traceback.format_exc())
                return jsonify(code=500, message=str(e)), 500
        
        # 如果是普通订单
        else:
            # 更新订单状态
            OrderModel.update_status(order_id, 'paid')
            
            try:
                # 检查日期和时间格式
                if not birth_date or not birth_time:
                    return jsonify(code=400, message="缺少出生日期或时间"), 400
                
                # 组合日期和时间
                birth_datetime = f"{birth_date} {birth_time}"
                logging.info(f"组合后的日期时间: {birth_datetime}")
                
                # 计算八字
                try:
                    bazi_chart = calculate_bazi(birth_datetime, gender)
                except Exception as e:
                    logging.error(f"八字计算失败: {str(e)}")
                    logging.error(traceback.format_exc())
                    return jsonify(code=500, message=f"八字计算失败: {str(e)}"), 500
                
                if not bazi_chart:
                    return jsonify(code=500, message="八字计算失败"), 500
                
                # 生成AI分析
                ai_analysis = generate_bazi_analysis(bazi_chart, gender)
                
                # 创建或更新分析结果
                if result_id:
                    # 更新现有结果
                    BaziResultModel.update_analysis(result_id, bazi_chart, ai_analysis)
                    new_result_id = result_id
                else:
                    # 创建新结果
                    new_result_id = f"RES{order_id}"
                    success = BaziResultModel.create_result_with_id(
                        new_result_id,
                        None,  # user_id
                        order_id,
                        birth_date,
                        birth_time,
                        gender,
                        None,  # area
                        bazi_chart
                    )
                    
                    # 更新AI分析
                    BaziResultModel.update_ai_analysis(new_result_id, ai_analysis)
                
                return jsonify(
                    code=200,
                    message="分析已生成",
                    data={
                        "orderId": order_id,
                        "resultId": new_result_id
                    }
                )
            except Exception as e:
                logging.error(f"生成八字分析失败: {str(e)}")
                logging.error(traceback.format_exc())
                return jsonify(code=500, message=str(e)), 500
                
    except Exception as e:
        logging.error(f"模拟支付失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=str(e)), 500 