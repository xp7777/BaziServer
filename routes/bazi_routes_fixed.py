from flask import Blueprint, jsonify, request, send_file, send_from_directory
import logging
import os
import threading
import time
import json
import requests
from datetime import datetime
from utils.bazi_calculator import calculate_bazi as calculate_bazi_util
from models.bazi_result_model import BaziResultModel
from models.order_model import OrderModel

# 创建蓝图
bazi_bp = Blueprint('bazi', __name__)

# 获取DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-a70d312fd07b4bce82624bd2373a4db4')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', "https://api.deepseek.com/v1/chat/completions")

# 存储正在进行分析的结果ID，避免重复分析
analyzing_results = {}

def calculate_bazi(birth_date, birth_time, gender):
    """计算八字信息
    
    Args:
        birth_date: 出生日期，格式为 YYYY-MM-DD
        birth_time: 出生时间，格式为 HH:MM
        gender: 性别，'male' 或 'female'
        
    Returns:
        包含八字信息的字典
    """
    try:
        # 使用八字计算工具
        bazi_data = calculate_bazi_util(birth_date, birth_time, gender)
        return bazi_data
    except Exception as e:
        logging.error(f"计算八字出错: {str(e)}")
        return None

def generate_ai_analysis(bazi_chart, focus_areas, gender):
    """生成八字AI分析
    
    Args:
        bazi_chart: 八字命盘数据
        focus_areas: 用户关注的领域
        gender: 性别，'male' 或 'female'
        
    Returns:
        包含各领域分析结果的字典
    """
    try:
        logging.info("开始生成AI分析")
        
        # 预设AI分析结果（如果API调用失败将使用这个）
        default_ai_analysis = {
            "health": "您的八字中五行分布较为平衡。从健康角度看，建议保持规律作息，避免过度劳累和情绪波动。定期体检，保持良好生活习惯。",
            "wealth": "您的财运有发展空间，适合稳健的理财方式。投资方面，建议分散投资组合，避免投机性强的项目。",
            "career": "您的事业发展有良好前景，具有一定的组织能力和执行力。建议持续提升专业技能，扩展人脉关系。",
            "relationship": "您的婚姻感情关系值得经营。已婚者需注意与伴侣的沟通，单身者有望遇到合适的对象。",
            "children": "您与子女关系和谐。教育方面，建议采用引导式的方法，尊重子女的兴趣发展。",
            "overall": "您的八字展现出潜力，人生发展有诸多可能。建议在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。"
        }
        
        # 构建性别信息
        gender_text = "男性" if gender == "male" else "女性"
        
        # 构建提示词
        prompt = f"""
        请你作为一位专业的命理师，为一位{gender_text}分析八字命盘。
        
        八字命盘信息:
        年柱: {bazi_chart['yearPillar']['heavenlyStem']}{bazi_chart['yearPillar']['earthlyBranch']}
        月柱: {bazi_chart['monthPillar']['heavenlyStem']}{bazi_chart['monthPillar']['earthlyBranch']}
        日柱: {bazi_chart['dayPillar']['heavenlyStem']}{bazi_chart['dayPillar']['earthlyBranch']}
        时柱: {bazi_chart['hourPillar']['heavenlyStem']}{bazi_chart['hourPillar']['earthlyBranch']}
        
        五行分布:
        金: {bazi_chart['fiveElements']['metal']}
        木: {bazi_chart['fiveElements']['wood']}
        水: {bazi_chart['fiveElements']['water']}
        火: {bazi_chart['fiveElements']['fire']}
        土: {bazi_chart['fiveElements']['earth']}
        
        流年信息(2025-2029):
        {', '.join([f"{y['year']}年: {y['heavenlyStem']}{y['earthlyBranch']}" for y in bazi_chart['flowingYears']])}
        
        请按照以下格式提供分析:
        
        健康分析:
        [详细的健康分析，包括体质特点、易发疾病、养生建议等]
        
        财运分析:
        [详细的财运分析，包括财运特点、适合行业、理财建议等]
        
        事业发展:
        [详细的事业分析，包括事业特点、职业方向、发展建议等]
        
        婚姻感情:
        [详细的婚姻感情分析，包括感情特点、相处方式、注意事项等]
        
        子女缘分:
        [详细的子女缘分分析，包括亲子关系、教育方式、注意事项等]
        
        综合建议:
        [综合分析和建议，未来5年的整体运势趋势]
        """
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一位专业的八字命理分析师，需要基于给定的八字信息提供专业分析。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        logging.info("准备调用DeepSeek API...")
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        
        logging.info(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result_data = response.json()
            ai_text = result_data['choices'][0]['message']['content']
            logging.info(f"成功获取DeepSeek API响应: {ai_text[:100]}...")
            
            # 解析AI回复，提取各部分分析
            new_analysis = {}
            
            # 提取健康分析
            if "健康分析" in ai_text:
                health_start = ai_text.find("健康分析")
                next_section = min(
                    [pos for pos in [ai_text.find("财运分析", health_start), 
                                    ai_text.find("事业发展", health_start),
                                    ai_text.find("婚姻感情", health_start),
                                    ai_text.find("子女缘分", health_start),
                                    ai_text.find("综合建议", health_start)] if pos > 0] or [len(ai_text)]
                )
                new_analysis['health'] = ai_text[health_start:next_section].replace("健康分析:", "").replace("健康分析", "").strip()
            
            # 提取财运分析
            if "财运分析" in ai_text:
                wealth_start = ai_text.find("财运分析")
                next_section = min(
                    [pos for pos in [ai_text.find("事业发展", wealth_start), 
                                    ai_text.find("婚姻感情", wealth_start),
                                    ai_text.find("子女缘分", wealth_start),
                                    ai_text.find("综合建议", wealth_start)] if pos > 0] or [len(ai_text)]
                )
                new_analysis['wealth'] = ai_text[wealth_start:next_section].replace("财运分析:", "").replace("财运分析", "").strip()
            
            # 提取事业发展
            if "事业发展" in ai_text:
                career_start = ai_text.find("事业发展")
                next_section = min(
                    [pos for pos in [ai_text.find("婚姻感情", career_start), 
                                    ai_text.find("子女缘分", career_start),
                                    ai_text.find("综合建议", career_start)] if pos > 0] or [len(ai_text)]
                )
                new_analysis['career'] = ai_text[career_start:next_section].replace("事业发展:", "").replace("事业发展", "").strip()
            
            # 提取婚姻感情
            if "婚姻感情" in ai_text:
                relationship_start = ai_text.find("婚姻感情")
                next_section = min(
                    [pos for pos in [ai_text.find("子女缘分", relationship_start), 
                                    ai_text.find("综合建议", relationship_start)] if pos > 0] or [len(ai_text)]
                )
                new_analysis['relationship'] = ai_text[relationship_start:next_section].replace("婚姻感情:", "").replace("婚姻感情", "").strip()
            
            # 提取子女缘分
            if "子女缘分" in ai_text:
                children_start = ai_text.find("子女缘分")
                next_section = min(
                    [pos for pos in [ai_text.find("综合建议", children_start)] if pos > 0] or [len(ai_text)]
                )
                new_analysis['children'] = ai_text[children_start:next_section].replace("子女缘分:", "").replace("子女缘分", "").strip()
            
            # 提取综合建议
            if "综合建议" in ai_text:
                overall_start = ai_text.find("综合建议")
                new_analysis['overall'] = ai_text[overall_start:].replace("综合建议:", "").replace("综合建议", "").strip()
            
            logging.info("DeepSeek API调用成功，返回分析结果")
            return new_analysis
        else:
            logging.error(f"调用DeepSeek API失败: {response.status_code}, {response.text[:200]}")
            logging.info("返回默认分析数据")
            return default_ai_analysis
    
    except Exception as e:
        logging.error(f"生成AI分析时出错: {str(e)}")
        return default_ai_analysis

@bazi_bp.route('/analyze', methods=['POST'])
def analyze_bazi():
    """分析八字"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 必需的字段
        required_fields = ['birthDate', 'birthTime', 'gender']
        if not all(field in data for field in required_fields):
            return jsonify(code=400, message="缺少必需字段"), 400
        
        # 提取参数
        birth_date = data['birthDate']
        birth_time = data['birthTime']
        gender = data['gender']
        
        # 记录日期时间信息
        logging.info(f"接收到的出生日期: {birth_date}, 出生时间: {birth_time}")
        
        # 保存原始日期格式，用于显示
        original_birth_date = birth_date
        
        # 确保日期格式正确
        if '/' in birth_date:
            # 将格式从YYYY/MM/DD转换为YYYY-MM-DD
            parts = birth_date.split('/')
            if len(parts) == 3:
                birth_date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                logging.info(f"日期格式已转换: {birth_date}")
        
        # 可选参数
        name = data.get('name', '匿名用户')
        focus_areas = data.get('focusAreas', ["health", "wealth", "career", "relationship"])
        birth_place = data.get('birthPlace', '未知')
        living_place = data.get('livingPlace', '未知')
        
        # 计算八字
        bazi_result = calculate_bazi(birth_date, birth_time, gender)
        
        if not bazi_result:
            return jsonify(code=500, message="八字计算失败"), 500
        
        # 生成结果ID
        timestamp = int(time.time() * 1000)
        result_id = f"RES{timestamp}"
        logging.info(f"生成新的结果ID: {result_id}, 使用用户指定的出生日期: {birth_date}")
        
        # 构建结果数据
        result_data = {
            '_id': result_id,
            'userId': 'test_user',  # 测试环境使用固定值
            'name': name,
            'birthDate': birth_date,
            'birthTime': birth_time,
            'gender': gender,
            'focusAreas': focus_areas,
            'originalRequest': {
                'birthDate': original_birth_date,
                'birthTime': birth_time,
                'gender': gender,
                'birthPlace': birth_place,
                'livingPlace': living_place
            },
            'basicInfo': {
                'solarYear': birth_date.split('-')[0],
                'solarMonth': birth_date.split('-')[1],
                'solarDay': birth_date.split('-')[2],
                'solarHour': birth_time,
                'gender': gender,
                'birthPlace': birth_place,
                'livingPlace': living_place
            },
            'baziChart': bazi_result,
            'aiAnalysis': {
                'overall': '正在分析中...',
                'health': '正在分析中...',
                'wealth': '正在分析中...',
                'career': '正在分析中...',
                'relationship': '正在分析中...',
                'children': '正在分析中...'
            },
            'createTime': datetime.now(),
            'analyzed': False
        }
        
        # 保存结果
        BaziResultModel.create(result_data)
        
        # 开始异步分析
        def perform_analysis():
            try:
                # 获取AI分析结果
                ai_analysis = generate_ai_analysis(bazi_result, focus_areas, gender)
                
                # 更新分析结果
                BaziResultModel.update_analysis(result_id, bazi_result, ai_analysis)
            except Exception as e:
                logging.error(f"异步分析失败: {str(e)}")
        
        # 启动异步分析线程
        analysis_thread = threading.Thread(target=perform_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        # 返回初步结果
        return jsonify(
            code=200,
            message="分析请求已接受，请稍后查询结果",
            data={
                'resultId': result_id,
                'baziChart': bazi_result
            }
        )
    
    except Exception as e:
        logging.error(f"分析八字出错: {str(e)}")
        return jsonify(code=500, message=f"分析请求失败: {str(e)}"), 500

@bazi_bp.route('/result/<result_id>', methods=['GET'])
def get_bazi_result(result_id):
    """获取分析结果"""
    try:
        # 查找结果
        result = BaziResultModel.find_by_id(result_id)
        
        if not result:
            return jsonify(code=404, message="结果不存在"), 404
        
        # 检查是否正在分析中
        if result_id in analyzing_results:
            logging.info(f"结果ID {result_id} 正在分析中，等待时间：{analyzing_results[result_id]}")
            return jsonify(
                code=202,  # 使用202表示请求已接受但尚未处理完成
                message=f"分析正在进行中，请稍候再试（已等待{analyzing_results[result_id]}秒）",
                data={
                    "status": "analyzing",
                    "waitTime": analyzing_results[result_id],
                    "baziChart": result.get('baziChart', {}),
                    "aiAnalysis": result.get('aiAnalysis', {})
                }
            ), 202
        
        # 如果已经分析过或有AI分析结果，直接返回
        if result.get('analyzed') or (result.get('aiAnalysis') and result.get('aiAnalysis').get('overall') != '正在分析中...'):
            logging.info(f"结果已分析，直接返回: {result_id}")
            return jsonify(
                code=200,
                message="获取结果成功",
                data=result
            )
        
        # 如果尚未分析但需要异步分析
        # 检查是否有八字信息
        if not result.get('birthDate') or not result.get('birthTime') or not result.get('gender'):
            return jsonify(code=400, message="分析数据不完整，缺少必要的出生信息"), 400
        
        # 获取出生信息，重新计算八字
        birth_date = result.get('birthDate')
        birth_time = result.get('birthTime')
        gender = result.get('gender')
        
        # 确保日期格式正确
        if birth_date and '/' in birth_date:
            # 将格式从YYYY/MM/DD转换为YYYY-MM-DD
            parts = birth_date.split('/')
            if len(parts) == 3:
                birth_date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                logging.info(f"日期格式已转换: {birth_date}")
        
        logging.info(f"准备计算八字: 生日={birth_date}, 时间={birth_time}")
        
        # 预设AI分析结果（如果API调用失败将使用这个）
        default_ai_analysis = {
            "health": "您的八字中五行分布较为平衡。从健康角度看，建议保持规律作息，避免过度劳累和情绪波动。定期体检，保持良好生活习惯。",
            "wealth": "您的财运有发展空间，适合稳健的理财方式。投资方面，建议分散投资组合，避免投机性强的项目。",
            "career": "您的事业发展有良好前景，具有一定的组织能力和执行力。建议持续提升专业技能，扩展人脉关系。",
            "relationship": "您的婚姻感情关系值得经营。已婚者需注意与伴侣的沟通，单身者有望遇到合适的对象。",
            "children": "您与子女关系和谐。教育方面，建议采用引导式的方法，尊重子女的兴趣发展。",
            "overall": "您的八字展现出潜力，人生发展有诸多可能。建议在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。"
        }
        
        # 记录开始分析的时间
        analyzing_results[result_id] = 0
        
        # 在单独的线程中进行分析
        def perform_analysis():
            try:
                from time import sleep, time
                start_time = time()
                
                # 更新等待时间
                def update_wait_time():
                    while result_id in analyzing_results:
                        current_time = time()
                        analyzing_results[result_id] = int(current_time - start_time)
                        sleep(1)
                
                # 启动计时线程
                timer_thread = threading.Thread(target=update_wait_time)
                timer_thread.daemon = True
                timer_thread.start()
                
                # 重新计算八字命盘信息
                logging.info(f"重新计算八字命盘信息: {result_id}, 生日={birth_date}, 时间={birth_time}")
                new_bazi_chart = calculate_bazi(birth_date, birth_time, gender)
                
                if not new_bazi_chart:
                    logging.error(f"重新计算八字失败: {result_id}")
                    # 使用原始八字信息
                    new_bazi_chart = result.get('baziChart', {})
                
                # 构建性别信息
                gender_text = "男性" if gender == "male" else "女性"
                
                # 构建提示词
                prompt = f"""
                请你作为一位专业的命理师，为一位{gender_text}分析八字命盘。
                
                八字命盘信息:
                年柱: {new_bazi_chart['yearPillar']['heavenlyStem']}{new_bazi_chart['yearPillar']['earthlyBranch']}
                月柱: {new_bazi_chart['monthPillar']['heavenlyStem']}{new_bazi_chart['monthPillar']['earthlyBranch']}
                日柱: {new_bazi_chart['dayPillar']['heavenlyStem']}{new_bazi_chart['dayPillar']['earthlyBranch']}
                时柱: {new_bazi_chart['hourPillar']['heavenlyStem']}{new_bazi_chart['hourPillar']['earthlyBranch']}
                
                五行分布:
                金: {new_bazi_chart['fiveElements']['metal']}
                木: {new_bazi_chart['fiveElements']['wood']}
                水: {new_bazi_chart['fiveElements']['water']}
                火: {new_bazi_chart['fiveElements']['fire']}
                土: {new_bazi_chart['fiveElements']['earth']}
                
                流年信息(2025-2029):
                {', '.join([f"{y['year']}年: {y['heavenlyStem']}{y['earthlyBranch']}" for y in new_bazi_chart['flowingYears']])}
                
                请按照以下格式提供分析:
                
                健康分析:
                [详细的健康分析，包括体质特点、易发疾病、养生建议等]
                
                财运分析:
                [详细的财运分析，包括财运特点、适合行业、理财建议等]
                
                事业发展:
                [详细的事业分析，包括事业特点、职业方向、发展建议等]
                
                婚姻感情:
                [详细的婚姻感情分析，包括感情特点、相处方式、注意事项等]
                
                子女缘分:
                [详细的子女缘分分析，包括亲子关系、教育方式、注意事项等]
                
                综合建议:
                [综合分析和建议，未来5年的整体运势趋势]
                """
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
                }
                
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一位专业的八字命理分析师，需要基于给定的八字信息提供专业分析。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3000
                }
                
                logging.info("准备调用DeepSeek API...")
                response = requests.post(
                    DEEPSEEK_API_URL,
                    headers=headers,
                    data=json.dumps(payload)
                )
                
                logging.info(f"API响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result_data = response.json()
                    ai_text = result_data['choices'][0]['message']['content']
                    logging.info(f"成功获取DeepSeek API响应: {ai_text[:100]}...")
                    
                    # 解析AI回复，提取各部分分析
                    new_analysis = {}
                    
                    # 提取健康分析
                    if "健康分析" in ai_text:
                        health_start = ai_text.find("健康分析")
                        next_section = min(
                            [pos for pos in [ai_text.find("财运分析", health_start), 
                                            ai_text.find("事业发展", health_start),
                                            ai_text.find("婚姻感情", health_start),
                                            ai_text.find("子女缘分", health_start),
                                            ai_text.find("综合建议", health_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['health'] = ai_text[health_start:next_section].replace("健康分析:", "").replace("健康分析", "").strip()
                    
                    # 提取财运分析
                    if "财运分析" in ai_text:
                        wealth_start = ai_text.find("财运分析")
                        next_section = min(
                            [pos for pos in [ai_text.find("事业发展", wealth_start), 
                                            ai_text.find("婚姻感情", wealth_start),
                                            ai_text.find("子女缘分", wealth_start),
                                            ai_text.find("综合建议", wealth_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['wealth'] = ai_text[wealth_start:next_section].replace("财运分析:", "").replace("财运分析", "").strip()
                    
                    # 提取事业发展
                    if "事业发展" in ai_text:
                        career_start = ai_text.find("事业发展")
                        next_section = min(
                            [pos for pos in [ai_text.find("婚姻感情", career_start), 
                                            ai_text.find("子女缘分", career_start),
                                            ai_text.find("综合建议", career_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['career'] = ai_text[career_start:next_section].replace("事业发展:", "").replace("事业发展", "").strip()
                    
                    # 提取婚姻感情
                    if "婚姻感情" in ai_text:
                        relationship_start = ai_text.find("婚姻感情")
                        next_section = min(
                            [pos for pos in [ai_text.find("子女缘分", relationship_start), 
                                            ai_text.find("综合建议", relationship_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['relationship'] = ai_text[relationship_start:next_section].replace("婚姻感情:", "").replace("婚姻感情", "").strip()
                    
                    # 提取子女缘分
                    if "子女缘分" in ai_text:
                        children_start = ai_text.find("子女缘分")
                        next_section = min(
                            [pos for pos in [ai_text.find("综合建议", children_start)] if pos > 0] or [len(ai_text)]
                        )
                        new_analysis['children'] = ai_text[children_start:next_section].replace("子女缘分:", "").replace("子女缘分", "").strip()
                    
                    # 提取综合建议
                    if "综合建议" in ai_text:
                        overall_start = ai_text.find("综合建议")
                        new_analysis['overall'] = ai_text[overall_start:].replace("综合建议:", "").replace("综合建议", "").strip()
                    
                    logging.info("DeepSeek API调用成功，使用真实分析结果")
                    
                    # 同时更新八字命盘和AI分析结果
                    BaziResultModel.update_full_analysis(
                        result_id,
                        new_bazi_chart,
                        new_analysis
                    )
                else:
                    logging.error(f"调用DeepSeek API失败: {response.status_code}, {response.text[:200]}")
                    logging.info("使用默认分析数据更新")
                    # 使用原始八字命盘和默认分析结果更新数据库
                    BaziResultModel.update_full_analysis(
                        result_id,
                        new_bazi_chart,
                        default_ai_analysis
                    )
            
            except Exception as e:
                logging.error(f"调用DeepSeek API出错: {str(e)}")
                logging.info("使用默认分析数据更新")
                # 使用原始八字命盘和默认分析结果更新数据库
                BaziResultModel.update_full_analysis(
                    result_id,
                    result.get('baziChart', {}),
                    default_ai_analysis
                )
            finally:
                # 分析完成，移除记录
                if result_id in analyzing_results:
                    del analyzing_results[result_id]
        
        # 启动分析线程
        analysis_thread = threading.Thread(target=perform_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        # 返回正在分析的状态和临时数据
        return jsonify(
            code=202,
            message="分析正在进行中，请稍后重试",
            data={
                "status": "analyzing",
                "waitTime": 0,
                "baziChart": result.get('baziChart', {}),
                "aiAnalysis": default_ai_analysis,
                "focusAreas": result.get('focusAreas', ["health", "wealth", "career", "relationship"])
            }
        ), 202
    
    except Exception as e:
        logging.error(f"获取结果时出错: {str(e)}")
        return jsonify(code=500, message=f"服务器内部错误: {str(e)}"), 500

@bazi_bp.route('/pdf/<result_id>', methods=['GET'])
def get_pdf(result_id):
    """下载PDF文档"""
    # 获取User-Agent，检测是否为微信浏览器
    user_agent = request.headers.get('User-Agent', '')
    is_weixin = 'MicroMessenger' in user_agent
    
    # 查找结果
    result = BaziResultModel.find_by_id(result_id)
    
    if not result:
        return jsonify(code=404, message="结果不存在"), 404
    
    # 检查是否已有PDF URL
    if result.get('pdfUrl'):
        # 检查本地PDF文件是否存在
        pdf_path = os.path.join(os.getcwd(), 'pdfs', f"{result_id}.pdf")
        
        if os.path.exists(pdf_path):
            # 微信环境中，优先返回JSON格式的URL
            if is_weixin:
                # 生成一个临时的可访问URL
                server_url = request.host_url.rstrip('/')
                pdf_url = f"{server_url}/pdfs/{result_id}.pdf"
                
                return jsonify(
                    code=200,
                    message="PDF生成成功",
                    data={"url": pdf_url}
                )
            
            # 非微信环境，直接发送文件
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"八字命理分析_{result_id}.pdf",
                mimetype='application/pdf'
            )
        
        # 如果文件不存在，但有URL，返回URL
        return jsonify(
            code=200,
            message="重定向到PDF",
            data={"url": result['pdfUrl']}
        )
    
    # 如果没有PDF URL，先生成PDF
    try:
        # 安全地导入PDF生成器，放在函数内部而非模块顶部
        from utils.pdf_generator import generate_pdf
        
        # 确保结果中包含必要的数据
        if not result.get('baziChart') or not result.get('aiAnalysis'):
            return jsonify(code=400, message="分析数据不完整，无法生成PDF"), 400
        
        # 生成PDF
        logging.info(f"开始生成PDF: {result_id}")
        pdf_url = generate_pdf(result)
        
        if not pdf_url:
            return jsonify(code=500, message="生成PDF失败"), 500
        
        # 更新数据库记录PDF URL
        BaziResultModel.update_pdf_url(result_id, pdf_url)
        
        # 检查PDF文件
        pdf_path = os.path.join(os.getcwd(), 'static', 'pdfs', f"bazi_analysis_{result_id}.html")
        if os.path.exists(pdf_path):
            # 微信环境中，优先返回JSON格式的URL
            if is_weixin:
                # 生成一个临时的可访问URL
                server_url = request.host_url.rstrip('/')
                pdf_url = f"{server_url}{pdf_url}"
                
                return jsonify(
                    code=200,
                    message="PDF生成成功",
                    data={"url": pdf_url}
                )
            
            # 非微信环境，直接发送文件
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"八字命理分析_{result_id}.html",
                mimetype='text/html'
            )
        
        # 如果本地文件不存在，返回URL
        return jsonify(
            code=200,
            message="PDF生成成功",
            data={"url": pdf_url}
        )
    
    except Exception as e:
        logging.error(f"生成PDF时出错: {str(e)}")
        return jsonify(code=500, message=f"生成PDF失败: {str(e)}"), 500

# 添加一个新的路由，用于展示神煞和大运流年的示例页面
@bazi_bp.route('/shen_sha_da_yun_demo')
def shen_sha_da_yun_demo():
    """展示神煞和大运流年的示例页面"""
    return send_from_directory('static', 'shen_sha_da_yun_demo.html')