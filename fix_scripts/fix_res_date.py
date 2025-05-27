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

logging.info('开始修复RES结果ID记录中的日期问题')

# 1. 查找所有RES前缀ID记录
res_results = list(results_collection.find({'_id': {'$regex': '^RES'}}))
logging.info(f'找到{len(res_results)}条RES前缀记录')

for result in res_results:
    result_id = result['_id']
    
    # 检查是否有前端传递的日期
    if 'birthDate' in result and result['birthDate']:
        birth_date = result['birthDate']
        logging.info(f'记录ID: {result_id}, 当前日期: {birth_date}')
        
        # 如果日期是2025-05-27，我们需要修复它
        if birth_date == '2025-05-27':
            # 从时间戳中提取日期
            try:
                timestamp = result_id.replace('RES', '')
                if timestamp.isdigit() and len(timestamp) > 8:
                    time_obj = datetime.fromtimestamp(int(timestamp) / 1000)
                    new_date = time_obj.strftime('%Y-%m-%d')
                    
                    # 如果新日期还是2025-05-27，则保留原值
                    if new_date == '2025-05-27':
                        logging.info(f'记录ID: {result_id}的时间戳日期也是2025-05-27，不修改')
                        continue
                    
                    logging.info(f'记录ID: {result_id}, 将日期从{birth_date}修改为{new_date}')
                    
                    # 更新日期
                    results_collection.update_one(
                        {'_id': result_id},
                        {'$set': {'birthDate': new_date, 'analyzed': False}}
                    )
                    
                    # 如果有basicInfo字段，也更新里面的日期
                    if 'basicInfo' in result:
                        results_collection.update_one(
                            {'_id': result_id},
                            {'$set': {
                                'basicInfo.solarYear': new_date.split('-')[0],
                                'basicInfo.solarMonth': new_date.split('-')[1],
                                'basicInfo.solarDay': new_date.split('-')[2]
                            }}
                        )
                    
                    logging.info(f'记录ID: {result_id}的日期已更新')
            except Exception as e:
                logging.error(f'更新记录ID: {result_id}时出错: {str(e)}')

logging.info('修复RES结果ID记录中的日期问题完成') 