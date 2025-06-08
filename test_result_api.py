import requests
import json

def test_result_api(result_id):
    """测试结果API"""
    url = f"http://localhost:5000/api/bazi/result/{result_id}"
    
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("请求成功!")
            print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求出错: {str(e)}")

# 测试结果ID
print("测试1: 使用RESBZ1749368370769")
test_result_api("RESBZ1749368370769")

print("\n" + "-" * 50 + "\n")

# 测试不存在的结果ID
print("测试2: 使用不存在的结果ID")
test_result_api("RES1749368371805") 