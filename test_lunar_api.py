from lunar_python.Solar import Solar
from lunar_python.Lunar import Lunar

def check_lunar_api():
    """检查lunar-python的Lunar对象API"""
    print("=== 检查Lunar对象API ===")
    
    # 创建公历对象
    solar = Solar.fromYmdHms(1990, 1, 15, 12, 0, 0)
    
    # 转换为农历
    lunar = solar.getLunar()
    
    print("Lunar对象的方法:")
    methods = [method for method in dir(lunar) if not method.startswith('_')]
    print(methods)
    
    print("\n农历信息:")
    print(f"年份: {lunar.getYear()}")
    print(f"月份: {lunar.getMonth()}")
    print(f"日: {lunar.getDay()}")
    
    # 检查闰月相关的方法
    print("\n检查闰月相关方法:")
    try:
        print("isLeap():", lunar.isLeap())
    except AttributeError:
        print("isLeap() 方法不存在")
    
    try:
        print("isLeapMonth():", lunar.isLeapMonth())
    except AttributeError:
        print("isLeapMonth() 方法不存在")
    
    try:
        print("isLeapYear():", lunar.isLeapYear())
    except AttributeError:
        print("isLeapYear() 方法不存在")
    
    try:
        print("getLeapMonth():", lunar.getLeapMonth())
    except AttributeError:
        print("getLeapMonth() 方法不存在")
        
    # 尝试其他可能的方法名
    print("\n尝试其他可能的方法:")
    for method_name in ["isLeap", "isLeapMonth", "isLeapYear", "getLeapMonth", "leapMonth", "isLeap", "leap", "isRun", "isRunMonth", "isRunYear"]:
        if method_name in methods:
            try:
                value = getattr(lunar, method_name)()
                print(f"{method_name}(): {value}")
            except:
                print(f"{method_name}(): 调用失败")

if __name__ == "__main__":
    check_lunar_api() 