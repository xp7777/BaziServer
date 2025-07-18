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
        
        # 只检查是否为明显的占位符
        if app_id.startswith('your_') or app_id == 'your_wechat_open_platform_app_id':
            logging.error(f"微信登录APP_ID未正确配置: {app_id}")
            return jsonify({'code': 500, 'message': '微信登录APP_ID未正确配置'}), 500
        
        # 生成唯一的登录token
        login_token = str(uuid.uuid4())
        
        # 构建微信登录URL - 这个URL会被嵌入到二维码中
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
        
        # 存储登录状态
        login_status[login_token] = {
            'status': 'waiting',
            'created_at': time.time()
        }
        
        logging.info(f"生成登录二维码成功，token: {login_token}")
        
        # 直接返回微信登录URL，让前端使用微信官方的二维码显示方式
        return jsonify({
            'code': 200,
            'message': '二维码生成成功',
            'data': {
                'loginUrl': wechat_login_url,
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

@auth_bp.route('/wechat/callback', methods=['GET'])
def wechat_callback():
    """微信登录回调处理"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')  # 这是我们的login_token
        
        logging.info(f"微信登录回调 - code: {code}, state: {state}")
        
        if not code or not state:
            return "缺少必要参数", 400
        
        # 检查state是否存在
        if state not in login_status:
            return "登录状态已过期", 400
        
        # 获取配置
        app_id = os.getenv('WECHAT_LOGIN_APP_ID')
        app_secret = os.getenv('WECHAT_LOGIN_APP_SECRET')
        
        # 使用code获取access_token
        token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={app_id}&secret={app_secret}&code={code}&grant_type=authorization_code"
        
        logging.info(f"请求access_token: {token_url}")
        token_response = requests.get(token_url)
        token_data = token_response.json()
        
        logging.info(f"access_token响应: {token_data}")
        
        if 'access_token' not in token_data:
            logging.error(f"获取access_token失败: {token_data}")
            return f"获取access_token失败: {token_data.get('errmsg', '未知错误')}", 400
        
        # 获取用户信息
        user_info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={token_data['access_token']}&openid={token_data['openid']}"
        
        logging.info(f"请求用户信息: {user_info_url}")
        user_response = requests.get(user_info_url)
        user_data = user_response.json()
        
        logging.info(f"用户信息响应: {user_data}")
        
        if 'openid' not in user_data:
            logging.error(f"获取用户信息失败: {user_data}")
            return f"获取用户信息失败: {user_data.get('errmsg', '未知错误')}", 400
        
        # 这里应该创建或查找用户，生成JWT token
        # 简化处理，直接生成token
        from flask_jwt_extended import create_access_token
        user_token = create_access_token(identity=user_data['openid'])
        
        # 更新登录状态
        login_status[state] = {
            'status': 'success',
            'userInfo': {
                'openid': user_data['openid'],
                'nickname': user_data.get('nickname', '微信用户'),
                'avatar': user_data.get('headimgurl', '')
            },
            'userToken': user_token,
            'created_at': time.time()
        }
        
        logging.info(f"登录成功，更新状态: {state}")
        
        return """
        <html>
        <head><title>登录成功</title></head>
        <body>
            <h2>登录成功</h2>
            <p>请关闭此页面，返回应用继续操作</p>
            <script>
                // 尝试关闭窗口
                setTimeout(function() {
                    window.close();
                }, 2000);
            </script>
        </body>
        </html>
        """
        
    except Exception as e:
        logging.error(f"微信登录回调处理失败: {str(e)}")
        return f"微信登录回调处理失败: {str(e)}", 500

@auth_bp.route('/wechat/check/<token>', methods=['GET'])
def check_wechat_login(token):
    """检查微信登录状态"""
    try:
        if token not in login_status:
            return jsonify({'code': 404, 'message': '登录token不存在'}), 404
        
        status_info = login_status[token]
        current_time = time.time()
        
        # 检查是否过期（10分钟过期）
        if current_time - status_info['created_at'] > 600:
            # 清理过期的token
            del login_status[token]
            return jsonify({
                'code': 200,
                'message': '二维码已过期',
                'data': {'status': 'expired'}
            })
        
        # 返回当前状态
        if status_info['status'] == 'success':
            return jsonify({
                'code': 200,
                'message': '登录成功',
                'data': {
                    'status': 'success',
                    'userInfo': status_info.get('userInfo'),
                    'token': status_info.get('userToken')
                }
            })
        else:
            return jsonify({
                'code': 200,
                'message': '等待扫码',
                'data': {'status': 'waiting'}
            })
            
    except Exception as e:
        logging.error(f"检查登录状态失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'检查登录状态失败: {str(e)}'}), 500
