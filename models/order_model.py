from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument
from app import db

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
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
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
        result = orders_collection.find_one_and_update(
            {"_id": ObjectId(order_id)},
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
        
        result = orders_collection.find_one_and_update(
            {"_id": ObjectId(order_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if result:
            result['_id'] = str(result['_id'])
        return result 