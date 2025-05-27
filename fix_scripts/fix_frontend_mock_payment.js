// 此脚本用于在浏览器控制台中执行，修复结果页面问题
// 复制粘贴到浏览器控制台中执行

(async function() {
  console.log('开始修复模拟支付参数问题...');
  
  // 获取当前结果ID
  const resultId = window.location.pathname.split('/').pop();
  console.log('当前结果ID:', resultId);
  
  // 设置日期参数
  const birthDate = '2022-06-21'; // 您可以根据需要修改
  const birthTime = '午时 (11:00-13:00)'; // 您可以根据需要修改
  const gender = 'male'; // 您可以根据需要修改
  
  console.log('使用以下参数进行修复:', { birthDate, birthTime, gender });
  
  // 构建请求URL
  const url = `/api/order/mock/pay/${resultId.replace('RES', '')}?birthDate=${encodeURIComponent(birthDate)}&birthTime=${encodeURIComponent(birthTime)}&gender=${encodeURIComponent(gender)}`;
  
  try {
    console.log('发送请求:', url);
    
    // 发送请求
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // 解析响应
    const data = await response.json();
    console.log('响应:', data);
    
    if (data.code === 200) {
      console.log('修复成功! 新的结果ID:', data.data.resultId);
      
      // 提示用户
      alert(`修复成功! 将跳转到新的结果页面(ID: ${data.data.resultId})`);
      
      // 跳转到新的结果页面，并传递参数
      window.location.href = `/result/${data.data.resultId}?birthDate=${encodeURIComponent(birthDate)}&birthTime=${encodeURIComponent(birthTime)}&gender=${encodeURIComponent(gender)}`;
    } else {
      console.error('修复失败:', data.message);
      alert('修复失败: ' + data.message);
    }
  } catch (error) {
    console.error('请求出错:', error);
    alert('请求出错，请查看控制台');
  }
})(); 