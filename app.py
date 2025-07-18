from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging
import requests
import json
import time

# 加载.env文件
load_dotenv()

# 设置日志级别
logging.basicConfig(level=logging.INFO)

# 微信登录配置
os.environ['WECHAT_LOGIN_APP_ID'] = os.getenv('WECHAT_LOGIN_APP_ID', '')
os.environ['WECHAT_LOGIN_APP_SECRET'] = os.getenv('WECHAT_LOGIN_APP_SECRET', '')
os.environ['WECHAT_LOGIN_REDIRECT_URI'] = os.getenv('WECHAT_LOGIN_REDIRECT_URI', 'https://baihexuegong.cn/api/auth/wechat/callback')

# 验证微信登录配置
def validate_wechat_login_vars():
    wechat_login_vars = {
        'WECHAT_LOGIN_APP_ID': os.getenv('WECHAT_LOGIN_APP_ID'),
        'WECHAT_LOGIN_APP_SECRET': os.getenv('WECHAT_LOGIN_APP_SECRET'),
        'WECHAT_LOGIN_REDIRECT_URI': os.getenv('WECHAT_LOGIN_REDIRECT_URI')
    }
    
    logging.info("=== 微信登录配置检查 ===")
    for key, value in wechat_login_vars.items():
        if not value:
            logging.error(f"{key} 未配置")
        else:
            # 对敏感信息进行脱敏显示
            if 'SECRET' in key:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            logging.info(f"{key}: {display_value}")
    
    missing_vars = [key for key, value in wechat_login_vars.items() if not value]
    if missing_vars:
        logging.error(f"微信登录配置缺失: {', '.join(missing_vars)}")
        return False
    
    logging.info("微信登录配置验证通过")
    return True

# 调用验证函数
validate_wechat_login_vars()

# PDF生成使用简易HTML模式
logging.info("PDF生成功能已配置为使用HTML模式")

# 创建Flask应用
app = Flask(__name__, static_folder='static')

# 配置JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
# 从环境变量获取JWT过期时间（单位：小时），默认24小时
jwt_expires_hours = int(os.getenv('JWT_EXPIRES_HOURS', '24'))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600 * jwt_expires_hours
jwt = JWTManager(app)

# 配置跨域
CORS(app)

# 连接MongoDB
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-a70d312fd07b4bce82624bd2373a4db4')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', "https://api.deepseek.com/v1/chat/completions")

# 打印环境变量用于调试(仅在非生产环境)
if os.getenv('ENV', 'development') != 'production':
    logging.info(f"DeepSeek API KEY: {'*' * 5}...{DEEPSEEK_API_KEY[-4:] if DEEPSEEK_API_KEY else ''}")
    logging.info(f"DeepSeek API URL: {DEEPSEEK_API_URL}")
    logging.info(f"MongoDB URI: {mongo_uri.split('@')[-1] if '@' in mongo_uri else mongo_uri}")  # 不显示凭据部分
    logging.info(f"JWT过期时间: {jwt_expires_hours}小时")
    logging.info(f"微信支付商户号: {os.getenv('WECHAT_MCH_ID')}")
    logging.info(f"微信支付证书序列号: {os.getenv('WECHAT_CERT_SERIAL_NO')[:8]}...")
else:
    logging.info("生产环境中，敏感配置信息已隐藏")

# 根路由
@app.route('/')
def index():
    return jsonify(message='八字命理AI人生指导系统API服务')

# 测试页面路由
@app.route('/test')
def test_page():
    return send_from_directory('static', 'bazi_test.html')

# 提供PDF文件的静态访问
@app.route('/pdfs/<path:filename>')
def serve_pdf(filename):
    pdf_dir = os.path.join(os.getcwd(), 'static', 'pdfs')
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir, exist_ok=True)
        
    # 检查文件是否存在
    file_path = os.path.join(pdf_dir, filename)
    if not os.path.isfile(file_path):
        app.logger.error(f"PDF文件不存在: {file_path}")
        return jsonify(code=404, message="PDF文件不存在"), 404
        
    app.logger.info(f"提供PDF文件: {filename}")
    return send_from_directory(pdf_dir, filename, mimetype='application/pdf')

# 在这里导入路由，避免循环导入
def register_blueprints():
    from routes.user_routes import user_bp
    from routes.order_routes import order_bp
    from routes.bazi_routes import bazi_bp
    from routes.auth_routes import auth_bp

    # 注册蓝图
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(order_bp, url_prefix='/api/order')
    app.register_blueprint(bazi_bp, url_prefix='/api/bazi')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify(code=404, message='资源不存在'), 404

@app.errorhandler(500)
def server_error(error):
    app.logger.error(f'服务器错误: {error}')
    return jsonify(code=500, message='服务器内部错误'), 500

# 注册蓝图
register_blueprints()

# 启动应用
if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logging.info(f"应用启动于 {host}:{port}，调试模式: {debug}")
    app.run(host=host, port=port, debug=debug) 
