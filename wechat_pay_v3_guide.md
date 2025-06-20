# 微信支付V3接口使用指南

## 前言

本系统已升级为支持微信支付V3接口，提供更安全、更便捷的支付体验。V3接口在安全性和功能上有显著提升，但需要特定的证书和配置。本文档将引导您完成配置过程。

## 配置步骤

### 1. 获取证书

1. 登录[微信商户平台](https://pay.weixin.qq.com/)
2. 进入【账户中心】-【API安全】-【API证书】
3. 下载API证书（包括`apiclient_cert.pem`和`apiclient_key.pem`）

### 2. 设置API V3密钥

1. 在商户平台【账户中心】-【API安全】-【设置APIv3密钥】
2. 设置32位字符的APIv3密钥，请妥善保存

### 3. 放置证书

1. 在项目根目录下的`cert`目录中，放置以下文件：
   - `apiclient_cert.pem` (证书文件)
   - `apiclient_key.pem` (私钥文件)

### 4. 配置环境变量

在`.env`文件中配置以下变量：

```
# 微信支付基础配置
WECHAT_MCH_ID=您的商户号
WECHAT_APP_ID=您的应用ID
WECHAT_CERT_SERIAL_NO=您的证书序列号

# V3 API配置
WECHAT_API_V3_KEY=您的API V3密钥
WECHAT_CERT_DIR=./cert
WECHAT_NOTIFY_URL=https://您的域名/api/order/wechat/notify/v3
```

### 5. 配置回调URL

1. 在商户平台设置V3回调地址为：`https://您的域名/api/order/wechat/notify/v3`
2. 确保此域名已获取SSL证书，必须使用HTTPS协议

## 验证配置

重启应用后，在日志中应观察到以下内容：

```
- utils.wechat_pay_v3 - INFO - 成功加载微信支付证书，商户号=xxxxxxxx, 证书序列号=xxxxxxxx
- utils.wechat_pay_v3 - INFO - 初始化微信支付V3: 商户号=xxxxxxxx, 应用ID=xxxxxxxx
- utils.payment_service - INFO - 使用全局微信支付V3接口实例
```

这表明微信支付V3配置成功。

## 故障排除

1. **未找到证书文件**：确保证书文件名称正确且放置在`cert`目录下
2. **证书加载失败**：检查证书格式是否正确，证书序列号是否正确
3. **支付失败**：检查API V3密钥是否配置正确
4. **回调不生效**：确保回调URL配置正确且可访问

## 降级机制

系统仍然保留了对V2接口的支持，当V3接口无法使用时，将自动降级使用V2接口。 