import os
import json
import logging
import sys
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 获取MongoDB URI
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()
results_collection = db.bazi_results

logging.info('开始修复当前数据的出生日期')

# 查找前端提交的出生日期（可以根据实际情况调整）
target_birth_date = "2020-01-09"
logging.info(f'将要更新的目标出生日期: {target_birth_date}')

# 查找所有RES前缀ID记录
res_results = list(results_collection.find({'_id': {'$regex': '^RES'}}))
logging.info(f'找到{len(res_results)}条RES前缀记录')

for result in res_results:
    result_id = result['_id']
    
    # 检查是否有原始请求信息
    if 'originalRequest' in result and result['originalRequest'].get('birthDate'):
        original_birth_date = result['originalRequest']['birthDate']
        logging.info(f'记录ID: {result_id}, 原始出生日期: {original_birth_date}')
        
        # 使用原始请求中的日期更新记录
        try:
            results_collection.update_one(
                {'_id': result_id},
                {'$set': {
                    'birthDate': original_birth_date,
                    'analyzed': False  # 设置为False，触发重新分析
                }}
            )
            logging.info(f'成功更新记录ID: {result_id}的出生日期为: {original_birth_date}')
        except Exception as e:
            logging.error(f'更新记录ID: {result_id}时出错: {str(e)}')
    
    # 如果没有原始请求信息，但有birthDate字段，并且不是预期的日期
    elif 'birthDate' in result:
        current_birth_date = result['birthDate']
        if current_birth_date != target_birth_date and '2025-05-27' in current_birth_date:
            logging.info(f'记录ID: {result_id}, 当前日期: {current_birth_date}, 需要更新为: {target_birth_date}')
            
            # 更新为目标出生日期
            try:
                results_collection.update_one(
                    {'_id': result_id},
                    {'$set': {
                        'birthDate': target_birth_date,
                        'basicInfo.solarYear': target_birth_date.split('-')[0] if '-' in target_birth_date else target_birth_date.split('/')[0],
                        'basicInfo.solarMonth': target_birth_date.split('-')[1] if '-' in target_birth_date else target_birth_date.split('/')[1],
                        'basicInfo.solarDay': target_birth_date.split('-')[2] if '-' in target_birth_date else target_birth_date.split('/')[2],
                        'analyzed': False  # 设置为False，触发重新分析
                    }}
                )
                logging.info(f'成功更新记录ID: {result_id}的出生日期为: {target_birth_date}')
            except Exception as e:
                logging.error(f'更新记录ID: {result_id}时出错: {str(e)}')

logging.info('修复当前数据的出生日期完成') 