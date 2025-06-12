from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
import os
import logging
import traceback
from models.bazi_result_model import BaziResultModel
from models.order_model import OrderModel
from utils.bazi_calculator import calculate_bazi, calculate_flowing_years
from utils.ai_service import generate_bazi_analysis
from datetime import datetime
from flask_cors import cross_origin

# 确保DeepSeek API密钥被设置
if not os.environ.get('DEEPSEEK_API_KEY'):
    os.environ['DEEPSEEK_API_KEY'] = 'sk-a70d312fd07b4bce82624bd2373a4db4'
    logging.info("已设置DeepSeek API密钥环境变量")

bazi_bp = Blueprint('bazi', __name__)

# 获取MongoDB客户端和数据库
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-a70d312fd07b4bce82624bd2373a4db4')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

logging.info(f"DeepSeek API密钥前5位: {DEEPSEEK_API_KEY[:5]}...")
logging.info(f"DeepSeek API URL: {DEEPSEEK_API_URL}")

# 存储正在进行分析的结果ID，避免重复分析
analyzing_results = {}

@bazi_bp.route('/result/<result_id>', methods=['GET'])
def get_bazi_result(result_id):
    try:
        logging.info(f"尝试查找结果ID: {result_id}")
        
        # 从数据库获取结果
        result = BaziResultModel.find_by_id(result_id)
        if not result:
            logging.error(f"未找到结果记录: {result_id}")
            return jsonify(code=404, message="未找到分析结果"), 404
            
        logging.info(f"找到结果记录: {result_id}")
        
        # 检查八字数据是否完整
        if not result.get('baziChart') or not result['baziChart'].get('yearPillar'):
            logging.error(f"八字数据不完整: {result_id}")
            return jsonify(code=500, message="八字数据不完整，请重新生成"), 500
            
        # 检查神煞数据
        if not result['baziChart'].get('shenSha'):
            logging.warning(f"神煞数据不存在，初始化空数据")
            result['baziChart']['shenSha'] = {
                'dayChong': '',
                'zhiShen': '',
                'pengZuGan': '',
                'pengZuZhi': '',
                'xiShen': '',
                'fuShen': '',
                'caiShen': '',
                'benMing': [],
                'yearGan': [],
                'yearZhi': [],
                'dayGan': [],
                'dayZhi': []
            }
            
        # 检查大运数据
        if not result['baziChart'].get('daYun'):
            logging.warning(f"大运数据不存在，初始化空数据")
            result['baziChart']['daYun'] = {
                'startAge': 1,
                'startYear': 2025,
                'isForward': True,
                'daYunList': []
            }
            
        # 检查流年数据
        if not result['baziChart'].get('flowingYears'):
            logging.warning(f"流年数据不存在，初始化空数据")
            result['baziChart']['flowingYears'] = []
        
        # 检查分析状态和进度
        if 'analysisStatus' not in result:
            result['analysisStatus'] = 'completed'  # 默认为已完成
        if 'analysisProgress' not in result:
            result['analysisProgress'] = 100  # 默认为100%完成
            
        # 检查分析内容是否存在，如果存在则标记为已完成
        if result.get('analysis') or result.get('aiAnalysis'):
            result['analysisStatus'] = 'completed'
            result['analysisProgress'] = 100
            
        # 如果分析状态是completed但进度不是100%，强制设置为100%
        if result.get('analysisStatus') == 'completed' and result.get('analysisProgress') != 100:
            result['analysisProgress'] = 100
            
        # 如果分析状态是pending但不在分析队列中，标记为已完成
        if result.get('analysisStatus') == 'pending' and result_id not in analyzing_results:
            result['analysisStatus'] = 'completed'
            result['analysisProgress'] = 100
            
        logging.info(f"成功获取分析结果: {result_id}, 分析状态: {result.get('analysisStatus')}, 分析进度: {result.get('analysisProgress')}%")
        return jsonify(code=200, data=result)
    except Exception as e:
        logging.error(f"获取八字分析结果失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=str(e)), 500

# 新增API端点：更新八字分析数据
@bazi_bp.route('/update/<result_id>', methods=['POST', 'OPTIONS'])
@cross_origin()  # 添加跨域支持
def update_bazi_analysis(result_id):
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200, 'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
        
    try:
        logging.info(f"更新八字分析数据: {result_id}")
        data = request.json
        
        # 检查结果是否存在
        result = BaziResultModel.find_by_id(result_id)
        if not result:
            logging.error(f"未找到结果记录: {result_id}")
            return jsonify(code=404, message="未找到分析结果"), 404
        
        # 解析输入数据
        birth_date = data.get('birthDate')
        birth_time = data.get('birthTime')
        gender = data.get('gender', 'male')
        calendar_type = data.get('calendarType', 'solar')
        force_recalculate = data.get('forceRecalculate', False)
        generate_shensha_data = data.get('generateShenshaData', False)
        generate_dayun_data = data.get('generateDayunData', False)
        generate_liunian_data = data.get('generateLiunianData', False)
        use_deepseek_api = data.get('useDeepseekAPI', False)
        
        logging.info(f"更新请求参数: birthDate={birth_date}, birthTime={birth_time}, gender={gender}, " 
                    f"forceRecalculate={force_recalculate}, generateShenshaData={generate_shensha_data}, " 
                    f"generateDayunData={generate_dayun_data}, generateLiunianData={generate_liunian_data}, "
                    f"useDeepseekAPI={use_deepseek_api}")
        
        # 组合出生日期时间
        birth_datetime = f"{birth_date} {birth_time}"
        
        # 计算八字(如果强制重新计算或没有八字数据)
        if force_recalculate or not result.get('baziChart'):
            logging.info(f"计算八字数据: {birth_datetime}, gender={gender}")
            bazi_chart = calculate_bazi(birth_datetime, gender)
            
            # 更新八字图
            result['baziChart'] = bazi_chart
            
            # 如果需要，生成神煞数据
            if generate_shensha_data:
                logging.info(f"生成神煞数据")
                # 这里应该调用神煞数据生成函数，当前直接使用calculate_bazi返回的数据
                
            # 如果需要，生成大运数据
            if generate_dayun_data:
                logging.info(f"生成大运数据")
                # 计算大运数据通常集成在calculate_bazi中，此处可以额外处理
                
            # 如果需要，生成流年数据
            if generate_liunian_data:
                logging.info(f"生成流年数据")
                # 生成流年数据
                current_year = datetime.now().year
                birth_year = int(birth_date.split('-')[0])
                
                # 使用calculate_flowing_years函数生成流年数据
                flowing_years = calculate_flowing_years(gender, {
                    "birthYear": birth_year,
                    "dayHeavenlyStem": result['baziChart']['dayPillar']['heavenlyStem'],
                    "dayEarthlyBranch": result['baziChart']['dayPillar']['earthlyBranch']
                })
                
                # 更新流年数据
                result['baziChart']['flowingYears'] = flowing_years
            
            # 更新数据库
            success = BaziResultModel.update(result_id, result)
            if not success:
                logging.error(f"更新八字图数据失败: {result_id}")
                return jsonify(code=500, message="更新八字图数据失败"), 500
                
            logging.info(f"已更新八字图数据: {result_id}")
            
            # 如果需要使用DeepSeek API进行分析，设置标志
            if use_deepseek_api:
                result['analysisStatus'] = 'pending'
                result['analysisProgress'] = 0
                analyzing_results[result_id] = True
                success = BaziResultModel.update(result_id, result)
                if not success:
                    logging.error(f"更新分析状态失败: {result_id}")
                
                # 异步调用分析接口
                from threading import Thread
                Thread(target=process_deepseek_analysis, args=(result_id, result)).start()
                logging.info(f"已触发异步DeepSeek分析: {result_id}")
        
        return jsonify(code=200, message="八字分析数据更新成功", data={"resultId": result_id})
    except Exception as e:
        logging.error(f"更新八字分析数据失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=str(e)), 500

# 新增API端点：触发八字深度分析
@bazi_bp.route('/analyze/<result_id>', methods=['POST', 'OPTIONS'])
@cross_origin()  # 添加跨域支持
def analyze_bazi(result_id):
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200, 'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
        
    try:
        logging.info(f"触发八字深度分析: {result_id}")
        data = request.json
        use_deepseek_api = data.get('useDeepseekAPI', True)
        
        # 检查结果是否存在
        result = BaziResultModel.find_by_id(result_id)
        if not result:
            logging.error(f"未找到结果记录: {result_id}")
            return jsonify(code=404, message="未找到分析结果"), 404
        
        # 检查是否已经在分析中
        if result_id in analyzing_results:
            logging.info(f"分析已在进行中: {result_id}")
            return jsonify(code=200, message="分析已在进行中", data={"resultId": result_id})
        
        # 更新分析状态
        result['analysisStatus'] = 'pending'
        result['analysisProgress'] = 0
        analyzing_results[result_id] = True
        success = BaziResultModel.update(result_id, result)
        if not success:
            logging.error(f"更新分析状态失败: {result_id}")
            return jsonify(code=500, message="更新分析状态失败"), 500
        
        # 异步调用DeepSeek API
        if use_deepseek_api:
            from threading import Thread
            Thread(target=process_deepseek_analysis, args=(result_id, result)).start()
            logging.info(f"已触发异步DeepSeek分析: {result_id}")
        
        return jsonify(code=200, message="八字分析已触发", data={"resultId": result_id})
    except Exception as e:
        logging.error(f"触发八字分析失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=str(e)), 500

# DeepSeek API处理函数
def process_deepseek_analysis(result_id, result):
    try:
        logging.info(f"开始进行DeepSeek API分析: {result_id}")
        
        # 更新分析进度
        result['analysisProgress'] = 10
        success = BaziResultModel.update(result_id, result)
        if not success:
            logging.error(f"更新分析进度失败(10%): {result_id}")
        
        # 获取八字数据
        bazi_chart = result.get('baziChart', {})
        if not bazi_chart:
            logging.error(f"没有八字数据，无法进行分析: {result_id}")
            result['analysisStatus'] = 'failed'
            result['analysisMessage'] = "没有八字数据，无法进行分析"
            BaziResultModel.update(result_id, result)
            del analyzing_results[result_id]
            return
        
        # 获取性别信息
        gender = result.get('gender', 'male')
        logging.info(f"使用性别信息: {gender}")
        
        # 更新分析进度
        result['analysisProgress'] = 20
        success = BaziResultModel.update(result_id, result)
        if not success:
            logging.error(f"更新分析进度失败(20%): {result_id}")
        
        # 调用DeepSeek API进行分析
        try:
            # 准备分析请求
            analysis = generate_bazi_analysis(bazi_chart, gender)
            logging.info(f"DeepSeek API分析完成: {result_id}")
            
            # 更新结果
            result['analysisStatus'] = 'completed'  # 明确设置为已完成
            result['analysisProgress'] = 100  # 明确设置为100%
            result['analysis'] = analysis
            
            # 同时更新到aiAnalysis字段，确保前端能正确显示
            if 'aiAnalysis' not in result or not result['aiAnalysis']:
                result['aiAnalysis'] = {}
            
            # 将analysis字段的内容复制到aiAnalysis字段
            for key, value in analysis.items():
                result['aiAnalysis'][key] = value
                
            # 确保分析状态明确标记为已完成
            result['analysisCompleted'] = True
            
            success = BaziResultModel.update(result_id, result)
            if not success:
                logging.error(f"更新分析结果失败: {result_id}")
            else:
                logging.info(f"成功更新分析结果: {result_id}")
            
        except Exception as api_error:
            logging.error(f"DeepSeek API调用失败: {str(api_error)}")
            result['analysisStatus'] = 'failed'
            result['analysisMessage'] = f"DeepSeek API调用失败: {str(api_error)}"
            result['analysisProgress'] = 0
            BaziResultModel.update(result_id, result)
        
    except Exception as e:
        logging.error(f"处理DeepSeek分析时出错: {str(e)}")
        logging.error(traceback.format_exc())
        
        try:
            result['analysisStatus'] = 'failed'
            result['analysisMessage'] = f"处理失败: {str(e)}"
            result['analysisProgress'] = 0
            BaziResultModel.update(result_id, result)
        except:
            pass
    finally:
        # 清理分析标志
        if result_id in analyzing_results:
            del analyzing_results[result_id]

@bazi_bp.route('/pdf/<result_id>', methods=['GET'])
def get_bazi_pdf(result_id):
    try:
        logging.info(f"请求下载PDF，结果ID: {result_id}")
        
        # 从数据库获取分析结果
        result = BaziResultModel.find_by_id(result_id)
        if not result:
            logging.error(f"未找到分析结果: {result_id}")
            return jsonify(code=404, message="未找到分析结果"), 404
        
        # 检查URL参数是否要求强制重新生成
        force_regenerate = request.args.get('force', 'false').lower() == 'true'
        
        # 检查是否需要解析Markdown，默认为true
        parse_markdown = request.args.get('parseMarkdown', 'true').lower() == 'true'
        logging.info(f"是否解析Markdown: {parse_markdown}")
        
        # 获取PDF内容（如果force_regenerate为True，则跳过缓存）
        pdf_content = None
        if not force_regenerate:
            pdf_content = BaziResultModel.get_pdf_content(result_id)
        
        # 如果没有PDF内容或强制重新生成，即时生成
        if not pdf_content or force_regenerate:
            logging.info(f"正在重新生成PDF内容: {result_id}, force={force_regenerate}, parseMarkdown={parse_markdown}")
            
            # 导入PDF生成器
            from utils.pdf_generator import generate_pdf_content
            
            # 生成PDF内容（返回二进制数据），传递parse_md参数
            pdf_content = generate_pdf_content(result, parse_md=parse_markdown)
            
            if not pdf_content:
                logging.error(f"生成PDF内容失败: {result_id}")
                return jsonify(code=500, message="生成PDF内容失败"), 500
            
            # 更新数据库，保存PDF内容
            BaziResultModel.update_pdf_content(result_id, pdf_content)
        
        # 设置ASCII文件名，避免编码问题
        ascii_filename = f'bazi_report_{result_id}.pdf'
        
        # 直接返回PDF文件流
        from io import BytesIO
        response = send_file(
            BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=ascii_filename
        )
        
        # 添加跨域头和缓存控制
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # 只使用ASCII字符设置Content-Disposition头
        response.headers['Content-Disposition'] = f'attachment; filename="{ascii_filename}"'
        
        logging.info(f"成功返回PDF内容，大小: {len(pdf_content)}字节")
        return response
    except Exception as e:
        logging.error(f"获取PDF文件失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=str(e)), 500

@bazi_bp.route('/followup/<result_id>/<area>', methods=['GET'])
def get_followup_analysis(result_id, area):
    try:
        # 记录请求的原始area值
        logging.info(f"请求追问分析: 结果ID={result_id}, 领域={area}")
        
        # 从数据库获取追问分析结果
        result = BaziResultModel.get_followup_analysis(result_id, area)
        if not result:
            logging.warning(f"未找到追问分析结果: {result_id}, {area}")
            return jsonify(code=404, message="未找到追问分析结果"), 404
        
        # 记录返回的结果结构
        logging.info(f"成功获取追问分析: 结果={result.get('area')}, 分析长度={len(result.get('analysis', '')) if result.get('analysis') else 0}")
            
        return jsonify(code=200, data=result)
    except Exception as e:
        logging.error(f"获取追问分析失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=str(e)), 500

@bazi_bp.route('/followup/list/<result_id>', methods=['GET'])
def get_followup_list(result_id):
    try:
        logging.info(f"获取追问列表: {result_id}")
        
        # 从数据库获取已支付的追问列表
        followups = BaziResultModel.get_followup_list(result_id)
        
        # 记录返回结果
        if followups:
            logging.info(f"找到{len(followups)}个追问分析，领域: {[f.get('area') for f in followups if isinstance(f, dict)]}")
        else:
            logging.info(f"未找到任何追问分析")
            
        return jsonify(code=200, data={"followups": followups})
    except Exception as e:
        logging.error(f"获取追问列表失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=str(e)), 500 