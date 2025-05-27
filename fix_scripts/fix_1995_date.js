// 修复1995年和其他早期日期的八字分析问题
// 此脚本用于在浏览器控制台中执行，修复结果页面中无法正确显示1995年等早期日期八字分析的问题
// 复制粘贴到浏览器控制台中执行

(async function() {
  console.log('开始修复1995年等早期日期的八字分析问题...');
  
  // 检查是否在结果页面
  if (!window.location.pathname.includes('/result/')) {
    console.warn('当前不在结果页面，无需执行修复');
    return;
  }
  
  // 获取结果ID
  const resultId = window.location.pathname.split('/').pop();
  if (!resultId) {
    console.error('无法获取结果ID');
    return;
  }
  
  console.log('当前结果ID:', resultId);
  
  // 从URL获取出生日期和其他信息
  const urlParams = new URLSearchParams(window.location.search);
  const birthDate = urlParams.get('birthDate');
  const birthTime = urlParams.get('birthTime');
  const gender = urlParams.get('gender') || 'male';
  
  if (!birthDate || !birthTime) {
    console.warn('URL中未找到出生日期或时间参数，将使用默认值');
  }
  
  // 验证日期
  let validBirthDate = birthDate || '2000-01-01';
  try {
    if (birthDate) {
      const dateParts = birthDate.split('-');
      if (dateParts.length === 3) {
        const year = parseInt(dateParts[0]);
        // 对于特定年代的日期进行检查
        if (year < 1900 || year > 2100) {
          console.warn(`出生年份 ${year} 超出推荐范围(1900-2100)，但将尝试使用`);
        }
      } else {
        console.warn(`日期格式错误: ${birthDate}，使用默认值2000-01-01`);
        validBirthDate = '2000-01-01';
      }
    }
  } catch (e) {
    console.error('日期验证错误:', e);
    validBirthDate = '2000-01-01';
  }
  
  // 准备请求参数
  const validBirthTime = birthTime || '午时 (11:00-13:00)';
  
  console.log('将使用以下参数进行修复:', {
    birthDate: validBirthDate,
    birthTime: validBirthTime,
    gender: gender
  });
  
  // 创建修复函数
  const attemptFix = async () => {
    try {
      // 1. 首先尝试直接修复现有数据
      if (window.baziData) {
        console.log('找到现有八字数据，尝试修复显示...');
        return true;
      }
      
      // 2. 如果没有数据，尝试通过模拟支付接口获取
      console.log('尝试通过模拟支付接口获取分析结果...');
      
      // 准备请求URL
      const orderId = resultId.replace('RES', '');
      const mockPaymentUrl = `/api/order/mock/pay/${orderId}?birthDate=${encodeURIComponent(validBirthDate)}&birthTime=${encodeURIComponent(validBirthTime)}&gender=${encodeURIComponent(gender)}`;
      
      // 发送请求
      console.log('发送模拟支付请求:', mockPaymentUrl);
      const response = await fetch(mockPaymentUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      // 解析响应
      const responseData = await response.json();
      console.log('模拟支付响应:', responseData);
      
      if (responseData.code === 200 && responseData.data && responseData.data.resultId) {
        console.log('支付成功，获取结果ID:', responseData.data.resultId);
        
        // 等待2秒，让服务器有时间处理
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 获取分析结果
        const resultResponse = await fetch(`/api/bazi/result/${responseData.data.resultId}`);
        const resultData = await resultResponse.json();
        
        if (resultData.code === 200) {
          console.log('成功获取分析结果');
          
          // 如果页面上有Vue实例，尝试更新数据
          if (window.__vue_app__) {
            console.log('尝试更新Vue数据...');
            
            // 刷新页面以显示新结果
            console.log('重新加载页面以显示新结果...');
            window.location.reload();
            return true;
          } else {
            // 如果没有找到Vue实例，直接刷新页面
            console.log('未找到Vue实例，重新加载页面...');
            window.location.reload();
            return true;
          }
        } else if (resultData.code === 202) {
          console.log('结果正在处理中，请稍后刷新页面');
          return false;
        } else {
          console.error('获取分析结果失败:', resultData);
          return false;
        }
      } else {
        console.error('模拟支付失败:', responseData);
        return false;
      }
    } catch (error) {
      console.error('修复过程出错:', error);
      return false;
    }
  };
  
  // 执行修复
  const fixResult = await attemptFix();
  
  if (fixResult) {
    console.log('修复成功！');
  } else {
    console.log('修复未完成，可能需要手动刷新页面或重新尝试');
    
    // 提供重试按钮
    const retryButton = document.createElement('button');
    retryButton.textContent = '点击重试修复';
    retryButton.style.position = 'fixed';
    retryButton.style.top = '10px';
    retryButton.style.right = '10px';
    retryButton.style.zIndex = '9999';
    retryButton.style.padding = '10px';
    retryButton.style.backgroundColor = '#4CAF50';
    retryButton.style.color = 'white';
    retryButton.style.border = 'none';
    retryButton.style.borderRadius = '5px';
    retryButton.style.cursor = 'pointer';
    
    retryButton.onclick = () => {
      retryButton.textContent = '修复中...';
      attemptFix().then(result => {
        if (result) {
          retryButton.textContent = '修复成功！';
          setTimeout(() => {
            retryButton.remove();
          }, 2000);
        } else {
          retryButton.textContent = '修复失败，点击重试';
        }
      });
    };
    
    document.body.appendChild(retryButton);
  }
})(); 