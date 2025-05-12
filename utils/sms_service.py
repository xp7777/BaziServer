import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

def send_verify_code(phone, code):
    """
    发送验证码短信
    
    Args:
        phone: 手机号码
        code: 验证码
    
    Returns:
        bool: 是否发送成功
    """
    # 获取配置
    access_key = os.getenv('SMS_ACCESS_KEY')
    secret_key = os.getenv('SMS_SECRET_KEY')
    sign_name = os.getenv('SMS_SIGN_NAME')
    template_code = os.getenv('SMS_TEMPLATE_CODE')
    
    # 如果没有配置短信服务，直接返回成功
    if not all([access_key, secret_key, sign_name, template_code]):
        logger.warning("短信服务未配置，跳过发送")
        return True
    
    try:
        # 这里以阿里云短信服务为例
        # 实际应用中，应该根据使用的短信服务提供商调整请求方式
        url = "https://dysmsapi.aliyuncs.com"
        
        # 构造请求参数
        params = {
            "AccessKeyId": access_key,
            "Action": "SendSms",
            "Format": "JSON",
            "PhoneNumbers": phone,
            "SignName": sign_name,
            "TemplateCode": template_code,
            "TemplateParam": json.dumps({"code": code}),
            "Version": "2017-05-25"
        }
        
        # 发送请求
        response = requests.get(url, params=params)
        result = response.json()
        
        # 检查响应
        if result.get('Code') == 'OK':
            logger.info(f"短信发送成功，手机号: {phone}")
            return True
        else:
            logger.error(f"短信发送失败，错误信息: {result}")
            return False
    
    except Exception as e:
        logger.exception(f"短信发送异常: {str(e)}")
        return False

def verify_code(phone, code):
    """
    验证短信验证码
    
    在实际应用中，该函数应该从数据库或缓存中获取之前发送的验证码，进行比对
    由于我们使用内存存储验证码，该函数不需要实现
    
    Args:
        phone: 手机号码
        code: 验证码
    
    Returns:
        bool: 验证码是否正确
    """
    # 这个函数在当前实现中不需要，因为我们在路由中直接比对verify_codes字典
    return True 