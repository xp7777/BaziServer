from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument
from app import db

users_collection = db.users

class UserModel:
    @staticmethod
    def create_user(phone):
        """创建新用户"""
        user = {
            "phone": phone,
            "createTime": datetime.now(),
            "lastLoginTime": datetime.now(),
            "status": "active"
        }
        result = users_collection.insert_one(user)
        user['_id'] = str(result.inserted_id)
        return user
    
    @staticmethod
    def find_by_phone(phone):
        """通过手机号查找用户"""
        user = users_collection.find_one({"phone": phone})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    @staticmethod
    def find_by_id(user_id):
        """通过ID查找用户"""
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    @staticmethod
    def update_last_login(user_id):
        """更新最后登录时间"""
        result = users_collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": {"lastLoginTime": datetime.now()}},
            return_document=ReturnDocument.AFTER
        )
        if result:
            result['_id'] = str(result['_id'])
        return result 