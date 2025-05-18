#!/usr/bin/env python
# coding: utf-8

import os
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_bazi_routes_indentation():
    """修复routes/bazi_routes.py文件中的缩进问题"""
    file_path = 'routes/bazi_routes.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复问题1: DeepSeek API密钥处的缩进
    pattern1 = r'# 检查DeepSeek API密钥并启动异步分析\s+deepseek_api_key = os\.getenv\(\'DEEPSEEK_API_KEY\'\)\s+if deepseek_api_key'
    replacement1 = '        # 检查DeepSeek API密钥并启动异步分析\n        deepseek_api_key = os.getenv(\'DEEPSEEK_API_KEY\')\n        if deepseek_api_key'
    content = re.sub(pattern1, replacement1, content)
    
    # 修复问题2: PDF路径处的缩进
    pattern2 = r'if result\.get\(\'pdfUrl\'\):\s+# 检查本地PDF文件是否存在\s+pdf_path = os\.path\.join\(os\.getcwd\(\), \'pdfs\', f\"\{result_id\}\.pdf\"\)'
    replacement2 = 'if result.get(\'pdfUrl\'):\n        # 检查本地PDF文件是否存在\n        pdf_path = os.path.join(os.getcwd(), \'pdfs\', f"{result_id}.pdf")'
    content = re.sub(pattern2, replacement2, content)
    
    # 修复问题3: 文件存在判断的缩进
    pattern3 = r'if os\.path\.exists\(pdf_path\):\s+# 微信环境中，优先返回JSON格式的URL'
    replacement3 = '        if os.path.exists(pdf_path):\n            # 微信环境中，优先返回JSON格式的URL'
    content = re.sub(pattern3, replacement3, content)
    
    # 修复问题4: 非微信环境下的返回缩进
    pattern4 = r'# 非微信环境，直接发送文件\s+return send_file'
    replacement4 = '            # 非微信环境，直接发送文件\n            return send_file'
    content = re.sub(pattern4, replacement4, content)
    
    # 修复问题5: 如果文件不存在的逻辑缩进
    pattern5 = r'# 如果文件不存在，但有URL，返回URL\s+return jsonify'
    replacement5 = '        # 如果文件不存在，但有URL，返回URL\n        return jsonify'
    content = re.sub(pattern5, replacement5, content)
    
    # 修复问题6: jsonify缩进问题
    pattern6 = r'code=200,\s+message="重定向到PDF",'
    replacement6 = 'code=200,\n            message="重定向到PDF",'
    content = re.sub(pattern6, replacement6, content)
    
    # 保存修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logging.info(f'修复成功: {file_path}')

if __name__ == '__main__':
    fix_bazi_routes_indentation()
    logging.info('修复完成') 