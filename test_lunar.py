from lunar_python import Solar, Lunar, LunarUtil, SolarUtil
import json

def test_lunar_bazi():
    """测试lunar-python库的八字计算功能"""
    # 测试用例：1990年1月15日12点出生的男性
    solar = Solar.fromYmdHms(1990, 1, 15, 12, 0, 0)
    
    # 转换为农历
    lunar = solar.getLunar()
    
    # 获取八字
    bazi = lunar.getBaZi()
    
    # 提取年柱、月柱、日柱、时柱
    year_gan, year_zhi = bazi[0], bazi[1]
    month_gan, month_zhi = bazi[2], bazi[3]
    day_gan, day_zhi = bazi[4], bazi[5]
    hour_gan, hour_zhi = bazi[6], bazi[7]
    
    # 组合八字
    bazi_str = f"{year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {hour_gan}{hour_zhi}"
    
    # 获取纳音
    year_na_yin = lunar.getYearNaYin()
    month_na_yin = lunar.getMonthNaYin()
    day_na_yin = lunar.getDayNaYin()
    hour_na_yin = lunar.getTimeNaYin()
    
    # 获取生肖
    animal = lunar.getYearShengXiao()
    
    # 获取农历日期
    lunar_date = {
        "year": lunar.getYear(),
        "month": lunar.getMonth(),
        "day": lunar.getDay(),
        "isLeap": lunar.isLeap()
    }
    
    # 获取当前大运
    yun = lunar.getEightChar().getYun(1)  # 1表示男性
    da_yun = []
    
    for i in range(8):
        da_yun.append({
            "index": i + 1,
            "startAge": yun.getStartAge() + i * 10,
            "endAge": yun.getStartAge() + (i + 1) * 10 - 1,
            "ganZhi": yun.getDaYun()[i]
        })
    
    # 输出结果
    result = {
        "bazi": bazi_str,
        "yearPillar": f"{year_gan}{year_zhi} ({year_na_yin})",
        "monthPillar": f"{month_gan}{month_zhi} ({month_na_yin})",
        "dayPillar": f"{day_gan}{day_zhi} ({day_na_yin})",
        "hourPillar": f"{hour_gan}{hour_zhi} ({hour_na_yin})",
        "animal": animal,
        "lunarDate": lunar_date,
        "daYun": da_yun,
        "qiYunAge": yun.getStartAge()
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试流年
    current_year = 2025
    liu_nian = lunar.getEightChar().getYearXun(current_year)
    print(f"\n{current_year}年流年: {liu_nian}")

if __name__ == "__main__":
    test_lunar_bazi() 