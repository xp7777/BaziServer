import os
import sys
import logging
import pymongo
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 获取MongoDB连接
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = pymongo.MongoClient(mongo_uri)
db = client.get_database()

def update_birth_date_fields():
    """更新已存在的结果记录，确保正确存储birthDate和birthTime字段"""
    results_collection = db.bazi_results
    orders_collection = db.orders
    
    # 查找所有结果记录
    results = list(results_collection.find({}))
    
    logging.info(f"找到 {len(results)} 条记录进行检查...")
    
    updated_count = 0
    for result in results:
        result_id = result.get('_id')
        birth_time_str = result.get('birthTime')
        
        # 检查是否已有birthDate字段
        if 'birthDate' in result and result['birthDate']:
            logging.info(f"ID {result_id} 已有birthDate字段：{result['birthDate']}")
            continue
            
        # 如果没有birthDate字段，但有birthTime字段，尝试分离
        if birth_time_str and ' ' in birth_time_str:
            parts = birth_time_str.split(' ')
            if len(parts) >= 2 and len(parts[0].split('-')) == 3:
                birth_date = parts[0]
                birth_time = ' '.join(parts[1:])
                
                # 更新记录
                results_collection.update_one(
                    {"_id": result_id},
                    {"$set": {
                        "birthDate": birth_date,
                        "birthTime": birth_time
                    }}
                )
                updated_count += 1
                logging.info(f"已更新记录 {result_id}：birthDate={birth_date}, birthTime={birth_time}")
    
    logging.info(f"共更新了 {updated_count} 条记录")

def fix_res_prefixed_records():
    """修复以RES为前缀的记录，确保它们有正确的出生日期和时间信息"""
    results_collection = db.bazi_results
    
    # 查找所有以RES开头的ID记录
    res_records = list(results_collection.find({"_id": {"$regex": "^RES"}}))
    
    logging.info(f"找到 {len(res_records)} 条RES前缀记录进行检查...")
    
    fixed_count = 0
    for record in res_records:
        record_id = record.get('_id')
        
        # 检查是否缺少关键字段
        missing_fields = []
        if 'birthDate' not in record or not record['birthDate']:
            missing_fields.append('birthDate')
        if 'birthTime' not in record or not record['birthTime']:
            missing_fields.append('birthTime')
        
        if not missing_fields:
            logging.info(f"记录 {record_id} 数据完整，无需修复")
            continue
            
        logging.info(f"记录 {record_id} 缺少字段：{', '.join(missing_fields)}")
        
        # 尝试从birthTime字段中分离日期和时间
        if 'birthTime' in record and record['birthTime'] and ' ' in record['birthTime']:
            parts = record['birthTime'].split(' ')
            if len(parts) >= 2 and len(parts[0].split('-')) == 3:
                birth_date = parts[0]
                birth_time = ' '.join(parts[1:])
                
                # 更新记录
                results_collection.update_one(
                    {"_id": record_id},
                    {"$set": {
                        "birthDate": birth_date,
                        "birthTime": birth_time
                    }}
                )
                fixed_count += 1
                logging.info(f"已修复记录 {record_id}：birthDate={birth_date}, birthTime={birth_time}")
        else:
            # 如果无法从现有数据中提取，设置默认值
            birth_date = "2023-06-06"
            birth_time = "辰时 (07:00-09:00)"
            
            # 更新记录
            results_collection.update_one(
                {"_id": record_id},
                {"$set": {
                    "birthDate": birth_date,
                    "birthTime": birth_time
                }}
            )
            fixed_count += 1
            logging.info(f"已修复记录 {record_id}（使用默认值）：birthDate={birth_date}, birthTime={birth_time}")
    
    logging.info(f"共修复了 {fixed_count} 条RES前缀记录")

def create_test_record():
    """创建一个测试记录，用于验证修复效果"""
    results_collection = db.bazi_results
    
    test_id = f"RES{int(datetime.now().timestamp() * 1000)}"
    
    test_record = {
        "_id": test_id,
        "userId": "test_user",
        "orderId": test_id.replace("RES", ""),
        "gender": "male",
        "birthDate": "2022-06-21",
        "birthTime": "午时 (11:00-13:00)",
        "focusAreas": ["health", "wealth", "career", "relationship"],
        "baziChart": None,
        "aiAnalysis": {},
        "createTime": datetime.now()
    }
    
    try:
        results_collection.insert_one(test_record)
        logging.info(f"已创建测试记录 {test_id}")
        return test_id
    except Exception as e:
        logging.error(f"创建测试记录失败：{str(e)}")
        return None

if __name__ == "__main__":
    logging.info("开始修复日期参数问题...")
    
    # 更新已存在的记录
    update_birth_date_fields()
    
    # 修复RES前缀记录
    fix_res_prefixed_records()
    
    # 创建测试记录
    test_id = create_test_record()
    if test_id:
        logging.info(f"测试记录ID：{test_id}，请使用此ID测试修复效果")
    
    logging.info("修复完成！") 