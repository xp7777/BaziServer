import sys
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入八字计算模块
from utils.bazi_calculator import calculate_bazi

def test_dates():
    """测试不同日期的八字计算"""
    test_cases = [
        {"date": "2022-06-21", "time": "午时 (11:00-13:00)", "gender": "male", "name": "2022年夏至日"},
        {"date": "2023-06-06", "time": "辰时 (07:00-09:00)", "gender": "male", "name": "2023年6月6日"},
        {"date": "2025-05-27", "time": "12:00", "gender": "male", "name": "2025年5月27日"},
        {"date": "2025-01-01", "time": "子时 (23:00-01:00)", "gender": "female", "name": "2025年元旦"},
        {"date": "2025-02-01", "time": "14:00", "gender": "female", "name": "2025年2月1日"},
        {"date": "2024-02-10", "time": "寅时 (03:00-05:00)", "gender": "male", "name": "2024年农历正月初一(龙年)"},
        {"date": "2025-01-29", "time": "寅时 (03:00-05:00)", "gender": "female", "name": "2025年农历正月初一(蛇年)"},
    ]
    
    for case in test_cases:
        logging.info(f"=========== 测试案例: {case['name']} ===========")
        result = calculate_bazi(case['date'], case['time'], case['gender'])
        
        # 打印四柱
        year_pillar = f"{result['yearPillar']['heavenlyStem']}{result['yearPillar']['earthlyBranch']}"
        month_pillar = f"{result['monthPillar']['heavenlyStem']}{result['monthPillar']['earthlyBranch']}"
        day_pillar = f"{result['dayPillar']['heavenlyStem']}{result['dayPillar']['earthlyBranch']}"
        hour_pillar = f"{result['hourPillar']['heavenlyStem']}{result['hourPillar']['earthlyBranch']}"
        
        logging.info(f"四柱: {year_pillar} {month_pillar} {day_pillar} {hour_pillar}")
        logging.info(f"五行: 金={result['fiveElements']['metal']}, 木={result['fiveElements']['wood']}, 水={result['fiveElements']['water']}, 火={result['fiveElements']['fire']}, 土={result['fiveElements']['earth']}")
        
        # 打印未来五年流年
        logging.info("未来五年流年:")
        for year_data in result['flowingYears']:
            logging.info(f"{year_data['year']}年: {year_data['heavenlyStem']}{year_data['earthlyBranch']} ({year_data['element']})")
        
        logging.info("=" * 50)

if __name__ == "__main__":
    logging.info("开始测试八字计算...")
    test_dates()
    logging.info("测试完成!") 