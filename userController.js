const User = require('../models/userModel');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

// 发送验证码
exports.sendVerifyCode = async (req, res) => {
  try {
    const { phone } = req.body;
    
    if (!phone) {
      return res.status(400).json({
        code: 400,
        message: '手机号不能为空'
      });
    }
    
    // 验证手机号格式
    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phoneRegex.test(phone)) {
      return res.status(400).json({
        code: 400,
        message: '手机号格式不正确'
      });
    }
    
    // 生成随机验证码
    const verifyCode = Math.floor(100000 + Math.random() * 900000).toString();
    
    // 实际项目中，这里应该调用短信服务发送验证码
    // 为了演示，我们假设验证码已发送，并将其存储在会话或缓存中
    console.log(`向 ${phone} 发送验证码: ${verifyCode}`);
    
    // 在实际项目中，应该将验证码和手机号存储在Redis等缓存中，设置过期时间
    // 这里简化处理，假设验证码已经存储
    
    return res.status(200).json({
      code: 200,
      message: '验证码已发送',
      data: null
    });
  } catch (error) {
    console.error('发送验证码错误:', error);
    return res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
};

// 用户登录/注册
exports.login = async (req, res) => {
  try {
    const { phone, verifyCode } = req.body;
    
    if (!phone || !verifyCode) {
      return res.status(400).json({
        code: 400,
        message: '手机号和验证码不能为空'
      });
    }
    
    // 验证手机号格式
    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phoneRegex.test(phone)) {
      return res.status(400).json({
        code: 400,
        message: '手机号格式不正确'
      });
    }
    
    // 实际项目中，这里应该验证验证码是否正确
    // 为了演示，我们假设验证码正确
    
    // 查找用户是否存在
    let user = await User.findOne({ phone });
    
    // 如果用户不存在，创建新用户
    if (!user) {
      user = new User({
        phone,
        createTime: new Date(),
        lastLoginTime: new Date()
      });
      await user.save();
    } else {
      // 更新最后登录时间
      user.lastLoginTime = new Date();
      await user.save();
    }
    
    // 生成JWT令牌
    const token = jwt.sign(
      { userId: user._id },
      process.env.JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    return res.status(200).json({
      code: 200,
      message: '登录成功',
      data: {
        token,
        userId: user._id
      }
    });
  } catch (error) {
    console.error('登录错误:', error);
    return res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
};

// 获取用户信息
exports.getUserInfo = async (req, res) => {
  try {
    const user = req.user;
    
    return res.status(200).json({
      code: 200,
      message: '成功',
      data: {
        userId: user._id,
        phone: user.phone,
        createTime: user.createTime
      }
    });
  } catch (error) {
    console.error('获取用户信息错误:', error);
    return res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
};
