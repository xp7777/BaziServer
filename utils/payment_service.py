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
                logger.info(f"使用微信JSAPI支付: {order_id}")
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
            # 出错后尝试使用V2接口
    
    # 以下是原有的V2接口代码（作为后备方案）
    logger.warning(f"使用微信支付V2接口创建订单（后备方案）: {order_id}")
    
    # 获取配置
    app_id = os.getenv('WECHAT_APP_ID')
    mch_id = os.getenv('WECHAT_MCH_ID')
    api_key = os.getenv('WECHAT_API_KEY')
    notify_url = os.getenv('WECHAT_NOTIFY_URL')
    cert_serial_no = os.getenv('WECHAT_CERT_SERIAL_NO')
    
    # 如果没有配置微信支付，返回测试URL
    if not all([app_id, mch_id, api_key, notify_url]):
        logger.warning("微信支付未完全配置，返回测试URL")
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
        logger.info(f"开始调用微信支付V2 API创建订单: {order_id}")
        
        # 构造请求参数
        nonce_str = str(uuid.uuid4()).replace('-', '')
        body = "八字命理AI人生指导"  # 确保没有多余空格
        out_trade_no = order_id
        total_fee = int(amount * 100)  # 微信支付金额以分为单位
        spbill_create_ip = "127.0.0.1"
        trade_type = "NATIVE"  # 原生扫码支付
        
        # 构造签名参数
        sign_params = {
            "appid": app_id.strip(),
            "mch_id": mch_id.strip(),
            "nonce_str": nonce_str.strip(),
            "body": body.strip(),
            "out_trade_no": out_trade_no.strip(),
            "total_fee": str(total_fee).strip(),
            "spbill_create_ip": spbill_create_ip.strip(),
            "notify_url": notify_url.strip(),
            "trade_type": trade_type.strip()
        }
        
        # 打印调试信息，检查签名前的各参数
        logger.info(f"appid: '{app_id}'")
        logger.info(f"mch_id: '{mch_id}'")
        logger.info(f"body值: '{body}'")
        
        # 生成签名
        sign_string = "&".join([f"{k}={v}" for k, v in sorted(sign_params.items())])
        sign_string = sign_string + "&key=" + api_key.strip()
        
        # 打印签名参数用于调试
        logger.info(f"生成签名参数: {sign_params}")
        logger.info(f"完整签名字符串: {sign_string}")
        logger.info(f"签名使用的API密钥(部分隐藏): {api_key[:4]}...{api_key[-4:]}")
        
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        logger.info(f"生成的MD5签名: {sign}")
        
        # 构造XML请求
        xml_data = "<xml>"
        for k, v in sign_params.items():
            # 确保XML中的值与签名计算使用的值完全一致
            xml_data += f"<{k}>{v}</{k}>"
        xml_data += f"<sign>{sign}</sign>"
        xml_data += "</xml>"
        
        logger.info("发送微信支付统一下单请求")
        logger.debug(f"请求XML: {xml_data}")
        
        # 发送请求
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        headers = {'Content-Type': 'application/xml; charset=utf-8'}  # 明确指定UTF-8编码
        response = requests.post(url, data=xml_data.encode('utf-8'), headers=headers)
        
        # 记录响应内容
        logger.info(f"微信支付响应状态码: {response.status_code}")
        logger.debug(f"微信支付原始响应: {response.text}")
        
        # 解析响应
        result = xmltodict.parse(response.content)['xml']
        
        if result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
            logger.info(f"微信支付V2下单成功: {order_id}")
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
                
                logger.info("已生成微信支付二维码图片")
                
                return {
                    "code_url": code_url,
                    "qr_image": f"data:image/png;base64,{img_str}"
                }
            
            return {"code_url": code_url}
        else:
            error_msg = result.get('err_code_des') or result.get('return_msg') or '未知错误'
            logger.error(f"微信支付V2下单失败: {error_msg}")
            return {"error": error_msg, "code": "WECHAT_API_ERROR"}
    
    except Exception as e:
        logger.exception(f"创建微信支付异常: {str(e)}")
        return {"error": str(e), "code": "SYSTEM_ERROR"}

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
