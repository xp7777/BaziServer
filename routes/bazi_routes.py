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
        # 检查PDF文件是否存在
        pdf_dir = os.path.join(current_app.static_folder, 'pdfs')
        pdf_path = os.path.join(pdf_dir, f'bazi_{result_id}.pdf')
        
        if not os.path.exists(pdf_path):
            return jsonify(code=404, message="PDF文件不存在"), 404
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'八字命理分析_{result_id}.pdf'
        )
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