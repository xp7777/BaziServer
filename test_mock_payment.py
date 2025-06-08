import requests
import json
import sys

def test_mock_payment(order_id, birth_date, birth_time, gender):
    """测试模拟支付API"""
    print(f"测试模拟支付API，订单ID: {order_id}")
    
    # 构造API请求URL
    url = f"http://localhost:5000/api/order/mock/pay/{order_id}"
    print(f"发送请求: {url}")
    
    # 准备请求数据
    data = {
        "birthDate": birth_date,
        "birthTime": birth_time,
        "gender": gender,
        "focusAreas": ["overall", "health", "wealth", "career", "relationship"]
    }
    print(f"请求数据: {json.dumps(data)}")
    
    try:
        # 发送请求
        response = requests.post(url, json=data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 如果支付成功，尝试获取结果
        if response.status_code == 200:
            result_data = response.json()
            if result_data.get("code") == 200:
                result_id = result_data.get("data", {}).get("resultId")
                if result_id:
                    print(f"支付成功，结果ID: {result_id}")
                    
                    # 尝试获取结果
                    result_url = f"http://localhost:5000/api/bazi/result/{result_id}"
                    print(f"获取结果: {result_url}")
                    
                    result_response = requests.get(result_url)
                    print(f"结果响应状态码: {result_response.status_code}")
                    print(f"结果响应内容: {result_response.text[:500]}...")
                    
                    return True
        
        return False
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) < 5:
        print("用法: python test_mock_payment.py <order_id> <birth_date> <birth_time> <gender>")
        print("示例: python test_mock_payment.py BZ1234567890 \"2025-06-08\" \"辰时 (07:00-09:00)\" \"male\"")
        sys.exit(1)
    
    # 获取命令行参数
    order_id = sys.argv[1]
    birth_date = sys.argv[2]
    birth_time = sys.argv[3]
    gender = sys.argv[4]
    
    # 执行测试
    success = test_mock_payment(order_id, birth_date, birth_time, gender)
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1) 