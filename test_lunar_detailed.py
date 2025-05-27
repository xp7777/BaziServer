import sys
import os
from datetime import datetime

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

try:
    from lunar_python.Solar import Solar
    from lunar_python.Lunar import Lunar
    from lunar_python import LunarUtil
    
    def test_basic_conversion():
        """测试基本的公历转农历和八字"""
        print("\n=== 测试基本的公历转农历和八字 ===")
        
        # 测试用例：1990年1月15日12点
        solar = Solar.fromYmdHms(1990, 1, 15, 12, 0, 0)
        lunar = solar.getLunar()
        
        print(f"公历: {solar.getYear()}年{solar.getMonth()}月{solar.getDay()}日 {solar.getHour()}时")
        print(f"农历: {lunar.toString()}")
        
        # 获取八字
        bazi = lunar.getBaZi()
        print(f"八字数组内容: {bazi}")
        print(f"八字: {bazi[0]}{bazi[1]} {bazi[2]}{bazi[3]} {bazi[4]}{bazi[5]} {bazi[6]}{bazi[7]}")
        
        # 验证数组长度，防止索引越界
        print(f"八字数组长度: {len(bazi)}")
        
    def test_get_methods():
        """测试各种获取方法"""
        print("\n=== 测试各种获取方法 ===")
        
        solar = Solar.fromYmdHms(1990, 1, 15, 12, 0, 0)
        lunar = solar.getLunar()
        
        # 测试各种获取方法
        print(f"年柱: {lunar.getYearInGanZhi()}")
        print(f"月柱: {lunar.getMonthInGanZhi()}")
        print(f"日柱: {lunar.getDayInGanZhi()}")
        print(f"时柱: {lunar.getTimeInGanZhi()}")
        
        # 获取年、月、日、时的天干地支
        print(f"年干: {lunar.getYearGan()}")
        print(f"年支: {lunar.getYearZhi()}")
        print(f"月干: {lunar.getMonthGan()}")
        print(f"月支: {lunar.getMonthZhi()}")
        print(f"日干: {lunar.getDayGan()}")
        print(f"日支: {lunar.getDayZhi()}")
        print(f"时干: {lunar.getTimeGan()}")
        print(f"时支: {lunar.getTimeZhi()}")
    
    def test_eight_char():
        """测试八字类"""
        print("\n=== 测试八字类 ===")
        
        solar = Solar.fromYmdHms(1990, 1, 15, 12, 0, 0)
        lunar = solar.getLunar()
        
        # 获取八字对象
        eight_char = lunar.getEightChar()
        print(f"八字对象: {eight_char}")
        
        # 获取大运
        yun_male = eight_char.getYun(1)  # 1表示男性
        print(f"男性大运起始年龄: {yun_male.getStartAge()}")
        print(f"男性大运方向: {yun_male.isForward()}")
        
        da_yun_male = yun_male.getDaYun()
        print(f"男性大运数组长度: {len(da_yun_male)}")
        for i, yun in enumerate(da_yun_male):
            if i < 8:  # 只显示前8个大运
                print(f"第{i+1}步大运: {yun}")
        
        # 女性大运
        yun_female = eight_char.getYun(0)  # 0表示女性
        print(f"女性大运起始年龄: {yun_female.getStartAge()}")
        print(f"女性大运方向: {yun_female.isForward()}")
        
        da_yun_female = yun_female.getDaYun()
        print(f"女性大运数组长度: {len(da_yun_female)}")
        for i, yun in enumerate(da_yun_female):
            if i < 8:  # 只显示前8个大运
                print(f"第{i+1}步大运: {yun}")
    
    def test_five_elements():
        """测试五行"""
        print("\n=== 测试五行 ===")
        
        solar = Solar.fromYmdHms(1990, 1, 15, 12, 0, 0)
        lunar = solar.getLunar()
        bazi = lunar.getBaZi()
        
        # 查看天干地支对应的五行
        wu_xing = {}
        for i in range(0, 8, 2):
            tian_gan = bazi[i]
            di_zhi = bazi[i+1]
            
            # 使用LunarUtil获取五行
            tian_gan_wuxing = LunarUtil.WU_XING_GAN.get(tian_gan)
            di_zhi_wuxing = LunarUtil.WU_XING_ZHI.get(di_zhi)
            
            wu_xing[tian_gan] = tian_gan_wuxing
            wu_xing[di_zhi] = di_zhi_wuxing
            
            print(f"{tian_gan}的五行: {tian_gan_wuxing}")
            print(f"{di_zhi}的五行: {di_zhi_wuxing}")
        
        # 统计五行分布
        five_elements = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        for element in wu_xing.values():
            five_elements[element] += 1
            
        print("五行分布:")
        for element, count in five_elements.items():
            print(f"{element}: {count}")
    
    def test_edge_cases():
        """测试边界情况"""
        print("\n=== 测试边界情况 ===")
        
        # 测试未来日期 (2025年5月21日)
        future_solar = Solar.fromYmdHms(2025, 5, 21, 12, 0, 0)
        future_lunar = future_solar.getLunar()
        
        print(f"未来公历: {future_solar.getYear()}年{future_solar.getMonth()}月{future_solar.getDay()}日")
        print(f"未来农历: {future_lunar.toString()}")
        
        future_bazi = future_lunar.getBaZi()
        print(f"未来八字: {future_bazi[0]}{future_bazi[1]} {future_bazi[2]}{future_bazi[3]} {future_bazi[4]}{future_bazi[5]} {future_bazi[6]}{future_bazi[7]}")
        
        # 测试特殊时间点 (午夜0点)
        midnight_solar = Solar.fromYmdHms(1990, 1, 15, 0, 0, 0)
        midnight_lunar = midnight_solar.getLunar()
        
        print(f"午夜0点公历: {midnight_solar.getYear()}年{midnight_solar.getMonth()}月{midnight_solar.getDay()}日 {midnight_solar.getHour()}时")
        print(f"午夜0点农历: {midnight_lunar.toString()}")
        
        midnight_bazi = midnight_lunar.getBaZi()
        print(f"午夜0点八字: {midnight_bazi[0]}{midnight_bazi[1]} {midnight_bazi[2]}{midnight_bazi[3]} {midnight_bazi[4]}{midnight_bazi[5]} {midnight_bazi[6]}{midnight_bazi[7]}")
    
    def test_format_bazi():
        """测试格式化八字数据为我们需要的格式"""
        print("\n=== 测试格式化八字数据 ===")
        
        solar = Solar.fromYmdHms(1990, 1, 15, 12, 0, 0)
        lunar = solar.getLunar()
        
        # 获取基本信息
        year_gan = lunar.getYearGan()
        year_zhi = lunar.getYearZhi()
        month_gan = lunar.getMonthGan()
        month_zhi = lunar.getMonthZhi()
        day_gan = lunar.getDayGan()
        day_zhi = lunar.getDayZhi()
        hour_gan = lunar.getTimeGan()
        hour_zhi = lunar.getTimeZhi()
        
        # 获取八字对象
        eight_char = lunar.getEightChar()
        yun = eight_char.getYun(1)  # 男性
        
        # 格式化年柱
        year_pillar = {
            "heavenlyStem": year_gan,
            "earthlyBranch": year_zhi,
            "element": LunarUtil.WU_XING_GAN.get(year_gan)
        }
        
        # 格式化月柱
        month_pillar = {
            "heavenlyStem": month_gan,
            "earthlyBranch": month_zhi,
            "element": LunarUtil.WU_XING_GAN.get(month_gan)
        }
        
        # 格式化日柱
        day_pillar = {
            "heavenlyStem": day_gan,
            "earthlyBranch": day_zhi,
            "element": LunarUtil.WU_XING_GAN.get(day_gan)
        }
        
        # 格式化时柱
        hour_pillar = {
            "heavenlyStem": hour_gan,
            "earthlyBranch": hour_zhi,
            "element": LunarUtil.WU_XING_GAN.get(hour_gan)
        }
        
        # 计算五行分布
        five_elements = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        
        # 添加天干的五行
        for gan in [year_gan, month_gan, day_gan, hour_gan]:
            five_elements[LunarUtil.WU_XING_GAN.get(gan)] += 1
        
        # 添加地支的五行
        for zhi in [year_zhi, month_zhi, day_zhi, hour_zhi]:
            five_elements[LunarUtil.WU_XING_ZHI.get(zhi)] += 1
        
        # 创建大运数据
        da_yun_data = []
        da_yun_list = yun.getDaYun()
        
        for i in range(min(8, len(da_yun_list))):
            gan_zhi = da_yun_list[i]
            start_age = yun.getStartAge() + i * 10
            end_age = start_age + 9
            
            da_yun_data.append({
                "gan": gan_zhi[0],
                "zhi": gan_zhi[1],
                "ganzhi": gan_zhi,
                "startAge": start_age,
                "endAge": end_age
            })
        
        # 将元素英文翻译成中文
        element_translation = {
            "wood": "木",
            "fire": "火",
            "earth": "土",
            "metal": "金",
            "water": "水"
        }
        
        # 格式化输出
        print(f"年柱: {year_pillar}")
        print(f"月柱: {month_pillar}")
        print(f"日柱: {day_pillar}")
        print(f"时柱: {hour_pillar}")
        print(f"五行分布: {five_elements}")
        print(f"起运年龄: {yun.getStartAge()}")
        print("大运:")
        for yun_item in da_yun_data:
            print(f"  {yun_item['startAge']}-{yun_item['endAge']}岁: {yun_item['ganzhi']}")
    
    # 执行测试
    test_basic_conversion()
    test_get_methods()
    test_eight_char()
    test_five_elements()
    test_edge_cases()
    test_format_bazi()
    
except ImportError as e:
    print("导入lunar_python相关模块失败:", str(e))
except Exception as e:
    print("测试过程中出现错误:", str(e))
    import traceback
    traceback.print_exc() 