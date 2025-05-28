#!/usr/bin/env python
# coding: utf-8

import os
import shutil
from datetime import datetime
import logging

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

def fix_bazi_calculator():
    """修复utils/bazi_calculator.py文件的编码和缩进问题"""
    file_path = 'utils/bazi_calculator.py'
    
    # 定义正确的神煞计算返回值（UTF-8编码）
    correct_shen_sha_return = '''    return {
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
    
    # 定义正确的大运计算返回值
    correct_da_yun_return = '''    return {
            "startAge": 1,
            "startYear": year + 1,
            "daYunList": [],
            "xiaoYunList": []
        }'''
    
    try:
        # 创建备份
        create_backup(file_path)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # 查找并替换神煞计算的return部分
        shen_sha_position = content.find("def calculate_shen_sha")
        da_yun_position = content.find("def calculate_da_yun", shen_sha_position)
        
        if shen_sha_position >= 0 and da_yun_position >= 0:
            # 找到异常处理部分
            except_position = content.find("except Exception as e:", shen_sha_position, da_yun_position)
            if except_position >= 0:
                # 找到return语句
                return_position = content.find("return {", except_position, da_yun_position)
                if return_position >= 0:
                    # 找到return语句的结束位置
                    end_position = content.find("}", return_position, da_yun_position)
                    if end_position >= 0:
                        # 查找下一个大括号，确保包含完整的return
                        next_pos = end_position + 1
                        while next_pos < da_yun_position:
                            if content[next_pos] == '}':
                                end_position = next_pos
                                break
                            next_pos += 1
                        
                        # 替换整个return语句
                        modified_content = content[:return_position] + correct_shen_sha_return + content[end_position+1:]
                        content = modified_content
        
        # 查找并替换大运计算的return部分
        da_yun_position = content.find("def calculate_da_yun")
        shi_shen_position = content.find("def calculate_shi_shen", da_yun_position)
        
        if da_yun_position >= 0 and shi_shen_position >= 0:
            # 找到异常处理部分
            except_position = content.find("except Exception as e:", da_yun_position, shi_shen_position)
            if except_position >= 0:
                # 找到return语句
                return_position = content.find("return {", except_position, shi_shen_position)
                if return_position >= 0:
                    # 找到return语句的结束位置
                    end_position = content.find("}", return_position, shi_shen_position)
                    if end_position >= 0:
                        # 查找下一个大括号，确保包含完整的return
                        next_pos = end_position + 1
                        while next_pos < shi_shen_position:
                            if content[next_pos] == '}':
                                end_position = next_pos
                                break
                            next_pos += 1
                        
                        # 替换整个return语句
                        modified_content = content[:return_position] + correct_da_yun_return + content[end_position+1:]
                        content = modified_content
        
        # 修复函数定义之间可能缺少的空行
        content = content.replace("}def ", "}\n\ndef ")
        
        # 保存修复后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"已修复 {file_path} 的编码和缩进问题")
        return True
    
    except Exception as e:
        logging.error(f"修复失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_bazi_calculator() 