import hashlib
import time
import random
import string
import requests
import logging
import os

logger = logging.getLogger(__name__)

class WechatJSAPI:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.jsapi_ticket = None
        self.token_expires_at = 0
        self.ticket_expires_at = 0
    
    def get_access_token(self):
        """获取access_token"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                self.token_expires_at = time.time() + data.get('expires_in', 7200) - 300
                logger.info("获取access_token成功")
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {data}")
                return None
        except Exception as e:
            logger.error(f"获取access_token异常: {str(e)}")
            return None
    
    def get_jsapi_ticket(self):
        """获取jsapi_ticket"""
        if self.jsapi_ticket and time.time() < self.ticket_expires_at:
            return self.jsapi_ticket
        
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = f"https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={access_token}&type=jsapi"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if data.get('errcode') == 0:
                self.jsapi_ticket = data['ticket']
                self.ticket_expires_at = time.time() + data.get('expires_in', 7200) - 300
                logger.info("获取jsapi_ticket成功")
                return self.jsapi_ticket
            else:
                logger.error(f"获取jsapi_ticket失败: {data}")
                return None
        except Exception as e:
            logger.error(f"获取jsapi_ticket异常: {str(e)}")
            return None
    
    def generate_signature(self, url):
        """生成JSSDK签名"""
        jsapi_ticket = self.get_jsapi_ticket()
        if not jsapi_ticket:
            return None
        
        timestamp = str(int(time.time()))
        nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        # 构造签名字符串
        sign_str = f"jsapi_ticket={jsapi_ticket}&noncestr={nonce_str}&timestamp={timestamp}&url={url}"
        
        # SHA1签名
        signature = hashlib.sha1(sign_str.encode('utf-8')).hexdigest()
        
        return {
            'appId': self.app_id,
            'timestamp': timestamp,
            'nonceStr': nonce_str,
            'signature': signature
        }

# 创建全局实例
wechat_jsapi = None
try:
    app_id = os.getenv('WECHAT_APP_ID')
    app_secret = os.getenv('WECHAT_APP_SECRET')
    
    if app_id and app_secret:
        wechat_jsapi = WechatJSAPI(app_id, app_secret)
        logger.info("微信JSAPI全局实例创建成功")
    else:
        logger.warning("微信JSAPI配置不完整，无法创建实例")
except Exception as e:
    logger.error(f"微信JSAPI全局实例创建失败: {str(e)}")
