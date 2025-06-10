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
        # 检查是否带有RES前缀
        original_id = order_id
        if order_id.startswith('RES'):
            logging.info(f"检测到RES前缀，尝试去掉前缀: {order_id}")
            order_id = order_id[3:]  # 去掉RES前缀
            logging.info(f"去掉前缀后的订单ID: {order_id}")
        
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
        
        # 如果去掉前缀后仍然找不到，尝试使用原始ID(包含RES前缀)查询
        if original_id != order_id:
            logging.info(f"尝试使用原始ID(包含RES前缀)查询: {original_id}")
            try:
                order = orders_collection.find_one({"_id": original_id})
                if order:
                    order['_id'] = str(order['_id'])
                    return order
            except Exception:
                pass
        
        return None
    
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
    
    @staticmethod
    def find_by_result_id_and_type(result_id, order_type):
        """根据结果ID和订单类型查找订单"""
        logging.info(f"查询订单: resultId={result_id}, orderType={order_type}")
        
        try:
            # 尝试查询
            orders = list(orders_collection.find({
                "resultId": result_id,
                "orderType": order_type
            }))
            
            logging.info(f"查询结果: 找到{len(orders)}个订单")
            
            # 转换ObjectId为字符串
            for order in orders:
                if '_id' in order:
                    order['_id'] = str(order['_id'])
            
            return orders
        except Exception as e:
            logging.error(f"查询订单出错: {str(e)}")
            # 返回空列表而不是抛出异常
            return []
    
    @staticmethod
    def insert(order):
        """插入订单"""
        orders_collection.insert_one(order)
        return order
    
    @staticmethod
    def get_order(order_id):
        """通过订单ID获取订单信息"""
        try:
            logging.info(f"获取订单: {order_id}")
            order = orders_collection.find_one({"_id": order_id})
            if order:
                # 如果_id是ObjectId，转换为字符串
                if isinstance(order['_id'], ObjectId):
                    order['_id'] = str(order['_id'])
                return order
            else:
                logging.warning(f"未找到订单: {order_id}")
                return None
        except Exception as e:
            logging.error(f"获取订单失败: {str(e)}")
            return None
    
    @staticmethod
    def update_order_status(order_id, status):
        """更新订单状态"""
        try:
            logging.info(f"更新订单状态: {order_id} -> {status}")
            update_data = {
                "status": status
            }
            
            if status == "paid":
                update_data["payTime"] = datetime.now()
            
            result = orders_collection.update_one(
                {"_id": order_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"更新订单状态失败: {str(e)}")
            return False
    
    @staticmethod
    def update_order_result_id(order_id, result_id):
        """更新订单关联的结果ID"""
        try:
            logging.info(f"更新订单结果ID: {order_id} -> {result_id}")
            result = orders_collection.update_one(
                {"_id": order_id},
                {"$set": {"resultId": result_id, "updateTime": datetime.now()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"更新订单结果ID失败: {str(e)}")
            return False 