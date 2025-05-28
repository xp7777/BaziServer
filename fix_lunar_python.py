#!/usr/bin/env python
# coding: utf-8

import os
import sys
import logging
import traceback
import shutil
from datetime import datetime

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

def fix_bazi_calculator():
    """修复utils/bazi_calculator.py中的lunar-python相关问题"""
    file_path = 'utils/bazi_calculator.py'
    
    try:
        # 创建备份
        create_backup(file_path)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修改calculate_shen_sha函数中的错误处理
        shen_sha_start = content.find('def calculate_shen_sha')
        shen_sha_end = content.find('def calculate_da_yun', shen_sha_start)
        
        if shen_sha_start >= 0 and shen_sha_end >= 0:
            shen_sha_func = content[shen_sha_start:shen_sha_end]
            
            # 改进错误处理
            improved_shen_sha_func = shen_sha_func.replace(
                'except Exception as e:',
                'except Exception as e:\n'
                '        logging.error(f"计算神煞时出错: {str(e)}")\n'
                '        import traceback\n'
                '        logging.error(traceback.format_exc())'
            )
            
            # 修改函数末尾的返回值，确保即使出错也返回基本结构
            if 'return {' in improved_shen_sha_func:
                # 在函数末尾添加默认返回值
                improved_return = '''    return {
            "shenSha": "计算出错",
            "dayChong": "计算失败",
            "zhiShen": "计算失败",
            "pengZuGan": "计算失败",
            "pengZuZhi": "计算失败",
            "xiShen": "计算失败",
            "fuShen": "计算失败",
            "caiShen": "计算失败",
            "benMing": []
        }'''
                
                # 替换原来的return语句
                last_return_index = improved_shen_sha_func.rfind('return')
                if last_return_index > 0:
                    improved_shen_sha_func = improved_shen_sha_func[:last_return_index] + improved_return
            
            # 更新内容
            content = content[:shen_sha_start] + improved_shen_sha_func + content[shen_sha_end:]
        
        # 修改calculate_da_yun函数中的错误处理
        da_yun_start = content.find('def calculate_da_yun')
        da_yun_end = content.find('def calculate_shi_shen', da_yun_start)
        
        if da_yun_start >= 0 and da_yun_end >= 0:
            da_yun_func = content[da_yun_start:da_yun_end]
            
            # 改进错误处理
            improved_da_yun_func = da_yun_func.replace(
                'except Exception as e:',
                'except Exception as e:\n'
                '        logging.error(f"计算大运时出错: {str(e)}")\n'
                '        import traceback\n'
                '        logging.error(traceback.format_exc())'
            )
            
            # 修改函数末尾的返回值
            if 'return {' in improved_da_yun_func:
                # 在函数末尾添加默认返回值
                improved_return = '''    return {
            "startAge": 1,
            "startYear": year + 1,
            "daYunList": [],
            "xiaoYunList": []
        }'''
                
                # 替换原来的return语句
                last_return_index = improved_da_yun_func.rfind('return')
                if last_return_index > 0:
                    improved_da_yun_func = improved_da_yun_func[:last_return_index] + improved_return
            
            # 更新内容
            content = content[:da_yun_start] + improved_da_yun_func + content[da_yun_end:]
        
        # 更新文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"已修复 {file_path}")
        return True
    
    except Exception as e:
        logging.error(f"修复 {file_path} 失败: {str(e)}")
        traceback.print_exc()
        return False

def check_lunar_python():
    """检查lunar-python库的安装和导入情况"""
    try:
        import lunar_python
        logging.info(f"lunar-python库已安装: {lunar_python.__file__ if hasattr(lunar_python, '__file__') else '无路径信息'}")
        
        # 检查具体模块
        try:
            from lunar_python.Solar import Solar
            from lunar_python.Lunar import Lunar
            from lunar_python.util import LunarUtil
            
            # 测试基本功能
            solar = Solar.fromYmd(2023, 1, 1)
            lunar = solar.getLunar()
            logging.info(f"lunar-python功能测试成功: {solar.toYmd()} -> {lunar.toString()}")
            
            return True
        except Exception as e:
            logging.error(f"lunar-python模块导入或使用失败: {str(e)}")
            traceback.print_exc()
            return False
    
    except ImportError:
        logging.error("lunar-python库未安装或无法导入")
        
        # 尝试安装
        try:
            logging.info("尝试安装lunar-python库...")
            import pip
            pip.main(['install', 'lunar-python'])
            logging.info("lunar-python库安装完成，请重新运行")
        except Exception as e:
            logging.error(f"安装lunar-python库失败: {str(e)}")
        
        return False

def main():
    """主函数"""
    logging.info("开始修复lunar-python相关问题...")
    
    # 检查lunar-python库
    if not check_lunar_python():
        logging.warning("lunar-python库检查失败，请手动安装")
        return
    
    # 修复bazi_calculator.py
    if fix_bazi_calculator():
        logging.info("修复完成")
    else:
        logging.error("修复失败")

if __name__ == "__main__":
    main() 