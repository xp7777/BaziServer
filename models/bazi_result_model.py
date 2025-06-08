from datetime import datetime
from pymongo import MongoClient, ReturnDocument
from bson import ObjectId
import os
import logging
import json
import traceback

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
            
            # 首先尝试直接使用字符串ID查询
            result = results_collection.find_one({"_id": result_id})
            
            # 如果找不到，尝试将字符串转换为ObjectId
            if not result:
                try:
                    logging.info(f"尝试使用ObjectId查询: {result_id}")
                    obj_id = ObjectId(result_id)
                    result = results_collection.find_one({"_id": obj_id})
                    
                    if result:
                        logging.info("使用ObjectId查询成功")
                        # 将_id转换为字符串，方便后续处理
                        result["_id"] = str(result["_id"])
                except Exception as e:
                    logging.error(f"ObjectId转换失败: {str(e)}")
            
            # 如果仍然找不到，且ID以RES开头，尝试去掉RES前缀后查询
            if not result and result_id.startswith('RES'):
                try:
                    # 去掉RES前缀
                    stripped_id = result_id[3:]
                    logging.info(f"尝试去掉RES前缀后查询: {stripped_id}")
                    
                    # 尝试使用去掉前缀的ID查询
                    result = results_collection.find_one({"_id": stripped_id})
                    
                    # 如果找不到，尝试将去掉前缀的ID转换为ObjectId
                    if not result:
                        try:
                            logging.info(f"尝试使用去掉前缀后的ObjectId查询: {stripped_id}")
                            obj_id = ObjectId(stripped_id)
                            result = results_collection.find_one({"_id": obj_id})
                            
                            if result:
                                logging.info("使用去掉前缀后的ObjectId查询成功")
                                # 将_id转换为字符串，方便后续处理
                                result["_id"] = str(result["_id"])
                        except Exception as e:
                            logging.error(f"去掉前缀后的ObjectId转换失败: {str(e)}")
                except Exception as e:
                    logging.error(f"去掉RES前缀后查询失败: {str(e)}")
            
            if result:
                logging.info(f"已找到结果ID: {result_id}")
                # 添加调试信息
                if 'baziChart' in result:
                    logging.info(f"结果包含baziChart: {bool(result['baziChart'])}")
                    if result['baziChart'] and 'yearPillar' in result['baziChart']:
                        logging.info(f"包含年柱: {result['baziChart']['yearPillar']}")
                else:
                    logging.warning(f"结果不包含baziChart")
                    
                if 'aiAnalysis' in result:
                    logging.info(f"结果包含aiAnalysis: {bool(result['aiAnalysis'])}")
                    if result['aiAnalysis'] and 'overall' in result['aiAnalysis']:
                        logging.info(f"分析整体内容: {result['aiAnalysis']['overall'][:50]}...")
                else:
                    logging.warning(f"结果不包含aiAnalysis")
            else:
                logging.warning(f"未找到结果ID: {result_id}")
                
            return result
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
    def update_ai_analysis(result_id, area, analysis):
        """更新特定领域的AI分析结果
        
        Args:
            result_id: 结果ID
            area: 分析领域，如'health', 'wealth'等
            analysis: 分析内容
            
        Returns:
            更新后的结果对象
        """
        try:
            logger.info(f"更新AI分析结果: {result_id}, 领域: {area}")
            
            # 构建更新字段
            update_field = f"aiAnalysis.{area}"
            
            # 尝试直接使用字符串ID更新
            result = results_collection.find_one_and_update(
                {"_id": result_id},
                {"$set": {update_field: analysis}},
                return_document=ReturnDocument.AFTER
            )
            
            # 如果没有匹配到记录，尝试将ID转换为ObjectId再更新
            if not result:
                try:
                    logger.info(f"使用字符串ID未找到记录，尝试转换为ObjectId: {result_id}")
                    obj_id = ObjectId(result_id)
                    result = results_collection.find_one_and_update(
                        {"_id": obj_id},
                        {"$set": {update_field: analysis}},
                        return_document=ReturnDocument.AFTER
                    )
                except Exception as e:
                    logger.error(f"ObjectId转换失败: {str(e)}")
            
            if result:
                logger.info(f"成功更新AI分析结果: {result_id}, 领域: {area}")
                result['_id'] = str(result['_id'])
                return result
            else:
                logger.warning(f"未找到要更新的结果: {result_id}")
                return None
                
        except Exception as e:
            logger.error(f"更新AI分析结果失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
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
            
            if bazi_chart:
                logger.info(f"更新八字命盘数据: {list(bazi_chart.keys())}")
                
                # 确保年月日时四柱都存在
                pillars = ['yearPillar', 'monthPillar', 'dayPillar', 'hourPillar']
                for pillar in pillars:
                    if pillar not in bazi_chart or not bazi_chart[pillar]:
                        logger.warning(f"baziChart缺少必要字段: {pillar}，添加默认值")
                        bazi_chart[pillar] = {'heavenlyStem': '?', 'earthlyBranch': '?'}
            
            if ai_analysis:
                logger.info(f"更新AI分析结果: {list(ai_analysis.keys())}")
                
                # 确保所有必要字段都存在
                required_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children']
                for field in required_fields:
                    if field not in ai_analysis or not ai_analysis[field]:
                        logger.warning(f"aiAnalysis缺少必要字段: {field}，添加默认值")
                        ai_analysis[field] = f"暂无{field}分析数据"
            
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
            
            # 尝试直接使用字符串ID更新
            result = results_collection.update_one(
                {'_id': result_id},
                {'$set': update_data}
            )
            
            # 如果没有匹配到记录，尝试将ID转换为ObjectId再更新
            if result.matched_count == 0:
                try:
                    logger.info(f"使用字符串ID未找到记录，尝试转换为ObjectId: {result_id}")
                    obj_id = ObjectId(result_id)
                    result = results_collection.update_one(
                        {'_id': obj_id},
                        {'$set': update_data}
                    )
                except Exception as e:
                    logger.error(f"ObjectId转换失败: {str(e)}")
            
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
            bool: 是否更新成功
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
            
            # 确保AI分析结果包含必要字段
            required_fields = ['overall', 'health', 'wealth', 'career', 'relationship', 'children', 'personality', 'education', 'parents', 'social', 'future']
            for field in required_fields:
                if field not in ai_analysis or not ai_analysis[field]:
                    logger.warning(f"aiAnalysis缺少必要字段: {field}，添加默认值")
                    ai_analysis[field] = f"暂无{field}分析数据"
            
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
            
            # 尝试直接使用字符串ID更新
            result = results_collection.update_one(
                {'_id': result_id},
                {'$set': update_data}
            )
            
            # 如果没有匹配到记录，尝试将ID转换为ObjectId再更新
            if result.matched_count == 0:
                try:
                    logger.info(f"使用字符串ID未找到记录，尝试转换为ObjectId: {result_id}")
                    obj_id = ObjectId(result_id)
                    result = results_collection.update_one(
                        {'_id': obj_id},
                        {'$set': update_data}
                    )
                except Exception as e:
                    logger.error(f"ObjectId转换失败: {str(e)}")
            
            if result.matched_count > 0:
                logger.info(f"成功完整更新分析结果: {result_id}")
                return True
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
                    return True
                except Exception as create_err:
                    logger.error(f"创建新记录失败: {str(create_err)}")
                    
                # 如果创建失败，返回原始错误
        except Exception as e:
            logger.error(f"完整更新分析结果失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def update_followup(result_id, area, analysis):
        """更新追问分析结果"""
        # 创建更新字段
        update_field = f"followups.{area}"
        
        # 更新结果记录
        results_collection.update_one(
            {"_id": result_id},
            {"$set": {
                update_field: analysis,
                "updateTime": datetime.now()
            }}
        )
        return True 