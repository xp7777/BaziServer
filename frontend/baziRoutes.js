const express = require('express');
const router = express.Router();
const baziController = require('../controllers/baziController');
const authMiddleware = require('../middlewares/authMiddleware');

// 所有路由都需要认证
router.use(authMiddleware);

// 获取分析结果
router.get('/result/:resultId', baziController.getResult);

// 获取历史分析记录
router.get('/history', baziController.getHistory);

// 生成八字分析结果
router.post('/generate', baziController.generateResult);

// 下载PDF文档
router.get('/pdf/:resultId', baziController.downloadPDF);

module.exports = router;
