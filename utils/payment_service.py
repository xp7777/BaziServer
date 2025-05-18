import os
import json
import logging
import hashlib
import uuid
import time
import requests
from alipay import AliPay
import xmltodict
import qrcode
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

def create_wechat_payment(order_id, amount, return_qr_image=False):
    """
    创建微信支付订单
    
    Args:
        order_id: 订单ID
        amount: 支付金额
        return_qr_image: 是否返回二维码图片的base64编码
        
    Returns:
        dict: 包含支付二维码URL和可选的二维码图片
    """
    # 获取配置
    app_id = os.getenv('WECHAT_APP_ID')
    mch_id = os.getenv('WECHAT_MCH_ID')
    api_key = os.getenv('WECHAT_API_KEY')
    notify_url = os.getenv('WECHAT_NOTIFY_URL')
    
    # 如果没有配置微信支付，返回测试URL
    if not all([app_id, mch_id, api_key, notify_url]):
        logger.warning("微信支付未配置，返回测试URL")
        test_url = f"https://example.com/test-pay?order_id={order_id}&amount={amount}"
        
        if return_qr_image:
            # 为测试URL生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(test_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "code_url": test_url,
                "qr_image": f"data:image/png;base64,{img_str}"
            }
        
        return {"code_url": test_url}
    
    try:
        # 构造请求参数
        nonce_str = str(uuid.uuid4()).replace('-', '')
        body = "八字命理AI人生指导"
        out_trade_no = order_id
        total_fee = int(amount * 100)  # 微信支付金额以分为单位
        spbill_create_ip = "127.0.0.1"
        trade_type = "NATIVE"  # 原生扫码支付
        
        # 构造签名参数
        sign_params = {
            "appid": app_id,
            "mch_id": mch_id,
            "nonce_str": nonce_str,
            "body": body,
            "out_trade_no": out_trade_no,
            "total_fee": str(total_fee),
            "spbill_create_ip": spbill_create_ip,
            "notify_url": notify_url,
            "trade_type": trade_type
        }
        
        # 生成签名
        sign_string = "&".join([f"{k}={v}" for k, v in sorted(sign_params.items())])
        sign_string = sign_string + "&key=" + api_key
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        
        # 构造XML请求
        xml_data = "<xml>"
        for k, v in sign_params.items():
            xml_data += f"<{k}>{v}</{k}>"
        xml_data += f"<sign>{sign}</sign>"
        xml_data += "</xml>"
        
        # 发送请求
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(url, data=xml_data.encode('utf-8'), headers=headers)
        
        # 解析响应
        result = xmltodict.parse(response.content)['xml']
        
        if result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
            code_url = result['code_url']
            
            if return_qr_image:
                # 生成二维码图片
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(code_url)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffered = BytesIO()
                img.save(buffered)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                return {
                    "code_url": code_url,
                    "qr_image": f"data:image/png;base64,{img_str}"
                }
            
            return {"code_url": code_url}
        else:
            logger.error(f"微信支付下单失败: {result}")
            return None
    
    except Exception as e:
        logger.exception(f"创建微信支付异常: {str(e)}")
        return None

def create_alipay_payment(order_id, amount, is_mobile=False):
    """
    创建支付宝支付订单
    
    Args:
        order_id: 订单ID
        amount: 支付金额
        is_mobile: 是否为移动端支付
        
    Returns:
        dict: 包含支付页面URL或支付表单HTML
    """
    # 获取配置
    app_id = os.getenv('ALIPAY_APP_ID')
    private_key = os.getenv('ALIPAY_PRIVATE_KEY')
    public_key = os.getenv('ALIPAY_PUBLIC_KEY')
    notify_url = os.getenv('ALIPAY_NOTIFY_URL')
    return_url = os.getenv('ALIPAY_RETURN_URL', 'https://yourdomain.com/payment/result')
    
    # 如果没有配置支付宝，返回测试URL
    if not all([app_id, private_key, public_key, notify_url]):
        logger.warning("支付宝支付未配置，返回测试URL")
        test_url = f"https://example.com/test-pay?order_id={order_id}&amount={amount}"
        return {"pay_url": test_url}
    
    try:
        # 初始化支付宝客户端
        alipay = AliPay(
            appid=app_id,
            app_notify_url=notify_url,
            app_private_key_string=private_key,
            alipay_public_key_string=public_key,
            sign_type="RSA2"
        )
        
        # 基本参数
        params = {
            "out_trade_no": order_id,
            "total_amount": float(amount),
            "subject": "八字命理AI人生指导",
            "return_url": return_url,
            "notify_url": notify_url
        }
        
        # 根据设备类型生成不同的支付链接
        if is_mobile:
            # 移动端支付
            order_string = alipay.api_alipay_trade_wap_pay(**params)
            gateway_url = "https://openapi.alipay.com/gateway.do?"
        else:
            # PC端支付
            order_string = alipay.api_alipay_trade_page_pay(**params)
            gateway_url = "https://openapi.alipay.com/gateway.do?"
            
        # 完整支付URL
        pay_url = f"{gateway_url}{order_string}"
        
        return {
            "pay_url": pay_url,
            "pay_form": f"""
            <form id='alipaySubmit' action='{gateway_url}' method='GET'>
                <input type='hidden' name='biz_content' value='{json.dumps(params)}'>
                <input type='hidden' name='app_id' value='{app_id}'>
                <input type='hidden' name='sign_type' value='RSA2'>
                <input type='submit' value='立即支付' style='display:none'>
            </form>
            <script>document.getElementById('alipaySubmit').submit();</script>
            """
        }
    
    except Exception as e:
        logger.exception(f"创建支付宝支付异常: {str(e)}")
        return None

def verify_wechat_payment(xml_data):
    """
    验证微信支付回调
    
    Args:
        xml_data: 微信支付回调XML数据
        
    Returns:
        dict: 验证结果
    """
    # 获取配置
    api_key = os.getenv('WECHAT_API_KEY')
    
    try:
        # 解析XML数据
        result = xmltodict.parse(xml_data)['xml']
        
        # 提取签名
        sign = result.pop('sign', None)
        
        # 验证签名
        sign_string = "&".join([f"{k}={v}" for k, v in sorted(result.items())])
        sign_string = sign_string + "&key=" + api_key
        calculated_sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        
        if calculated_sign == sign:
            return result
        else:
            logger.error("微信支付回调签名验证失败")
            return None
    
    except Exception as e:
        logger.exception(f"验证微信支付回调异常: {str(e)}")
        return None

def verify_alipay_payment(data):
    """
    验证支付宝支付回调
    
    Args:
        data: 支付宝回调数据
        
    Returns:
        dict: 验证结果
    """
    # 获取配置
    app_id = os.getenv('ALIPAY_APP_ID')
    private_key = os.getenv('ALIPAY_PRIVATE_KEY')
    public_key = os.getenv('ALIPAY_PUBLIC_KEY')
    
    try:
        # 初始化支付宝客户端
        alipay = AliPay(
            appid=app_id,
            app_notify_url=None,
            app_private_key_string=private_key,
            alipay_public_key_string=public_key,
            sign_type="RSA2"
        )
        
        # 验证签名
        sign = data.pop('sign', None)
        sign_type = data.pop('sign_type', None)
        
        if alipay.verify(data, sign):
            return data
        else:
            logger.error("支付宝回调签名验证失败")
            return None
    
    except Exception as e:
        logger.exception(f"验证支付宝支付回调异常: {str(e)}")
        return None 