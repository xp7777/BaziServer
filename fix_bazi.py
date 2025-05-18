#!/usr/bin/env python
import re

with open('routes/bazi_routes.py', 'r', encoding='utf-8') as file:
    content = file.read()

# 修复第757行附近的缩进问题
pattern1 = r'            # 检查DeepSeek API密钥并启动异步分析\n            deepseek_api_key = os.getenv\(\'DEEPSEEK_API_KEY\'\)'
replacement1 = '        # 检查DeepSeek API密钥并启动异步分析\n        deepseek_api_key = os.getenv(\'DEEPSEEK_API_KEY\')'

content = re.sub(pattern1, replacement1, content)

# 修复if语句的缩进
pattern2 = r'            if deepseek_api_key and result_id not in analyzing_results:'
replacement2 = '        if deepseek_api_key and result_id not in analyzing_results:'

content = re.sub(pattern2, replacement2, content)

# 保存修改后的文件
with open('routes/bazi_routes.py', 'w', encoding='utf-8') as file:
    file.write(content)

print("缩进问题已修复!") 