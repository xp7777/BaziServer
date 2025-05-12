from datetime import datetime
from bson import ObjectId
from app import db

bazi_results_collection = db.bazi_results

class BaziResultModel:
    @staticmethod
    def create_result(user_id, order_id, gender, birth_time, focus_areas):
        """创建新的八字分析结果"""
        result = {
            "userId": user_id,
            "orderId": order_id,
            "gender": gender,
            "birthTime": birth_time,
            "focusAreas": focus_areas,
            "baziData": None,
            "aiAnalysis": {},
            "pdfUrl": None,
            "createTime": datetime.now()
        }
        
        inserted = bazi_results_collection.insert_one(result)
        result['_id'] = str(inserted.inserted_id)
        return result
    
    @staticmethod
    def find_by_id(result_id):
        """通过ID查找结果"""
        result = bazi_results_collection.find_one({"_id": ObjectId(result_id)})
        if result:
            result['_id'] = str(result['_id'])
        return result
    
    @staticmethod
    def find_by_user(user_id):
        """查找用户的所有结果"""
        results = list(bazi_results_collection.find({"userId": user_id}))
        for result in results:
            result['_id'] = str(result['_id'])
        return results
    
    @staticmethod
    def update_bazi_data(result_id, bazi_data):
        """更新八字数据"""
        bazi_results_collection.update_one(
            {"_id": ObjectId(result_id)},
            {"$set": {"baziData": bazi_data}}
        )
        return BaziResultModel.find_by_id(result_id)
    
    @staticmethod
    def update_ai_analysis(result_id, area, analysis):
        """更新AI分析结果"""
        bazi_results_collection.update_one(
            {"_id": ObjectId(result_id)},
            {"$set": {f"aiAnalysis.{area}": analysis}}
        )
        return BaziResultModel.find_by_id(result_id)
    
    @staticmethod
    def update_pdf_url(result_id, pdf_url):
        """更新PDF URL"""
        bazi_results_collection.update_one(
            {"_id": ObjectId(result_id)},
            {"$set": {"pdfUrl": pdf_url}}
        )
        return BaziResultModel.find_by_id(result_id) 