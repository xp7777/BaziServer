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

def generate_ai_analysis(bazi_chart, focus_areas, gender, birth_date=None, birth_time=None):
    """生成八字AI分析
    
    Args:
        bazi_chart: 八字命盘数据
        focus_areas: 用户关注的领域
        gender: 性别，'male' 或 'female'
        birth_date: 出生日期，格式为 YYYY-MM-DD
        birth_time: 出生时间
        
    Returns:
        包含各领域分析结果的字典
    """
    try:
        logging.info("开始生成AI分析")
        
        # 如果未提供出生日期时间，使用默认分析
        if not birth_date or not birth_time:
            logging.warning("未提供出生日期或时间，返回默认分析")
            return {
                "health": "您的八字中五行分布较为平衡。从健康角度看，建议保持规律作息，避免过度劳累和情绪波动。定期体检，保持良好生活习惯。",
                "wealth": "您的财运有发展空间，适合稳健的理财方式。投资方面，建议分散投资组合，避免投机性强的项目。",
                "career": "您的事业发展有良好前景，具有一定的组织能力和执行力。建议持续提升专业技能，扩展人脉关系。",
                "relationship": "您的婚姻感情关系值得经营。已婚者需注意与伴侣的沟通，单身者有望遇到合适的对象。",
                "children": "您与子女关系和谐。教育方面，建议采用引导式的方法，尊重子女的兴趣发展。",
                "overall": "您的八字展现出潜力，人生发展有诸多可能。建议在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。"
            }
        
        # 构建性别信息
        gender_text = "男性" if gender == "male" else "女性"
        
        # 计算年龄
        birth_year = int(birth_date.split('-')[0])
        current_year = datetime.now().year
        age = current_year - birth_year
        
        # 根据年龄确定分析类型
        age_category = "成人"
        if age < 3:
            age_category = "婴幼儿"
        elif age < 12:
            age_category = "儿童"
        elif age < 18:
            age_category = "青少年"
        elif age < 30:
            age_category = "青年"
        elif age < 50:
            age_category = "中年"
        else:
            age_category = "老年"
            
        logging.info(f"用户年龄: {age}岁，年龄类别: {age_category}")
        
        # 针对2003年出生的用户特别处理
        if birth_year == 2003:
            # 已经进入青少年后期或青年期，重点关注学业和性格发展
            logging.info("检测到2003年出生的用户，已进入青少年后期或青年期")
            age_category = "青少年"  # 或根据实际情况设为青年
        
        # 根据年龄类别设置默认分析结果
        default_ai_analysis = {}
        
        if age_category in ["婴幼儿", "儿童", "青少年"]:
            default_ai_analysis = {
                "health": f"您的孩子今年{age}岁，正处于{age_category}阶段。八字显示体质较为{['偏弱', '中和', '偏强'][age % 3]}，应注重均衡饮食和充足睡眠，增强免疫力，多参加户外活动增强体质。",
                "wealth": f"对于{age}岁的{age_category}，财运主要表现为家庭经济环境对其成长的影响。建议家长培养孩子正确的金钱观，适当教导储蓄和消费的概念。",
                "career": f"{age}岁的{age_category}，事业主要体现为学业发展。八字显示学习能力较强，具有{['逻辑思维', '创造性思维', '记忆力'][age % 3]}方面的优势，适合通过{'多种教学方式' if age < 12 else '自主学习'}发展潜能。",
                "relationship": f"您的孩子性格{['内向稳重', '活泼开朗', '温和平静'][age % 3]}，在人际交往中{['需要更多鼓励', '善于表达', '较为谨慎'][age % 3]}。与父母关系{['亲密', '有时需要沟通', '和谐'][age % 3]}，建议家长{['多陪伴', '尊重独立性', '耐心引导'][age % 3]}。",
                "children": f"对于{age}岁的{age_category}，此项分析主要关注其与父母的缘分。八字显示与{['父亲', '母亲', '双亲'][age % 3]}有较深的缘分，家长宜{['耐心教导', '给予空间', '以身作则'][age % 3]}。",
                "overall": f"{age}岁的{age_category}正处于重要的成长阶段。未来几年是培养兴趣和能力的关键期，建议重点发展{['语言表达', '逻辑思维', '艺术天赋', '体育特长', '社交能力'][age % 5]}，为将来打下良好基础。"
            }
        elif age_category == "青年":
            default_ai_analysis = {
                "health": "您的八字显示体质中等，精力充沛但易有压力过大的倾向。建议保持规律作息，适当锻炼，注意调节情绪，避免过度劳累。",
                "wealth": "您的财运起伏有度，适合稳健成长型的理财方式。目前正处于积累阶段，建议增加金融知识，规划长期投资，为未来打好基础。",
                "career": "您的事业发展前景广阔，具有较强的学习能力和适应性。建议在现阶段着重提升专业技能和拓展人脉，为职业发展创造更多可能。",
                "relationship": "您的感情生活需要用心经营。性格中的独立与依赖需要平衡，建议在感情中保持真诚沟通，理解包容，共同成长。",
                "children": "您与子女的缘分取决于当前及未来的人生选择。如有子女计划，建议提前做好身心准备；如已为人父母，注重亲子沟通和家庭和谐。",
                "overall": "青年时期是人生的黄金阶段，您有较多发展机遇。建议明确目标，持续学习，保持积极心态，未来几年将是个人成长的重要时期。"
            }
        elif age_category == "中年":
            default_ai_analysis = {
                "health": "您的八字显示体质趋于平稳，但需注意保养。建议定期体检，加强锻炼，调整饮食结构，预防慢性疾病，保持心情舒畅。",
                "wealth": "您的财运已进入稳定期，有一定的积累基础。建议做好资产配置，平衡风险与收益，注重养老规划，同时可适当考虑投资与子女教育相关的领域。",
                "career": "您的事业发展已有一定基础，经验丰富，判断力强。未来可着重发挥专业优势，提升管理能力，或考虑适度转型，寻找新的增长点。",
                "relationship": "您的婚姻关系需要持续经营。中年阶段面临家庭与事业的双重压力，建议加强与伴侣的沟通，共同面对挑战，维护家庭和谐。",
                "children": "您与子女的关系正处于重要阶段。建议在教育方式上既要有原则，又要尊重子女个性，引导其健康成长，建立良好的亲子关系。",
                "overall": "中年阶段是事业与家庭的平衡期。您具备丰富的人生经验，未来几年将是巩固成果、稳步发展的时期，建议合理规划，保持积极心态。"
            }
        else:  # 老年
            default_ai_analysis = {
                "health": "您的八字显示体质需要特别关注。建议坚持适度锻炼，保持良好作息，定期体检，关注慢性疾病管理，调整饮食习惯，保持心情愉悦。",
                "wealth": "您的财运已进入收获期。建议做好养老规划，确保资金安全，适当考虑遗产安排，享受当下生活的同时也为家人提供支持。",
                "career": "您的事业已有丰硕成果，经验丰富。现阶段可考虑将经验传授他人，发挥余热，或从事一些力所能及的顾问工作，丰富晚年生活。",
                "relationship": "您的婚姻关系是重要的精神支柱。老年阶段更需要相互扶持，共度晚年。建议多关心伴侣健康，增加共同活动，维系情感连接。",
                "children": "您与子女的关系进入新阶段。建议尊重子女的生活方式，适度参与但不过多干预，保持良好沟通，享受天伦之乐。",
                "overall": "老年阶段是人生的总结与享受期。您拥有丰富的人生阅历，未来几年建议保持健康的生活方式，培养兴趣爱好，享受家庭生活，传承人生智慧。"
            }
        
        # 构建提示词
        prompt = f"""
        请你作为一位专业的命理师，为一位{gender_text}分析八字命盘。
        
        【基本信息】
        性别: {gender_text}
        出生日期: {birth_date}
        出生时间: {birth_time}
        年龄: {age}岁
        年龄类别: {age_category}
        
        【八字命盘信息】
        年柱: {bazi_chart['yearPillar']['heavenlyStem']}{bazi_chart['yearPillar']['earthlyBranch']}
        月柱: {bazi_chart['monthPillar']['heavenlyStem']}{bazi_chart['monthPillar']['earthlyBranch']}
        日柱: {bazi_chart['dayPillar']['heavenlyStem']}{bazi_chart['dayPillar']['earthlyBranch']}
        时柱: {bazi_chart['hourPillar']['heavenlyStem']}{bazi_chart['hourPillar']['earthlyBranch']}
        
        【五行分布】
        金: {bazi_chart['fiveElements']['metal']}
        木: {bazi_chart['fiveElements']['wood']}
        水: {bazi_chart['fiveElements']['water']}
        火: {bazi_chart['fiveElements']['fire']}
        土: {bazi_chart['fiveElements']['earth']}
        
        【神煞信息】
        日冲: {bazi_chart['shenSha'].get('dayChong', '无')}
        值神: {bazi_chart['shenSha'].get('zhiShen', '无')}
        彭祖百忌: {bazi_chart['shenSha'].get('pengZuGan', '无')}, {bazi_chart['shenSha'].get('pengZuZhi', '无')}
        喜神方位: {bazi_chart['shenSha'].get('xiShen', '无')}
        福神方位: {bazi_chart['shenSha'].get('fuShen', '无')}
        财神方位: {bazi_chart['shenSha'].get('caiShen', '无')}
        本命神煞: {', '.join(bazi_chart['shenSha'].get('benMing', ['无']))}
        年干神煞: {', '.join(bazi_chart['shenSha'].get('yearGan', ['无']))}
        年支神煞: {', '.join(bazi_chart['shenSha'].get('yearZhi', ['无']))}
        日干神煞: {', '.join(bazi_chart['shenSha'].get('dayGan', ['无']))}
        日支神煞: {', '.join(bazi_chart['shenSha'].get('dayZhi', ['无']))}
        
        【大运信息】
        起运年龄: {bazi_chart['daYun'].get('startAge', '无')}岁
        起运年份: {bazi_chart['daYun'].get('startYear', '无')}年
        大运列表: {', '.join([f"{da_yun['index']}运({da_yun['startYear']}-{da_yun['endYear']}): {da_yun['ganZhi']}" for da_yun in bazi_chart['daYun'].get('daYun', [])[:5]])}
        
        【流年信息】
        以下是当前及未来几年的流年信息:
        """
        
        # 添加流年信息
        current_year = datetime.now().year
        liu_nian_found = False
        
        # 从大运中获取流年信息
        for da_yun in bazi_chart['daYun'].get('daYun', []):
            if da_yun.get('isCurrent', False) and da_yun.get('liuNian'):
                liu_nian_text = ""
                for liu_nian in da_yun['liuNian']:
                    if liu_nian['year'] >= current_year and liu_nian['year'] <= current_year + 5:
                        liu_nian_text += f"\n{liu_nian['year']}年({liu_nian['ganZhi']}): 岁运-{liu_nian['suiYun']['taiSui']}, "
                        liu_nian_text += f"太阴-{liu_nian['suiYun']['taiYin']}, "
                        liu_nian_text += f"太阳-{liu_nian['suiYun']['taiYang']}, "
                        liu_nian_text += f"神煞-{', '.join(liu_nian['shenSha']) if liu_nian['shenSha'] else '无'}"
                if liu_nian_text:
                    prompt += liu_nian_text
                    liu_nian_found = True
                break
        
        # 如果没有找到流年信息，添加默认文本
        if not liu_nian_found:
            prompt += "\n暂无详细流年信息，请根据大运总体情况分析未来几年运势"
        
        # 继续添加分析要求
        prompt += """
        
        【分析要求】
        请根据此人的年龄({age}岁)和年龄类别({age_category})提供相应的分析。
        - 对于儿童和青少年，重点分析性格特点、学习发展、健康成长，不必过多关注婚姻和事业；
        - 对于青年人，重点分析事业发展、感情关系、性格特点；
        - 对于中年人，全面分析事业、健康、财运、家庭关系；
        - 对于老年人，重点分析健康、家庭关系、养生之道。
        
        请按照以下格式提供分析:
        
        健康分析:
        [详细的健康分析，包括体质特点、易发疾病、养生建议等，根据年龄段调整内容]
        
        财运分析:
        [详细的财运分析，包括财运特点、适合行业、理财建议等，根据年龄段调整内容]
        
        事业发展:
        [详细的事业分析，包括事业特点、职业方向、发展建议等，对于儿童青少年则分析学业发展情况]
        
        婚姻感情:
        [详细的婚姻感情分析，包括感情特点、相处方式、注意事项等，对于儿童则分析人际关系和与父母的相处]
        
        子女缘分:
        [详细的子女缘分分析，包括亲子关系、教育方式、注意事项等，对于未成年人则可分析与父母的关系]
        
        综合建议:
        [综合分析和建议，未来5年的整体运势趋势，根据年龄段调整内容]
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
                ai_analysis = generate_ai_analysis(bazi_result, focus_areas, gender, birth_date, birth_time)
                
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
        
        # 计算年龄和年龄类别
        if birth_date:
            birth_year = int(birth_date.split('-')[0])
            current_year = datetime.now().year
            age = current_year - birth_year
            
            # 根据年龄确定分析类型
            age_category = "成人"
            if age < 3:
                age_category = "婴幼儿"
            elif age < 12:
                age_category = "儿童"
            elif age < 18:
                age_category = "青少年"
            elif age < 30:
                age_category = "青年"
            elif age < 50:
                age_category = "中年"
            else:
                age_category = "老年"
                
            logging.info(f"用户年龄: {age}岁，年龄类别: {age_category}")
            
            # 针对2003年出生的用户特别处理
            if birth_year == 2003:
                # 已经进入青少年后期或青年期，重点关注学业和性格发展
                logging.info("检测到2003年出生的用户，已进入青少年后期或青年期")
                age_category = "青少年"  # 或根据实际情况设为青年
            
            # 根据年龄类别设置默认分析结果
            default_ai_analysis = {}
            
            if age_category in ["婴幼儿", "儿童", "青少年"]:
                default_ai_analysis = {
                    "health": f"您的孩子今年{age}岁，正处于{age_category}阶段。八字显示体质较为{['偏弱', '中和', '偏强'][age % 3]}，应注重均衡饮食和充足睡眠，增强免疫力，多参加户外活动增强体质。",
                    "wealth": f"对于{age}岁的{age_category}，财运主要表现为家庭经济环境对其成长的影响。建议家长培养孩子正确的金钱观，适当教导储蓄和消费的概念。",
                    "career": f"{age}岁的{age_category}，事业主要体现为学业发展。八字显示学习能力较强，具有{['逻辑思维', '创造性思维', '记忆力'][age % 3]}方面的优势，适合通过{'多种教学方式' if age < 12 else '自主学习'}发展潜能。",
                    "relationship": f"您的孩子性格{['内向稳重', '活泼开朗', '温和平静'][age % 3]}，在人际交往中{['需要更多鼓励', '善于表达', '较为谨慎'][age % 3]}。与父母关系{['亲密', '有时需要沟通', '和谐'][age % 3]}，建议家长{['多陪伴', '尊重独立性', '耐心引导'][age % 3]}。",
                    "children": f"对于{age}岁的{age_category}，此项分析主要关注其与父母的缘分。八字显示与{['父亲', '母亲', '双亲'][age % 3]}有较深的缘分，家长宜{['耐心教导', '给予空间', '以身作则'][age % 3]}。",
                    "overall": f"{age}岁的{age_category}正处于重要的成长阶段。未来几年是培养兴趣和能力的关键期，建议重点发展{['语言表达', '逻辑思维', '艺术天赋', '体育特长', '社交能力'][age % 5]}，为将来打下良好基础。"
                }
            elif age_category == "青年":
                default_ai_analysis = {
                    "health": "您的八字显示体质中等，精力充沛但易有压力过大的倾向。建议保持规律作息，适当锻炼，注意调节情绪，避免过度劳累。",
                    "wealth": "您的财运起伏有度，适合稳健成长型的理财方式。目前正处于积累阶段，建议增加金融知识，规划长期投资，为未来打好基础。",
                    "career": "您的事业发展前景广阔，具有较强的学习能力和适应性。建议在现阶段着重提升专业技能和拓展人脉，为职业发展创造更多可能。",
                    "relationship": "您的感情生活需要用心经营。性格中的独立与依赖需要平衡，建议在感情中保持真诚沟通，理解包容，共同成长。",
                    "children": "您与子女的缘分取决于当前及未来的人生选择。如有子女计划，建议提前做好身心准备；如已为人父母，注重亲子沟通和家庭和谐。",
                    "overall": "青年时期是人生的黄金阶段，您有较多发展机遇。建议明确目标，持续学习，保持积极心态，未来几年将是个人成长的重要时期。"
                }
            elif age_category == "中年":
                default_ai_analysis = {
                    "health": "您的八字显示体质趋于平稳，但需注意保养。建议定期体检，加强锻炼，调整饮食结构，预防慢性疾病，保持心情舒畅。",
                    "wealth": "您的财运已进入稳定期，有一定的积累基础。建议做好资产配置，平衡风险与收益，注重养老规划，同时可适当考虑投资与子女教育相关的领域。",
                    "career": "您的事业发展已有一定基础，经验丰富，判断力强。未来可着重发挥专业优势，提升管理能力，或考虑适度转型，寻找新的增长点。",
                    "relationship": "您的婚姻关系需要持续经营。中年阶段面临家庭与事业的双重压力，建议加强与伴侣的沟通，共同面对挑战，维护家庭和谐。",
                    "children": "您与子女的关系正处于重要阶段。建议在教育方式上既要有原则，又要尊重子女个性，引导其健康成长，建立良好的亲子关系。",
                    "overall": "中年阶段是事业与家庭的平衡期。您具备丰富的人生经验，未来几年将是巩固成果、稳步发展的时期，建议合理规划，保持积极心态。"
                }
            else:  # 老年
                default_ai_analysis = {
                    "health": "您的八字显示体质需要特别关注。建议坚持适度锻炼，保持良好作息，定期体检，关注慢性疾病管理，调整饮食习惯，保持心情愉悦。",
                    "wealth": "您的财运已进入收获期。建议做好养老规划，确保资金安全，适当考虑遗产安排，享受当下生活的同时也为家人提供支持。",
                    "career": "您的事业已有丰硕成果，经验丰富。现阶段可考虑将经验传授他人，发挥余热，或从事一些力所能及的顾问工作，丰富晚年生活。",
                    "relationship": "您的婚姻关系是重要的精神支柱。老年阶段更需要相互扶持，共度晚年。建议多关心伴侣健康，增加共同活动，维系情感连接。",
                    "children": "您与子女的关系进入新阶段。建议尊重子女的生活方式，适度参与但不过多干预，保持良好沟通，享受天伦之乐。",
                    "overall": "老年阶段是人生的总结与享受期。您拥有丰富的人生阅历，未来几年建议保持健康的生活方式，培养兴趣爱好，享受家庭生活，传承人生智慧。"
                }
        else:
            # 预设AI分析结果（如果没有出生日期或API调用失败将使用这个）
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
                
                # 获取分析结果
                new_analysis = generate_ai_analysis(new_bazi_chart, result.get('focusAreas', ["health", "wealth", "career", "relationship"]), gender, birth_date, birth_time)
                
                # 更新数据库
                BaziResultModel.update_full_analysis(result_id, new_bazi_chart, new_analysis)
                
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

# 添加一个计算八字的API，仅返回计算结果而不保存到数据库
@bazi_bp.route('/calculate', methods=['POST'])
def calculate_bazi_api():
    """计算八字API，供测试页面使用"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(code=400, message="请提供出生信息"), 400
        
        birth_date = data.get('birthDate')
        birth_time = data.get('birthTime')
        gender = data.get('gender', 'male')
        
        if not birth_date:
            return jsonify(code=400, message="请提供出生日期"), 400
        
        if not birth_time:
            birth_time = "12:00"  # 默认中午
            
        # 调用计算函数
        bazi_data = calculate_bazi(birth_date, birth_time, gender)
        
        if not bazi_data:
            return jsonify(code=500, message="计算八字失败"), 500
            
        return jsonify(code=200, message="计算成功", data=bazi_data), 200
        
    except Exception as e:
        logging.error(f"计算八字API出错: {str(e)}")
        return jsonify(code=500, message=f"服务器内部错误: {str(e)}"), 500