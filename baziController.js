const axios = require('axios');
const BaziResult = require('../models/baziResultModel');
const Order = require('../models/orderModel');
const { calculateBazi } = require('../utils/baziCalculator');
const { buildCompletePrompt, processAIResponse } = require('../utils/aiPromptBuilder');

// 获取分析结果
exports.getResult = async (req, res) => {
  try {
    const { resultId } = req.params;
    const userId = req.user._id;
    
    // 查找结果
    const result = await BaziResult.findOne({ _id: resultId, userId });
    if (!result) {
      return res.status(404).json({
        code: 404,
        message: '分析结果不存在'
      });
    }
    
    return res.status(200).json({
      code: 200,
      message: '成功',
      data: {
        resultId: result._id,
        baziData: result.baziData,
        aiAnalysis: result.aiAnalysis,
        pdfUrl: result.pdfUrl
      }
    });
  } catch (error) {
    console.error('获取分析结果错误:', error);
    return res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
};

// 获取历史分析记录
exports.getHistory = async (req, res) => {
  try {
    const userId = req.user._id;
    
    // 查找用户的所有分析结果
    const results = await BaziResult.find({ userId }).sort({ createTime: -1 });
    
    const historyList = results.map(result => ({
      resultId: result._id,
      createTime: result.createTime,
      focusAreas: result.focusAreas,
      pdfUrl: result.pdfUrl
    }));
    
    return res.status(200).json({
      code: 200,
      message: '成功',
      data: historyList
    });
  } catch (error) {
    console.error('获取历史分析记录错误:', error);
    return res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
};

// 生成八字分析结果
exports.generateResult = async (req, res) => {
  try {
    const { orderId } = req.body;
    const userId = req.user._id;
    
    // 查找订单
    const order = await Order.findOne({ _id: orderId, userId });
    if (!order) {
      return res.status(404).json({
        code: 404,
        message: '订单不存在'
      });
    }
    
    // 检查订单状态
    if (order.status !== 'paid') {
      return res.status(400).json({
        code: 400,
        message: '订单未支付'
      });
    }
    
    // 检查是否已生成结果
    if (order.resultId) {
      const existingResult = await BaziResult.findById(order.resultId);
      if (existingResult) {
        return res.status(200).json({
          code: 200,
          message: '分析结果已存在',
          data: {
            resultId: existingResult._id
          }
        });
      }
    }
    
    // 计算八字
    const baziData = calculateBazi(
      order.orderData.birthTime,
      order.orderData.birthTime.isLunar,
      order.orderData.gender
    );
    
    // 调用AI接口生成分析结果
    const aiAnalysis = await generateAIAnalysis(baziData, order.orderData.focusAreas);
    
    // 创建分析结果记录
    const result = new BaziResult({
      userId,
      orderId,
      gender: order.orderData.gender,
      birthTime: order.orderData.birthTime,
      focusAreas: order.orderData.focusAreas,
      baziData,
      aiAnalysis,
      pdfUrl: `https://example.com/pdf/${orderId}.pdf` // 实际项目中应该生成真实的PDF
    });
    
    await result.save();
    
    // 更新订单的结果ID
    order.resultId = result._id;
    await order.save();
    
    return res.status(200).json({
      code: 200,
      message: '分析结果生成成功',
      data: {
        resultId: result._id
      }
    });
  } catch (error) {
    console.error('生成分析结果错误:', error);
    return res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
};

// 调用AI接口生成分析结果
async function generateAIAnalysis(baziData, focusAreas) {
  try {
    // 使用优化后的提示词构建工具
    const { systemPrompt, userPrompt } = buildCompletePrompt(baziData, focusAreas);
    
    // 实际项目中，这里应该调用ChatGPT API
    // const response = await axios.post('https://api.openai.com/v1/chat/completions', {
    //   model: 'gpt-3.5-turbo',
    //   messages: [
    //     { role: 'system', content: systemPrompt },
    //     { role: 'user', content: userPrompt }
    //   ],
    //   temperature: 0.7,
    //   max_tokens: 2000
    // }, {
    //   headers: {
    //     'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
    //     'Content-Type': 'application/json'
    //   }
    // });
    
    // const aiResponse = response.data.choices[0].message.content;
    
    // 使用优化后的响应处理函数
    // return processAIResponse(aiResponse, focusAreas);
    
    // 为了演示，返回模拟的处理结果
    return processAIResponse("模拟的AI响应", focusAreas);
  } catch (error) {
    console.error('AI分析生成错误:', error);
    // 返回默认分析结果
    return {
      overall: '由于技术原因，无法生成详细分析。请稍后再试。'
    };
  }
}

// 下载PDF文档
exports.downloadPDF = async (req, res) => {
  try {
    const { resultId } = req.params;
    const userId = req.user._id;
    
    // 查找结果
    const result = await BaziResult.findOne({ _id: resultId, userId });
    if (!result) {
      return res.status(404).json({
        code: 404,
        message: '分析结果不存在'
      });
    }
    
    // 实际项目中，这里应该生成PDF并返回文件流
    // 为了演示，我们返回成功消息
    return res.status(200).json({
      code: 200,
      message: '成功',
      data: {
        pdfUrl: result.pdfUrl
      }
    });
  } catch (error) {
    console.error('下载PDF错误:', error);
    return res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
};
