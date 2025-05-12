from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from models.bazi_result_model import BaziResultModel
from models.order_model import OrderModel
from utils.bazi_calculator import calculate_bazi, calculate_flowing_years
from utils.ai_service import generate_bazi_analysis
from utils.pdf_generator import generate_pdf

bazi_bp = Blueprint('bazi', __name__)

@bazi_bp.route('/result/<result_id>', methods=['GET'])
@jwt_required()
def get_result(result_id):
    """获取分析结果"""
    user_id = get_jwt_identity()
    
    # 查找结果
    result = BaziResultModel.find_by_id(result_id)
    
    if not result:
        return jsonify(code=404, message="结果不存在"), 404
    
    if result['userId'] != user_id:
        return jsonify(code=403, message="无权访问此结果"), 403
    
    # 查找关联的订单
    order = OrderModel.find_by_id(result['orderId'])
    
    if not order or order['status'] != 'paid':
        return jsonify(code=400, message="订单未支付"), 400
    
    # 如果八字数据为空，进行计算
    if not result['baziData']:
        bazi_data = calculate_bazi(
            gender=result['gender'],
            birth_time=result['birthTime']
        )
        
        # 计算流年大运
        flowing_years = calculate_flowing_years(
            gender=result['gender'],
            bazi_data=bazi_data
        )
        
        bazi_data['flowingYears'] = flowing_years
        
        # 更新八字数据
        BaziResultModel.update_bazi_data(result_id, bazi_data)
        result['baziData'] = bazi_data
    
    # 检查是否需要进行AI分析
    for area in result['focusAreas']:
        if area not in result.get('aiAnalysis', {}):
            # 生成分析
            analysis = generate_bazi_analysis(
                bazi_data=result['baziData'],
                gender=result['gender'],
                birth_time=result['birthTime'],
                focus_area=area
            )
            
            # 更新分析结果
            BaziResultModel.update_ai_analysis(result_id, area, analysis)
            
            if 'aiAnalysis' not in result:
                result['aiAnalysis'] = {}
            
            result['aiAnalysis'][area] = analysis
    
    # 如果PDF URL为空且已经有完整的分析结果，生成PDF
    if not result.get('pdfUrl') and len(result.get('aiAnalysis', {})) == len(result['focusAreas']):
        pdf_url = generate_pdf(result)
        if pdf_url:
            BaziResultModel.update_pdf_url(result_id, pdf_url)
            result['pdfUrl'] = pdf_url
    
    return jsonify(
        code=200,
        message="成功",
        data={
            "resultId": result['_id'],
            "baziData": result['baziData'],
            "aiAnalysis": result['aiAnalysis'],
            "pdfUrl": result.get('pdfUrl')
        }
    )

@bazi_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """获取历史分析记录"""
    user_id = get_jwt_identity()
    
    # 查找用户的所有结果
    results = BaziResultModel.find_by_user(user_id)
    
    # 简化结果数据
    history = []
    for result in results:
        history.append({
            "resultId": result['_id'],
            "createTime": result['createTime'].isoformat(),
            "focusAreas": result['focusAreas'],
            "pdfUrl": result.get('pdfUrl')
        })
    
    return jsonify(
        code=200,
        message="成功",
        data=history
    )

@bazi_bp.route('/pdf/<result_id>', methods=['GET'])
@jwt_required()
def get_pdf(result_id):
    """下载PDF文档"""
    user_id = get_jwt_identity()
    
    # 查找结果
    result = BaziResultModel.find_by_id(result_id)
    
    if not result:
        return jsonify(code=404, message="结果不存在"), 404
    
    if result['userId'] != user_id:
        return jsonify(code=403, message="无权访问此结果"), 403
    
    # 查找关联的订单
    order = OrderModel.find_by_id(result['orderId'])
    
    if not order or order['status'] != 'paid':
        return jsonify(code=400, message="订单未支付"), 400
    
    if not result.get('pdfUrl'):
        return jsonify(code=404, message="PDF文档不存在"), 404
    
    # 假设PDF文件存储在本地
    pdf_path = os.path.join(os.getcwd(), 'pdfs', f"{result_id}.pdf")
    
    if os.path.exists(pdf_path):
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"八字命理分析_{result_id}.pdf",
            mimetype='application/pdf'
        )
    
    # 如果文件不存在，重定向到URL
    return jsonify(
        code=302,
        message="重定向到PDF",
        data={"url": result['pdfUrl']}
    ) 