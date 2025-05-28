#!/usr/bin/env python
# coding: utf-8

import sys
import os
import logging
import re
import shutil
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_backup(file_path):
    """创建文件备份"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{file_path}.bak_{timestamp}"
    
    try:
        shutil.copy2(file_path, backup_path)
        logging.info(f"已创建备份文件: {backup_path}")
        return True
    except Exception as e:
        logging.error(f"创建备份文件失败: {str(e)}")
        return False

def fix_indentation():
    """修复bazi_calculator.py中的缩进问题"""
    file_path = 'utils/bazi_calculator.py'
    
    try:
        # 创建备份
        create_backup(file_path)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 检查并修复缩进
        fixed_lines = []
        line_number = 0
        
        for line in lines:
            line_number += 1
            
            # 尝试检测明显的缩进错误
            # 1. 如果行以多个空格开头，但不是4的倍数
            if line.startswith(' ') and not line.startswith('    '):
                # 检查是否是函数定义后的缩进问题
                if re.match(r'^( {1,3})(def |if |else:|elif |for |while |try:|except |finally:|with )', line):
                    logging.warning(f"行 {line_number}: 函数定义后的缩进不正确: {line.strip()}")
                    # 修复为4个空格的倍数
                    indent_level = (len(line) - len(line.lstrip())) // 4 + 1
                    fixed_line = ' ' * (indent_level * 4) + line.lstrip()
                    fixed_lines.append(fixed_line)
                    continue
            
            # 2. 如果前一行是冒号结尾，但当前行没有缩进
            if line_number > 1 and lines[line_number - 2].strip().endswith(':') and not line.startswith(' '):
                if not line.strip().startswith(('else:', 'elif ', 'except ', 'finally:', 'except:')):
                    logging.warning(f"行 {line_number}: 冒号后应该缩进: {line.strip()}")
                    fixed_line = ' ' * 4 + line
                    fixed_lines.append(fixed_line)
                    continue
            
            # 3. 检查常见的if-else缩进问题
            if re.match(r'^(\s*)else:', line) and fixed_lines and re.match(r'^(\s*)if ', fixed_lines[-1]):
                # 确保else和if的缩进级别相同
                if_indent = len(fixed_lines[-1]) - len(fixed_lines[-1].lstrip())
                else_indent = len(line) - len(line.lstrip())
                
                if if_indent != else_indent:
                    logging.warning(f"行 {line_number}: if-else缩进不匹配")
                    fixed_line = ' ' * if_indent + line.lstrip()
                    fixed_lines.append(fixed_line)
                    continue
            
            # 4. 特别检查大约760行附近的问题
            if 750 <= line_number <= 770:
                if line.strip() and not line.strip().startswith('#'):
                    # 检查这一行是否缩进有问题
                    indent = len(line) - len(line.lstrip())
                    if indent % 4 != 0:
                        logging.warning(f"行 {line_number}: 可能的缩进问题: {line.strip()}")
                        # 尝试修复为最接近的4的倍数
                        correct_indent = (indent // 4) * 4
                        fixed_line = ' ' * correct_indent + line.lstrip()
                        fixed_lines.append(fixed_line)
                        continue
            
            # 如果没有检测到缩进问题，保持原样
            fixed_lines.append(line)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        logging.info(f"已完成对 {file_path} 的缩进修复")
        return True
    
    except Exception as e:
        logging.error(f"修复缩进失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    logging.info("开始修复缩进问题...")
    
    if fix_indentation():
        logging.info("缩进修复完成")
    else:
        logging.error("缩进修复失败")

if __name__ == "__main__":
    main() 