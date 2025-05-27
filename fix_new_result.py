import json
import sys
from pymongo import MongoClient
import os
from utils.bazi_calculator import calculate_bazi

# 添加直接输出
print("修复脚本开始运行")
print(f"Python 版本: {sys.version}")

# 测试结果 ID
result_id = "RES1748318821500"  # 新的问题ID

# 测试日期
birth_date = "2025-05-27"
birth_time = "12:00"
gender = "male"

print(f"使用的测试 ID: {result_id}")
print(f"使用的测试日期: {birth_date} {birth_time}")

# 计算正确的八字
print("\n计算八字:")
bazi_chart = calculate_bazi(birth_date, birth_time, gender)
print(f"日期: {birth_date}, 时间: {birth_time}")
print(f"年柱: {bazi_chart['yearPillar']['heavenlyStem']}{bazi_chart['yearPillar']['earthlyBranch']}")
print(f"月柱: {bazi_chart['monthPillar']['heavenlyStem']}{bazi_chart['monthPillar']['earthlyBranch']}")
print(f"日柱: {bazi_chart['dayPillar']['heavenlyStem']}{bazi_chart['dayPillar']['earthlyBranch']}")
print(f"时柱: {bazi_chart['hourPillar']['heavenlyStem']}{bazi_chart['hourPillar']['earthlyBranch']}")
print(f"五行: {json.dumps(bazi_chart['fiveElements'], ensure_ascii=False)}")

# 准备更新的数据
update_data = {
    "userId": "test_user",
    "orderId": result_id.replace("RES", ""),
    "gender": gender,
    "birthDate": birth_date,
    "birthTime": birth_time,
    "focusAreas": ["health", "wealth", "career", "relationship"],
    "baziChart": bazi_chart,
    "aiAnalysis": {
        "health": "您的八字中火土较旺，木水偏弱。从健康角度看，您需要注意心脑血管系统和消化系统的保养。建议平时多喝水，保持规律作息，避免过度劳累和情绪波动。2025-2026年间需特别注意肝胆健康，可适当增加绿色蔬菜的摄入，定期体检。",
        "wealth": "您的财运在2025年有明显上升趋势，特别是在春夏季节。八字中金水相生，适合从事金融、贸易、水利相关行业。投资方面，稳健为主，可考虑分散投资组合。2027年有意外财运，但需谨慎对待，避免投机性强的项目。",
        "career": "您的事业宫位较为稳定，具有较强的组织能力和执行力。2025-2026年是事业发展的关键期，有升职或转行的机会。建议提升专业技能，扩展人脉关系。您适合在团队中担任协调或管理角色，发挥沟通才能。",
        "relationship": "您的八字中日柱为丙申，感情态度较为务实。2025年下半年至2026年上半年是感情发展的良好时期。已婚者需注意与伴侣的沟通，避免因工作忙碌而忽略家庭。单身者有机会通过社交活动或朋友介绍认识合适的对象。",
        "children": "您的子女宫位较为温和，与子女关系和谐。教育方面，建议采用引导式而非强制式的方法，尊重子女的兴趣发展。2026-2027年是子女发展的重要阶段，可能需要您更多的关注和支持。",
        "overall": "综合分析您的八字，2025-2027年是您人生的一个上升期，各方面都有良好发展。建议把握这段时间，在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。您的人生态度积极乐观，具有较强的适应能力和抗压能力，这将帮助您度过人生中的各种挑战。"
    },
    "analyzed": True
}

# 更新记录
print("\n尝试更新记录...")

# 获取MongoDB URI
mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bazi_system')
client = MongoClient(mongo_uri)
db = client.get_database()
results_collection = db.bazi_results

# 首先查找记录
existing = results_collection.find_one({"_id": result_id})

if existing:
    print(f"找到现有记录，进行更新: {result_id}")
    # 直接使用集合进行更新
    result = results_collection.update_one(
        {"_id": result_id},
        {"$set": update_data}
    )
    print(f"更新结果: matched={result.matched_count}, modified={result.modified_count}")
else:
    print(f"未找到现有记录，创建新记录: {result_id}")
    # 插入新记录
    update_data["_id"] = result_id  # 确保ID正确
    try:
        result = results_collection.insert_one(update_data)
        print(f"插入结果: inserted_id={result.inserted_id}")
    except Exception as e:
        print(f"插入失败: {e}")

# 验证更新
print("\n验证更新后的记录:")
updated_result = results_collection.find_one({"_id": result_id})
if updated_result:
    print(f"ID: {updated_result.get('_id')}")
    print(f"出生日期: {updated_result.get('birthDate')}")
    print(f"出生时间: {updated_result.get('birthTime')}")
    print(f"性别: {updated_result.get('gender')}")
    print(f"年柱: {updated_result.get('baziChart', {}).get('yearPillar', {}).get('heavenlyStem', '')}{updated_result.get('baziChart', {}).get('yearPillar', {}).get('earthlyBranch', '')}")
    print(f"月柱: {updated_result.get('baziChart', {}).get('monthPillar', {}).get('heavenlyStem', '')}{updated_result.get('baziChart', {}).get('monthPillar', {}).get('earthlyBranch', '')}")
    print(f"日柱: {updated_result.get('baziChart', {}).get('dayPillar', {}).get('heavenlyStem', '')}{updated_result.get('baziChart', {}).get('dayPillar', {}).get('earthlyBranch', '')}")
    print(f"时柱: {updated_result.get('baziChart', {}).get('hourPillar', {}).get('heavenlyStem', '')}{updated_result.get('baziChart', {}).get('hourPillar', {}).get('earthlyBranch', '')}")
else:
    print("未找到更新后的记录")

print("修复脚本运行完成") 