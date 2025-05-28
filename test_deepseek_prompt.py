import os
import sys
import json
from datetime import datetime
from utils.bazi_calculator import calculate_bazi

# 测试数据
birth_date = "2025-05-27"
birth_time = "12:00"
gender = "male"

# 计算八字
bazi_chart = calculate_bazi(birth_date, birth_time, gender)

# 打印结果
print("八字计算结果:")
print(f"年柱: {bazi_chart['yearPillar']['heavenlyStem']}{bazi_chart['yearPillar']['earthlyBranch']}")
print(f"月柱: {bazi_chart['monthPillar']['heavenlyStem']}{bazi_chart['monthPillar']['earthlyBranch']}")
print(f"日柱: {bazi_chart['dayPillar']['heavenlyStem']}{bazi_chart['dayPillar']['earthlyBranch']}")
print(f"时柱: {bazi_chart['hourPillar']['heavenlyStem']}{bazi_chart['hourPillar']['earthlyBranch']}")

# 打印五行
print("\n五行分布:")
print(f"金: {bazi_chart['fiveElements']['metal']}")
print(f"木: {bazi_chart['fiveElements']['wood']}")
print(f"水: {bazi_chart['fiveElements']['water']}")
print(f"火: {bazi_chart['fiveElements']['fire']}")
print(f"土: {bazi_chart['fiveElements']['earth']}")

# 打印神煞信息
print("\n神煞信息:")
if 'shenSha' in bazi_chart:
    shen_sha = bazi_chart['shenSha']
    print(f"日冲: {shen_sha.get('dayChong', '无')}")
    print(f"值神: {shen_sha.get('zhiShen', '无')}")
    print(f"彭祖百忌: {shen_sha.get('pengZuGan', '无')}, {shen_sha.get('pengZuZhi', '无')}")
    print(f"喜神方位: {shen_sha.get('xiShen', '无')}")
    print(f"福神方位: {shen_sha.get('fuShen', '无')}")
    print(f"财神方位: {shen_sha.get('caiShen', '无')}")
    print(f"本命神煞: {', '.join(shen_sha.get('benMing', ['无']))}")
else:
    print("无神煞信息")

# 打印大运信息
print("\n大运信息:")
if 'daYun' in bazi_chart:
    da_yun = bazi_chart['daYun']
    print(f"起运年龄: {da_yun.get('startAge', '无')}岁")
    print(f"起运年份: {da_yun.get('startYear', '无')}年")
    print("大运列表:")
    for i in da_yun.get('daYunList', [])[:5]:
        print(f"  {i['index']}运({i['startYear']}-{i['endYear']}): {i['ganZhi']}")
else:
    print("无大运信息")

# 打印流年信息
print("\n流年信息(2025-2029):")
for y in bazi_chart['flowingYears']:
    print(f"{y['year']}年: {y['heavenlyStem']}{y['earthlyBranch']}")

# 生成DeepSeek提示模板
gender_text = "男性" if gender == "male" else "女性"

prompt = f"""
请你作为一位专业的命理师，为一位{gender_text}分析八字命盘。

【基本信息】
性别: {gender_text}
出生日期: {birth_date}
出生时间: {birth_time}
年龄: {datetime.now().year - int(birth_date.split('-')[0])}岁

【八字命盘信息】
年柱: {bazi_chart['yearPillar']['heavenlyStem']}{bazi_chart['yearPillar']['earthlyBranch']}
月柱: {bazi_chart['monthPillar']['heavenlyStem']}{bazi_chart['monthPillar']['earthlyBranch']}
日柱: {bazi_chart['dayPillar']['heavenlyStem']}{bazi_chart['dayPillar']['earthlyBranch']}
时柱: {bazi_chart['hourPillar']['heavenlyStem']}{bazi_chart['hourPillar']['earthlyBranch']}

【五行分布】
金: {bazi_chart['fiveElements']['metal']}
木: {bazi_chart['fiveElements']['wood']}
水: {bazi_chart['fiveElements']['water']}
火: {bazi_chart['fiveElements']['fire']}
土: {bazi_chart['fiveElements']['earth']}

【神煞信息】
日冲: {bazi_chart['shenSha'].get('dayChong', '无')}
值神: {bazi_chart['shenSha'].get('zhiShen', '无')}
彭祖百忌: {bazi_chart['shenSha'].get('pengZuGan', '无')}, {bazi_chart['shenSha'].get('pengZuZhi', '无')}
喜神方位: {bazi_chart['shenSha'].get('xiShen', '无')}
福神方位: {bazi_chart['shenSha'].get('fuShen', '无')}
财神方位: {bazi_chart['shenSha'].get('caiShen', '无')}
本命神煞: {', '.join(bazi_chart['shenSha'].get('benMing', ['无']))}

【大运信息】
起运年龄: {bazi_chart['daYun'].get('startAge', '无')}岁
起运年份: {bazi_chart['daYun'].get('startYear', '无')}年
大运列表: {', '.join([f"{i['index']}运({i['startYear']}-{i['endYear']}): {i['ganZhi']}" for i in bazi_chart['daYun'].get('daYunList', [])[:5]])}
    
【流年信息(2025-2029)】
{', '.join([f"{y['year']}年: {y['heavenlyStem']}{y['earthlyBranch']}" for y in bazi_chart['flowingYears']])}

请按照以下格式提供分析:

健康分析:
[详细的健康分析，包括体质特点、易发疾病、养生建议等]

财运分析:
[详细的财运分析，包括财运特点、适合行业、理财建议等]

事业发展:
[详细的事业分析，包括事业特点、职业方向、发展建议等]

婚姻感情:
[详细的婚姻感情分析，包括感情特点、相处方式、注意事项等]

子女缘分:
[详细的子女缘分分析，包括亲子关系、教育方式、注意事项等]

综合建议:
[综合分析和建议，未来5年的整体运势趋势]
"""

print("\nDeepSeek提示模板:")
print(prompt) 