from datetime import datetime
from pymongo import MongoClient, ReturnDocument
from bson import ObjectId
import os
import logging
import json
import traceback
import base64

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取MongoDB URI
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()

results_collection = db.bazi_results

# 自定义JSON编码器处理datetime对象
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

class BaziResultModel:
    @staticmethod
    def create_result(user_id, order_id, gender, birth_time, focus_areas, birth_date=None):
        """创建新的八字分析结果"""
        result_id = "RES" + order_id if not order_id.startswith("RES") else order_id
        
        result = {
            "_id": result_id,
            "userId": user_id,
            "orderId": order_id,
            "gender": gender,
            "birthTime": birth_time,
            "focusAreas": focus_areas,
            "baziData": None,
            "aiAnalysis": {},
            "pdfUrl": None,
            "createTime": datetime.now()
        }
        
        if birth_date:
            result["birthDate"] = birth_date
        
        inserted = results_collection.insert_one(result)
        result['_id'] = str(inserted.inserted_id)
        return result
    
    @staticmethod
    def create(data):
        """创建新的分析结果
        
        Args:
            data: 分析结果数据
            
        Returns:
            str: 新创建的结果ID
        """
        try:
            # 确保有_id字段
            if '_id' not in data:
                data['_id'] = str(ObjectId())
                
            # 添加创建时间
            if 'createTime' not in data:
                data['createTime'] = datetime.now()
                
            # 检查aiAnalysis字段的完整性
            if 'aiAnalysis' in data:
                logger.info(f"创建结果时检查aiAnalysis字段: {list(data['aiAnalysis'].keys())}")
                
                # 确保所有必要字段都存在
                required_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children']
                for field in required_fields:
                    if field not in data['aiAnalysis'] or not data['aiAnalysis'][field]:
                        logger.warning(f"aiAnalysis缺少必要字段: {field}，添加默认值")
                        data['aiAnalysis'][field] = f"正在分析{field}..."
                        
            # 检查baziChart字段的完整性
            if 'baziChart' in data:
                logger.info(f"创建结果时检查baziChart字段: {list(data['baziChart'].keys() if isinstance(data['baziChart'], dict) else [])}")
                
                # 确保年月日时四柱都存在
                pillars = ['yearPillar', 'monthPillar', 'dayPillar', 'hourPillar']
                for pillar in pillars:
                    if pillar not in data['baziChart'] or not data['baziChart'][pillar]:
                        logger.warning(f"baziChart缺少必要字段: {pillar}，添加默认值")
                        data['baziChart'][pillar] = {'heavenlyStem': '?', 'earthlyBranch': '?'}
                
                # 确保五行分布存在
                if 'fiveElements' not in data['baziChart'] or not data['baziChart']['fiveElements']:
                    logger.warning("baziChart缺少五行分布，添加默认值")
                    data['baziChart']['fiveElements'] = {'metal': 0, 'wood': 0, 'water': 0, 'fire': 0, 'earth': 0}
            
            # 检查JSON序列化
            try:
                json_str = json.dumps(data, default=str)
                logger.debug(f"数据JSON序列化成功，长度: {len(json_str)}")
            except Exception as json_err:
                logger.error(f"数据JSON序列化失败: {str(json_err)}")
                # 尝试找出问题字段
                for key, value in data.items():
                    try:
                        json.dumps({key: value}, default=str)
                    except:
                        logger.error(f"问题字段: {key}, 类型: {type(value)}")
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                try:
                                    json.dumps({sub_key: sub_value}, default=str)
                                except:
                                    logger.error(f"问题子字段: {key}.{sub_key}, 类型: {type(sub_value)}")
                                    # 尝试修复问题字段
                                    data[key][sub_key] = str(sub_value)
            
            # 插入数据
            result = results_collection.insert_one(data)
            result_id = str(result.inserted_id)
            logger.info(f"成功创建分析结果: {result_id}")
            return result_id
        except Exception as e:
            logger.error(f"创建分析结果失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def find_by_id(result_id):
        """根据ID查找分析结果"""
        try:
            logging.info(f"尝试查找结果ID: {result_id}")
            
            # 尝试使用原始ID查询
            result = results_collection.find_one({'_id': result_id})
            
            # 如果没有找到且原始ID不是以RES开头的，尝试添加RES前缀
            if not result and isinstance(result_id, str) and not result_id.startswith('RES'):
                res_id = f"RES{result_id}"
                logging.info(f"尝试使用RES前缀查询: {res_id}")
                result = results_collection.find_one({'_id': res_id})
                
                # 如果找到了，更新result_id为添加了RES前缀的ID
                if result:
                    result_id = res_id
            
            # 对于已经以RES开头的ID，尝试去掉RES前缀
            elif not result and isinstance(result_id, str) and result_id.startswith('RES'):
                no_prefix_id = result_id[3:]  # 去掉RES前缀
                logging.info(f"尝试去掉RES前缀查询: {no_prefix_id}")
                result = results_collection.find_one({'_id': no_prefix_id})
                
                # 如果找到了，更新result_id为去掉了RES前缀的ID
                if result:
                    result_id = no_prefix_id
            
            if result:
                logging.info(f"找到结果记录: {result.get('_id')}")
                
                # 检查八字数据是否完整
                if not result.get('baziChart'):
                    logging.warning(f"八字数据不存在，初始化空数据")
                    result['baziChart'] = {
                        'yearPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'monthPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'dayPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'hourPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                        'fiveElements': {'metal': 0, 'wood': 0, 'water': 0, 'fire': 0, 'earth': 0},
                        'shenSha': {
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
                        },
                        'daYun': {
                            'startAge': 1,
                            'startYear': datetime.now().year,
                            'isForward': True,
                            'daYunList': []
                        },
                        'flowingYears': []
                    }
                    
                    # 更新数据库
                    results_collection.update_one(
                        {"_id": result['_id']},
                        {"$set": {"baziChart": result['baziChart']}}
                    )
                
                # 检查AI分析数据是否完整
                if not result.get('aiAnalysis'):
                    logging.warning(f"AI分析数据不存在，初始化空数据")
                    result['aiAnalysis'] = {
                        'overall': '正在分析整体运势...',
                        'health': '正在分析健康运势...',
                        'wealth': '正在分析财运...',
                        'career': '正在分析事业运势...',
                        'relationship': '正在分析感情运势...',
                        'children': '正在分析子女运势...'
                    }
                    
                    # 更新数据库
                    results_collection.update_one(
                        {"_id": result['_id']},
                        {"$set": {"aiAnalysis": result['aiAnalysis']}}
                    )
                else:
                    # 确保所有必要字段都存在
                    required_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children']
                    updates = {}
                    for field in required_fields:
                        if field not in result['aiAnalysis'] or not result['aiAnalysis'][field]:
                            logging.warning(f"AI分析缺少字段: {field}，添加默认值")
                            result['aiAnalysis'][field] = f"正在分析{field}..."
                            updates[f"aiAnalysis.{field}"] = f"正在分析{field}..."
                    
                    # 如果有需要更新的字段，执行更新
                    if updates:
                        results_collection.update_one(
                            {"_id": result['_id']},
                            {"$set": updates}
                        )
                
                # 检查神煞数据是否完整
                if 'baziChart' in result and 'shenSha' not in result['baziChart']:
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
                    
                    # 更新数据库
                    results_collection.update_one(
                        {"_id": result['_id']},
                        {"$set": {"baziChart.shenSha": result['baziChart']['shenSha']}}
                    )
                
                # 检查大运数据是否完整
                if 'baziChart' in result and 'daYun' not in result['baziChart']:
                    logging.warning(f"大运数据不存在，初始化空数据")
                    result['baziChart']['daYun'] = {
                        'startAge': 1,
                        'startYear': datetime.now().year,
                        'isForward': True,
                        'daYunList': []
                    }
                    
                    # 更新数据库
                    results_collection.update_one(
                        {"_id": result['_id']},
                        {"$set": {"baziChart.daYun": result['baziChart']['daYun']}}
                    )
                
                # 检查流年数据是否完整
                if 'baziChart' in result and 'flowingYears' not in result['baziChart']:
                    logging.warning(f"流年数据不存在，初始化空数据")
                    result['baziChart']['flowingYears'] = []
                    
                    # 更新数据库
                    results_collection.update_one(
                        {"_id": result['_id']},
                        {"$set": {"baziChart.flowingYears": result['baziChart']['flowingYears']}}
                    )
                
                return result
            else:
                logging.warning(f"未找到结果记录: {result_id}")
                return None
                
        except Exception as e:
            logging.error(f"查找分析结果失败: {str(e)}")
            logging.error(traceback.format_exc())
            return None
    
    @staticmethod
    def find_by_user(user_id):
        """查找用户的所有结果"""
        results = list(results_collection.find({"userId": user_id}))
        for result in results:
            result['_id'] = str(result['_id'])
        return results
    
    @staticmethod
    def find_by_order_id(order_id):
        """通过订单ID查找结果"""
        logging.info(f"尝试通过订单ID查找结果: {order_id}")
        
        # 尝试各种方式查询订单
        try:
            # 尝试直接通过orderId字段查询
            logging.info(f"尝试直接通过orderId字段查询: {order_id}")
            result = results_collection.find_one({"orderId": order_id})
            if result:
                logging.info(f"通过orderId字段查询成功")
                result['_id'] = str(result['_id'])
                return result
            
            # 尝试将订单ID转换为ObjectId再查询
            logging.info(f"尝试通过ObjectId转换查询: {order_id}")
            try:
                obj_order_id = ObjectId(order_id)
                result = results_collection.find_one({"orderId": obj_order_id})
                if result:
                    logging.info(f"通过ObjectId orderId查询成功")
                    result['_id'] = str(result['_id'])
                    return result
            except Exception as e:
                logging.warning(f"订单ID无法转换为ObjectId: {str(e)}")
            
            # 尝试通过字符串形式查询
            if order_id.isdigit():
                logging.info(f"尝试通过数字字符串查询: {order_id}")
                result = results_collection.find_one({"orderId": str(order_id)})
                if result:
                    logging.info(f"通过数字字符串查询成功")
                    result['_id'] = str(result['_id'])
                    return result
            
            logging.warning(f"未找到与订单ID匹配的记录: {order_id}")
            return None
            
        except Exception as e:
            logging.error(f"查询订单ID时出错: {str(e)}")
            return None
    
    @staticmethod
    def update_bazi_data(result_id, bazi_data):
        """更新八字数据"""
        try:
            logger.info(f"更新八字数据: {result_id}")
            
            # 尝试直接使用字符串ID更新
            result = results_collection.update_one(
                {"_id": result_id},
                {"$set": {"baziData": bazi_data}}
            )
            
            # 如果没有匹配到记录，尝试将ID转换为ObjectId再更新
            if result.matched_count == 0:
                try:
                    logger.info(f"使用字符串ID未找到记录，尝试转换为ObjectId: {result_id}")
                    obj_id = ObjectId(result_id)
                    result = results_collection.update_one(
                        {"_id": obj_id},
                        {"$set": {"baziData": bazi_data}}
                    )
                except Exception as e:
                    logger.error(f"ObjectId转换失败: {str(e)}")
            
            if result.matched_count > 0:
                logger.info(f"成功更新八字数据: {result_id}")
                return BaziResultModel.find_by_id(result_id)
            else:
                logger.warning(f"未找到要更新的记录: {result_id}")
                return None
        except Exception as e:
            logger.error(f"更新八字数据失败: {str(e)}")
            return None
    
    @staticmethod
    def update_ai_analysis(result_id, analysis_data):
        """更新AI分析结果"""
        try:
            # 记录更新内容
            logger.info(f"更新AI分析结果: {result_id}")
            
            # 检查分析数据
            if not analysis_data:
                logger.warning(f"AI分析数据为空: {result_id}")
                analysis_data = {}
            
            # 确保所有必要字段都存在
            required_fields = [
                'overall', 'health', 'wealth', 'career', 'relationship', 'children',
                'personality', 'education', 'parents', 'social', 'future',
                'coreAnalysis', 'fiveElements', 'shenShaAnalysis', 'keyPoints'
            ]
            for field in required_fields:
                if field not in analysis_data or not analysis_data[field]:
                    logger.warning(f"aiAnalysis缺少必要字段: {field}，添加默认值")
                    analysis_data[field] = f"正在分析{field}..."
            
            # 尝试直接使用原始ID更新
            result = results_collection.find_one_and_update(
                {'_id': result_id},
                {'$set': {
                    'aiAnalysis': analysis_data,
                    'updateTime': datetime.now()
                }},
                return_document=ReturnDocument.AFTER
            )
            
            # 如果没找到，尝试添加RES前缀
            if not result and isinstance(result_id, str) and not result_id.startswith('RES'):
                res_id = f"RES{result_id}"
                logger.info(f"尝试使用RES前缀更新: {res_id}")
                result = results_collection.find_one_and_update(
                    {'_id': res_id},
                    {'$set': {
                        'aiAnalysis': analysis_data,
                        'updateTime': datetime.now()
                    }},
                    return_document=ReturnDocument.AFTER
                )
            
            if result:
                logger.info(f"成功更新AI分析结果: {result_id}")
                return True
            else:
                logger.warning(f"未找到要更新的记录: {result_id}")
                return False
                
        except Exception as e:
            logger.error(f"更新AI分析结果失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def update_single_area_analysis(result_id, area, analysis_content):
        """更新单个领域的分析结果，用于按需付费的追问功能
        
        Args:
            result_id: 结果ID
            area: 分析领域，如'relationship', 'career', 'health'等
            analysis_content: 该领域的详细分析内容
            
        Returns:
            更新后的结果对象
        """
        try:
            logger.info(f"更新单个领域分析: {result_id}, 领域: {area}")
            
            # 构建更新字段
            update_field = f"aiAnalysis.{area}"
            
            # 记录分析内容长度
            content_length = len(analysis_content) if analysis_content else 0
            logger.info(f"分析内容长度: {content_length} 字符")
            
            # 尝试直接使用字符串ID更新
            result = results_collection.find_one_and_update(
                {"_id": result_id},
                {"$set": {
                    update_field: analysis_content,
                    f"paidAreas.{area}": True,  # 标记该领域已付费分析
                    f"analysisTime.{area}": datetime.now()  # 记录分析时间
                }},
                return_document=ReturnDocument.AFTER
            )
            
            # 如果没有匹配到记录，尝试将ID转换为ObjectId再更新
            if not result:
                try:
                    logger.info(f"使用字符串ID未找到记录，尝试转换为ObjectId: {result_id}")
                    obj_id = ObjectId(result_id)
                    result = results_collection.find_one_and_update(
                        {"_id": obj_id},
                        {"$set": {
                            update_field: analysis_content,
                            f"paidAreas.{area}": True,  # 标记该领域已付费分析
                            f"analysisTime.{area}": datetime.now()  # 记录分析时间
                        }},
                        return_document=ReturnDocument.AFTER
                    )
                except Exception as e:
                    logger.error(f"ObjectId转换失败: {str(e)}")
            
            if result:
                logger.info(f"成功更新单个领域分析: {result_id}, 领域: {area}")
                result['_id'] = str(result['_id'])
                return result
            else:
                logger.warning(f"未找到要更新的结果: {result_id}")
                return None
                
        except Exception as e:
            logger.error(f"更新单个领域分析失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def update_analysis(result_id, bazi_chart, ai_analysis):
        """更新分析结果
        
        Args:
            result_id: 结果ID
            bazi_chart: 八字命盘数据
            ai_analysis: AI分析结果
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 记录更新内容
            logger.info(f"更新分析结果: {result_id}")
            
            # 获取现有记录
            existing_result = results_collection.find_one({"_id": result_id})
            if not existing_result:
                logger.warning(f"未找到现有记录，尝试添加RES前缀: {result_id}")
                if isinstance(result_id, str) and not result_id.startswith("RES"):
                    existing_result = results_collection.find_one({"_id": f"RES{result_id}"})
                    if existing_result:
                        result_id = f"RES{result_id}"
            
            # 准备八字命盘数据
            if bazi_chart:
                logger.info(f"更新八字命盘数据: {list(bazi_chart.keys())}")
                
                # 确保年月日时四柱都存在
                pillars = ['yearPillar', 'monthPillar', 'dayPillar', 'hourPillar']
                for pillar in pillars:
                    if pillar not in bazi_chart or not bazi_chart[pillar]:
                        logger.warning(f"baziChart缺少必要字段: {pillar}，添加默认值")
                        bazi_chart[pillar] = {'heavenlyStem': '?', 'earthlyBranch': '?'}
                
                # 确保五行分布存在
                if 'fiveElements' not in bazi_chart or not bazi_chart['fiveElements']:
                    logger.warning("baziChart缺少五行分布，添加默认值")
                    bazi_chart['fiveElements'] = {'metal': 0, 'wood': 0, 'water': 0, 'fire': 0, 'earth': 0}
                
                # 确保神煞数据存在
                if 'shenSha' not in bazi_chart:
                    logger.warning("baziChart缺少神煞数据，添加默认值")
                    bazi_chart['shenSha'] = {
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
                
                # 确保大运数据存在
                if 'daYun' not in bazi_chart:
                    logger.warning("baziChart缺少大运数据，添加默认值")
                    bazi_chart['daYun'] = {
                        'startAge': 1,
                        'startYear': datetime.now().year,
                        'isForward': True,
                        'daYunList': []
                    }
                
                # 确保流年数据存在
                if 'flowingYears' not in bazi_chart:
                    logger.warning("baziChart缺少流年数据，添加默认值")
                    bazi_chart['flowingYears'] = []
            
            # 准备AI分析数据
            if ai_analysis:
                logger.info(f"更新AI分析结果: {list(ai_analysis.keys())}")
                
                # 确保所有必要字段都存在
                required_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children']
                for field in required_fields:
                    if field not in ai_analysis or not ai_analysis[field]:
                        logger.warning(f"aiAnalysis缺少必要字段: {field}，添加默认值")
                        ai_analysis[field] = f"正在分析{field}..."
            
            # 准备更新数据
            update_data = {
                'analyzed': True,
                'updateTime': datetime.now()
            }
            
            if bazi_chart:
                update_data['baziChart'] = bazi_chart
            
            if ai_analysis:
                update_data['aiAnalysis'] = ai_analysis
            
            # 检查JSON序列化
            try:
                json_str = json.dumps(update_data, default=str)
                logger.debug(f"更新数据JSON序列化成功，长度: {len(json_str)}")
            except Exception as json_err:
                logger.error(f"更新数据JSON序列化失败: {str(json_err)}")
                # 尝试找出问题字段
                for key, value in update_data.items():
                    try:
                        json.dumps({key: value}, default=str)
                    except:
                        logger.error(f"问题字段: {key}, 类型: {type(value)}")
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                try:
                                    json.dumps({sub_key: sub_value}, default=str)
                                except:
                                    logger.error(f"问题子字段: {key}.{sub_key}, 类型: {type(sub_value)}")
                                    # 尝试修复问题字段
                                    update_data[key][sub_key] = str(sub_value)
            
            # 尝试更新记录
            result = results_collection.update_one(
                {'_id': result_id},
                {'$set': update_data}
            )
            
            if result.matched_count > 0:
                logger.info(f"成功更新分析结果: {result_id}")
                return True
            else:
                logger.warning(f"未找到要更新的分析结果: {result_id}")
                # 尝试创建新记录
                try:
                    logger.warning(f"未找到要更新的分析结果，尝试创建新记录: {result_id}")
                    new_data = {
                        '_id': result_id,
                        'baziChart': bazi_chart,
                        'aiAnalysis': ai_analysis,
                        'analyzed': True,
                        'createTime': datetime.now(),
                        'updateTime': datetime.now()
                    }
                    results_collection.insert_one(new_data)
                    logger.info(f"成功创建新的分析结果: {result_id}")
                    return True
                except Exception as create_err:
                    logger.error(f"创建新记录失败: {str(create_err)}")
                return False
        except Exception as e:
            logger.error(f"更新分析结果失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def update_pdf_url(result_id, pdf_url):
        """更新PDF URL"""
        try:
            result = results_collection.find_one_and_update(
                {"_id": result_id},
                {"$set": {"pdfUrl": pdf_url}},
                return_document=ReturnDocument.AFTER
            )
            
            if not result:
                # 尝试使用ObjectId
                try:
                    obj_id = ObjectId(result_id)
                    result = results_collection.find_one_and_update(
                        {"_id": obj_id},
                        {"$set": {"pdfUrl": pdf_url}},
                        return_document=ReturnDocument.AFTER
                    )
                except:
                    pass
            
            return result
        except Exception as e:
            logging.error(f"更新PDF URL失败: {str(e)}")
            return None
    
    @staticmethod
    def update_birth_info(result_id, birth_date, birth_time, gender):
        """更新出生信息
        
        Args:
            result_id: 结果ID
            birth_date: 出生日期
            birth_time: 出生时间
            gender: 性别
            
        Returns:
            dict: 更新后的结果
        """
        try:
            logging.info(f"更新出生信息: result_id={result_id}, birth_date={birth_date}, birth_time={birth_time}, gender={gender}")
            
            # 准备更新数据
            update_data = {}
            if birth_date:
                update_data["birthDate"] = birth_date
            if birth_time:
                update_data["birthTime"] = birth_time
            if gender:
                update_data["gender"] = gender
                
            # 如果没有需要更新的数据，直接返回
            if not update_data:
                logging.warning("没有需要更新的出生信息")
                return None
                
            # 更新数据
            result = results_collection.find_one_and_update(
                {"_id": result_id},
                {"$set": update_data},
                return_document=ReturnDocument.AFTER
            )
            
            if not result:
                # 尝试使用ObjectId
                try:
                    obj_id = ObjectId(result_id)
                    result = results_collection.find_one_and_update(
                        {"_id": obj_id},
                        {"$set": update_data},
                        return_document=ReturnDocument.AFTER
                    )
                except Exception as e:
                    logging.error(f"使用ObjectId更新出生信息失败: {str(e)}")
            
            if result:
                logging.info(f"出生信息更新成功: {result_id}")
                
                # 如果有baziChart字段，也更新其中的出生信息
                if 'baziChart' in result and result['baziChart']:
                    bazi_chart_update = {}
                    if birth_date:
                        bazi_chart_update["baziChart.birthDate"] = birth_date
                    if birth_time:
                        bazi_chart_update["baziChart.birthTime"] = birth_time
                    if gender:
                        bazi_chart_update["baziChart.gender"] = gender
                        
                    if bazi_chart_update:
                        logging.info(f"更新baziChart中的出生信息: {result_id}")
                        results_collection.update_one(
                            {"_id": result_id},
                            {"$set": bazi_chart_update}
                        )
            else:
                logging.warning(f"出生信息更新失败，未找到记录: {result_id}")
                
            return result
        except Exception as e:
            logging.error(f"更新出生信息失败: {str(e)}")
            logging.error(traceback.format_exc())
            return None
    
    @staticmethod
    def update_full_analysis(result_id, bazi_chart, ai_analysis):
        """完整更新分析结果
        
        Args:
            result_id: 结果ID
            bazi_chart: 八字命盘数据
            ai_analysis: AI分析结果
            
        Returns:
            dict: 更新后的结果记录
        """
        try:
            # 记录更新内容
            logger.info(f"完整更新分析结果: {result_id}")
            
            # 检查八字命盘数据
            if not bazi_chart:
                logger.warning(f"八字命盘数据为空: {result_id}")
                bazi_chart = {}
            
            # 检查AI分析结果
            if not ai_analysis:
                logger.warning(f"AI分析结果为空: {result_id}")
                ai_analysis = {}
            
            # 确保八字命盘数据包含必要字段
            pillars = ['yearPillar', 'monthPillar', 'dayPillar', 'hourPillar']
            for pillar in pillars:
                if pillar not in bazi_chart or not bazi_chart[pillar]:
                    logger.warning(f"baziChart缺少必要字段: {pillar}，添加默认值")
                    bazi_chart[pillar] = {'heavenlyStem': '?', 'earthlyBranch': '?'}
            
            # 确保五行分布存在
            if 'fiveElements' not in bazi_chart or not bazi_chart['fiveElements']:
                logger.warning("baziChart缺少五行分布，添加默认值")
                bazi_chart['fiveElements'] = {'metal': 0, 'wood': 0, 'water': 0, 'fire': 0, 'earth': 0}
            
            # 确保神煞数据存在
            if 'shenSha' not in bazi_chart or not bazi_chart['shenSha']:
                logger.warning("baziChart缺少神煞数据，添加默认值")
                bazi_chart['shenSha'] = {
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
                
            # 确保大运数据存在
            if 'daYun' not in bazi_chart or not bazi_chart['daYun']:
                logger.warning("baziChart缺少大运数据，添加默认值")
                bazi_chart['daYun'] = {
                    'startAge': 1,
                    'startYear': datetime.now().year,
                    'isForward': True,
                    'daYunList': []
                }
            
            # 确保流年数据存在
            if 'flowingYears' not in bazi_chart:
                logger.warning("baziChart缺少流年数据，添加默认值")
                bazi_chart['flowingYears'] = []
            
            # 确保AI分析结果包含必要字段
            required_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children']
            for field in required_fields:
                if field not in ai_analysis or not ai_analysis[field]:
                    logger.warning(f"aiAnalysis缺少必要字段: {field}，添加默认值")
                    ai_analysis[field] = f"正在分析{field}..."
            
            # 准备更新数据
            update_data = {
                'baziChart': bazi_chart,
                'aiAnalysis': ai_analysis,
                'analyzed': True,
                'updateTime': datetime.now()
            }
            
            # 检查JSON序列化
            try:
                json_str = json.dumps(update_data, default=str)
                logger.debug(f"更新数据JSON序列化成功，长度: {len(json_str)}")
            except Exception as json_err:
                logger.error(f"更新数据JSON序列化失败: {str(json_err)}")
                # 尝试找出问题字段并修复
                for key, value in update_data.items():
                    try:
                        json.dumps({key: value}, default=str)
                    except:
                        logger.error(f"问题字段: {key}, 类型: {type(value)}")
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                try:
                                    json.dumps({sub_key: sub_value}, default=str)
                                except:
                                    logger.error(f"问题子字段: {key}.{sub_key}, 类型: {type(sub_value)}")
                                    # 尝试修复问题字段
                                    update_data[key][sub_key] = str(sub_value)
            
            # 尝试直接使用原始ID更新
            result = results_collection.find_one_and_update(
                {'_id': result_id},
                {'$set': update_data},
                return_document=ReturnDocument.AFTER
            )
            
            # 如果没找到，尝试添加RES前缀
            if not result and isinstance(result_id, str) and not result_id.startswith('RES'):
                res_id = f"RES{result_id}"
                logger.info(f"尝试使用RES前缀更新: {res_id}")
                result = results_collection.find_one_and_update(
                    {'_id': res_id},
                    {'$set': update_data},
                    return_document=ReturnDocument.AFTER
                )
            
            if result:
                logger.info(f"成功完整更新分析结果: {result_id}")
                return result
            else:
                # 尝试创建新记录
                try:
                    logger.warning(f"未找到要更新的分析结果，尝试创建新记录: {result_id}")
                    new_data = {
                        '_id': result_id,
                        'baziChart': bazi_chart,
                        'aiAnalysis': ai_analysis,
                        'analyzed': True,
                        'createTime': datetime.now(),
                        'updateTime': datetime.now()
                    }
                    results_collection.insert_one(new_data)
                    logger.info(f"成功创建新的分析结果: {result_id}")
                    return new_data
                except Exception as create_err:
                    logger.error(f"创建新记录失败: {str(create_err)}")
                    return None
                    
        except Exception as e:
            logger.error(f"完整更新分析结果失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def update_followup(result_id, area, analysis):
        """更新追问分析结果"""
        try:
            logger.info(f"更新追问分析结果: {result_id}, 领域: {area}")
            
            # 记录原始area值，用于前端匹配
            original_area = area
            
            # 获取当前记录
            result = results_collection.find_one({"_id": result_id})
            if not result:
                logger.warning(f"无法找到结果记录: {result_id}")
                return False

            # 获取已有的followups数据，确保其为字典格式
            followups = result.get('followups', {})
            if not isinstance(followups, dict):
                # 如果不是字典，则创建一个新的字典
                followups = {}
                
            # 更新指定领域的分析结果
            followups[original_area] = analysis
                
            # 更新结果记录
            update_result = results_collection.update_one(
                {"_id": result_id},
                {"$set": {
                    "followups": followups,
                    "updateTime": datetime.now()
                }}
            )
            
            success = update_result.modified_count > 0
            logger.info(f"更新追问分析结果{'成功' if success else '失败'}")
            return success
        except Exception as e:
            logger.error(f"更新追问分析结果失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def create_result_with_id(result_id, user_id, order_id, birth_date, birth_time, gender, area, bazi_data=None):
        """创建新的结果记录，使用指定的结果ID"""
        try:
            logging.info(f"创建结果记录: result_id={result_id}, user_id={user_id}, order_id={order_id}")
            
            # 检查是否已存在相同ID的记录
            existing = results_collection.find_one({"_id": result_id})
            if existing:
                logging.warning(f"已存在相同ID的记录: {result_id}")
                # 更新现有记录
                update_result = results_collection.update_one(
                    {"_id": result_id},
                    {
                        "$set": {
                            "userId": user_id,
                            "orderId": order_id,
                            "birthDate": birth_date,
                            "birthTime": birth_time,
                            "gender": gender,
                            "area": area,
                            "updateTime": datetime.now()
                        }
                    }
                )
                if bazi_data:
                    update_result = results_collection.update_one(
                        {"_id": result_id},
                        {"$set": {"baziChart": bazi_data}}
                    )
                logging.info(f"更新现有记录成功: {result_id}")
                return True
            
            # 创建新记录
            result = {
                "_id": result_id,
                "userId": user_id,
                "orderId": order_id,
                "birthDate": birth_date,
                "birthTime": birth_time,
                "gender": gender,
                "area": area,
                "createTime": datetime.now(),
                "updateTime": datetime.now(),
                "aiAnalysis": {
                    'overall': '正在分析整体运势...',
                    'health': '正在分析健康运势...',
                    'wealth': '正在分析财运...',
                    'career': '正在分析事业运势...',
                    'relationship': '正在分析感情运势...',
                    'children': '正在分析子女运势...'
                }
            }
            
            # 如果提供了八字数据，添加到记录中
            if bazi_data:
                # 确保八字数据完整
                if not isinstance(bazi_data, dict):
                    bazi_data = {}
                
                # 确保年月日时四柱都存在
                pillars = ['yearPillar', 'monthPillar', 'dayPillar', 'hourPillar']
                for pillar in pillars:
                    if pillar not in bazi_data or not bazi_data[pillar]:
                        logging.warning(f"baziChart缺少必要字段: {pillar}，添加默认值")
                        bazi_data[pillar] = {'heavenlyStem': '?', 'earthlyBranch': '?'}
                
                # 确保五行分布存在
                if 'fiveElements' not in bazi_data or not bazi_data['fiveElements']:
                    logging.warning("baziChart缺少五行分布，添加默认值")
                    bazi_data['fiveElements'] = {'metal': 0, 'wood': 0, 'water': 0, 'fire': 0, 'earth': 0}
                
                # 确保神煞数据存在
                if 'shenSha' not in bazi_data:
                    logging.warning("baziChart缺少神煞数据，添加默认值")
                    bazi_data['shenSha'] = {
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
                
                # 确保大运数据存在
                if 'daYun' not in bazi_data:
                    logging.warning("baziChart缺少大运数据，添加默认值")
                    bazi_data['daYun'] = {
                        'startAge': 1,
                        'startYear': datetime.now().year,
                        'isForward': True,
                        'daYunList': []
                    }
                
                # 确保流年数据存在
                if 'flowingYears' not in bazi_data:
                    logging.warning("baziChart缺少流年数据，添加默认值")
                    bazi_data['flowingYears'] = []
                
                result["baziChart"] = bazi_data
            else:
                # 如果没有提供八字数据，创建空的数据结构
                result["baziChart"] = {
                    'yearPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                    'monthPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                    'dayPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                    'hourPillar': {'heavenlyStem': '?', 'earthlyBranch': '?'},
                    'fiveElements': {'metal': 0, 'wood': 0, 'water': 0, 'fire': 0, 'earth': 0},
                    'shenSha': {
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
                    },
                    'daYun': {
                        'startAge': 1,
                        'startYear': datetime.now().year,
                        'isForward': True,
                        'daYunList': []
                    },
                    'flowingYears': []
                }
            
            # 插入记录
            results_collection.insert_one(result)
            logging.info(f"创建结果记录成功: {result_id}")
            return True
            
        except Exception as e:
            logging.error(f"创建结果记录失败: {str(e)}")
            logging.error(traceback.format_exc())
            return False
    
    @staticmethod
    def update_field(result_id, field_name, field_value):
        """更新结果记录的特定字段"""
        try:
            logger.info(f"更新结果字段: {result_id}, 字段: {field_name}")
            
            # 更新结果记录
            update_result = results_collection.update_one(
                {"_id": result_id},
                {"$set": {
                    field_name: field_value,
                    "updateTime": datetime.now()
                }}
            )
            
            success = update_result.modified_count > 0
            logger.info(f"更新结果字段{'成功' if success else '失败'}")
            return success
        except Exception as e:
            logger.error(f"更新结果字段失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
    @staticmethod
    def get_result(result_id):
        """获取完整的结果记录"""
        try:
            logger.info(f"获取结果记录: {result_id}")
            return results_collection.find_one({"_id": result_id})
        except Exception as e:
            logger.error(f"获取结果记录失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    @staticmethod
    def get_followup_list(result_id):
        """获取已支付的追问列表"""
        try:
            logger.info(f"获取追问列表: {result_id}")
            
            # 从数据库获取结果记录
            result = results_collection.find_one({"_id": result_id})
            if not result:
                logger.warning(f"找不到结果记录: {result_id}")
                return []
                
            # 首先检查是否有新的followupPaid字段
            paid_areas = result.get('followupPaid', [])
            if paid_areas and isinstance(paid_areas, list):
                logger.info(f"从followupPaid字段找到已支付领域: {paid_areas}")
                # 格式化为前端需要的格式
                return [{"area": area} for area in paid_areas]
                
            # 如果没有找到followupPaid字段，尝试从followups中获取
            followups = result.get('followups', {})
            if not followups:
                logger.info(f"结果记录中没有追问数据")
                return []
                
            # 检查followups是否是字典类型
            if isinstance(followups, dict):
                # 如果是字典，将其转换为列表格式
                logger.info(f"从followups字典中提取领域: {list(followups.keys())}")
                return [{"area": area} for area in followups.keys()]
            elif isinstance(followups, list):
                # 如果已经是列表，直接返回
                logger.info(f"followups已经是列表格式")
                return followups
                
            # 如果无法处理，返回空列表
            logger.warning(f"无法处理的followups格式: {type(followups)}")
            return []
        except Exception as e:
            logger.error(f"获取追问列表失败: {str(e)}")
            logger.error(traceback.format_exc())
            return []
    
    @staticmethod
    def get_followup_analysis(result_id, area):
        """获取特定追问分析结果"""
        try:
            logger.info(f"查询追问分析: {result_id}, 领域: {area}")
            
            # 获取结果记录
            result = results_collection.find_one({"_id": result_id})
            if not result:
                logger.warning(f"找不到结果记录: {result_id}")
                return None
            
            # 获取追问分析结果
            followups = result.get('followups', {})
            if not isinstance(followups, dict):
                logger.warning(f"追问分析结果不是字典格式: {type(followups)}")
                return None
                
            # 尝试直接匹配
            if area in followups:
                logger.info(f"找到精确匹配的追问分析: {area}")
                return {"area": area, "analysis": followups[area]}
                
            # 尝试键名映射
            key_mappings = {
                "fiveYears": "future", 
                "future": "fiveYears"
            }
            
            if area in key_mappings and key_mappings[area] in followups:
                mapped_key = key_mappings[area]
                logger.info(f"找到键名映射的追问分析: {area} -> {mapped_key}")
                return {"area": area, "analysis": followups[mapped_key]}
                
            # 最后尝试大小写不敏感匹配
            for key in followups:
                if key.lower() == area.lower():
                    logger.info(f"找到大小写不敏感匹配的追问分析: {key}")
                    return {"area": area, "analysis": followups[key]}
                    
            logger.warning(f"未找到追问分析: {area}, 可用键: {list(followups.keys())}")
            return None
        except Exception as e:
            logger.error(f"获取追问分析失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def update_bazi_chart(result_id, bazi_chart):
        """只更新八字命盘数据，不更新AI分析
        
        Args:
            result_id: 结果ID
            bazi_chart: 八字命盘数据
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 记录更新内容
            logger.info(f"更新八字命盘数据: {result_id}")
            
            # 确保年月日时四柱都存在
            if bazi_chart:
                pillars = ['yearPillar', 'monthPillar', 'dayPillar', 'hourPillar']
                for pillar in pillars:
                    if pillar not in bazi_chart or not bazi_chart[pillar]:
                        logger.warning(f"baziChart缺少必要字段: {pillar}，添加默认值")
                        bazi_chart[pillar] = {'heavenlyStem': '?', 'earthlyBranch': '?'}
                
                # 确保五行分布存在
                if 'fiveElements' not in bazi_chart or not bazi_chart['fiveElements']:
                    logger.warning("baziChart缺少五行分布，添加默认值")
                    bazi_chart['fiveElements'] = {'metal': 0, 'wood': 0, 'water': 0, 'fire': 0, 'earth': 0}
                
                # 确保神煞数据存在
                if 'shenSha' not in bazi_chart:
                    logger.warning("baziChart缺少神煞数据，添加默认值")
                    bazi_chart['shenSha'] = {
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
                
                # 确保大运数据存在
                if 'daYun' not in bazi_chart:
                    logger.warning("baziChart缺少大运数据，添加默认值")
                    bazi_chart['daYun'] = {
                        'startAge': 1,
                        'startYear': datetime.now().year,
                        'isForward': True,
                        'daYunList': []
                    }
                
                # 确保流年数据存在
                if 'flowingYears' not in bazi_chart:
                    logger.warning("baziChart缺少流年数据，添加默认值")
                    bazi_chart['flowingYears'] = []
            
            # 尝试直接使用原始ID更新
            result = results_collection.find_one_and_update(
                {'_id': result_id},
                {'$set': {
                    'baziChart': bazi_chart,
                    'updateTime': datetime.now()
                }},
                return_document=ReturnDocument.AFTER
            )
            
            # 如果没找到，尝试添加RES前缀
            if not result and isinstance(result_id, str) and not result_id.startswith('RES'):
                res_id = f"RES{result_id}"
                logger.info(f"尝试使用RES前缀更新: {res_id}")
                result = results_collection.find_one_and_update(
                    {'_id': res_id},
                    {'$set': {
                        'baziChart': bazi_chart,
                        'updateTime': datetime.now()
                    }},
                    return_document=ReturnDocument.AFTER
                )
            
            if result:
                logger.info(f"成功更新八字命盘数据: {result_id}")
                return True
            else:
                logger.warning(f"未找到要更新的记录: {result_id}")
                return False
                
        except Exception as e:
            logger.error(f"更新八字命盘数据失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def update_pdf_content(result_id, pdf_content):
        """更新PDF内容（存储PDF二进制内容到数据库）
        
        Args:
            result_id: 结果ID
            pdf_content: PDF二进制内容
            
        Returns:
            bool: 是否更新成功
        """
        try:
            if not pdf_content:
                logging.error(f"PDF内容为空，无法更新: {result_id}")
                return False
            
            # 将二进制内容转换为Base64编码字符串存储
            encoded_content = base64.b64encode(pdf_content).decode('utf-8')
            
            # 更新数据库
            result = results_collection.find_one_and_update(
                {"_id": result_id},
                {"$set": {
                    "pdfContent": encoded_content,
                    "pdfSize": len(pdf_content),
                    "pdfUpdateTime": datetime.now()
                }},
                return_document=ReturnDocument.AFTER
            )
            
            if not result:
                # 尝试使用ObjectId
                try:
                    obj_id = ObjectId(result_id)
                    result = results_collection.find_one_and_update(
                        {"_id": obj_id},
                        {"$set": {
                            "pdfContent": encoded_content,
                            "pdfSize": len(pdf_content),
                            "pdfUpdateTime": datetime.now()
                        }},
                        return_document=ReturnDocument.AFTER
                    )
                except:
                    pass
                
            if result:
                logging.info(f"成功更新PDF内容: {result_id}, 大小: {len(pdf_content)} 字节")
                return True
            else:
                logging.error(f"更新PDF内容失败，未找到记录: {result_id}")
                return False
        except Exception as e:
            logging.error(f"更新PDF内容失败: {str(e)}")
            logging.error(traceback.format_exc())
            return False
        
    @staticmethod
    def get_pdf_content(result_id):
        """获取PDF内容
        
        Args:
            result_id: 结果ID
            
        Returns:
            bytes: PDF二进制内容
        """
        try:
            # 查询数据库
            result = results_collection.find_one({"_id": result_id})
            
            if not result:
                # 尝试使用ObjectId
                try:
                    obj_id = ObjectId(result_id)
                    result = results_collection.find_one({"_id": obj_id})
                except:
                    pass
                
            if not result:
                logging.error(f"获取PDF内容失败，未找到记录: {result_id}")
                return None
            
            # 检查是否有PDF内容
            if "pdfContent" not in result or not result["pdfContent"]:
                logging.warning(f"记录中没有PDF内容: {result_id}")
                return None
            
            # 解码Base64内容为二进制
            try:
                pdf_content = base64.b64decode(result["pdfContent"])
                logging.info(f"成功获取PDF内容: {result_id}, 大小: {len(pdf_content)} 字节")
                return pdf_content
            except Exception as e:
                logging.error(f"解码PDF内容失败: {str(e)}")
                return None
        except Exception as e:
            logging.error(f"获取PDF内容失败: {str(e)}")
            logging.error(traceback.format_exc())
            return None 