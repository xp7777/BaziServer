import os
import json
import logging
import sys
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 获取MongoDB URI
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()
results_collection = db.bazi_results
orders_collection = db.orders

# 检查命令行参数
result_id = None
if len(sys.argv) > 1:
    result_id = sys.argv[1]
else:
    result_id = input("请输入要检查的结果ID: ")

logging.info(f'开始检查记录ID: {result_id}')

# 查找记录
result = None
try:
    # 尝试使用ObjectId
    if len(result_id) == 24 and all(c in '0123456789abcdef' for c in result_id):
        result = results_collection.find_one({"_id": ObjectId(result_id)})
        if result:
            logging.info("使用ObjectId查询成功")
except Exception as e:
    logging.warning(f"ObjectId查询错误: {str(e)}")

# 尝试使用字符串ID
if not result:
    try:
        result = results_collection.find_one({"_id": result_id})
        if result:
            logging.info("使用字符串ID查询成功")
    except Exception as e:
        logging.warning(f"字符串ID查询错误: {str(e)}")

if result:
    # 打印记录信息
    logging.info(f"找到记录: {result_id}")
    
    # 打印主要字段
    print("\n记录主要信息:")
    print(f"ID: {result['_id']}")
    print(f"用户ID: {result.get('userId', '未知')}")
    print(f"订单ID: {result.get('orderId', '未知')}")
    print(f"性别: {result.get('gender', '未知')}")
    
    # 检查日期和时间字段
    print("\n日期时间信息:")
    if 'birthDate' in result:
        print(f"出生日期 (birthDate): {result['birthDate']}")
    else:
        print("出生日期 (birthDate): 未设置")
    
    if 'birthTime' in result:
        print(f"出生时间 (birthTime): {result['birthTime']}")
    else:
        print("出生时间 (birthTime): 未设置")
    
    # 检查基本信息字段
    if 'basicInfo' in result:
        print("\n基本信息:")
        basic_info = result['basicInfo']
        print(f"阳历年: {basic_info.get('solarYear', '未知')}")
        print(f"阳历月: {basic_info.get('solarMonth', '未知')}")
        print(f"阳历日: {basic_info.get('solarDay', '未知')}")
        print(f"阳历时: {basic_info.get('solarHour', '未知')}")
    else:
        print("\n基本信息: 未设置")
    
    # 检查原始请求
    if 'originalRequest' in result:
        print("\n原始请求信息:")
        original_request = result['originalRequest']
        print(f"出生日期: {original_request.get('birthDate', '未知')}")
        print(f"出生时间: {original_request.get('birthTime', '未知')}")
        print(f"出生地点: {original_request.get('birthPlace', '未知')}")
    else:
        print("\n原始请求信息: 未设置")
    
    # 检查八字信息
    if 'baziChart' in result:
        print("\n八字信息:")
        bazi_chart = result['baziChart']
        if 'yearPillar' in bazi_chart:
            year_pillar = bazi_chart['yearPillar']
            print(f"年柱: {year_pillar.get('heavenlyStem', '')}{year_pillar.get('earthlyBranch', '')}")
            print(f"出生年份: {year_pillar.get('birthYear', '未知')}")
        
        if 'monthPillar' in bazi_chart:
            month_pillar = bazi_chart['monthPillar']
            print(f"月柱: {month_pillar.get('heavenlyStem', '')}{month_pillar.get('earthlyBranch', '')}")
        
        if 'dayPillar' in bazi_chart:
            day_pillar = bazi_chart['dayPillar']
            print(f"日柱: {day_pillar.get('heavenlyStem', '')}{day_pillar.get('earthlyBranch', '')}")
        
        if 'hourPillar' in bazi_chart:
            hour_pillar = bazi_chart['hourPillar']
            print(f"时柱: {hour_pillar.get('heavenlyStem', '')}{hour_pillar.get('earthlyBranch', '')}")
        
        if 'fiveElements' in bazi_chart:
            five_elements = bazi_chart['fiveElements']
            print(f"\n五行:")
            print(f"金: {five_elements.get('metal', 0)}")
            print(f"木: {five_elements.get('wood', 0)}")
            print(f"水: {five_elements.get('water', 0)}")
            print(f"火: {five_elements.get('fire', 0)}")
            print(f"土: {five_elements.get('earth', 0)}")
    else:
        print("\n八字信息: 未设置")
    
    # 检查分析状态
    print(f"\n分析状态: {'已分析' if result.get('analyzed', False) else '未分析'}")
    print(f"创建时间: {result.get('createTime', '未知')}")
    print(f"更新时间: {result.get('updateTime', '未知')}")
    
    # 查找关联的订单
    order_id = result.get('orderId')
    if order_id:
        try:
            order = orders_collection.find_one({"_id": order_id})
            if not order:
                # 尝试将订单ID转为ObjectId再查询
                try:
                    order = orders_collection.find_one({"_id": ObjectId(order_id)})
                except:
                    pass
            
            if order:
                print("\n关联订单信息:")
                print(f"订单ID: {order['_id']}")
                print(f"订单状态: {order.get('status', '未知')}")
                print(f"创建时间: {order.get('createTime', '未知')}")
                print(f"支付时间: {order.get('payTime', '未知')}")
            else:
                print(f"\n未找到关联订单: {order_id}")
        except Exception as e:
            print(f"查询订单时出错: {str(e)}")
    
else:
    logging.error(f"未找到记录: {result_id}")
    
    # 查找RES前缀相关记录
    if result_id.startswith("RES"):
        timestamp = result_id.replace("RES", "")
        logging.info(f"尝试查找相关订单，时间戳: {timestamp}")
        
        # 查找订单
        order = None
        try:
            order = orders_collection.find_one({"_id": timestamp})
            if not order:
                # 尝试通过orderId字段查询
                order = orders_collection.find_one({"orderId": timestamp})
        except Exception as e:
            logging.warning(f"查询相关订单出错: {str(e)}")
        
        if order:
            logging.info(f"找到相关订单: {order['_id']}")
            print(f"\n相关订单信息:")
            print(f"订单ID: {order['_id']}")
            print(f"用户ID: {order.get('userId', '未知')}")
            print(f"订单状态: {order.get('status', '未知')}")
            print(f"创建时间: {order.get('createTime', '未知')}")
            
            # 查找关联的结果记录
            related_result = results_collection.find_one({"orderId": str(order['_id'])})
            if related_result:
                logging.info(f"找到相关结果记录: {related_result['_id']}")
                print(f"\n相关结果记录: {related_result['_id']}")
                print(f"出生日期: {related_result.get('birthDate', '未知')}")
                print(f"出生时间: {related_result.get('birthTime', '未知')}")
        else:
            logging.info("未找到相关订单")

logging.info('检查记录完成') 