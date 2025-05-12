const express = require('express');
const router = express.Router();
const orderController = require('../controllers/orderController');
const authMiddleware = require('../middlewares/authMiddleware');

// 所有路由都需要认证
router.use(authMiddleware);

// 创建订单
router.post('/create', orderController.createOrder);

// 获取支付信息
router.post('/payment', orderController.getPaymentInfo);

// 查询订单状态
router.get('/status/:orderId', orderController.getOrderStatus);

// 支付回调处理（这个路由实际上应该是公开的，但为了演示简化处理）
router.post('/callback', orderController.paymentCallback);

module.exports = router;
