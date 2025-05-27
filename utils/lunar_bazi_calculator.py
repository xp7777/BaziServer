import logging
import datetime
import traceback
from lunar_python import Solar, Lunar
from lunar_python.util import LunarUtil

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 天干
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def get_bazi(year, month, day, hour, gender='男'):
    """
    计算八字和神煞
    year, month, day: 阳历年月日
    hour: 小时（0-23）
    gender: '男' 或 '女'
    """
    try:
        print(f"输入参数: 年={year}, 月={month}, 日={day}, 时={hour}, 性别={gender}")
        
        # 创建公历对象
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        print(f"公历日期: {solar.toYmd()} {hour}时")
        
        # 转换为农历
        lunar = solar.getLunar()
        print(f"农历日期: {lunar.toString()}")
        
        # 获取八字对象
        eight_char = lunar.getEightChar()
        print(f"八字对象: {eight_char}")
        
        # 获取年、月、日、时的天干地支
        year_gan = lunar.getYearGan()
        year_zhi = lunar.getYearZhi()
        month_gan = lunar.getMonthGan()
        month_zhi = lunar.getMonthZhi()
        day_gan = lunar.getDayGan()
        day_zhi = lunar.getDayZhi()
        hour_gan = lunar.getTimeGan()
        hour_zhi = lunar.getTimeZhi()
        
        print(f"年柱: {year_gan}{year_zhi}")
        print(f"月柱: {month_gan}{month_zhi}")
        print(f"日柱: {day_gan}{day_zhi}")
        print(f"时柱: {hour_gan}{hour_zhi}")
        
        # 组合八字
        bazi = {
            "year": f"{year_gan}{year_zhi}",
            "month": f"{month_gan}{month_zhi}",
            "day": f"{day_gan}{day_zhi}",
            "time": f"{hour_gan}{hour_zhi}"
        }
        
        # 获取农历日期
        lunar_date = {
            "year": lunar.getYear(),
            "month": lunar.getMonth(),
            "day": lunar.getDay(),
            "isLeap": False  # lunar-python库没有提供直接的方法检查是否闰月
        }
        
        # 计算五行分布
        five_elements = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        
        # 添加天干的五行
        wu_xing_gan = {
            "甲": "木", "乙": "木",
            "丙": "火", "丁": "火",
            "戊": "土", "己": "土",
            "庚": "金", "辛": "金",
            "壬": "水", "癸": "水"
        }
        
        wu_xing_zhi = {
            "子": "水", "丑": "土",
            "寅": "木", "卯": "木",
            "辰": "土", "巳": "火",
            "午": "火", "未": "土",
            "申": "金", "酉": "金",
            "戌": "土", "亥": "水"
        }
        
        # 添加天干的五行
        for gan in [year_gan, month_gan, day_gan, hour_gan]:
            five_elements[wu_xing_gan.get(gan, "木")] += 1
        
        # 添加地支的五行
        for zhi in [year_zhi, month_zhi, day_zhi, hour_zhi]:
            five_elements[wu_xing_zhi.get(zhi, "木")] += 1
        
        print(f"五行分布: {five_elements}")
        
        # 获取神煞（简化示例）
        shen_sha = {}
        
        # 计算大运
        try:
            yun = eight_char.getYun(1 if gender == '男' else 0)
            print(f"大运方向: {'顺行' if yun.isForward() else '逆行'}")
            print(f"起运年龄: {yun.getStartAge()}")
            print(f"起运日期: {yun.getStartSolar().toYmd()}")
            
            da_yun_list = yun.getDaYun()
            print(f"大运数量: {len(da_yun_list)}")
            
            # 格式化大运信息
            da_yun = {
                "qi_yun": {
                    "days": 0,  # lunar-python不提供具体天数
                    "years": yun.getStartAge(),
                    "date": yun.getStartSolar().toYmd()
                },
                "da_yun_list": []
            }
            
            # 添加大运列表
            for i, dy in enumerate(da_yun_list):
                if i >= 8:  # 只取前8个大运
                    break
                    
                # 获取大运干支
                try:
                    gan_zhi = dy.getGanZhi()
                    gan = gan_zhi[0]
                    zhi = gan_zhi[1]
                    print(f"第{i+1}步大运: {gan}{zhi}")
                except Exception as e:
                    print(f"获取第{i+1}步大运干支出错: {str(e)}")
                    # 如果无法直接获取，则根据索引计算
                    if yun.isForward():
                        gan_idx = (HEAVENLY_STEMS.index(month_gan) + i + 1) % 10
                        zhi_idx = (EARTHLY_BRANCHES.index(month_zhi) + i + 1) % 12
                    else:
                        gan_idx = (HEAVENLY_STEMS.index(month_gan) - i - 1) % 10
                        zhi_idx = (EARTHLY_BRANCHES.index(month_zhi) - i - 1) % 12
                        
                    gan = HEAVENLY_STEMS[gan_idx]
                    zhi = EARTHLY_BRANCHES[zhi_idx]
                    print(f"计算得到第{i+1}步大运: {gan}{zhi}")
                
                # 计算年龄范围
                start_age = yun.getStartAge() + i * 10
                end_age = start_age + 9
                
                # 计算年份范围
                start_year = solar.getYear() + start_age
                end_year = start_year + 9
                
                da_yun["da_yun_list"].append({
                    "da_yun": f"{gan}{zhi}",
                    "shi_shen": "比肩",  # 简化，实际应该计算十神
                    "chang_sheng": "长生",  # 简化，实际应该计算长生十二宫
                    "start_age": start_age,
                    "end_age": end_age,
                    "start_year": start_year,
                    "end_year": end_year
                })
        except Exception as e:
            print(f"计算大运出错: {str(e)}")
            traceback.print_exc()
            # 创建一个空的大运对象
            da_yun = {
                "qi_yun": {
                    "days": 0,
                    "years": 0,
                    "date": "未知"
                },
                "da_yun_list": []
            }
        
        result = {
            "bazi": bazi,
            "shen_sha": shen_sha,
            "da_yun": da_yun,
            "lunar_date": lunar_date
        }
        
        print("八字计算完成")
        return result
        
    except Exception as e:
        logger.error(f"计算八字出错: {str(e)}")
        traceback.print_exc()
        raise

def format_bazi_analysis(bazi_data):
    """
    格式化八字分析数据，生成DeepSeek API需要的提示内容
    """
    try:
        bazi = bazi_data["bazi"]
        shen_sha = bazi_data["shen_sha"]
        da_yun = bazi_data["da_yun"]
        
        # 格式化八字
        bazi_str = f"{bazi['year']}，{bazi['month']}，{bazi['day']}，{bazi['time']}"
        
        # 格式化神煞
        shen_sha_str = ""
        for position, sha_list in shen_sha.items():
            if sha_list:
                shen_sha_str += f"[{position}]  {' '.join(sha_list)}    \n"
        
        # 格式化大运
        qi_yun_info = da_yun["qi_yun"]
        qi_yun_str = f"起运：我于出生后{int(qi_yun_info['years'])}年开始起运，在公历{qi_yun_info['date']}交运"
        
        da_yun_table = "旺衰\t大运\t十神\t年龄\t开始时间\t结束时间\n"
        for yun in da_yun["da_yun_list"]:
            da_yun_table += f"{yun['chang_sheng']}\t{yun['da_yun']}\t{yun['shi_shen']}\t{yun['start_age']}-{yun['end_age']}\t{yun['start_year']}\t{yun['end_year']}\n"
        
        return {
            "bazi": bazi_str,
            "shen_sha": shen_sha_str,
            "qi_yun": qi_yun_str,
            "da_yun": da_yun_table
        }
    except Exception as e:
        logger.error(f"格式化八字分析出错: {str(e)}")
        traceback.print_exc()
        raise

# 使用示例
if __name__ == "__main__":
    try:
        # 测试用例：1986年4月23日17点出生的女性
        bazi_data = get_bazi(1986, 4, 23, 17, '女')
        formatted = format_bazi_analysis(bazi_data)
        
        print(f"八字：{formatted['bazi']}")
        print(f"神煞：\n{formatted['shen_sha']}")
        print(f"{formatted['qi_yun']}")
        print(f"大运：\n{formatted['da_yun']}")
    except Exception as e:
        print(f"测试出错: {str(e)}")
        traceback.print_exc() 