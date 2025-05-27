import json
from utils.bazi_calculator import calculate_bazi, format_bazi_analysis

def test_bazi_calculator():
    """测试八字计算功能"""
    print("测试八字计算功能...")
    
    # 测试用例1：1990年1月15日12点出生的男性
    birth_time1 = "1990-01-15 12:00:00"
    gender1 = "男"
    
    print(f"\n测试用例1: {gender1}，出生时间: {birth_time1}")
    try:
        bazi_data1 = calculate_bazi(gender1, birth_time1)
        formatted1 = format_bazi_analysis(bazi_data1)
        
        print(f"八字: {formatted1['bazi']}")
        print(f"神煞: {formatted1['shenSha']}")
        print(f"{formatted1['qiYun']}")
        print(f"大运: \n{formatted1['daYun']}")
        
        # 输出五行分析
        print("五行分析:")
        for element, value in bazi_data1["fiveElements"].items():
            print(f"  {element}: {value}")
    except Exception as e:
        print(f"测试用例1失败: {str(e)}")
    
    # 测试用例2：1986年4月23日17点出生的女性
    birth_time2 = "1986-04-23 17:00:00"
    gender2 = "女"
    
    print(f"\n测试用例2: {gender2}，出生时间: {birth_time2}")
    try:
        bazi_data2 = calculate_bazi(gender2, birth_time2)
        formatted2 = format_bazi_analysis(bazi_data2)
        
        print(f"八字: {formatted2['bazi']}")
        print(f"神煞: {formatted2['shenSha']}")
        print(f"{formatted2['qiYun']}")
        print(f"大运: \n{formatted2['daYun']}")
        
        # 输出五行分析
        print("五行分析:")
        for element, value in bazi_data2["fiveElements"].items():
            print(f"  {element}: {value}")
    except Exception as e:
        print(f"测试用例2失败: {str(e)}")

if __name__ == "__main__":
    test_bazi_calculator() 