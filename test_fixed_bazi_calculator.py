import sys
import os
import traceback
import json

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    # 导入修改后的bazi_calculator模块
    from utils.bazi_calculator import calculate_bazi, format_bazi_analysis, get_bazi
    
    print("bazi_calculator模块已成功导入")
    
    def test_case(year, month, day, hour, gender, description=""):
        """测试单个用例"""
        print(f"\n=== 测试用例: {description or f'{year}年{month}月{day}日{hour}时 {gender}'} ===")
        
        try:
            # 直接使用get_bazi测试
            bazi_data = get_bazi(year, month, day, hour, gender)
            
            # 格式化输出
            formatted_data = format_bazi_analysis(bazi_data)
            
            print(f"八字: {formatted_data['bazi']}")
            print(f"神煞: {formatted_data['shenSha']}")
            print(f"{formatted_data['qiYun']}")
            print(f"大运: \n{formatted_data['daYun']}")
            
            # 输出五行分布
            print("五行分布:")
            five_elements = bazi_data["fiveElements"]
            for element, count in five_elements.items():
                print(f"  {element}: {count}")
                
            # 输出流年
            print("流年:")
            for year_data in bazi_data["flowingYears"][:3]:  # 只显示前3年
                print(f"  {year_data['year']}年: {year_data['heavenlyStem']}{year_data['earthlyBranch']} ({year_data['element']})")
                
            return True
        except Exception as e:
            print(f"测试失败: {str(e)}")
            traceback.print_exc()
            return False
            
    def test_by_birth_time(birth_time, gender, description=""):
        """使用birth_time字符串测试"""
        print(f"\n=== 测试用例: {description or f'{birth_time} {gender}'} ===")
        
        try:
            # 使用calculate_bazi函数测试
            bazi_data = calculate_bazi(gender, birth_time)
            
            # 格式化输出
            formatted_data = format_bazi_analysis(bazi_data)
            
            print(f"八字: {formatted_data['bazi']}")
            print(f"神煞: {formatted_data['shenSha']}")
            print(f"{formatted_data['qiYun']}")
            print(f"大运: \n{formatted_data['daYun']}")
            
            # 输出五行分布
            print("五行分布:")
            five_elements = bazi_data["fiveElements"]
            for element, count in five_elements.items():
                print(f"  {element}: {count}")
                
            # 输出流年
            print("流年:")
            for year_data in bazi_data["flowingYears"][:3]:  # 只显示前3年
                print(f"  {year_data['year']}年: {year_data['heavenlyStem']}{year_data['earthlyBranch']} ({year_data['element']})")
                
            return True
        except Exception as e:
            print(f"测试失败: {str(e)}")
            traceback.print_exc()
            return False
    
    # 测试用例
    test_cases = [
        (1990, 1, 15, 12, '男', "1990年男性"),
        (1986, 4, 23, 17, '女', "1986年女性"),
        (2025, 5, 21, 12, '男', "2025年未出生男婴")
    ]
    
    # 测试每个用例
    results = []
    for year, month, day, hour, gender, desc in test_cases:
        result = test_case(year, month, day, hour, gender, desc)
        results.append(result)
    
    # 测试使用birth_time字符串的方式
    birth_time_cases = [
        ("1990-01-15 12:00:00", "男", "1990年男性 (字符串时间)"),
        ("2025-05-21 12", "男", "2025年未出生男婴 (简化时间字符串)")
    ]
    
    for birth_time, gender, desc in birth_time_cases:
        result = test_by_birth_time(birth_time, gender, desc)
        results.append(result)
    
    # 输出总结果
    total = len(test_cases) + len(birth_time_cases)
    success = sum(1 for r in results if r)
    print(f"\n总结: {success}/{total} 测试通过")
    
except ImportError as e:
    print("导入bazi_calculator模块失败:", str(e))
except Exception as e:
    print("发生其他错误:", str(e))
    traceback.print_exc() 