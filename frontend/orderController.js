const Order = require('../models/orderModel');
const BaziResult = require('../models/baziResultModel');

// 创建订单
exports.createOrder = async (req, res) => {
  try {
    const { gender, birthTime, focusAreas } = req.body;
    const userId = req.user._id;
    
    // 验证必要字段
    if (!gender || !birthTime || !focusAreas || focusAreas.length === 0) {
      return res.status(400).json({
        code: 400,
        message: '缺少必要参数'
      });
    }
    
    // 创建新订单
    const order = new Order({
      userId,
      amount: 9.9, // 固定价格
      status: 'pending',
      paymentMethod: 'wechat', // 默认支付方式，后续可更改
      orderData: {
        gender,
        birthTime,
        focusAreas
      }
    });
    
    await order.save();
    
    return res.status(200).json({
      code: 200,
      message: '订单创建成功',
      data: {
        orderId: order._id,
        amount: order.amount
      }
    });
  } catch (error) {
    console.error('创建订单错误:', error);
    return res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
};

// 获取支付信息
exports.getPaymentInfo = async (req, res) => {
  try {
    const { orderId, paymentMethod } = req.body;
    const userId = req.user._id;
    
    // 验证必要字段
    if (!orderId || !paymentMethod) {
      return res.status(400).json({
        code: 400,
        message: '缺少必要参数'
      });
    }
    
    // 查找订单
    const order = await Order.findOne({ _id: orderId, userId });
    if (!order) {
      return res.status(404).json({
        code: 404,
        message: '订单不存在'
      });
    }
    
    // 检查订单状态
    if (order.status === 'paid') {
      return res.status(400).json({
        code: 400,
        message: '订单已支付'
      });
    }
    
    // 更新支付方式
    order.paymentMethod = paymentMethod;
    await order.save();
    
    // 生成支付参数
    // 实际项目中，这里应该调用微信支付或支付宝API生成支付参数
    // 为了演示，我们返回模拟的支付URL
    let paymentUrl = '';
    if (paymentMethod === 'wechat') {
      paymentUrl = `https://example.com/wechat-pay?orderId=${orderId}`;
    } else if (paymentMethod === 'alipay') {
      paymentUrl = `https://example.com/alipay?orderId=${orderId}`;
    }
    
    return res.status(200).json({
      code: 200,
      message: '成功',
      data: {
        paymentUrl,
        orderId
      }
    });
  } catch (error) {
    console.error('获取支付信息错误:', error);
    return res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
};

// 查询订单状态
exports.getOrderStatus = async (req, res) => {
  try {
    const { orderId } = req.params;
    const userId = req.user._id;
    
    // 查找订单
    const order = await Order.findOne({ _id: orderId, userId });
    if (!order) {
      return res.status(404).json({
        code: 404,
        message: '订单不存在'
      });
    }
    
    return res.status(200).json({
      code: 200,
      message: '成功',
      data: {
        orderId: order._id,
        status: order.status,
        resultId: order.resultId
      }
    });
  } catch (error) {
    console.error('查询订单状态错误:', error);
    return res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
};

// 支付回调处理（微信支付和支付宝的回调接口）
exports.paymentCallback = async (req, res) => {
  try {
    // 实际项目中，这里应该根据支付平台的回调参数验证支付结果
    // 为了演示，我们假设支付成功，并直接更新订单状态
    
    const { orderId, paymentMethod } = req.body;
    
    // 查找订单
    const order = await Order.findById(orderId);
    if (!order) {
      return res.status(404).json({
        code: 404,
        message: '订单不存在'
      });
    }
    
    // 更新订单状态
    order.status = 'paid';
    order.payTime = new Date();
    await order.save();
    
    // 实际项目中，这里应该返回支付平台要求的响应格式
    // 为了演示，我们返回简单的成功响应
    return res.status(200).json({
      code: 200,
      message: '支付回调处理成功'
    });
  } catch (error) {
    console.error('支付回调处理错误:', error);
    return res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
};
