from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import random
import os
from models.user_model import UserModel
from utils.sms_service import send_verify_code, verify_code

user_bp = Blueprint('user', __name__)

# 模拟验证码存储（生产环境应使用Redis等）
verify_codes = {}

@user_bp.route('/sendVerifyCode', methods=['POST'])
def send_verify_code_route():
    """发送验证码"""
    data = request.json
    phone = data.get('phone')
    
    if not phone:
        return jsonify(code=400, message="请提供手机号码"), 400
    
    # 生成6位随机验证码
    code = ''.join(random.choices('0123456789', k=6))
    
    # 保存验证码（生产环境应使用Redis等）
    verify_codes[phone] = code
    
    # 如果配置了短信服务，则发送短信
    if os.getenv('SMS_ACCESS_KEY'):
        send_verify_code(phone, code)
        return jsonify(code=200, message="验证码已发送")
    else:
        # 开发环境直接返回验证码
        return jsonify(code=200, message="验证码已发送", data={"code": code})

@user_bp.route('/login', methods=['POST'])
def login():
    """用户登录/注册"""
    data = request.json
    phone = data.get('phone')
    verify_code = data.get('verifyCode')
    
    if not phone or not verify_code:
        return jsonify(code=400, message="请提供手机号码和验证码"), 400
    
    # 验证验证码
    if verify_codes.get(phone) != verify_code:
        return jsonify(code=400, message="验证码错误"), 400
    
    # 清除验证码
    if phone in verify_codes:
        del verify_codes[phone]
    
    # 查找用户
    user = UserModel.find_by_phone(phone)
    
    # 如果用户不存在，创建新用户
    if not user:
        user = UserModel.create_user(phone)
    else:
        # 更新最后登录时间
        UserModel.update_last_login(user['_id'])
    
    # 创建JWT令牌
    access_token = create_access_token(identity=user['_id'])
    
    return jsonify(
        code=200,
        message="登录成功",
        data={
            "token": access_token,
            "userId": user['_id']
        }
    )

@user_bp.route('/info', methods=['GET'])
@jwt_required()
def get_info():
    """获取用户信息"""
    user_id = get_jwt_identity()
    user = UserModel.find_by_id(user_id)
    
    if not user:
        return jsonify(code=404, message="用户不存在"), 404
    
    return jsonify(
        code=200,
        message="成功",
        data={
            "userId": user['_id'],
            "phone": user['phone'],
            "createTime": user['createTime'].isoformat()
        }
    ) 