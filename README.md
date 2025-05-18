# 八字命理AI指导系统

本系统利用AI技术和传统八字命理，为用户提供个人命理分析和人生指导服务。

## 主要功能

1. **八字命盘生成**：根据用户出生年月日时，自动计算八字命盘
2. **命理AI分析**：调用DeepSeek AI对八字进行全面分析
3. **PDF报告生成**：自动生成八字分析PDF报告供用户下载
4. **多领域分析**：包括健康、财富、事业、婚姻感情、子女等多个方面
5. **在线测试系统**：提供在线测试页面，无需登录即可体验

## 安装说明

### 环境要求

- Python 3.8+
- MongoDB
- 必要的Python依赖项
- ReportLab用于PDF报告生成

### 安装步骤

1. 克隆代码库
```bash
git clone <repository_url>
cd 八字命理AI指导系统
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
创建 `.env` 文件并设置必要的环境变量，参考 `.env.example`

4. 启动服务
```bash
python app.py
```

## 系统架构

本系统采用前后端分离架构：

- 前端：Vue.js（暂未完成）
- 后端：Flask REST API
- 数据库：MongoDB
- AI接口：DeepSeek API

## API接口说明

### 八字分析接口

- **URL**: `/api/bazi/analyze`
- **方法**: POST
- **说明**: 提交出生信息进行八字分析
- **参数**:
  ```json
  {
    "solarYear": 1986,
    "solarMonth": 4,
    "solarDay": 23,
    "solarHour": 17,
    "gender": "女",
    "birthPlace": "甘肃陇南",
    "livingPlace": "陕西汉中"
  }
  ```
- **返回**:
  ```json
  {
    "code": 200,
    "message": "分析成功",
    "data": {
      "analysis_id": "xxx",
      "bazi": "乙巳 庚辰 癸丑 壬戌",
      "analysis": "分析内容...",
      "pdf_url": "/pdfs/xxx.pdf"
    }
  }
  ```

### 查询分析结果接口

- **URL**: `/api/bazi/result/<result_id>`
- **方法**: GET
- **说明**: 查询特定ID的分析结果
- **返回**: 与分析接口相同

### PDF下载接口

- **URL**: `/api/bazi/pdf/<result_id>`
- **方法**: GET
- **说明**: 下载特定ID的分析PDF报告

## 测试页面

系统提供了测试页面，访问以下地址即可使用：

```
http://localhost:5000/test
```

## 八字命理分析原理

系统结合了传统命理学和现代AI技术：

1. 使用sxtwl库计算八字命盘和大运
2. 提取神煞、五行旺衰等关键信息
3. 构建专业的提示词传递给DeepSeek AI
4. AI根据八字命理理论进行分析
5. 生成多个领域的生活建议
6. 制作精美的PDF报告

## 开发计划

- [ ] 完善前端页面
- [ ] 增加更多神煞和命理指标
- [ ] 优化AI提示词，提高分析准确性
- [ ] 增加用户管理系统
- [ ] 实现支付功能

## 许可证

[授权许可说明] 