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

# 添加数据库连接
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()
orders_collection = db.orders  # 添加这行

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


@bazi_bp.route('/history', methods=['GET'])
@jwt_required()
def get_user_history():
    """获取用户的八字分析历史记录"""
    try:
        user_id = get_jwt_identity()
        
        # 从数据库获取用户的已支付订单，包含更多字段
        user_orders = list(orders_collection.find(
            {'userId': user_id, 'status': 'paid'},
            {
                '_id': 1, 
                'resultId': 1, 
                'createdAt': 1, 
                'createTime': 1,  # 添加这个字段
                'orderType': 1,
                'birthDate': 1,   # 从订单中获取出生日期
                'birthTime': 1,   # 从订单中获取出生时间
                'gender': 1,      # 从订单中获取性别
                'focusAreas': 1   # 从订单中获取关注领域
            }
        ).sort('createdAt', -1))
        
        # 格式化输出
        results = []
        for order in user_orders:
            if order.get('resultId'):
                # 优先使用 createdAt，如果没有则使用 createTime
                created_time = order.get('createdAt') or order.get('createTime')
                
                results.append({
                    'resultId': order.get('resultId'),
                    'birthDate': order.get('birthDate', ''),
                    'gender': order.get('gender', ''),
                    'focusAreas': order.get('focusAreas', []),
                    'createdAt': created_time
                })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': results
        })
    
    except Exception as e:
        logging.error(f"获取八字分析历史错误: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@bazi_bp.route('/result/<result_id>', methods=['GET'])
def get_bazi_result(result_id):
    """获取八字分析结果"""
    try:
        logging.info(f"尝试查找结果ID: {result_id}")
        
        # 从数据库获取结果
        result = BaziResultModel.find_by_id(result_id)
        
        if not result:
            logging.warning(f"未找到结果记录: {result_id}")
            return jsonify(code=404, message="未找到分析结果"), 404
        
        logging.info(f"找到结果记录: {result_id}")
        
        # 获取分析状态
        analysis_status = result.get('analysisStatus', 'pending')
        analysis_progress = result.get('analysisProgress', 0)
        
        # 检查AI分析是否真正完成 - 关键修改点
        ai_analysis = result.get('aiAnalysis', {})
        ai_analysis_complete = True
        
        # 检查关键字段是否包含"正在分析"或"分析生成中"
        if ai_analysis:
            for key, value in ai_analysis.items():
                if isinstance(value, str) and any(phrase in value for phrase in 
                                                ['正在分析', '分析生成中', '暂无']):
                    ai_analysis_complete = False
                    analysis_status = 'pending'  # 强制设置为进行中
                    break
        else:
            # 如果没有AI分析数据，也视为未完成
            ai_analysis_complete = False
            analysis_status = 'pending'
        
        # 只有当AI分析真正完成时，才返回completed状态
        if ai_analysis_complete:
            analysis_status = 'completed'
            analysis_progress = 100
        
        logging.info(f"成功获取分析结果: {result_id}, 分析状态: {analysis_status}, 分析进度: {analysis_progress}%")
        
        # 返回结果
        return jsonify(
            code=200,
            message="获取成功",
            data={
                "resultId": result_id,
                "baziChart": result.get('baziChart', {}),
                "aiAnalysis": result.get('aiAnalysis', {}),
                "analysisStatus": analysis_status,
                "analysisProgress": analysis_progress
            }
        )
    except Exception as e:
        logging.error(f"获取八字分析结果出错: {str(e)}")
        return jsonify(code=500, message=f"获取分析结果出错: {str(e)}"), 500

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
        
        # 获取性别信息并转换为中文
        gender = result.get('gender', 'male')
        gender_cn = '男' if gender == 'male' else '女'
        logging.info(f"使用性别信息: {gender} -> {gender_cn}")
        
        # 更新分析进度
        result['analysisProgress'] = 20
        success = BaziResultModel.update(result_id, result)
        if not success:
            logging.error(f"更新分析进度失败(20%): {result_id}")
        
        # 调用DeepSeek API进行分析
        try:
            # 准备分析请求
            analysis = generate_bazi_analysis(bazi_chart, gender_cn)
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

@bazi_bp.route('/followup/<result_id>', methods=['POST'])
def followup_analysis(result_id):
    """处理用户追问请求，生成特定领域的详细分析
    
    接收参数:
    - area: 追问领域，如'relationship', 'career', 'health'等
    - orderId: 支付订单ID (可选，如果提供则会更新订单状态)
    
    返回:
    - 该领域的详细分析结果
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify(code=400, message="请提供追问信息"), 400
        
        # 获取追问领域
        area = data.get('area')
        order_id = data.get('orderId')
        
        # 验证追问领域
        valid_areas = ["relationship", "career", "wealth", "health", "children", 
                      "parents", "education", "study", "social", "future", "fiveYears", "personality"]
        
        if not area:
            return jsonify(code=400, message="请提供追问领域"), 400
        
        # 如果不是标准领域，尝试映射
        if area not in valid_areas:
            area_mapping = {
                "marriage": "relationship",
                "work": "career",
                "money": "wealth",
                "friends": "social",
                "lifePlan": "future"
            }
            if area in area_mapping:
                logging.info(f"将非标准领域 {area} 映射为 {area_mapping[area]}")
                area = area_mapping[area]
        
        # 查找分析结果
        result = BaziResultModel.find_by_id(result_id)
        
        if not result:
            return jsonify(code=404, message="找不到分析结果"), 404
        
        # 检查是否有八字命盘数据
        if not result.get('baziChart'):
            return jsonify(code=400, message="分析结果缺少八字命盘数据"), 400
        
        # 获取基本信息
        bazi_chart = result.get('baziChart', {})
        gender = result.get('gender', 'male')
        birth_date = result.get('birthDate')
        birth_time = result.get('birthTime')
        
        # 检查是否已经有该领域的分析
        if result.get('followups') and isinstance(result['followups'], dict) and area in result['followups']:
            # 如果已经有分析结果，直接返回
            analysis = result['followups'][area]
            if analysis and not analysis.startswith('正在分析'):
                logging.info(f"已有追问分析，直接返回: {result_id}, {area}")
                return jsonify(
                    code=200,
                    message="分析已存在",
                    data={
                        "area": area,
                        "analysis": analysis
                    }
                )
        
        # 如果没有分析结果或者分析结果是"正在分析"，启动异步分析
        logging.info(f"启动异步追问分析: {result_id}, {area}")
        
        # 先在数据库中标记为正在分析
        if not result.get('followups'):
            result['followups'] = {}
        result['followups'][area] = '正在分析中，请稍候...'
        BaziResultModel.update(result_id, result)
        
        # 启动异步线程进行分析
        import threading
        threading.Thread(
            target=async_generate_followup,
            args=(result_id, area, birth_date, birth_time, gender)
        ).start()
        
        return jsonify(
            code=200,
            message="分析已启动",
            data={
                "area": area,
                "analysis": "正在分析中，请稍候..."
            }
        )
    except Exception as e:
        logging.error(f"启动追问分析失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=str(e)), 500

# 异步生成追问分析的函数
def async_generate_followup(result_id, area, birth_date=None, birth_time=None, gender=None):
    """异步生成追问分析"""
    try:
        logging.info(f"开始异步生成追问分析: {result_id}, {area}")
        
        # 查找分析结果
        result = BaziResultModel.find_by_id(result_id)
        if not result:
            logging.error(f"找不到分析结果: {result_id}")
            return
        
        # 获取基本信息
        bazi_chart = result.get('baziChart', {})
        gender = gender or result.get('gender', 'male')
        gender_cn = '男' if gender == 'male' else '女'
        birth_date = birth_date or result.get('birthDate')
        birth_time = birth_time or result.get('birthTime')
        
        # 构建性别信息
        gender_text = "男性" if gender == "male" else "女性"
        
        # 计算年龄
        if birth_date:
            try:
                birth_year = int(birth_date.split('-')[0])
                current_year = datetime.now().year
                age = current_year - birth_year
            except:
                age = None
        else:
            age = None
        
        # 根据年龄确定分析类型
        age_category = "成人"
        if age is not None:
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
        
        # 构建针对特定领域的提示词
        area_prompts = {
            "relationship": "请详细分析此人的婚姻感情状况，包括感情特点、婚姻质量、伴侣选择、相处方式、情感挑战及应对策略等。分析内容至少200字，要具体、专业、有针对性。",
            "career": "请详细分析此人的事业发展情况，包括事业特点、职业方向、发展建议、职场人际关系、晋升机会、创业可能性等。分析内容至少200字，要具体、专业、有针对性。",
            "wealth": "请详细分析此人的财运情况，包括财运特点、财富来源、适合行业、理财建议、投资方向、财运高低期等。分析内容至少200字，要具体、专业、有针对性。",
            "health": "请详细分析此人的身体健康状况，包括体质特点、五行与健康的关系、易发疾病、养生建议、饮食调理、作息建议等。分析内容至少200字，要具体、专业、有针对性。",
            "children": "请详细分析此人的子女缘分，包括子女数量、性别倾向、亲子关系、教育方式、子女发展方向、注意事项等。分析内容至少200字，要具体、专业、有针对性。",
            "parents": "请详细分析此人与父母的关系，包括与父母的关系特点、相处模式、沟通方式、孝道表现、潜在冲突及化解方法等。分析内容至少200字，要具体、专业、有针对性。",
            "education": "请详细分析此人的学业情况，包括学习能力、适合的学习方式、学科优势、学业发展建议、考试应对等。分析内容至少200字，要具体、专业、有针对性。",
            "social": "请详细分析此人的人际关系，包括人际交往特点、社交能力、朋友圈特征、人脉发展、团队合作能力、社交策略等。分析内容至少200字，要具体、专业、有针对性。",
            "future": "请详细分析此人未来五年的运势，包括事业、财运、健康、感情等方面的变化趋势，重大转折点，机遇与挑战，以及应对策略。分析内容至少200字，要具体、专业、有针对性。",
            "personality": "请详细分析此人的性格特点，包括性格优势、劣势、人际交往特点、情绪特点、思维方式、行为模式等。分析内容至少200字，要具体、专业、有针对性。",
            "fiveYears": "请详细分析此人未来五年的运势，包括事业、财运、健康、感情等方面的变化趋势，重大转折点，机遇与挑战，以及应对策略。分析内容至少200字，要具体、专业、有针对性。",
            "study": "请详细分析此人的学业情况，包括学习能力、适合的学习方式、学科优势、学业发展建议、考试应对等。分析内容至少200字，要具体、专业、有针对性。"
        }
        
        # 获取对应领域的提示词
        area_prompt = area_prompts.get(area, "请详细分析此人的情况。分析内容至少200字，要具体、专业、有针对性。")
        
        # 构建完整提示词
        prompt = f"""
        请你作为一位专业的命理师，为一位{gender_text}分析八字命盘中关于【{area}】方面的详细情况。
        
        【基本信息】
        性别: {gender_text}
        出生日期: {birth_date}
        出生时间: {birth_time}
        年龄: {age}岁
        年龄类别: {age_category}
        
        【八字命盘信息】
        年柱: {bazi_chart.get('yearPillar', {}).get('heavenlyStem', '')}{bazi_chart.get('yearPillar', {}).get('earthlyBranch', '')}
        月柱: {bazi_chart.get('monthPillar', {}).get('heavenlyStem', '')}{bazi_chart.get('monthPillar', {}).get('earthlyBranch', '')}
        日柱: {bazi_chart.get('dayPillar', {}).get('heavenlyStem', '')}{bazi_chart.get('dayPillar', {}).get('earthlyBranch', '')}
        时柱: {bazi_chart.get('hourPillar', {}).get('heavenlyStem', '')}{bazi_chart.get('hourPillar', {}).get('earthlyBranch', '')}
        
        【五行分布】
        金: {bazi_chart.get('fiveElements', {}).get('metal', 0)}
        木: {bazi_chart.get('fiveElements', {}).get('wood', 0)}
        水: {bazi_chart.get('fiveElements', {}).get('water', 0)}
        火: {bazi_chart.get('fiveElements', {}).get('fire', 0)}
        土: {bazi_chart.get('fiveElements', {}).get('earth', 0)}
        
        【神煞信息】
        日冲: {bazi_chart.get('shenSha', {}).get('dayChong', '无')}
        值神: {bazi_chart.get('shenSha', {}).get('zhiShen', '无')}
        喜神方位: {bazi_chart.get('shenSha', {}).get('xiShen', '无')}
        福神方位: {bazi_chart.get('shenSha', {}).get('fuShen', '无')}
        财神方位: {bazi_chart.get('shenSha', {}).get('caiShen', '无')}
        本命神煞: {', '.join(bazi_chart.get('shenSha', {}).get('benMing', ['无']))}
        
        【分析要求】
        {area_prompt}
        
        请直接给出分析内容，无需标题，无需前言，直接开始分析。
        """
        
        # 调用DeepSeek API生成分析
        from utils.ai_service import call_deepseek_api
        
        # 尝试调用AI服务
        try:
            ai_text = call_deepseek_api(prompt)
            
            if ai_text:
                logging.info(f"成功获取DeepSeek API响应: {ai_text[:100]}...")
                
                # 更新数据库中的分析结果
                if not result.get('followups'):
                    result['followups'] = {}
                result['followups'][area] = ai_text
                BaziResultModel.update(result_id, result)
                
                logging.info(f"成功更新追问分析: {result_id}, {area}")
                return ai_text
            else:
                logging.error(f"DeepSeek API返回空结果")
                # 更新为错误信息
                if not result.get('followups'):
                    result['followups'] = {}
                result['followups'][area] = "分析生成失败，请稍后重试"
                BaziResultModel.update(result_id, result)
                return None
        except Exception as api_error:
            logging.error(f"调用DeepSeek API失败: {str(api_error)}")
            # 更新为错误信息
            if not result.get('followups'):
                result['followups'] = {}
            result['followups'][area] = f"分析生成失败: {str(api_error)[:50]}"
            BaziResultModel.update(result_id, result)
            return None
    except Exception as e:
        logging.error(f"异步生成追问分析失败: {str(e)}")
        logging.error(traceback.format_exc())
        return None 
