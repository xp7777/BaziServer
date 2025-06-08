import sys
import os
import json
import requests
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append('.')

# 尝试导入模型
try:
    from models.bazi_result_model import BaziResultModel
    from models.order_model import OrderModel
    print("成功导入模型")
except Exception as e:
    print(f"导入模型失败: {str(e)}")
    sys.exit(1)

def test_find_result_by_id(result_id):
    """测试通过ID查找结果"""
    print(f"\n=== 测试通过ID查找结果: {result_id} ===")
    result = BaziResultModel.find_by_id(result_id)
    if result:
        print(f"结果存在: {result['_id']}")
        print(f"包含命盘数据: {bool(result.get('baziChart'))}")
        print(f"包含AI分析: {bool(result.get('aiAnalysis'))}")
        return result
    else:
        print(f"结果不存在: {result_id}")
        return None

def test_api_result(result_id):
    """测试API获取结果"""
    print(f"\n=== 测试API获取结果: {result_id} ===")
    try:
        response = requests.get(f"http://localhost:5000/api/bazi/result/{result_id}")
        print(f"API响应状态码: {response.status_code}")
        data = response.json()
        print(f"API响应码: {data.get('code')}")
        print(f"API响应消息: {data.get('message')}")
        
        if data.get('code') == 200:
            result_data = data.get('data', {})
            print(f"包含命盘数据: {bool(result_data.get('baziChart'))}")
            print(f"包含AI分析: {bool(result_data.get('aiAnalysis'))}")
            return result_data
        else:
            print(f"API返回错误: {data.get('message')}")
            return None
    except Exception as e:
        print(f"API请求失败: {str(e)}")
        return None

def test_mock_payment(order_id, birth_date, birth_time, gender):
    """测试模拟支付"""
    print(f"\n=== 测试模拟支付: {order_id} ===")
    try:
        payload = {
            "birthDate": birth_date,
            "birthTime": birth_time,
            "gender": gender,
            "focusAreas": ["overall", "health", "wealth", "career"]
        }
        
        response = requests.post(
            f"http://localhost:5000/api/order/mock/pay/{order_id}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"API响应状态码: {response.status_code}")
        data = response.json()
        print(f"API响应码: {data.get('code')}")
        print(f"API响应消息: {data.get('message')}")
        
        if data.get('code') == 200:
            result_data = data.get('data', {})
            print(f"订单ID: {result_data.get('orderId')}")
            print(f"结果ID: {result_data.get('resultId')}")
            print(f"状态: {result_data.get('status')}")
            return result_data
        else:
            print(f"API返回错误: {data.get('message')}")
            return None
    except Exception as e:
        print(f"API请求失败: {str(e)}")
        return None

def create_test_result(result_id, birth_date, birth_time, gender):
    """创建测试结果"""
    print(f"\n=== 创建测试结果: {result_id} ===")
    
    # 检查结果是否已存在
    existing_result = BaziResultModel.find_by_id(result_id)
    if existing_result:
        print(f"结果已存在，无需创建: {result_id}")
        return existing_result
    
    # 创建新的结果记录
    order_id = result_id.replace('RES', '')
    
    # 检查订单是否存在
    existing_order = OrderModel.find_by_id(order_id)
    if not existing_order:
        print(f"订单不存在，创建新订单: {order_id}")
        # 创建订单
        order = {
            "_id": order_id,
            "userId": "anonymous",
            "amount": 9.9,
            "status": "paid",
            "createTime": datetime.now()
        }
        OrderModel.insert(order)
        print(f"订单创建成功: {order_id}")
    
    # 创建结果
    result = {
        "_id": result_id,
        "userId": "anonymous",
        "orderId": order_id,
        "gender": gender,
        "birthDate": birth_date,
        "birthTime": birth_time,
        "focusAreas": ["overall", "health", "wealth", "career"],
        "baziChart": None,
        "aiAnalysis": {
            "overall": "您的八字命盘显示您具有良好的发展潜力。",
            "health": "健康方面需注意肝胆系统。",
            "wealth": "财运较为稳定，适合稳健投资。",
            "career": "事业上有领导才能，适合管理岗位。",
            "relationship": "感情上需要更多耐心和沟通。",
            "children": "与子女关系和谐，教育方式需灵活。"
        },
        "createTime": datetime.now(),
        "analyzed": True
    }
    
    # 插入结果
    inserted = BaziResultModel.create(result)
    if inserted:
        print(f"结果创建成功: {inserted}")
        return BaziResultModel.find_by_id(result_id)
    else:
        print(f"结果创建失败")
        return None

def main():
    """主函数"""
    # 测试数据
    result_id = "RES1749370419469"
    order_id = "1749370419469"
    birth_date = "2025-06-08"
    birth_time = "辰时 (07:00-09:00)"
    gender = "male"
    
    # 测试通过ID查找结果
    db_result = test_find_result_by_id(result_id)
    
    # 如果结果不存在，创建测试结果
    if not db_result:
        print("\n结果不存在，创建测试数据")
        db_result = create_test_result(result_id, birth_date, birth_time, gender)
    
    # 测试API获取结果
    api_result = test_api_result(result_id)
    
    # 测试模拟支付
    payment_result = test_mock_payment(order_id, birth_date, birth_time, gender)
    
    # 测试带有RES前缀的订单ID
    res_payment_result = test_mock_payment(result_id, birth_date, birth_time, gender)
    
    # 打印测试结果摘要
    print("\n=== 测试结果摘要 ===")
    print(f"数据库查询结果: {'成功' if db_result else '失败'}")
    print(f"API获取结果: {'成功' if api_result else '失败'}")
    print(f"模拟支付(不带RES): {'成功' if payment_result else '失败'}")
    print(f"模拟支付(带RES): {'成功' if res_payment_result else '失败'}")

if __name__ == "__main__":
    main() 