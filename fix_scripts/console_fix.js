// 复制此脚本，在浏览器控制台中执行以修复结果页面问题

// 用户填写的出生日期和时间
const birthDate = '2022-06-21'; // 更改为您的出生日期
const birthTime = '午时 (11:00-13:00)'; // 更改为您的出生时间
const gender = 'male'; // 更改为您的性别

// 从URL获取resultId
const resultId = window.location.pathname.split('/').pop();
console.log('当前结果ID:', resultId);

// 发送模拟支付请求，包含出生日期和时间
(async function() {
  // 请求URL中添加参数
  const url = `/api/order/mock/pay/${resultId}?birthDate=${encodeURIComponent(birthDate)}&birthTime=${encodeURIComponent(birthTime)}&gender=${encodeURIComponent(gender)}`;
  console.log('发送请求:', url);
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    console.log('响应:', data);
    
    if (data.code === 200) {
      console.log('成功! 新的结果ID:', data.data.resultId);
      
      // 重定向到新的结果页
      window.location.href = `/result/${data.data.resultId}?birthDate=${encodeURIComponent(birthDate)}&birthTime=${encodeURIComponent(birthTime)}&gender=${encodeURIComponent(gender)}`;
    } else {
      console.error('失败:', data.message);
      alert('模拟支付失败: ' + data.message);
    }
  } catch (error) {
    console.error('请求出错:', error);
    alert('请求出错，请查看控制台');
  }
})(); 