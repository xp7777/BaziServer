import lunar_python
from lunar_python.Solar import Solar
from lunar_python.Lunar import Lunar

def test_lunar_basic():
    """测试lunar_python库的基本用法"""
    print("测试lunar_python库的基本用法...")
    
    # 创建公历对象
    solar = Solar.fromYmdHms(1990, 1, 15, 12, 0, 0)
    print("公历:", solar.toYmd())
    
    # 转换为农历
    lunar = solar.getLunar()
    print("农历:", lunar.toString())
    
    # 获取八字
    bazi = lunar.getBaZi()
    print("八字:", bazi)
    
    # 获取年柱
    year_gan_zhi = lunar.getYearInGanZhi()
    print("年柱:", year_gan_zhi)
    
    # 获取月柱
    month_gan_zhi = lunar.getMonthInGanZhi()
    print("月柱:", month_gan_zhi)
    
    # 获取日柱
    day_gan_zhi = lunar.getDayInGanZhi()
    print("日柱:", day_gan_zhi)
    
    # 获取时柱
    hour_gan_zhi = lunar.getTimeInGanZhi()
    print("时柱:", hour_gan_zhi)
    
    # 获取八字对象
    eight_char = lunar.getEightChar()
    print("八字对象:", eight_char)
    
    # 获取大运
    yun = eight_char.getYun(1)  # 1表示男性
    print("大运起始年龄:", yun.getStartAge())
    
    # 获取大运干支
    da_yun = yun.getDaYun()
    print("大运干支:", da_yun)

if __name__ == "__main__":
    test_lunar_basic() 