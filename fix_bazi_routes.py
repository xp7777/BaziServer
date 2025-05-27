#!/usr/bin/env python
# coding: utf-8

import os
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_bazi_routes_indentation():
    """修复routes/bazi_routes.py文件中的缩进问题"""
    file_path = 'routes/bazi_routes.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复问题1: DeepSeek API密钥处的缩进
    pattern1 = r'# 检查DeepSeek API密钥并启动异步分析\s+deepseek_api_key = os\.getenv\(\'DEEPSEEK_API_KEY\'\)\s+if deepseek_api_key'
    replacement1 = '        # 检查DeepSeek API密钥并启动异步分析\n        deepseek_api_key = os.getenv(\'DEEPSEEK_API_KEY\')\n        if deepseek_api_key'
    content = re.sub(pattern1, replacement1, content)
    
    # 修复问题2: PDF路径处的缩进
    pattern2 = r'if result\.get\(\'pdfUrl\'\):\s+# 检查本地PDF文件是否存在\s+pdf_path = os\.path\.join\(os\.getcwd\(\), \'pdfs\', f\"\{result_id\}\.pdf\"\)'
    replacement2 = 'if result.get(\'pdfUrl\'):\n        # 检查本地PDF文件是否存在\n        pdf_path = os.path.join(os.getcwd(), \'pdfs\', f"{result_id}.pdf")'
    content = re.sub(pattern2, replacement2, content)
    
    # 修复问题3: 文件存在判断的缩进
    pattern3 = r'if os\.path\.exists\(pdf_path\):\s+# 微信环境中，优先返回JSON格式的URL'
    replacement3 = '        if os.path.exists(pdf_path):\n            # 微信环境中，优先返回JSON格式的URL'
    content = re.sub(pattern3, replacement3, content)
    
    # 修复问题4: 非微信环境下的返回缩进
    pattern4 = r'# 非微信环境，直接发送文件\s+return send_file'
    replacement4 = '            # 非微信环境，直接发送文件\n            return send_file'
    content = re.sub(pattern4, replacement4, content)
    
    # 修复问题5: 如果文件不存在的逻辑缩进
    pattern5 = r'# 如果文件不存在，但有URL，返回URL\s+return jsonify'
    replacement5 = '        # 如果文件不存在，但有URL，返回URL\n        return jsonify'
    content = re.sub(pattern5, replacement5, content)
    
    # 修复问题6: jsonify缩进问题
    pattern6 = r'code=200,\s+message="重定向到PDF",'
    replacement6 = 'code=200,\n            message="重定向到PDF",'
    content = re.sub(pattern6, replacement6, content)
    
    # 保存修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logging.info(f'修复成功: {file_path}')

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
    backup_path = f"{file_path}.bak_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
    fix_bazi_routes_indentation()
    fix_calculate_route()
    logging.info('修复完成') 