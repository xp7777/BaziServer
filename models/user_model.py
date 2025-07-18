from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import time

class UserModel:
    def __init__(self):
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
        self.client = MongoClient(mongo_uri)
        self.db = self.client.get_database()
        self.collection = self.db.users
        
        # 创建索引
        self.collection.create_index("wechat_openid", unique=True, sparse=True)
        self.collection.create_index("phone", unique=True, sparse=True)
    
    def find_by_wechat_openid(self, openid):
        """根据微信openid查找用户"""
        return self.collection.find_one({"wechat_openid": openid})
    
    def find_by_id(self, user_id):
        """根据用户ID查找用户"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return self.collection.find_one({"_id": user_id})
    
    def create_wechat_user(self, user_info):
        """创建微信用户"""
        user_info['created_at'] = time.time()
        user_info['updated_at'] = time.time()
        result = self.collection.insert_one(user_info)
        return result.inserted_id
    
    def update_user(self, user_id, update_data):
        """更新用户信息"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        update_data['updated_at'] = time.time()
        return self.collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
