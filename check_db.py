from pymongo import MongoClient
import json

# 连接数据库
client = MongoClient('mongodb://localhost:27017/bazi_system')
db = client.get_database()

# 检查订单集合
orders = list(db.orders.find())
print(f"订单数量: {len(orders)}")
for i, order in enumerate(orders):
    order['_id'] = str(order['_id'])
    if 'createTime' in order:
        order['createTime'] = str(order['createTime'])
    if 'payTime' in order and order['payTime']:
        order['payTime'] = str(order['payTime'])
    print(f"订单 {i+1}: {json.dumps(order, ensure_ascii=False, indent=2)}")
    print("-" * 50)

# 检查结果集合
results = list(db.bazi_results.find())
print(f"\n结果数量: {len(results)}")
for i, result in enumerate(results):
    result['_id'] = str(result['_id'])
    if 'createTime' in result:
        result['createTime'] = str(result['createTime'])
    print(f"结果 {i+1}: ID={result['_id']}, 订单ID={result.get('orderId', '无')}")
    print("-" * 50)

# 创建测试订单
def create_test_order():
    order_id = "BZ1749368370769"
    
    # 检查订单是否已存在
    existing_order = db.orders.find_one({"_id": order_id})
    if existing_order:
        print(f"测试订单已存在: {order_id}")
        return
    
    # 创建新订单
    from datetime import datetime
    order = {
        "_id": order_id,
        "userId": "test_user",
        "amount": 9.9,
        "status": "pending",
        "createTime": datetime.now()
    }
    db.orders.insert_one(order)
    print(f"创建测试订单成功: {order_id}")
    
    # 创建对应的结果记录
    result_id = "RES" + order_id
    existing_result = db.bazi_results.find_one({"_id": result_id})
    if existing_result:
        print(f"测试结果记录已存在: {result_id}")
        return
    
    result = {
        "_id": result_id,
        "userId": "test_user",
        "orderId": order_id,
        "gender": "male",
        "birthTime": "辰时 (07:00-09:00)",
        "birthDate": "2025-06-08",
        "focusAreas": ["overall", "health", "wealth", "career", "relationship"],
        "createTime": datetime.now()
    }
    db.bazi_results.insert_one(result)
    print(f"创建测试结果记录成功: {result_id}")

# 创建测试数据
create_test_order() 