#!/usr/bin/env python
# coding: utf-8

import sxtwl

# 天干列表
tian_gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支列表
di_zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def print_gz(gz):
    """打印干支"""
    print(f"{tian_gan[gz.tg]}{di_zhi[gz.dz]}")

# 测试日期: 2025年5月21日12点
year = 2025
month = 5
day = 21
hour = 12

print(f"测试日期: {year}年{month}月{day}日{hour}时")

# 创建公历对象
day_obj = sxtwl.fromSolar(year, month, day)

# 获取八字
gz_year = day_obj.getYearGZ()
gz_month = day_obj.getMonthGZ()
gz_day = day_obj.getDayGZ()

# 计算时辰干支
time_zhi = hour // 2
time_gan = (gz_day.tg * 2 + time_zhi) % 10

# 打印结果
print("年柱:", tian_gan[gz_year.tg] + di_zhi[gz_year.dz])
print("月柱:", tian_gan[gz_month.tg] + di_zhi[gz_month.dz])
print("日柱:", tian_gan[gz_day.tg] + di_zhi[gz_day.dz])
print("时柱:", tian_gan[time_gan] + di_zhi[time_zhi])

# 打印八字
print("八字:", tian_gan[gz_year.tg] + di_zhi[gz_year.dz], 
      tian_gan[gz_month.tg] + di_zhi[gz_month.dz], 
      tian_gan[gz_day.tg] + di_zhi[gz_day.dz], 
      tian_gan[time_gan] + di_zhi[time_zhi]) 