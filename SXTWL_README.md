# SXTWL 四柱万年历安装指南

本项目使用了sxtwl（四柱万年历）Python扩展包来实现农历和干支的计算。这个包提供了精确的农历年历表，包括二十四节气、天干地支、生肖等信息。

## 安装要求

sxtwl是一个C++扩展包，需要编译安装。在Windows系统上，需要安装Microsoft Visual C++ 14.0或更高版本的构建工具。

### Windows系统安装步骤

1. 安装Python（推荐3.7或以上版本）
2. 安装Microsoft Visual C++ Build Tools:
   - 访问 [Visual Studio下载页面](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - 下载并安装 "Build Tools for Visual Studio"
   - 在安装过程中，选择 "C++ build tools" 工作负载，确保选中以下组件：
     - MSVC（最新版本）- VS C++ x64/x86 build tools
     - Windows 10 SDK
   - 完成安装后，可能需要重启电脑

3. 安装sxtwl包:
   ```
   pip install sxtwl
   ```

如果安装过程中出现编译错误，可以尝试直接安装预编译的wheel包：
```
pip install --only-binary=:all: sxtwl
```

### 简化安装方法（使用脚本）

我们提供了一个自动化安装脚本，可以尝试安装sxtwl包并测试其功能：
```
python install_sxtwl.py
```

如果脚本运行失败，它会提供详细的安装指南。

## 使用示例

```python
import sxtwl

# 获取公历某一天的信息
day = sxtwl.fromSolar(2024, 1, 1)  # 获取2024年1月1日的信息

# 获取农历信息
print(f"农历：{day.getLunarYear()}年{('闰' if day.isLunarLeap() else '')}{day.getLunarMonth()}月{day.getLunarDay()}日")

# 获取干支信息
gz_year = day.getYearGZ()
gz_month = day.getMonthGZ()
gz_day = day.getDayGZ()

# 天干地支对照表
Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

print(f"年干支：{Gan[gz_year.tg]}{Zhi[gz_year.dz]}")
print(f"月干支：{Gan[gz_month.tg]}{Zhi[gz_month.dz]}")
print(f"日干支：{Gan[gz_day.tg]}{Zhi[gz_day.dz]}")

# 获取节气信息
if day.hasJieQi():
    jqmc = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏",
            "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", 
            "霜降", "立冬", "小雪", "大雪"]
    print(f"节气：{jqmc[day.getJieQi()]}")
```

## 常见问题

### 1. 安装时出现 "Microsoft Visual C++ 14.0 or greater is required" 错误

这表示您需要安装Microsoft Visual C++ Build Tools。请按照上面的安装步骤进行安装。

### 2. 无法编译安装sxtwl

尝试安装预编译的wheel包：
```
pip install --only-binary=:all: sxtwl
```

### 3. 安装成功但导入失败

确保您使用的是与编译时相同的Python环境。如果使用虚拟环境，确保已激活正确的环境。

## 参考资源

- [sxtwl PyPI主页](https://pypi.org/project/sxtwl/)
- [原始sxtwl_cpp项目](https://github.com/yuangu/sxtwl_cpp)
- [Microsoft C++ Build Tools下载](https://visualstudio.microsoft.com/visual-cpp-build-tools/) 