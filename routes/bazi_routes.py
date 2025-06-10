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
            logging.error(f"神煞数据缺失: {result_id}")
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
            logging.error(f"大运数据缺失: {result_id}")
            result['baziChart']['daYun'] = {
                'startAge': 1,
                'startYear': 2025,
                'isForward': True,
                'daYunList': []
            }
            
        # 检查流年数据
        if not result['baziChart'].get('flowingYears'):
            logging.error(f"流年数据缺失: {result_id}")
            result['baziChart']['flowingYears'] = []
            
        logging.info(f"成功获取分析结果: {result_id}")
        return jsonify(code=200, data=result)
    except Exception as e:
        logging.error(f"获取八字分析结果失败: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify(code=500, message=str(e)), 500

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
        
        # 获取PDF内容（如果force_regenerate为True，则跳过缓存）
        pdf_content = None
        if not force_regenerate:
            pdf_content = BaziResultModel.get_pdf_content(result_id)
        
        # 如果没有PDF内容或强制重新生成，即时生成
        if not pdf_content or force_regenerate:
            logging.info(f"正在重新生成PDF内容: {result_id}, force={force_regenerate}")
            
            # 导入PDF生成器
            from utils.pdf_generator import generate_pdf_content
            
            # 生成PDF内容（返回二进制数据）
            pdf_content = generate_pdf_content(result)
            
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