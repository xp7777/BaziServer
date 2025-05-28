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
    def create_result(user_id, order_id, gender, birth_time, focus_areas):
        """创建新的八字分析结果"""
        result = {
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
            # 尝试使用ObjectId
            results_collection.update_one(
            {"_id": ObjectId(result_id)},
            {"$set": {"baziData": bazi_data}}
        )
        except:
            # 尝试使用字符串ID
            results_collection.update_one(
                {"_id": result_id},
                {"$set": {"baziData": bazi_data}}
            )
        return BaziResultModel.find_by_id(result_id)
    
    @staticmethod
    def update_ai_analysis(result_id, area, analysis):
        """更新AI分析结果"""
        try:
            # 尝试使用ObjectId
            results_collection.update_one(
            {"_id": ObjectId(result_id)},
            {"$set": {f"aiAnalysis.{area}": analysis}}
        )
        except:
            # 尝试使用字符串ID
            results_collection.update_one(
                {"_id": result_id},
                {"$set": {f"aiAnalysis.{area}": analysis}}
            )
        return BaziResultModel.find_by_id(result_id)
    
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
            
            # 更新数据
            result = results_collection.update_one(
                {'_id': result_id},
                {'$set': update_data}
            )
            
            if result.matched_count > 0:
                logger.info(f"成功更新分析结果: {result_id}")
                return True
            else:
                logger.warning(f"未找到要更新的分析结果: {result_id}")
                return False
        except Exception as e:
            logger.error(f"更新分析结果失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def update_pdf_url(result_id, pdf_url):
        """更新PDF URL
        
        Args:
            result_id: 结果ID
            pdf_url: PDF文件URL
            
        Returns:
            bool: 是否更新成功
        """
        try:
            logger.info(f"更新PDF URL: {result_id} -> {pdf_url}")
            
            # 更新数据
            result = results_collection.update_one(
                {'_id': result_id},
                {'$set': {'pdfUrl': pdf_url, 'pdfGenerated': True, 'pdfGenerateTime': datetime.now()}}
            )
            
            if result.matched_count > 0:
                logger.info(f"成功更新PDF URL: {result_id}")
                return True
            else:
                logger.warning(f"未找到要更新的分析结果: {result_id}")
                return False
        except Exception as e:
            logger.error(f"更新PDF URL失败: {str(e)}")
            return False
    
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
            
            # 更新数据
            result = results_collection.update_one(
                {'_id': result_id},
                {'$set': update_data}
            )
            
            if result.matched_count > 0:
                logger.info(f"成功完整更新分析结果: {result_id}")
                return True
            else:
                # 尝试创建新记录
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
        except Exception as e:
            logger.error(f"完整更新分析结果失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False 