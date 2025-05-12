const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const authMiddleware = require('../middlewares/authMiddleware');

// 公开路由
router.post('/sendVerifyCode', userController.sendVerifyCode);
router.post('/login', userController.login);

// 需要认证的路由
router.get('/info', authMiddleware, userController.getUserInfo);

module.exports = router;
