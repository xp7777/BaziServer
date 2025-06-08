import requests
import json

def test_mock_payment():
    """测试模拟支付API"""
    url = 'http://localhost:5000/api/order/mock/pay/BZ1749370419469'
    data = {
        'birthDate': '2025-06-08',
        'birthTime': '辰时 (07:00-09:00)',
        'gender': 'male'
    }
    
    print("正在测试模拟支付API...")
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("模拟支付成功!")
                result_id = result.get('data', {}).get('resultId')
                if result_id:
                    print(f"获取到结果ID: {result_id}")
                    return result_id
                else:
                    print("响应中没有结果ID")
            else:
                print(f"API返回错误: {result.get('message')}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    return None

def test_result_api(result_id):
    """测试结果API"""
    url = f'http://localhost:5000/api/bazi/result/{result_id}'
    
    print(f"\n正在测试结果API，结果ID: {result_id}...")
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("获取结果成功!")
                print("结果数据摘要:")
                data = result.get('data', {})
                if 'aiAnalysis' in data:
                    print("- AI分析数据:")
                    for key, value in data['aiAnalysis'].items():
                        print(f"  - {key}: {value[:30]}..." if value and len(value) > 30 else f"  - {key}: {value}")
                if 'baziChart' in data:
                    print("- 八字命盘数据: 存在")
                return True
            else:
                print(f"API返回错误: {result.get('message')}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    return False

if __name__ == "__main__":
    # 测试模拟支付API
    result_id = test_mock_payment()
    
    # 如果没有获取到结果ID，使用已知的结果ID
    if not result_id:
        result_id = "RESBZ1749370419469"
        print(f"使用已知的结果ID: {result_id}")
    
    # 测试结果API
    test_result_api(result_id) 