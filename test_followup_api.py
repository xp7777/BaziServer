import requests
import json
import sys
import time

def test_followup_list_api(result_id):
    """测试followup/list接口"""
    print(f"\n===== 测试followup/list接口 =====")
    url = f"http://localhost:5000/api/bazi/followup/list/{result_id}"
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("响应内容:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return response.json()
        else:
            print(f"请求失败: {response.text}")
            return None
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None

def test_bazi_result_api(result_id):
    """测试bazi/result接口，检查八字计算结果是否包含神煞、大运和流年信息"""
    print(f"\n===== 测试bazi/result接口 =====")
    url = f"http://localhost:5000/api/bazi/result/{result_id}"
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # 检查八字命盘数据
            if 'data' in result and 'baziChart' in result['data']:
                bazi_chart = result['data']['baziChart']
                
                print("\n八字命盘数据检查:")
                # 检查神煞信息
                if 'shenSha' in bazi_chart:
                    print("✓ 包含神煞信息")
                    print(f"  神煞数据示例: {json.dumps(list(bazi_chart['shenSha'].items())[:3], ensure_ascii=False)}")
                else:
                    print("✗ 缺少神煞信息")
                
                # 检查大运信息
                if 'daYun' in bazi_chart:
                    print("✓ 包含大运信息")
                    print(f"  起运年龄: {bazi_chart['daYun'].get('startAge')}")
                    print(f"  起运年份: {bazi_chart['daYun'].get('startYear')}")
                    da_yun_list = bazi_chart['daYun'].get('daYun') or bazi_chart['daYun'].get('daYunList') or []
                    print(f"  大运数量: {len(da_yun_list)}")
                else:
                    print("✗ 缺少大运信息")
                
                # 检查流年信息
                if 'flowingYears' in bazi_chart:
                    print("✓ 包含流年信息")
                    print(f"  流年数量: {len(bazi_chart['flowingYears'])}")
                    if len(bazi_chart['flowingYears']) > 0:
                        print(f"  流年示例: {json.dumps(bazi_chart['flowingYears'][0], ensure_ascii=False)}")
                else:
                    print("✗ 缺少流年信息")
                
                return result
            else:
                print("响应中缺少八字命盘数据")
                return None
        else:
            print(f"请求失败: {response.text}")
            return None
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None

def create_test_followup_order(result_id, area="career"):
    """创建测试追问订单"""
    print(f"\n===== 创建测试追问订单 =====")
    url = "http://localhost:5000/api/order/create"
    data = {
        "userId": "test_user",
        "amount": 9.9,
        "orderType": "followup",
        "resultId": result_id,
        "area": area
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            order_data = response.json()
            print(f"订单创建成功: {json.dumps(order_data, indent=2, ensure_ascii=False)}")
            
            # 模拟支付订单
            order_id = order_data['data']['_id']
            pay_url = f"http://localhost:5000/api/order/mock/pay/{order_id}"
            pay_data = {"confirm": True}
            
            print(f"\n模拟支付订单: {order_id}")
            pay_response = requests.post(pay_url, json=pay_data)
            print(f"支付响应状态码: {pay_response.status_code}")
            
            if pay_response.status_code == 200:
                print(f"订单支付成功: {json.dumps(pay_response.json(), indent=2, ensure_ascii=False)}")
                return order_id
            else:
                print(f"订单支付失败: {pay_response.text}")
                return None
        else:
            print(f"创建订单失败: {response.text}")
            return None
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None

def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python test_followup_api.py <result_id> [create_order]")
        print("参数:")
        print("  result_id: 八字分析结果ID")
        print("  create_order: 可选，设置为'true'时创建测试追问订单")
        return
    
    result_id = sys.argv[1]
    create_order = len(sys.argv) > 2 and sys.argv[2].lower() == 'true'
    
    # 测试八字结果API
    test_bazi_result_api(result_id)
    
    # 如果指定创建订单，则创建测试追问订单
    if create_order:
        order_id = create_test_followup_order(result_id)
        if order_id:
            print("\n等待3秒后检查追问列表...")
            time.sleep(3)
    
    # 测试追问列表API
    test_followup_list_api(result_id)

if __name__ == "__main__":
    main() 