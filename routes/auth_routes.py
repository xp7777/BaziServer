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
        
        # 生成二维码图片
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
        img.save(buffered)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        logging.info(f"生成登录二维码成功，token: {login_token}")

        # 返回包含二维码图片的响应
        return jsonify({
            'code': 200,
            'message': '二维码生成成功',
            'data': {
                'loginUrl': wechat_login_url,
                'token': login_token,
                'qrCodeImage': f"data:image/png;base64,{img_str}",
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
        
        logging.info(f"微信登录回调开始 - code: {code}, state: {state}")
        
        if not code or not state:
            logging.error("缺少必要参数")
            return render_callback_page("缺少必要参数", False)
        
        # 检查state是否存在
        if state not in login_status:
            logging.error(f"登录状态不存在: {state}")
            return render_callback_page("登录状态已过期", False)
        
        # 获取配置
        app_id = os.getenv('WECHAT_LOGIN_APP_ID')
        app_secret = os.getenv('WECHAT_LOGIN_APP_SECRET')
        
        logging.info(f"使用配置 - APP_ID: {app_id}, APP_SECRET: {'*' * len(app_secret) if app_secret else 'None'}")
        
        if not app_id or not app_secret:
            logging.error("微信登录配置不完整")
            return render_callback_page("微信登录配置不完整", False)
        
        # 使用code获取access_token
        token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={app_id}&secret={app_secret}&code={code}&grant_type=authorization_code"
        
        logging.info(f"请求access_token: {token_url}")
        
        try:
            token_response = requests.get(token_url, timeout=10)
            token_data = token_response.json()
            logging.info(f"access_token响应: {token_data}")
        except Exception as e:
            logging.error(f"请求access_token失败: {str(e)}")
            return render_callback_page(f"请求access_token失败: {str(e)}", False)
        
        if 'access_token' not in token_data:
            error_msg = token_data.get('errmsg', '未知错误')
            logging.error(f"获取access_token失败: {error_msg}")
            return render_callback_page(f"获取access_token失败: {error_msg}", False)
        
        # 获取用户信息
        user_info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={token_data['access_token']}&openid={token_data['openid']}&lang=zh_CN"
        
        logging.info(f"请求用户信息: {user_info_url}")
        
        try:
            user_response = requests.get(user_info_url, timeout=10)
            user_data = user_response.json()
            logging.info(f"用户信息响应: {user_data}")
        except Exception as e:
            logging.error(f"请求用户信息失败: {str(e)}")
            return render_callback_page(f"请求用户信息失败: {str(e)}", False)
        
        if 'openid' not in user_data:
            error_msg = user_data.get('errmsg', '未知错误')
            logging.error(f"获取用户信息失败: {error_msg}")
            return render_callback_page(f"获取用户信息失败: {error_msg}", False)
        
        # 生成JWT token
        try:
            from flask_jwt_extended import create_access_token
            user_token = create_access_token(identity=user_data['openid'])
            logging.info(f"生成JWT token成功")
        except Exception as e:
            logging.error(f"生成JWT token失败: {str(e)}")
            return render_callback_page(f"生成JWT token失败: {str(e)}", False)
        
        # 更新登录状态
        try:
            login_status[state] = {
                'status': 'success',
                'userInfo': {
                    'openid': user_data['openid'],
                    'nickname': user_data.get('nickname', '微信用户'),
                    'avatar': user_data.get('headimgurl', ''),
                    'sex': user_data.get('sex', 0),
                    'city': user_data.get('city', ''),
                    'province': user_data.get('province', ''),
                    'country': user_data.get('country', '')
                },
                'userToken': user_token,
                'created_at': time.time()
            }
            logging.info(f"登录成功，更新状态: {state}")
        except Exception as e:
            logging.error(f"更新登录状态失败: {str(e)}")
            return render_callback_page(f"更新登录状态失败: {str(e)}", False)
        
        # 返回成功页面
        logging.info("准备返回成功页面")
        return render_callback_page("登录成功", True, state)
        
    except Exception as e:
        logging.error(f"微信登录回调处理异常: {str(e)}", exc_info=True)
        return render_callback_page(f"系统错误: {str(e)}", False)

def render_callback_page(message, success=False, token=None):
    """渲染回调页面"""
    logging.info(f"渲染回调页面 - message: {message}, success: {success}, token: {token}")
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>微信登录结果</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            text-align: center; 
            padding: 50px 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            background: white;
            border-radius: 15px;
            padding: 40px 30px;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .success {{ color: #52c41a; }}
        .error {{ color: #ff4d4f; }}
        .icon {{ font-size: 64px; margin-bottom: 20px; }}
        .message {{ font-size: 20px; font-weight: 600; margin-bottom: 15px; }}
        .tips {{ color: #666; font-size: 14px; line-height: 1.5; margin-top: 20px; }}
        .countdown {{ color: #1890ff; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">{'🎉' if success else '❌'}</div>
        <div class="message {'success' if success else 'error'}">{message}</div>
        <div class="tips">
            {'窗口将在 <span class="countdown" id="countdown">3</span> 秒后自动关闭' if success else '请关闭此窗口重试'}
        </div>
    </div>
    
    <script>
        console.log('微信登录回调页面加载完成');
        console.log('登录结果:', {str(success).lower()});
        console.log('Token:', '{token or ''}');
        
        // 向父窗口发送消息
        if (window.opener && !window.opener.closed) {{
            console.log('向父窗口发送登录结果消息');
            try {{
                window.opener.postMessage({{
                    type: 'WECHAT_LOGIN_RESULT',
                    success: {str(success).lower()},
                    message: '{message}',
                    token: '{token or ''}'
                }}, '*');
                console.log('消息发送成功');
            }} catch (e) {{
                console.error('发送消息失败:', e);
            }}
        }} else {{
            console.log('没有父窗口或父窗口已关闭');
        }}
        
        // 倒计时关闭窗口
        let countdown = 3;
        const countdownEl = document.getElementById('countdown');
        
        if (countdownEl) {{
            const timer = setInterval(() => {{
                countdown--;
                countdownEl.textContent = countdown;
                
                if (countdown <= 0) {{
                    clearInterval(timer);
                    console.log('准备关闭窗口');
                    try {{
                        window.close();
                    }} catch (e) {{
                        console.error('关闭窗口失败:', e);
                        document.querySelector('.tips').innerHTML = '请手动关闭此窗口';
                    }}
                }}
            }}, 1000);
        }}
    </script>
</body>
</html>"""
    
    logging.info("HTML内容生成完成，准备返回响应")
    return html_content


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

@auth_bp.route('/wechatPhone/authorize', methods=['POST'])
def wechat_phone_authorize():
    """生成微信网页授权链接"""
    try:
        # 获取手机端微信登录配置
        app_id = os.getenv('WECHAT_PHONE_LOGIN_APP_ID')
        redirect_uri = os.getenv('WECHAT_PHONE_LOGIN_REDIRECT_URI')
        
        logging.info(f"手机端微信登录配置 - APP_ID: {app_id}, REDIRECT_URI: {redirect_uri}")
        
        if not app_id or not redirect_uri:
            logging.error("手机端微信登录配置不完整")
            return jsonify({'code': 500, 'message': '微信登录配置不完整'}), 500
        
        # 生成state参数
        state = str(uuid.uuid4())
        
        # 构建微信网页授权URL
        from urllib.parse import quote
        redirect_uri_encoded = quote(redirect_uri, safe='')
        authorize_url = (
            f"https://open.weixin.qq.com/connect/oauth2/authorize?"
            f"appid={app_id}&"
            f"redirect_uri={redirect_uri_encoded}&"
            f"response_type=code&"
            f"scope=snsapi_userinfo&"
            f"state={state}#wechat_redirect"
        )
        
        # 存储授权状态
        login_status[state] = {
            'status': 'waiting',
            'type': 'phone',
            'created_at': time.time()
        }
        
        logging.info(f"生成手机端微信授权URL: {authorize_url}")
        
        return jsonify({
            'code': 200,
            'message': '授权链接生成成功',
            'data': {
                'authorizeUrl': authorize_url,
                'state': state
            }
        })
        
    except Exception as e:
        logging.error(f"生成手机端微信授权链接失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'生成授权链接失败: {str(e)}'}), 500

@auth_bp.route('/wechatPhone/callback', methods=['GET', 'POST'])
def wechat_phone_callback():
    """手机端微信网页授权回调"""
    try:
        if request.method == 'GET':
            # 微信回调的GET请求，重定向到前端页面
            code = request.args.get('code')
            state = request.args.get('state')
            
            if code and state:
                # 重定向到前端登录页面，携带授权码
                return redirect(f"https://baihexuegong.cn/login?code={code}&state={state}")
            else:
                return redirect("https://baihexuegong.cn/login?error=授权失败")
        
        # POST请求处理授权码
        data = request.json
        code = data.get('code')
        state = data.get('state')
        
        logging.info(f"手机端微信授权回调 - code: {code}, state: {state}")
        
        if not code or not state:
            return jsonify({'code': 400, 'message': '缺少授权码或状态参数'}), 400
        
        # 检查state是否存在
        if state not in login_status:
            return jsonify({'code': 400, 'message': '授权状态已过期'}), 400
        
        # 获取配置
        app_id = os.getenv('WECHAT_PHONE_LOGIN_APP_ID')
        app_secret = os.getenv('WECHAT_PHONE_LOGIN_APP_SECRET')
        
        if not app_id or not app_secret:
            return jsonify({'code': 500, 'message': '微信登录配置不完整'}), 500
        
        # 获取access_token
        token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={app_id}&secret={app_secret}&code={code}&grant_type=authorization_code"
        
        token_response = requests.get(token_url, timeout=10)
        token_data = token_response.json()
        
        if 'access_token' not in token_data:
            error_msg = token_data.get('errmsg', '获取access_token失败')
            return jsonify({'code': 400, 'message': error_msg}), 400
        
        # 获取用户信息
        user_info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={token_data['access_token']}&openid={token_data['openid']}&lang=zh_CN"
        
        user_response = requests.get(user_info_url, timeout=10)
        user_data = user_response.json()
        
        if 'openid' not in user_data:
            error_msg = user_data.get('errmsg', '获取用户信息失败')
            return jsonify({'code': 400, 'message': error_msg}), 400
        
        # 生成用户token
        user_token = str(uuid.uuid4())
        
        # 清理登录状态
        del login_status[state]
        
        return jsonify({
            'code': 200,
            'message': '授权登录成功',
            'data': {
                'userInfo': {
                    'openid': user_data['openid'],
                    'nickname': user_data.get('nickname', '微信用户'),
                    'avatar': user_data.get('headimgurl', ''),
                    'sex': user_data.get('sex', 0),
                    'city': user_data.get('city', ''),
                    'province': user_data.get('province', ''),
                    'country': user_data.get('country', '')
                },
                'token': user_token
            }
        })
        
    except Exception as e:
        logging.error(f"手机端微信授权回调处理失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'授权处理失败: {str(e)}'}), 500
