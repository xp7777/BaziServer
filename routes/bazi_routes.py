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
        
        # 从数据库获取用户的分析历史
        # 1. 先获取用户的订单
        user_orders = list(orders_collection.find(
            {'userId': user_id, 'status': 'paid'},
            {'_id': 1, 'resultId': 1, 'createdAt': 1, 'orderType': 1}
        ).sort('createdAt', -1))
        
        # 提取所有结果ID
        result_ids = [order.get('resultId') for order in user_orders if order.get('resultId')]
        
        # 2. 直接从数据库获取八字分析结果
        results = []
        bazi_results_collection = db.bazi_results  # 直接使用数据库集合
        
        for result_id in result_ids:
            # 直接查询数据库而不是使用模型方法
            result = bazi_results_collection.find_one({'_id': result_id})
            if result:
                # 提取需要的字段
                birth_time = result.get('birthTime', {})
                results.append({
                    'resultId': result_id,
                    'birthDate': birth_time.get('date', '') if isinstance(birth_time, dict) else '',
                    'gender': result.get('gender', ''),
                    'focusAreas': result.get('focusAreas', []),
                    'createdAt': result.get('createdAt', '')
                })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': results
        })
    
    except Exception as e:
        logging.error(f"获取八字分析历史错误: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500
