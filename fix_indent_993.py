#!/usr/bin/env python
# coding: utf-8

import os
import datetime

def fix_indentation():
    """修复routes/bazi_routes.py文件中第993行附近的缩进问题"""
    
    # 源文件和目标文件
    source_file = 'routes/bazi_routes.py'
    backup_file = f"{source_file}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 读取源文件
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 创建备份
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"已创建备份: {backup_file}")
    
    # 查找第990行附近的问题
    start_line = max(0, 980)
    end_line = min(len(lines), 1010)
    
    print(f"检查第{start_line+1}行到第{end_line}行...")
    
    # 打印这些行的内容
    for i in range(start_line, end_line):
        print(f"{i+1}: {lines[i].rstrip()}")
    
    # 查找问题行
    problem_start = -1
    for i in range(start_line, end_line):
        if "prompt = f" in lines[i] and lines[i].startswith("                "):
            problem_start = i
            print(f"找到匹配行: 第{i+1}行 - {lines[i].rstrip()}")
            break
    
    if problem_start > 0:
        # 修复缩进问题
        print(f"找到问题行: 第{problem_start+1}行 - {lines[problem_start].rstrip()}")
        lines[problem_start] = lines[problem_start][12:]  # 减少12个空格的缩进
        print(f"修复了第 {problem_start+1} 行的缩进")
        
        # 修复后续行的缩进
        j = problem_start + 1
        while j < len(lines) and j < problem_start + 30 and lines[j].startswith("                "):
            lines[j] = lines[j][12:]  # 减少12个空格的缩进
            print(f"修复了第 {j+1} 行的缩进")
            j += 1
        
        # 保存修复后的文件
        with open(source_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"已修复文件: {source_file}")
    else:
        print("未找到缩进问题行")

if __name__ == '__main__':
    fix_indentation() 