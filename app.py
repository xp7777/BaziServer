from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging
import requests
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 配置JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600 * 24  # 1天过期
jwt = JWTManager(app)

# 配置跨域
CORS(app)

# 连接MongoDB
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 根路由
@app.route('/')
def index():
    return jsonify(message='八字命理AI人生指导系统API服务')

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
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=os.getenv('DEBUG', 'False').lower() == 'true') 