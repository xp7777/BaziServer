from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

wechat_bp = Blueprint('wechat', __name__)

@wechat_bp.route('/jsapi/config', methods=['GET'])
def get_wechat_jsapi_config():
    """获取微信JSSDK配置"""
    try:
        from utils.wechat_jsapi import wechat_jsapi
        
        url = request.args.get('url')
        if not url:
            return jsonify({"code": 400, "message": "缺少URL参数"})
        
        if not wechat_jsapi:
            return jsonify({"code": 500, "message": "微信JSAPI未正确配置"})
        
        # 生成签名配置
        config = wechat_jsapi.generate_signature(url)
        
        if config:
            logger.info(f"生成JSSDK配置成功: {url}")
            return jsonify({
                "code": 200,
                "data": config
            })
        else:
            return jsonify({"code": 500, "message": "生成签名失败"})
            
    except Exception as e:
        logger.error(f"获取JSSDK配置失败: {str(e)}")
        return jsonify({"code": 500, "message": "获取配置失败"})