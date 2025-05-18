#!/usr/bin/env python
# coding: utf-8

import os
import re
import logging
import shutil
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_backup(file_path):
    """创建文件备份"""
    if not os.path.exists(file_path):
        logging.warning(f"文件不存在: {file_path}")
        return False
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak_{timestamp}"
    
    try:
        shutil.copy2(file_path, backup_path)
        logging.info(f"已创建备份: {backup_path}")
        return True
    except Exception as e:
        logging.error(f"创建备份失败: {str(e)}")
        return False

def fix_bazi_calculator():
    """修复utils/bazi_calculator.py中的sxtwl.Lunar()错误"""
    file_path = 'utils/bazi_calculator.py'
    
    try:
        # 创建备份
        create_backup(file_path)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加注释说明已使用真实的sxtwl包
        sxtwl_comment = """
# 注意: 现在使用的是PyPI上的真实sxtwl包(https://pypi.org/project/sxtwl/)
# 不再使用模拟的sxtwl.py文件
"""
        
        # 在导入语句后添加注释
        content = re.sub(r'(import\s+sxtwl.*?)(\n+)', r'\1\n' + sxtwl_comment + r'\2', content)
        
        # 替换所有sxtwl.Lunar()调用
        content = content.replace('lunar = sxtwl.Lunar()', '# lunar = sxtwl.Lunar() # 已弃用，现使用sxtwl.fromSolar()方法')
        content = content.replace('day_obj = lunar.getDayBySolar(year, month, day)', 'day_obj = sxtwl.fromSolar(year, month, day)')
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"已修复 {file_path}")
        return True
    
    except Exception as e:
        logging.error(f"修复 {file_path} 失败: {str(e)}")
        return False

def fix_route_indentation():
    """修复routes/bazi_routes.py中analyze_bazi函数的缩进问题"""
    file_path = 'routes/bazi_routes.py'
    
    try:
        # 创建备份
        create_backup(file_path)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找import sxtwl语句，添加注释
        for i, line in enumerate(lines):
            if 'import sxtwl' in line:
                sxtwl_comment = "# 注意: 现在使用的是PyPI上的真实sxtwl包(https://pypi.org/project/sxtwl/)\n"
                sxtwl_comment += "# 不再使用模拟的sxtwl.py文件\n"
                lines.insert(i+1, sxtwl_comment)
                break
        
        # 查找analyze_bazi函数的位置
        analyze_line_index = -1
        for i, line in enumerate(lines):
            if 'def analyze_bazi():' in line:
                analyze_line_index = i
                break
        
        if analyze_line_index == -1:
            logging.warning("找不到analyze_bazi函数，请手动检查文件")
            return False
        
        # 检查接下来的几行，修复缩进问题
        for i in range(analyze_line_index + 1, min(analyze_line_index + 20, len(lines))):
            if 'try:' in lines[i]:
                # 确保接下来的行正确缩进
                next_line = lines[i + 1].strip()
                if next_line.startswith('data ='):
                    # 修复缩进
                    fixed_line = ' ' * 8 + next_line + '\n'  # 添加8个空格缩进
                    lines[i + 1] = fixed_line
                    logging.info(f"已修复第{i+1}行缩进")
                break
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        logging.info(f"已修复 {file_path}")
        return True
    
    except Exception as e:
        logging.error(f"修复 {file_path} 失败: {str(e)}")
        return False

def update_test_sxtwl():
    """更新test_sxtwl.py,添加注释说明使用真实sxtwl包"""
    file_path = 'test_sxtwl.py'
    
    try:
        # 创建备份
        create_backup(file_path)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加注释说明已使用真实的sxtwl包
        sxtwl_comment = """
# 注意: 该测试使用PyPI上的真实sxtwl包(https://pypi.org/project/sxtwl/)
# 如果测试失败，可能需要安装Visual C++ Build Tools
# 请运行 install_sxtwl.py 脚本获取安装帮助
"""
        
        # 在import语句后添加注释
        content = re.sub(r'(import\s+sxtwl.*?)(\n+)', r'\1\n' + sxtwl_comment + r'\2', content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"已更新 {file_path}")
        return True
    
    except Exception as e:
        logging.error(f"更新 {file_path} 失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 更新test_sxtwl.py
    update_test_sxtwl()
    
    # 修复bazi_calculator.py
    fix_bazi_calculator()
    
    # 修复bazi_routes.py缩进问题
    fix_route_indentation()
    
    logging.info("修复完成")
    logging.info("请注意：已删除模拟的sxtwl.py文件，改为使用PyPI上的真实sxtwl包")
    logging.info("如果遇到安装问题，请运行 install_sxtwl.py 脚本获取帮助") 