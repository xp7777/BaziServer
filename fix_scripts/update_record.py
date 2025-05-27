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

# 检查命令行参数
if len(sys.argv) < 3:
    print("用法: python update_record.py <结果ID> <出生日期> [出生时间] [性别]")
    print("例如: python update_record.py 68353fb52c239f7fc0d4d63a 2018-07-19 '午时 (11:00-13:00)' male")
    sys.exit(1)

result_id = sys.argv[1]
birth_date = sys.argv[2]
birth_time = sys.argv[3] if len(sys.argv) > 3 else None
gender = sys.argv[4] if len(sys.argv) > 4 else None

logging.info(f'开始更新记录ID: {result_id}')
logging.info(f'更新出生日期为: {birth_date}')
if birth_time:
    logging.info(f'更新出生时间为: {birth_time}')
if gender:
    logging.info(f'更新性别为: {gender}')

# 查找记录
result = None
try:
    # 尝试使用ObjectId
    if len(result_id) == 24 and all(c in '0123456789abcdef' for c in result_id):
        result = results_collection.find_one({"_id": ObjectId(result_id)})
        if result:
            logging.info("使用ObjectId查询成功")
except Exception as e:
    logging.warning(f"ObjectId查询错误: {str(e)}")

# 尝试使用字符串ID
if not result:
    try:
        result = results_collection.find_one({"_id": result_id})
        if result:
            logging.info("使用字符串ID查询成功")
    except Exception as e:
        logging.warning(f"字符串ID查询错误: {str(e)}")

if not result:
    logging.error(f"未找到记录: {result_id}")
    sys.exit(1)

# 准备更新数据
update_data = {}

# 更新出生日期
if birth_date:
    update_data["birthDate"] = birth_date
    
    # 如果已经有basicInfo，需要更新其中的字段
    if 'basicInfo' in result:
        # 复制现有的basicInfo
        basic_info = dict(result['basicInfo'])
        # 更新年月日
        basic_info["solarYear"] = birth_date.split('-')[0] if '-' in birth_date else birth_date.split('/')[0]
        basic_info["solarMonth"] = birth_date.split('-')[1] if '-' in birth_date else birth_date.split('/')[1]
        basic_info["solarDay"] = birth_date.split('-')[2] if '-' in birth_date else birth_date.split('/')[2]
        # 设置更新后的basicInfo
        update_data["basicInfo"] = basic_info
    else:
        # 如果没有basicInfo字段，创建一个
        update_data["basicInfo"] = {
            "solarYear": birth_date.split('-')[0] if '-' in birth_date else birth_date.split('/')[0],
            "solarMonth": birth_date.split('-')[1] if '-' in birth_date else birth_date.split('/')[1],
            "solarDay": birth_date.split('-')[2] if '-' in birth_date else birth_date.split('/')[2]
        }

# 更新出生时间
if birth_time:
    # 如果有现有的birthTime，保留日期部分
    if 'birthTime' in result and ' ' in result['birthTime']:
        current_birth_time = result['birthTime']
        date_part = current_birth_time.split(' ')[0]
        # 确保日期部分是有效的日期格式
        if '-' in date_part and len(date_part.split('-')) == 3:
            update_data["birthTime"] = f"{date_part} {birth_time}"
        else:
            update_data["birthTime"] = f"{birth_date} {birth_time}"
    else:
        update_data["birthTime"] = f"{birth_date} {birth_time}"
    
    # 更新basicInfo中的时间信息
    if "basicInfo" in update_data:
        update_data["basicInfo"]["solarHour"] = birth_time
    elif 'basicInfo' in result:
        basic_info = dict(result['basicInfo'])
        basic_info["solarHour"] = birth_time
        update_data["basicInfo"] = basic_info
    else:
        update_data["basicInfo"] = {"solarHour": birth_time}

# 更新性别
if gender:
    update_data["gender"] = gender
    if "basicInfo" in update_data:
        update_data["basicInfo"]["gender"] = gender
    elif 'basicInfo' in result:
        basic_info = dict(result['basicInfo'])
        basic_info["gender"] = gender
        update_data["basicInfo"] = basic_info

# 设置分析状态为未分析，以触发重新分析
update_data["analyzed"] = False
update_data["updateTime"] = datetime.now()

# 更新记录
try:
    # 选择正确的ID类型进行更新
    if isinstance(result['_id'], ObjectId):
        update_result = results_collection.update_one(
            {"_id": ObjectId(result_id)},
            {"$set": update_data}
        )
    else:
        update_result = results_collection.update_one(
            {"_id": result_id},
            {"$set": update_data}
        )
    
    if update_result.modified_count > 0:
        logging.info(f"成功更新记录ID: {result_id}")
        print(f"成功更新记录ID: {result_id}")
    else:
        logging.warning(f"记录ID: {result_id} 未发生变更")
        print(f"记录ID: {result_id} 未发生变更")
except Exception as e:
    logging.error(f"更新记录ID: {result_id} 时出错: {str(e)}")
    print(f"更新记录失败: {str(e)}")

logging.info('更新记录完成') 