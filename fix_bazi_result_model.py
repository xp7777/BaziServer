#!/usr/bin/env python
# coding: utf-8

import os
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_indentation():
    """修复models/bazi_result_model.py文件中的缩进问题"""
    file_path = 'models/bazi_result_model.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复缩进问题1: update_bazi_data函数中的缩进
    pattern1 = r'try:\s+# 尝试使用ObjectId\s+bazi_results_collection\.update_one'
    replacement1 = 'try:\n            # 尝试使用ObjectId\n            bazi_results_collection.update_one'
    content = re.sub(pattern1, replacement1, content)
    
    # 修复缩进问题2: update_ai_analysis函数中的缩进
    pattern2 = r'try:\s+# 尝试使用ObjectId\s+bazi_results_collection\.update_one\(\s+\{"_id": ObjectId\(result_id\)\},\s+\{"\\$set": \{f"aiAnalysis\.\{area\}": analysis\}\}'
    replacement2 = 'try:\n            # 尝试使用ObjectId\n            bazi_results_collection.update_one(\n                {"_id": ObjectId(result_id)},\n                {"$set": {f"aiAnalysis.{area}": analysis}}'
    content = re.sub(pattern2, replacement2, content)
    
    # 修复缩进问题3: 第80-85行左右的if not existing_result块中的缩进
    pattern3 = r'if not existing_result:\s+try:\s+order_id = result_id\.replace\("RES", ""\)\s+existing_result = bazi_results_collection\.find_one\(\{"orderId": order_id\}\)\s+if existing_result:\s+logging\.info\("使用订单ID查询成功"\)'
    replacement3 = 'if not existing_result:\n                try:\n                    order_id = result_id.replace("RES", "")\n                    existing_result = bazi_results_collection.find_one({"orderId": order_id})\n                    if existing_result:\n                        logging.info("使用订单ID查询成功")'
    content = re.sub(pattern3, replacement3, content)
    
    # 保存修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logging.info(f'修复成功: {file_path}')

if __name__ == '__main__':
    fix_indentation()
    logging.info('所有修复完成') 