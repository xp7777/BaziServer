from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.bazi_result_model import BaziResultModel
from models.order_model import OrderModel
import logging
import os
from pymongo import MongoClient

# 添加数据库连接
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()
orders_collection = db.orders  # 添加这行

bazi_bp = Blueprint('bazi', __name__)

@bazi_bp.route('/history', methods=['GET'])
@jwt_required()
def get_user_history():
    """获取用户的八字分析历史记录"""
    try:
        user_id = get_jwt_identity()
        
        # 从数据库获取用户的已支付订单，包含更多字段
        user_orders = list(orders_collection.find(
            {'userId': user_id, 'status': 'paid'},
            {
                '_id': 1, 
                'resultId': 1, 
                'createdAt': 1, 
                'createTime': 1,  # 添加这个字段
                'orderType': 1,
                'birthDate': 1,   # 从订单中获取出生日期
                'birthTime': 1,   # 从订单中获取出生时间
                'gender': 1,      # 从订单中获取性别
                'focusAreas': 1   # 从订单中获取关注领域
            }
        ).sort('createdAt', -1))
        
        # 格式化输出
        results = []
        for order in user_orders:
            if order.get('resultId'):
                # 优先使用 createdAt，如果没有则使用 createTime
                created_time = order.get('createdAt') or order.get('createTime')
                
                results.append({
                    'resultId': order.get('resultId'),
                    'birthDate': order.get('birthDate', ''),
                    'gender': order.get('gender', ''),
                    'focusAreas': order.get('focusAreas', []),
                    'createdAt': created_time
                })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': results
        })
    
    except Exception as e:
        logging.error(f"获取八字分析历史错误: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500
