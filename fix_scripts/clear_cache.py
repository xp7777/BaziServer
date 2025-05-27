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

logging.info('开始清除RES缓存记录')

# 1. 查找所有RES前缀ID记录
res_results = list(results_collection.find({'_id': {'$regex': '^RES'}}))
logging.info(f'找到{len(res_results)}条RES前缀记录，准备删除')

# 删除所有RES前缀记录
if len(res_results) > 0:
    try:
        result = results_collection.delete_many({'_id': {'$regex': '^RES'}})
        logging.info(f'成功删除{result.deleted_count}条RES前缀记录')
    except Exception as e:
        logging.error(f'删除RES前缀记录时出错: {str(e)}')
else:
    logging.info('没有RES前缀记录需要删除')

logging.info('缓存清除完成') 