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
import hmac
from utils.wechat_pay_v3 import wechat_pay_v3, WechatPayV3

logger = logging.getLogger(__name__)

# 初始化微信支付V3接口
# wechat_pay_v3 = None
# try:
#     wechat_pay_v3 = WechatPayV3()
#     logger.info("微信支付V3接口初始化成功")
# except Exception as e:
#     logger.error(f"微信支付V3接口初始化失败: {str(e)}")

# 使用统一实例，已在wechat_pay_v3.py中创建
if wechat_pay_v3 is not None:
    logger.info("使用全局微信支付V3接口实例")
else:
    logger.warning("全局微信支付V3接口实例不可用")

def create_wechat_payment(order_id, amount, return_qr_image=False, device_type='pc', openid=None):
    """
    创建微信支付订单
    
    Args:
        order_id: 订单ID
        amount: 支付金额
        return_qr_image: 是否返回二维码图片
        device_type: 设备类型 ('mobile', 'pc')
        openid: 微信用户openid (JSAPI支付必需)
    """
    if wechat_pay_v3 is not None:
        try:
            amount_in_cents = int(amount * 100)
            
            # 手机端使用JSAPI支付
            if device_type == 'mobile' and openid:
                logger.info(f"使用微信JSAPI支付: {order_id}, openid: {openid[:8]}***")
                
                # 验证openid格式
                if not openid or len(openid) < 10:
                    logger.error(f"openid格式无效: {openid}")
                    raise Exception(f"openid格式无效，长度: {len(openid) if openid else 0}")
                
                result = wechat_pay_v3.create_jsapi_order(
                    out_trade_no=order_id,
                    amount=amount_in_cents,
                    description="八字命理AI人生指导",
                    openid=openid
                )
                
                if result.get("code") == "SUCCESS":
                    # 获取JSAPI支付参数
                    prepay_id = result.get("prepay_id")
                    jsapi_params = wechat_pay_v3.get_jsapi_params(prepay_id)
                    
                    return {
                        "payment_type": "jsapi",
                        "jsapi_params": jsapi_params,
                        "prepay_id": prepay_id
                    }
                else:
                    # JSAPI支付失败，记录具体错误并抛出异常，不降级到V2
                    error_msg = result.get("message", "未知错误")
                    logger.error(f"微信JSAPI支付失败: {error_msg}, 订单: {order_id}, openid: {openid[:8]}***")
                    raise Exception(f"微信JSAPI支付失败: {error_msg}")
            
            # PC端使用Native扫码支付
            else:
                logger.info(f"使用微信Native支付: {order_id}")
                result = wechat_pay_v3.create_native_order(
                    out_trade_no=order_id,
                    amount=amount_in_cents,
                    description="八字命理AI人生指导",
                    return_qr_image=return_qr_image
                )
                
                if result.get("code") == "SUCCESS":
                    return {
                        "payment_type": "native",
                        **result
                    }
        except Exception as e:
            logger.exception(f"微信支付V3创建订单异常: {str(e)}")
            # 直接返回失败，不使用V2后备方案
            return None
    
    # V3支付不可用时直接返回失败
    logger.error(f"微信支付V3不可用，订单创建失败: {order_id}")
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
