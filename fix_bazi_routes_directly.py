#!/usr/bin/env python
# coding: utf-8

import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_file_directly():
    """直接使用行号修复routes/bazi_routes.py文件中的缩进问题"""
    file_path = 'routes/bazi_routes.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 根据前面的错误提示，修复特定行的缩进问题
    
    # 修复第1014行左右的缩进问题
    for i in range(1010, 1020):
        if i < len(lines) and 'pdf_path = os.path.join' in lines[i]:
            lines[i] = '        ' + lines[i].lstrip()
            logging.info(f"修复行 {i+1}: {lines[i].strip()}")
    
    # 修复第1016行左右的if语句缩进问题
    for i in range(1015, 1025):
        if i < len(lines) and 'if os.path.exists(pdf_path):' in lines[i]:
            lines[i] = '        ' + lines[i].lstrip()
            logging.info(f"修复行 {i+1}: {lines[i].strip()}")
    
    # 可能的非微信环境相关的缩进问题
    for i in range(1025, 1035):
        if i < len(lines) and '# 非微信环境，直接发送文件' in lines[i]:
            lines[i] = '            ' + lines[i].lstrip()
            if i+1 < len(lines) and 'return send_file' in lines[i+1]:
                lines[i+1] = '            ' + lines[i+1].lstrip()
                logging.info(f"修复行 {i+2}: {lines[i+1].strip()}")
    
    # 修复"如果文件不存在"相关的缩进
    for i in range(1035, 1045):
        if i < len(lines) and '# 如果文件不存在' in lines[i]:
            lines[i] = '        ' + lines[i].lstrip()
            if i+1 < len(lines) and 'return jsonify' in lines[i+1]:
                lines[i+1] = '        ' + lines[i+1].lstrip()
                logging.info(f"修复行 {i+2}: {lines[i+1].strip()}")
    
    # 保存修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    logging.info(f'完成直接修复: {file_path}')

if __name__ == '__main__':
    fix_file_directly()
    logging.info('修复完成') 