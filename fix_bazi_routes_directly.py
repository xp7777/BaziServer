#!/usr/bin/env python
# coding: utf-8

import os
import logging
import datetime
import re

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

def fix_calculate_route():
    """
    修复bazi_routes.py中的calculate_bazi路由，使用新的lunar-python实现
    """
    print("开始修复八字计算路由...")
    
    # 读取原始文件
    file_path = "routes/bazi_routes.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 创建备份
    backup_path = f"{file_path}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"创建备份文件: {backup_path}")
    
    # 查找calculate_bazi路由函数
    pattern = r'(@bazi_bp\.route\(\s*[\'"]\/calculate[\'"]\s*,\s*methods=\s*\[[\'"]POST[\'"]\]\s*\)\s*\n)def calculate_bazi\(\):\s*.*?(?=@bazi_bp\.route|$)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("未找到calculate_bazi路由函数，退出")
        return
    
    # 替换为新的路由实现
    new_route = r'''@bazi_bp.route('/calculate', methods=['POST'])
def calculate_bazi():
    """
    计算八字数据（不包含AI分析）
    
    此接口仅计算八字命盘数据，不进行AI分析，主要用于测试八字计算功能。
    所有八字计算均基于公历生日进行。
    """
    try:
        data = request.json
        
        # 验证必要参数
        required_params = ['solarYear', 'solarMonth', 'solarDay', 'solarHour', 
                          'gender', 'birthPlace', 'livingPlace']
        
        for param in required_params:
            if param not in data:
                return jsonify({'code': 400, 'message': f'缺少参数: {param}'}), 400
        
        # 从请求中获取数据
        solar_year = int(data['solarYear'])
        solar_month = int(data['solarMonth'])
        solar_day = int(data['solarDay'])
        solar_hour = int(data['solarHour'])
        gender = data['gender']
        birth_place = data['birthPlace']
        living_place = data['livingPlace']
        
        # 使用新的八字计算函数
        birth_time = f"{solar_year}-{solar_month:02d}-{solar_day:02d} {solar_hour:02d}:00:00"
        from utils.bazi_calculator import calculate_bazi as calc_bazi
        bazi_data = calc_bazi(gender, birth_time)
        
        # 格式化八字分析结果
        from utils.bazi_calculator import format_bazi_analysis
        formatted_data = format_bazi_analysis(bazi_data)
        
        # 获取农历日期
        lunar_date = bazi_data.get("lunarDate", {})
        lunar_year = lunar_date.get("year", solar_year)
        lunar_month = lunar_date.get("month", solar_month)
        lunar_day = lunar_date.get("day", solar_day)
        
        return jsonify({
            'code': 200,
            'message': '计算成功',
            'data': {
                'solar_date': {
                    'year': solar_year,
                    'month': solar_month,
                    'day': solar_day,
                    'hour': solar_hour
                },
                'lunar_date': {
                    'year': lunar_year,
                    'month': lunar_month,
                    'day': lunar_day
                },
                'gender': gender,
                'birth_place': birth_place,
                'living_place': living_place,
                'bazi': formatted_data['bazi'],
                'shen_sha': formatted_data['shenSha'],
                'qi_yun': formatted_data['qiYun'],
                'da_yun': formatted_data['daYun'],
                'bazi_data': bazi_data,
                'formatted_data': formatted_data
            }
        })
    
    except Exception as e:
        logging.error(f"八字计算错误: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'计算失败: {str(e)}'}), 500
'''
    
    # 替换路由函数
    new_content = re.sub(pattern, new_route, content, flags=re.DOTALL)
    
    # 写回文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("八字计算路由修复完成!")

if __name__ == '__main__':
    fix_file_directly()
    fix_calculate_route()
    logging.info('修复完成') 