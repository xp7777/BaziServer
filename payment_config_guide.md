# 八字命理AI系统支付配置指南

本文档详细说明如何为八字命理AI系统配置微信支付和支付宝支付。

## 一、前提准备

### 1.1 服务器要求
- 必须有公网可访问的域名
- 必须配置HTTPS证书
- 需要备案（微信支付和支付宝都要求域名备案）

### 1.2 商户资质
- 企业营业执照
- 企业对公银行账户
- 企业法人身份证件

## 二、微信支付配置

### 2.1 申请过程
1. 访问[微信商户平台](https://pay.weixin.qq.com)注册微信支付商户号
2. 完成企业资质审核（提交营业执照、银行账户等信息）
3. 获取微信支付商户号(WECHAT_MCH_ID)
4. 设置API密钥(WECHAT_API_KEY)
5. 在[微信公众平台](https://mp.weixin.qq.com)注册公众号或小程序
6. 获取AppID(WECHAT_APP_ID)和AppSecret

### 2.2 配置过程
1. 登录微信商户平台
2. 产品中心 -> JSAPI -> 开通支付
3. 账户中心 -> API安全 -> 设置API密钥
4. 配置支付授权目录（公众号支付）或网页域名（H5支付）
5. 配置支付回调通知URL(WECHAT_NOTIFY_URL)

### 2.3 环境变量配置
在项目的`.env`文件中添加以下配置：
```
WECHAT_APP_ID=您的微信公众号/小程序AppID
WECHAT_MCH_ID=您的微信商户号
WECHAT_API_KEY=您的微信支付API密钥
WECHAT_NOTIFY_URL=https://您的域名/api/order/wechat/notify
```

## 三、支付宝支付配置

### 3.1 申请过程
1. 访问[支付宝开放平台](https://open.alipay.com)注册开发者账号
2. 创建应用并完成企业资质认证
3. 获取支付宝应用ID(ALIPAY_APP_ID)
4. 生成RSA2密钥对
   - 可以使用支付宝开发助手或OpenSSL生成
   - 私钥保存在服务器，公钥上传到支付宝

### 3.2 配置过程
1. 登录支付宝开放平台
2. 我的应用 -> 设置 -> 开发设置
3. 配置接口加签方式（上传应用公钥）
4. 下载支付宝公钥
5. 配置授权回调地址和网关回调地址

### 3.3 环境变量配置
在项目的`.env`文件中添加以下配置：
```
ALIPAY_APP_ID=您的支付宝应用ID
ALIPAY_PRIVATE_KEY=您的应用私钥
ALIPAY_PUBLIC_KEY=支付宝公钥
ALIPAY_NOTIFY_URL=https://您的域名/api/order/alipay/notify
ALIPAY_RETURN_URL=https://您的域名/payment/result
```

### 3.4 RSA2密钥生成步骤
使用OpenSSL生成RSA2密钥对：
```bash
# 生成私钥
openssl genrsa -out app_private_key.pem 2048

# 生成公钥
openssl rsa -in app_private_key.pem -pubout -out app_public_key.pem

# 转换为PKCS8格式（Java等语言需要）
openssl pkcs8 -topk8 -inform PEM -in app_private_key.pem -outform PEM -nocrypt -out app_private_key_pkcs8.pem
```

### 3.5 检查密钥格式
私钥格式应类似：
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAydp4...省略...UNlcQ==
-----END RSA PRIVATE KEY-----
```

公钥格式应类似：
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BA...省略...QQIDAQAB
-----END PUBLIC KEY-----
```

## 四、集成测试

### 4.1 微信支付测试
1. 使用微信支付的测试账号进行测试
2. 通过[微信支付沙箱](https://pay.weixin.qq.com/wiki/doc/api/wxpay/ch/ontwofactorstd/chapter3_3.shtml)模拟支付流程
3. 检查回调通知是否正常接收

### 4.2 支付宝支付测试
1. 使用[支付宝沙箱环境](https://opendocs.alipay.com/open/200/105311)
2. 在沙箱环境创建测试账号
3. 使用测试密钥和沙箱网关
4. 使用沙箱环境的支付宝客户端进行测试

## 五、常见问题

### 5.1 微信支付常见问题
- 签名验证失败：检查API密钥是否正确
- 回调通知收不到：检查域名是否可访问，防火墙是否开放
- 支付失败：检查商户号状态，是否有异常限制

### 5.2 支付宝常见问题
- 密钥格式错误：确保密钥格式正确，包含完整的头尾标记
- 签名验证失败：检查公私钥是否匹配
- 应用权限问题：确认应用已获得支付相关的权限

## 六、上线注意事项

1. 先在测试环境充分测试
2. 确保回调通知URL安全可靠
3. 实现订单状态的定时查询机制，防止回调通知丢失
4. 做好交易记录的日志保存
5. 实现退款功能
6. 定期对账

如有问题，请参考[微信支付官方文档](https://pay.weixin.qq.com/wiki/doc/api/index.html)和[支付宝开放平台文档](https://opendocs.alipay.com/open/270/105899)。 