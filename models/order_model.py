from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument, MongoClient
import os
import logging

# 获取MongoDB URI
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()

orders_collection = db.orders

class OrderModel:
    @staticmethod
    def create_order(user_id, amount):
        """创建新订单"""
        order = {
            "userId": user_id,
            "amount": amount,
            "status": "pending",  # pending, paid, failed
            "paymentMethod": None,  # wechat, alipay
            "createTime": datetime.now(),
            "payTime": None,
            "resultId": None
        }
        result = orders_collection.insert_one(order)
        order['_id'] = str(result.inserted_id)
        return order
    
    @staticmethod
    def find_by_id(order_id):
        """通过ID查找订单"""
        # 尝试使用ObjectId查询
        try:
            logging.info(f"尝试使用ObjectId查询: {order_id}")
            order = orders_collection.find_one({"_id": ObjectId(order_id)})
            if order:
                order['_id'] = str(order['_id'])
                return order
        except Exception as e:
            logging.warning(f"ObjectId查询错误: {str(e)}")
            
        # 如果ObjectId查询失败，尝试使用字符串ID查询
        logging.info(f"尝试使用字符串ID查询: {order_id}")
        order = orders_collection.find_one({"_id": order_id})
        if order:
            order['_id'] = str(order['_id'])
            return order
            
        # 最后尝试使用字符串ID作为订单号查询
        logging.info(f"尝试使用订单ID查询: {order_id}")
        order = orders_collection.find_one({"orderId": order_id})
        if order:
            order['_id'] = str(order['_id'])
        return order
    
    @staticmethod
    def find_by_user(user_id):
        """查找用户的所有订单"""
        orders = list(orders_collection.find({"userId": user_id}))
        for order in orders:
            order['_id'] = str(order['_id'])
        return orders
    
    @staticmethod
    def update_payment(order_id, payment_method):
        """更新支付方式"""
        try:
            result = orders_collection.find_one_and_update(
                {"_id": ObjectId(order_id)},
                {"$set": {"paymentMethod": payment_method}},
                return_document=ReturnDocument.AFTER
            )
        except:
            # 尝试使用字符串ID
            result = orders_collection.find_one_and_update(
                {"_id": order_id},
                {"$set": {"paymentMethod": payment_method}},
                return_document=ReturnDocument.AFTER
            )
            
        if result:
            result['_id'] = str(result['_id'])
        return result
    
    @staticmethod
    def update_status(order_id, status, result_id=None):
        """更新订单状态"""
        update_data = {
            "status": status
        }
        
        if status == "paid":
            update_data["payTime"] = datetime.now()
            if result_id:
                update_data["resultId"] = result_id
        
        try:
            result = orders_collection.find_one_and_update(
                {"_id": ObjectId(order_id)},
                {"$set": update_data},
                return_document=ReturnDocument.AFTER
            )
        except:
            # 尝试使用字符串ID
            result = orders_collection.find_one_and_update(
                {"_id": order_id},
                {"$set": update_data},
                return_document=ReturnDocument.AFTER
            )
        
        if result:
            result['_id'] = str(result['_id'])
        return result 