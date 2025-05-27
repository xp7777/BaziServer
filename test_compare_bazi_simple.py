#!/usr/bin/env python
# coding: utf-8

import sys
import os
import traceback

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    # 导入sxtwl库
    import sxtwl
    
    # 导入lunar-python库
    from lunar_python import Solar, Lunar
    
    print("已成功导入sxtwl和lunar-python库")
    
    # 测试日期: 2025年5月21日12点
    year = 2025
    month = 5
    day = 21
    hour = 12
    
    print(f"\n测试日期: {year}年{month}月{day}日{hour}时")
    print("-" * 50)
    
    # 使用sxtwl计算
    try:
        # 创建公历对象
        day_obj = sxtwl.fromSolar(year, month, day)
        
        # 获取八字
        gz_year = day_obj.getYearGZ()
        gz_month = day_obj.getMonthGZ()
        gz_day = day_obj.getDayGZ()
        
        # 计算时辰干支
        time_zhi = hour // 2
        time_gan = (gz_day.tg * 2 + time_zhi) % 10
        
        # 天干列表
        tian_gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        # 地支列表
        di_zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        # 天干
        year_tg = tian_gan[gz_year.tg]
        month_tg = tian_gan[gz_month.tg]
        day_tg = tian_gan[gz_day.tg]
        time_tg = tian_gan[time_gan]
        
        # 地支
        year_dz = di_zhi[gz_year.dz]
        month_dz = di_zhi[gz_month.dz]
        day_dz = di_zhi[gz_day.dz]
        time_dz = di_zhi[time_zhi]
        
        print(f"sxtwl计算结果:")
        print(f"  年柱: {year_tg}{year_dz}")
        print(f"  月柱: {month_tg}{month_dz}")
        print(f"  日柱: {day_tg}{day_dz}")
        print(f"  时柱: {time_tg}{time_dz}")
        
        sxtwl_bazi = f"{year_tg}{year_dz} {month_tg}{month_dz} {day_tg}{day_dz} {time_tg}{time_dz}"
    except Exception as e:
        print(f"sxtwl计算出错: {str(e)}")
        traceback.print_exc()
        sxtwl_bazi = "计算出错"
    
    # 使用lunar-python计算
    try:
        # 创建公历对象
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        
        # 转换为农历
        lunar = solar.getLunar()
        
        # 获取年、月、日、时的天干地支
        year_gan = lunar.getYearGan()
        year_zhi = lunar.getYearZhi()
        month_gan = lunar.getMonthGan()
        month_zhi = lunar.getMonthZhi()
        day_gan = lunar.getDayGan()
        day_zhi = lunar.getDayZhi()
        hour_gan = lunar.getTimeGan()
        hour_zhi = lunar.getTimeZhi()
        
        print(f"lunar-python计算结果:")
        print(f"  年柱: {year_gan}{year_zhi}")
        print(f"  月柱: {month_gan}{month_zhi}")
        print(f"  日柱: {day_gan}{day_zhi}")
        print(f"  时柱: {hour_gan}{hour_zhi}")
        
        lunar_bazi = f"{year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {hour_gan}{hour_zhi}"
    except Exception as e:
        print(f"lunar-python计算出错: {str(e)}")
        traceback.print_exc()
        lunar_bazi = "计算出错"
    
    # 比较结果
    print("\n比较结果:")
    print(f"sxtwl:        {sxtwl_bazi}")
    print(f"lunar-python: {lunar_bazi}")
    
    if sxtwl_bazi == lunar_bazi:
        print("结果一致")
    else:
        print("结果不一致")
        
        # 检查哪一柱不同
        if f"{year_tg}{year_dz}" != f"{year_gan}{year_zhi}":
            print(f"  年柱不同: sxtwl={year_tg}{year_dz}, lunar-python={year_gan}{year_zhi}")
        if f"{month_tg}{month_dz}" != f"{month_gan}{month_zhi}":
            print(f"  月柱不同: sxtwl={month_tg}{month_dz}, lunar-python={month_gan}{month_zhi}")
        if f"{day_tg}{day_dz}" != f"{day_gan}{day_zhi}":
            print(f"  日柱不同: sxtwl={day_tg}{day_dz}, lunar-python={day_gan}{day_zhi}")
        if f"{time_tg}{time_dz}" != f"{hour_gan}{hour_zhi}":
            print(f"  时柱不同: sxtwl={time_tg}{time_dz}, lunar-python={hour_gan}{hour_zhi}")
    
except ImportError as e:
    print("导入模块失败:", str(e))
except Exception as e:
    print("发生其他错误:", str(e))
    traceback.print_exc() 