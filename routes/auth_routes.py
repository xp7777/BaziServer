from flask import Blueprint, request, jsonify
import qrcode
import base64
from io import BytesIO
import uuid
import time
import requests
import os
import logging
from urllib.parse import quote

auth_bp = Blueprint('auth', __name__)

# 临时存储登录状态的字典（生产环境建议使用Redis）
login_status = {}

@auth_bp.route('/wechat/qrcode', methods=['POST'])
def generate_wechat_qrcode():
    """生成微信登录二维码"""
    try:
        # 从环境变量重新读取配置
        app_id = os.getenv('WECHAT_LOGIN_APP_ID')
        redirect_uri = os.getenv('WECHAT_LOGIN_REDIRECT_URI')
        
        logging.info(f"读取到的配置 - APP_ID: {app_id}, REDIRECT_URI: {redirect_uri}")
        
        # 检查配置
        if not app_id or not redirect_uri:
            logging.error(f"微信登录配置不完整 - APP_ID: {app_id}, REDIRECT_URI: {redirect_uri}")
            return jsonify({'code': 500, 'message': '微信登录配置不完整，请检查环境变量'}), 500
        
        # 只检查是否为明显的占位符，移除对具体AppID的判断
        if app_id.startswith('your_') or app_id == 'your_wechat_open_platform_app_id':
            logging.error(f"微信登录APP_ID未正确配置: {app_id}")
            return jsonify({'code': 500, 'message': '微信登录APP_ID未正确配置'}), 500
        
        # 生成唯一的登录token
        login_token = str(uuid.uuid4())
        
        # 构建微信登录URL
        redirect_uri_encoded = quote(redirect_uri, safe='')
        wechat_login_url = (
            f"https://open.weixin.qq.com/connect/qrconnect?"
            f"appid={app_id}&"
            f"redirect_uri={redirect_uri_encoded}&"
            f"response_type=code&"
            f"scope=snsapi_login&"
            f"state={login_token}#wechat_redirect"
        )
        
        logging.info(f"生成的微信登录URL: {wechat_login_url}")
        
        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(wechat_login_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # 存储登录状态
        login_status[login_token] = {
            'status': 'waiting',
            'created_at': time.time()
        }
        
        logging.info(f"生成登录二维码成功，token: {login_token}")
        
        return jsonify({
            'code': 200,
            'message': '二维码生成成功',
            'data': {
                'qrCodeUrl': f"data:image/png;base64,{img_str}",
                'token': login_token,
                'debug_info': {
                    'app_id': app_id,
                    'redirect_uri': redirect_uri
                }
            }
        })
        
    except Exception as e:
        logging.error(f"生成二维码失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'生成二维码失败: {str(e)}'}), 500

@auth_bp.route('/wechat/check/<token>', methods=['GET'])
def check_login_status(token):
    """检查微信登录状态"""
    try:
        if token not in login_status:
            return jsonify({'code': 404, 'message': '登录token不存在'}), 404
        
        status_info = login_status[token]
        
        # 检查是否过期（5分钟过期）
        if time.time() - status_info['created_at'] > 300:
            del login_status[token]
            return jsonify({
                'code': 200,
                'data': {'status': 'expired'}
            })
        
        return jsonify({
            'code': 200,
            'data': {
                'status': status_info['status'],
                'userInfo': status_info.get('userInfo'),
                'token': status_info.get('userToken')
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'检查登录状态失败: {str(e)}'}), 500

@auth_bp.route('/wechat/callback', methods=['GET'])
def wechat_callback():
    """微信登录回调处理"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')  # 这是我们的login_token
        
        if not code or not state:
            return jsonify({'code': 400, 'message': '缺少必要参数'}), 400
        
        # 使用code获取access_token
        token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid=YOUR_APPID&secret=YOUR_SECRET&code={code}&grant_type=authorization_code"
        token_response = requests.get(token_url)
        token_data = token_response.json()
        
        if 'access_token' not in token_data:
            return jsonify({'code': 400, 'message': '获取access_token失败'}), 400
        
        # 获取用户信息
        user_info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={token_data['access_token']}&openid={token_data['openid']}"
        user_response = requests.get(user_info_url)
        user_data = user_response.json()
        
        # 更新登录状态
        if state in login_status:
            # 这里应该创建或查找用户，生成JWT token
            user_token = create_access_token(identity=user_data['openid'])
            
            login_status[state] = {
                'status': 'success',
                'userInfo': {
                    'openid': user_data['openid'],
                    'nickname': user_data['nickname'],
                    'avatar': user_data['headimgurl']
                },
                'userToken': user_token,
                'created_at': time.time()
            }
        
        return "登录成功，请关闭此页面"
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'微信登录回调处理失败: {str(e)}'}), 500

