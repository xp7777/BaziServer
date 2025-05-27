from lunar_python.Solar import Solar
from lunar_python.Lunar import Lunar

def test_dayun_str():
    """测试DaYun对象的字符串表示"""
    print("=== 测试DaYun对象的字符串表示 ===")
    
    # 创建公历对象
    solar = Solar.fromYmdHms(1990, 1, 15, 12, 0, 0)
    lunar = solar.getLunar()
    
    # 获取八字对象
    eight_char = lunar.getEightChar()
    
    # 获取大运
    yun_male = eight_char.getYun(1)  # 1表示男性
    da_yun_list = yun_male.getDaYun()
    
    print(f"大运列表包含 {len(da_yun_list)} 项")
    print("大运对象及其字符串表示:")
    
    for i, da_yun in enumerate(da_yun_list[:8]):  # 只显示前8个大运
        print(f"大运 {i+1}:")
        print(f"  对象: {da_yun}")
        print(f"  对象类型: {type(da_yun)}")
        print(f"  字符串表示: '{str(da_yun)}'")
        print(f"  字符串长度: {len(str(da_yun))}")
        
        # 尝试从对象中提取干支
        try:
            print(f"  大运索引: {da_yun.getIndex()}")
            gan_zhi = str(da_yun)
            print(f"  干支字符: '{gan_zhi}'")
            
            # 分析字符串的组成
            if len(gan_zhi) > 0:
                print(f"  第一个字符: '{gan_zhi[0]}'")
                if len(gan_zhi) > 1:
                    print(f"  第二个字符: '{gan_zhi[1]}'")
                if len(gan_zhi) > 2:
                    print(f"  剩余字符: '{gan_zhi[2:]}'")
        except Exception as e:
            print(f"  提取干支信息失败: {e}")
    
    print("\n=== 尝试访问DaYun的其他属性和方法 ===")
    if da_yun_list:
        first_da_yun = da_yun_list[0]
        methods = [method for method in dir(first_da_yun) if not method.startswith('_')]
        print(f"可用方法: {methods}")
        
        # 尝试调用方法
        for method in methods:
            try:
                func = getattr(first_da_yun, method)
                result = func()
                print(f"{method}(): {result}")
            except Exception as e:
                print(f"{method}(): 调用失败 - {e}")
    
    # 测试不同的对象表示方式
    print("\n=== 测试不同的对象表示方式 ===")
    if da_yun_list:
        first_da_yun = da_yun_list[0]
        print(f"__str__: {str(first_da_yun)}")
        print(f"__repr__: {repr(first_da_yun)}")
        
        # 尝试手动调用__str__方法
        try:
            print(f"直接调用__str__: {first_da_yun.__str__()}")
        except Exception as e:
            print(f"直接调用__str__失败: {e}")

if __name__ == "__main__":
    test_dayun_str() 