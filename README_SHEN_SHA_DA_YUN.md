# 神煞与大运流年功能实现文档

## 功能概述

使用lunar-python库实现了八字命理系统中的神煞和大运流年计算功能，并在前端页面中展示。

## 实现内容

### 1. 后端功能

在`utils/bazi_calculator.py`中添加了以下函数：

- `calculate_shen_sha(year, month, day, hour, gender)`: 计算神煞信息
  - 日冲（与日支对冲的生肖）
  - 建除十二值神
  - 彭祖百忌
  - 喜神、福神、财神方位
  - 本命神煞（如天乙贵人、文昌、桃花等）

- `calculate_da_yun(year, month, day, hour, gender)`: 计算大运信息
  - 起运年龄
  - 起运年份
  - 大运列表（10个大运的干支、五行、年份范围）

- 修改了`calculate_bazi()`函数，集成上述功能

### 2. 前端展示

在`frontend/src/Result.vue`中添加了以下内容：

- 神煞信息展示区域
  - 使用van-cell-group展示各类神煞信息
  - 包括日冲、值神、彭祖百忌、喜神方位、福神方位、财神方位、本命神煞

- 大运信息展示区域
  - 显示起运年龄和起运年份
  - 使用van-cell-group列表展示大运信息
  - 每个大运项显示序号、干支、五行和年份范围

### 3. 示例页面

创建了`static/shen_sha_da_yun_demo.html`示例页面，展示神煞和大运流年信息的完整样例。

添加了路由`/api/bazi/shen_sha_da_yun_demo`用于访问示例页面。

## 测试验证

创建了`test_shen_sha_da_yun.py`测试脚本，验证了以下内容：

- 神煞计算功能
  - 测试不同年份和性别的神煞计算
  - 验证神煞信息的正确性

- 大运计算功能
  - 测试不同年份和性别的大运计算
  - 验证起运年龄、起运年份和大运列表的正确性

## 使用方法

### 1. API调用

```python
from utils.bazi_calculator import calculate_bazi

# 计算八字（包含神煞和大运信息）
bazi_data = calculate_bazi("2006-10-15", "午时 (11:00-13:00)", "male")

# 获取神煞信息
shen_sha = bazi_data["shenSha"]
print(f"日冲: {shen_sha['dayChong']}")
print(f"值神: {shen_sha['zhiShen']}")

# 获取大运信息
da_yun = bazi_data["daYun"]
print(f"起运年龄: {da_yun['startAge']}岁")
print(f"起运年份: {da_yun['startYear']}年")
```

### 2. 前端访问

- 在结果页面中，可以看到神煞和大运流年信息
- 访问`/api/bazi/shen_sha_da_yun_demo`查看示例页面

## 注意事项

1. 神煞计算中的部分内容（如喜神方位、福神方位等）使用了简化计算，可以根据需要进一步完善
2. 大运计算使用了简化的起运年龄计算方法，可以根据实际需求调整
3. 本命神煞的计算可以根据需要添加更多类型

## 未来扩展

1. 添加更多类型的神煞计算
2. 完善流年小运的计算
3. 增加神煞和大运对命主的吉凶影响分析
4. 优化前端展示效果，增加更多交互功能 