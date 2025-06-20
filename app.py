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

# 配置日志。
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 尝试加载环境变量，但忽略错误
try:
    load_dotenv()
    logging.info("成功加载.env文件")
except Exception as e:
    logging.warning(f".env文件加载失败，使用默认值: {str(e)}")

# 设置微信支付环境变量
os.environ['WECHAT_MCH_ID'] = os.getenv('WECHAT_MCH_ID', '1706110646') #微信支付商户号
os.environ['WECHAT_CERT_SERIAL_NO'] = os.getenv('WECHAT_CERT_SERIAL_NO', '69D653B5EB73DB2B9A5175FEF05AAFE6EDD66083')  #微信支付API证书序列号
os.environ['WECHAT_APP_ID'] = os.getenv('WECHAT_APP_ID', 'wxa7b459b6aa6e3ad1')  # 替换为您的真实AppID

# V2 API密钥配置（保留向后兼容）
# 例如: os.environ['WECHAT_API_KEY'] = os.getenv('WECHAT_API_KEY', '3Yf8jzZqK9XW6bNcRv7d2pLtH1sGhJ9P')
os.environ['WECHAT_API_KEY'] = os.getenv('WECHAT_API_KEY', '3Yf8jzZqK9XW6bNcRv7d2pLtH1sGhJ9P')

# V3 API配置
os.environ['WECHAT_NOTIFY_URL'] = os.getenv('WECHAT_NOTIFY_URL', 'https://wlmqhxswyxgs.top/api/order/wechat/notify/v3') #微信支付V3回调地址
os.environ['WECHAT_CERT_DIR'] = os.getenv('WECHAT_CERT_DIR', './cert')  # 证书存放目录
os.environ['WECHAT_API_V3_KEY'] = os.getenv('WECHAT_API_V3_KEY', '')  # V3 API密钥，用于解密回调报文

# 根据环境变量设置回调URL，优先使用配置的域名，如果没有，则使用本地地址
if os.getenv('ENV', 'development') == 'development':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    # 如果是本地开发环境，可以使用内网穿透服务如ngrok提供外部访问URL
    os.environ['WECHAT_NOTIFY_URL'] = os.getenv('WECHAT_NOTIFY_URL', f'http://{host}:{port}/api/order/wechat/notify/v3')

# 验证关键环境变量
def validate_env_vars():
    critical_vars = {
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
        'MONGODB_URI': os.getenv('MONGODB_URI'),
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY')
    }
    
    missing_vars = [key for key, value in critical_vars.items() if not value]
    
    if missing_vars:
        logging.warning(f"以下关键环境变量未设置，将使用默认值: {', '.join(missing_vars)}")
    
    # 验证API密钥格式
    api_key = os.getenv('DEEPSEEK_API_KEY', '')
    if api_key and not api_key.startswith('sk-'):
        logging.warning("DEEPSEEK_API_KEY格式可能不正确，应以'sk-'开头")
    
    # 验证微信支付配置
    wechat_vars = {
        'WECHAT_MCH_ID': os.getenv('WECHAT_MCH_ID'),
        'WECHAT_CERT_SERIAL_NO': os.getenv('WECHAT_CERT_SERIAL_NO'),
        'WECHAT_APP_ID': os.getenv('WECHAT_APP_ID'),
        'WECHAT_API_KEY': os.getenv('WECHAT_API_KEY')
    }
    
    for key, value in wechat_vars.items():
        if value and (value.startswith('需要配置') or value.endswith('需要配置')):
            logging.warning(f"{key}未正确配置，部分支付功能可能不可用")

# 验证环境变量
validate_env_vars()

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

    # 注册蓝图
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(order_bp, url_prefix='/api/order')
    app.register_blueprint(bazi_bp, url_prefix='/api/bazi')

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