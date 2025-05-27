#!/usr/bin/env python
# coding: utf-8

import os
import re
import datetime

def fix_indentation():
    """修复routes/bazi_routes.py文件中的缩进问题"""
    
    # 源文件和目标文件
    source_file = 'routes/bazi_routes.py'
    backup_file = f"{source_file}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    target_file = 'routes/bazi_routes.py'
    
    # 读取源文件
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建备份
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"已创建备份: {backup_file}")
    
    # 修复第436行附近的缩进问题
    pattern = r'overall_match = re\.search\(r\'综合建议\[：:\]\([\s\S]*?\)\$\'\, content\)\s+if overall_match:\s+analysis_result\["overall"\] = overall_match\.group\(1\)\.strip\(\)\s+else:\s+# 如果没有找到综合建议，使用全部内容\s+analysis_result\["overall"\] = content\s+\s+return analysis_result\s+else:\s+logging\.error'
    
    replacement = '''overall_match = re.search(r'综合建议[：:]([\s\S]*?)$', content)
            if overall_match:
                analysis_result["overall"] = overall_match.group(1).strip()
            else:
                # 如果没有找到综合建议，使用全部内容
                analysis_result["overall"] = content
            
            return analysis_result
        else:
            logging.error'''
    
    fixed_content = re.sub(pattern, replacement, content)
    
    # 保存修复后的文件
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"已修复文件: {target_file}")

if __name__ == '__main__':
    fix_indentation() 