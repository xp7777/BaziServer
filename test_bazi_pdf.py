import os
import sys
import json
from utils.pdf_generator import generate_bazi_pdf

def test_bazi_pdf_generation():
    """测试八字PDF生成功能"""
    print("开始测试八字PDF生成...")
    
    # 创建测试数据
    analysis_id = "test_bazi_123"
    
    # 模拟格式化的八字数据
    formatted_data = {
        "bazi": "甲子 乙丑 丙寅 丁卯",
        "five_elements": {
            "metal": 2,
            "wood": 3,
            "water": 1,
            "fire": 2,
            "earth": 0
        },
        "shen_sha": {
            "吉神": ["天乙贵人", "文昌星"],
            "凶煞": ["孤辰", "寡宿"]
        },
        "da_yun": "癸卯运 - 癸卯 甲辰 乙巳 丙午 丁未 戊申 己酉 庚戌",
        "qi_yun": "于12岁8个月起运"
    }
    
    # 模拟分析结果
    analysis = {
        "overall": "总体分析：命主八字中木旺，为人性格温和，聪明有才华，但做事欠缺决断力。一生起伏不大，中年后运势渐佳。",
        "health": "健康分析：命主八字中木旺火旺，心脏、血液循环系统较好，但金水偏弱，呼吸系统和泌尿系统需注意保养。",
        "wealth": "财富分析：命主财运中等偏上，中年后财运渐佳，适合从事木火相关行业，如文教、设计、餐饮等行业有利于财运。",
        "career": "事业分析：命主八字中木旺生火，适合从事需要创意和表达能力的工作，如教育、文艺、设计等领域。",
        "relationship": "婚姻感情分析：命主桃花运不旺，但婚姻稳定，配偶贤良，婚后生活和睦。",
        "children": "子女分析：命主子女缘佳，子女聪明伶俐，对命主有助益。",
        "education": "学业分析：命主聪慧过人，学业有成，适合深造。"
    }
    
    # 生成PDF
    title = "2025年5月18日 女命 八字分析"
    pdf_path = generate_bazi_pdf(analysis_id, formatted_data, analysis, title)
    
    if pdf_path and os.path.exists(pdf_path):
        print(f"PDF生成成功: {pdf_path}")
        print("测试通过！")
        return True
    else:
        print("PDF生成失败")
        print("测试失败！")
        return False

if __name__ == "__main__":
    test_bazi_pdf_generation() 