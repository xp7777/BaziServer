import sys
from datetime import datetime
from pymongo import MongoClient
import os

# 获取MongoDB URI
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()

# 获取订单集合
orders_collection = db.orders

def create_test_order(order_id):
    """创建测试订单"""
    print(f"创建测试订单，ID: {order_id}")
    
    # 检查订单是否已存在
    existing_order = orders_collection.find_one({"_id": order_id})
    if existing_order:
        print(f"订单已存在: {order_id}")
        return existing_order
    
    # 创建新订单
    order = {
        "_id": order_id,
        "userId": "testuser",
        "amount": 9.9,
        "status": "pending",
        "createTime": datetime.now()
    }
    
    # 插入订单
    try:
        orders_collection.insert_one(order)
        print(f"订单创建成功: {order_id}")
        print(f"订单金额: {order['amount']}")
        print(f"订单状态: {order['status']}")
        print(f"创建时间: {order['createTime']}")
        return order
    except Exception as e:
        print(f"创建订单失败: {str(e)}")
        return None

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python create_test_order.py <order_id>")
        print("示例: python create_test_order.py BZ1234567890")
        sys.exit(1)
    
    # 获取订单ID
    order_id = sys.argv[1]
    
    # 导入OrderModel类
    try:
        from models.order_model import OrderModel
        print("成功导入OrderModel")
        
        # 使用OrderModel直接插入订单
        order = {
            "_id": order_id,
            "userId": "testuser",
            "amount": 9.9,
            "status": "pending",
            "createTime": datetime.now()
        }
        OrderModel.insert(order)
        print(f"使用OrderModel创建订单成功: {order_id}")
        print(f"订单金额: {order['amount']}")
        print(f"订单状态: {order['status']}")
        print(f"创建时间: {order['createTime']}")
    except Exception as e:
        print(f"使用OrderModel创建订单失败: {str(e)}")
        print("尝试使用直接操作MongoDB的方式")
        create_test_order(order_id) 