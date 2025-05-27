#!/usr/bin/env python
# coding: utf-8

import os
import datetime

def fix_indentation():
    """使用简单方法修复routes/bazi_routes.py文件中的缩进问题"""
    
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
    
    # 打印文件的前几行，了解内容
    print("文件内容预览:")
    for i in range(min(10, len(lines))):
        print(f"{i+1}: {lines[i].rstrip()}")
    
    # 查找问题行
    problem_start = -1
    for i, line in enumerate(lines):
        if "overall_match = re.search" in line:
            problem_start = i
            print(f"找到匹配行: 第{i+1}行 - {line.rstrip()}")
            # 打印后续几行，查看上下文
            for j in range(i+1, min(i+10, len(lines))):
                print(f"  后续行 {j+1}: {lines[j].rstrip()}")
            break
    
    if problem_start > 0:
        # 修复缩进问题
        found_else = False
        for i in range(problem_start, problem_start + 20):  # 检查接下来的20行
            if i < len(lines):
                print(f"检查第{i+1}行: {lines[i].rstrip()}")
                if "else:" in lines[i] and lines[i].strip() == "else:":
                    # 找到了问题行，修复缩进
                    print(f"找到问题行: 第{i+1}行 - {lines[i].rstrip()}")
                    lines[i] = "            else:\n"
                    print(f"修复了第 {i+1} 行的缩进")
                    found_else = True
                    break
        
        if found_else:
            # 保存修复后的文件
            with open(source_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"已修复文件: {source_file}")
        else:
            print("未找到需要修复的'else:'行")
    else:
        print("未找到'overall_match = re.search'行")

if __name__ == '__main__':
    fix_indentation() 