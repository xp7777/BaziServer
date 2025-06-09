import logging
import traceback
import json

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from utils.bazi_calculator import calculate_bazi
    
    # 测试2025-05-27日的八字
    print("测试2025年5月27日的八字:")
    result = calculate_bazi('2025-05-27', '12:00', 'male')
    
    # 打印完整的结果
    print("\n===== 完整结果(JSON) =====")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n===== 八字命盘信息 =====")
    print(f"年柱: {result['yearPillar']['heavenlyStem']}{result['yearPillar']['earthlyBranch']}")
    print(f"月柱: {result['monthPillar']['heavenlyStem']}{result['monthPillar']['earthlyBranch']}")
    print(f"日柱: {result['dayPillar']['heavenlyStem']}{result['dayPillar']['earthlyBranch']}")
    print(f"时柱: {result['hourPillar']['heavenlyStem']}{result['hourPillar']['earthlyBranch']}")
    
    print("\n===== 五行分布 =====")
    print(f"金: {result['fiveElements']['metal']}")
    print(f"木: {result['fiveElements']['wood']}")
    print(f"水: {result['fiveElements']['water']}")
    print(f"火: {result['fiveElements']['fire']}")
    print(f"土: {result['fiveElements']['earth']}")
    
    print("\n===== 流年信息 =====")
    for y in result['flowingYears']:
        print(f"{y['year']}年: {y['heavenlyStem']}{y['earthlyBranch']} ({y['element']})")

    def test_bazi():
        result = calculate_bazi('2000-01-01', '子时 (23:00-01:00)', 'male')
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if __name__ == '__main__':
        test_bazi()
except Exception as e:
    print(f"发生错误: {str(e)}")
    logging.error(f"错误详情: {str(e)}")
    traceback.print_exc() 