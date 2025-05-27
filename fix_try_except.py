#!/usr/bin/env python
# coding: utf-8

import os
import datetime
import re

def fix_indentation():
    """修复routes/bazi_routes.py文件中的try-except块问题"""
    
    # 源文件和目标文件
    source_file = 'routes/bazi_routes.py'
    backup_file = f"{source_file}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 读取源文件
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建备份
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"已创建备份: {backup_file}")
    
    # 查找问题区域
    try_pattern = r'try:.*?except Exception as e:.*?logging\.warning\(f"无法提取出生年份: {str\(e\)}"\)(.*?)# 构建提示词'
    
    match = re.search(try_pattern, content, re.DOTALL)
    if match:
        # 找到了try-except块
        print("找到了try-except块")
        
        # 获取try-except块后面的内容
        after_try = match.group(1)
        
        # 检查是否有缩进问题
        if "                " in after_try:
            print("检测到缩进问题")
            
            # 修复try-except块后面的内容
            fixed_content = content.replace(after_try, "\n        " + after_try.lstrip())
            
            # 保存修复后的文件
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"已修复文件: {source_file}")
        else:
            print("未检测到缩进问题")
    else:
        print("未找到try-except块")
        
        # 尝试使用更简单的方法修复
        lines = content.split('\n')
        
        # 查找问题行
        problem_start = -1
        for i, line in enumerate(lines):
            if "# 构建提示词" in line and line.startswith("                "):
                problem_start = i
                print(f"找到问题行: 第{i+1}行 - {line}")
                break
        
        if problem_start > 0:
            # 修复这一行和后续行的缩进
            fixed_lines = lines[:problem_start]
            
            # 减少缩进
            for i in range(problem_start, len(lines)):
                if lines[i].startswith("                "):
                    fixed_lines.append(lines[i][12:])  # 减少12个空格的缩进
                else:
                    fixed_lines.append(lines[i])
            
            # 保存修复后的文件
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
            
            print(f"已使用简单方法修复文件: {source_file}")
        else:
            print("未找到问题行")

if __name__ == '__main__':
    fix_indentation() 