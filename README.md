# 八字命理AI人生指导系统

八字命理AI人生指导系统是一个结合传统八字命理与现代AI技术的人生指导应用。用户可以输入出生信息，系统将计算八字命盘并通过AI分析，为用户提供个性化的人生指导建议。

## 功能特点

- 根据用户出生信息计算八字命盘
- 支持公历和农历日期转换
- 计算真太阳时和流年大运
- 集成ChatGPT/DeepSeek API进行八字分析
- 提供多个分析维度：健康、财富、事业、婚姻感情、子女
- 支持微信支付和支付宝在线支付
- 结果可在线查看和下载PDF
- 用户历史结果查询功能

## 技术架构

### 前端

- 框架：Vue.js
- UI组件库：Vant UI
- HTTP客户端：Axios

### 后端

- 开发语言：Python
- Web框架：Flask
- 数据库：MongoDB
- 身份认证：JWT
- AI接口：OpenAI API、DeepSeek API
- PDF生成：pdfkit

## 项目结构

```
├── app.py               # 应用入口
├── requirements.txt     # 依赖包列表
├── .env                 # 环境变量配置
├── models/              # 数据模型
│   ├── user_model.py
│   ├── order_model.py
│   └── bazi_result_model.py
├── routes/              # 路由控制器
│   ├── user_routes.py
│   ├── order_routes.py
│   └── bazi_routes.py
├── utils/               # 工具类
│   ├── bazi_calculator.py
│   ├── ai_service.py
│   ├── payment_service.py
│   ├── pdf_generator.py
│   └── sms_service.py
├── config/              # 配置文件
└── pdfs/                # 生成的PDF文件
```

## 安装部署

### 环境要求

- Python 3.8+
- MongoDB 4.4+
- wkhtmltopdf (用于PDF生成)

### 安装步骤

1. 克隆代码仓库
```bash
git clone https://github.com/yourusername/bazi-ai-system.git
cd bazi-ai-system
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入相关配置
```

4. 运行应用
```bash
python app.py
```

### 部署到生产环境

使用gunicorn作为WSGI服务器：

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

建议使用Nginx作为反向代理。

## API接口

### 用户模块
- `/api/user/sendVerifyCode` - 发送验证码
- `/api/user/login` - 用户登录/注册
- `/api/user/info` - 获取用户信息

### 订单模块
- `/api/order/create` - 创建订单
- `/api/order/payment` - 获取支付信息
- `/api/order/status/<order_id>` - 查询订单状态
- `/api/order/wechat/notify` - 微信支付回调
- `/api/order/alipay/notify` - 支付宝回调

### 八字分析模块
- `/api/bazi/result/<result_id>` - 获取分析结果
- `/api/bazi/history` - 获取历史分析记录
- `/api/bazi/pdf/<result_id>` - 下载PDF文档

## 使用说明

1. 用户通过手机号注册/登录
2. 在主页填写基本信息（性别、出生年月日时）和选择分析侧重点
3. 提交信息后进入支付页面
4. 支付成功后，系统会自动计算八字并进行AI分析
5. 分析完成后，用户可以在结果页面查看分析内容，并下载PDF报告
6. 历史记录可在用户中心页面查看

## 许可证

本项目采用MIT许可证 