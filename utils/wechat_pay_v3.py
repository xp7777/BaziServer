import os
import time
import json
import uuid
import base64
import logging
import requests
from datetime import datetime
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
import qrcode
from io import BytesIO

logger = logging.getLogger(__name__)

class WechatPayV3:
    def __init__(self):
        """初始化微信支付V3接口"""
        self.app_id = os.getenv('WECHAT_APP_ID')
        self.mch_id = os.getenv('WECHAT_MCH_ID')
        self.notify_url = os.getenv('WECHAT_NOTIFY_URL')
        self.cert_loaded = False
        self.private_key = None
        self.serial_no = os.getenv('WECHAT_CERT_SERIAL_NO')
        
        # 加载商户证书私钥
        cert_dir = os.getenv('WECHAT_CERT_DIR', './cert')
        key_path = os.path.join(cert_dir, 'apiclient_key.pem')
        cert_path = os.path.join(cert_dir, 'apiclient_cert.pem')
        
        try:
            if os.path.exists(key_path) and os.path.exists(cert_path):
                # 加载商户私钥
                with open(key_path, 'rb') as f:
                    self.private_key = load_pem_private_key(
                        f.read(),
                        password=None,
                        backend=default_backend()
                    )
                
                # 加载商户证书
                with open(cert_path, 'rb') as f:
                    cert = load_pem_x509_certificate(f.read(), backend=default_backend())
                    self.serial_no = cert.serial_number.to_bytes((cert.serial_number.bit_length() + 7) // 8, byteorder='big').hex().upper()
                
                self.cert_loaded = True
                logger.info(f"成功加载微信支付证书，商户号={self.mch_id}, 证书序列号={self.serial_no}")
            else:
                logger.warning(f"未找到微信支付证书文件，无法使用完整功能: {key_path}, {cert_path}")
                logger.warning("将使用环境变量中的证书序列号")
        except Exception as e:
            logger.error(f"加载微信支付证书失败: {str(e)}")
            logger.exception("证书加载异常详情:")
            
        # 微信支付平台证书，用于验证回调
        self.platform_cert = None
        
        # API基础URL
        self.base_url = "https://api.mch.weixin.qq.com"
        
        logger.info(f"初始化微信支付V3: 商户号={self.mch_id}, 应用ID={self.app_id}")
    
    def _generate_sign(self, method, url_path, data=None):
        """生成签名"""
        if not self.cert_loaded or not self.private_key:
            logger.error("无法生成签名，证书未正确加载")
            return None
            
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4()).replace('-', '')
        
        # 构造签名字符串
        sign_str = method + "\n"
        sign_str += url_path + "\n"
        sign_str += timestamp + "\n"
        sign_str += nonce + "\n"
        
        if data:
            if isinstance(data, dict):
                sign_str += json.dumps(data) + "\n"
            else:
                sign_str += data + "\n"
        else:
            sign_str += "\n"
            
        # 使用私钥签名
        signature = self.private_key.sign(
            sign_str.encode('utf-8'),
            PKCS1v15(),
            SHA256()
        )
        
        # Base64编码
        signature = base64.b64encode(signature).decode('utf-8')
        
        # 构造Authorization
        auth = f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",'
        auth += f'serial_no="{self.serial_no}",'
        auth += f'nonce_str="{nonce}",'
        auth += f'timestamp="{timestamp}",'
        auth += f'signature="{signature}"'
        
        return auth
    
    def create_jsapi_order(self, out_trade_no, amount, description, openid):
        """创建JSAPI/小程序支付订单"""
        if not self.cert_loaded:
            logger.warning("未加载正确的微信支付证书，无法使用JSAPI支付")
            return {
                "code": "FAIL",
                "message": "证书未加载，无法使用API"
            }
            
        url_path = "/v3/pay/transactions/jsapi"
        data = {
            "appid": self.app_id,
            "mchid": self.mch_id,
            "description": description,
            "out_trade_no": out_trade_no,
            "notify_url": self.notify_url,
            "amount": {
                "total": amount,
                "currency": "CNY"
            },
            "payer": {
                "openid": openid
            }
        }
        
        # 生成签名
        auth = self._generate_sign("POST", url_path, data)
        if not auth:
            logger.error("生成签名失败")
            return {
                "code": "FAIL",
                "message": "生成签名失败"
            }

        # 发送请求
        try:
            response = requests.post(
                self.base_url + url_path,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": auth
                }
            )
            
            # 返回结果
            result = response.json()
            logger.info(f"微信JSAPI支付下单结果: {result}")
            
            if response.status_code == 200 and "prepay_id" in result:
                return {
                    "code": "SUCCESS",
                    "prepay_id": result["prepay_id"]
                }
            else:
                logger.error(f"微信JSAPI支付下单失败: {result}")
                return {
                    "code": "FAIL",
                    "message": result.get("message", "未知错误")
                }
        except Exception as e:
            logger.exception(f"微信JSAPI支付下单异常: {str(e)}")
            return {
                "code": "FAIL",
                "message": str(e)
            }
    
    def create_native_order(self, out_trade_no, amount, description, return_qr_image=False):
        """创建Native支付订单（扫码支付）"""
        if not self.cert_loaded:
            logger.warning("未加载正确的微信支付证书，降级为V2接口或模拟支付")
            # 返回失败但提供模拟二维码
            if return_qr_image:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                mock_url = f"https://example.com/mock_pay?order_id={out_trade_no}" 
                qr.add_data(mock_url)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffered = BytesIO()
                img.save(buffered)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                return {
                    "code": "FAIL",
                    "message": "证书未加载，使用模拟支付",
                    "code_url": mock_url,
                    "qr_image": f"data:image/png;base64,{img_str}",
                    "error": "证书未加载"
                }
            return {
                "code": "FAIL",
                "message": "证书未加载，无法使用API",
                "error": "证书未加载"
            }
            
        url_path = "/v3/pay/transactions/native"
        data = {
            "appid": self.app_id,
            "mchid": self.mch_id,
            "description": description,
            "out_trade_no": out_trade_no,
            "notify_url": self.notify_url,
            "amount": {
                "total": amount,
                "currency": "CNY"
            }
        }
        
        # 生成签名
        auth = self._generate_sign("POST", url_path, data)
        if not auth:
            logger.error("生成签名失败")
            return {
                "code": "FAIL",
                "message": "生成签名失败"
            }
        
        # 发送请求
        try:
            response = requests.post(
                self.base_url + url_path,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": auth
                }
            )
            
            # 返回结果
            result = response.json()
            logger.info(f"微信Native支付下单结果: {result}")
            
            if response.status_code == 200 and "code_url" in result:
                code_url = result["code_url"]
                
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
                        "code": "SUCCESS",
                        "code_url": code_url,
                        "qr_image": f"data:image/png;base64,{img_str}"
                    }
                
                return {
                    "code": "SUCCESS",
                    "code_url": code_url
                }
            else:
                logger.error(f"微信Native支付下单失败: {result}")
                return {
                    "code": "FAIL",
                    "message": result.get("message", "未知错误")
                }
        except Exception as e:
            logger.exception(f"微信Native支付下单异常: {str(e)}")
            return {
                "code": "FAIL",
                "message": str(e)
            }
    
    def query_order(self, out_trade_no):
        """查询订单状态"""
        if not self.cert_loaded:
            logger.warning("未加载正确的微信支付证书，无法查询订单")
            return {
                "code": "FAIL",
                "message": "证书未加载，无法使用API"
            }
            
        url_path = f"/v3/pay/transactions/out-trade-no/{out_trade_no}?mchid={self.mch_id}"
        
        # 生成签名
        auth = self._generate_sign("GET", url_path)
        if not auth:
            logger.error("生成签名失败")
            return {
                "code": "FAIL",
                "message": "生成签名失败"
            }
            
        # 发送请求
        try:
            response = requests.get(
                self.base_url + url_path,
                headers={
                    "Accept": "application/json",
                    "Authorization": auth
                }
            )
            
            # 返回结果
            result = response.json()
            logger.info(f"微信订单查询结果: {result}")
            
            if response.status_code == 200:
                trade_state = result.get("trade_state")
                return {
                    "code": "SUCCESS",
                    "trade_state": trade_state,
                    "is_paid": trade_state == "SUCCESS",
                    "transaction_id": result.get("transaction_id"),
                    "amount": result.get("amount", {}).get("total"),
                    "payer": result.get("payer")
                }
            else:
                logger.error(f"微信订单查询失败: {result}")
                return {
                    "code": "FAIL",
                    "message": result.get("message", "未知错误")
                }
        except Exception as e:
            logger.exception(f"微信订单查询异常: {str(e)}")
            return {
                "code": "FAIL",
                "message": str(e)
            }
    
    def verify_notify(self, headers, body):
        """验证回调通知"""
        if not self.cert_loaded:
            logger.warning("未加载正确的微信支付证书，无法验证回调通知")
            return None
            
        try:
            # 解析通知数据
            data = json.loads(body)
            logger.debug(f"微信支付回调数据: {data}")
            
            # TODO: 验证签名和解密数据
            # 当前简化处理，仅返回数据
            return data
        except Exception as e:
            logger.error(f"解析回调数据失败: {str(e)}")
            return None
    
    def get_jsapi_params(self, prepay_id):
        """获取JSAPI支付参数，用于前端调起支付"""
        timestamp = str(int(time.time()))
        nonce_str = str(uuid.uuid4()).replace('-', '')
        package = f"prepay_id={prepay_id}"
        
        # 构造签名字符串
        sign_str = f"{self.app_id}\n{timestamp}\n{nonce_str}\n{package}\n"
        
        # 签名
        signature = self.private_key.sign(
            sign_str.encode('utf-8'),
            PKCS1v15(),
            SHA256()
        )
        
        # Base64编码
        sign = base64.b64encode(signature).decode('utf-8')
        
        return {
            "appId": self.app_id,
            "timeStamp": timestamp,
            "nonceStr": nonce_str,
            "package": package,
            "signType": "RSA",
            "paySign": sign
        }

# 创建全局实例
wechat_pay_v3 = None
try:
    wechat_pay_v3 = WechatPayV3()
    logger.info("微信支付V3接口全局实例创建成功")
except Exception as e:
    logger.error(f"微信支付V3接口全局实例创建失败: {str(e)}")
    logger.exception("初始化异常详情:") 