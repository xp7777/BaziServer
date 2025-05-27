// 前端补丁 - 修复模拟支付请求
// 在Result.vue中查找callMockPayment方法，并替换为以下代码

/*
async callMockPayment() {
  console.log('尝试使用模拟支付接口...');
  try {
    // 从URL获取参数
    const birthDate = new URLSearchParams(window.location.search).get('birthDate') || '2022-06-21';
    const birthTime = new URLSearchParams(window.location.search).get('birthTime') || '午时 (11:00-13:00)';
    const gender = new URLSearchParams(window.location.search).get('gender') || 'male';
    
    console.log('使用参数:', { birthDate, birthTime, gender });
    
    // 将这些参数作为查询参数添加到URL中
    const url = `/api/order/mock/pay/${this.resultId}?birthDate=${encodeURIComponent(birthDate)}&birthTime=${encodeURIComponent(birthTime)}&gender=${encodeURIComponent(gender)}`;
    
    const response = await this.$http.post(url);
    if (response.data.code === 200) {
      console.log('获取到新的resultId:', response.data.data.resultId);
      this.resultId = response.data.data.resultId;
      await this.getResult();
    } else {
      console.error('模拟支付失败:', response.data.message);
    }
  } catch (error) {
    console.error('模拟支付失败:', error);
  }
}
*/

// 或者使用请求体传递参数

/*
async callMockPayment() {
  console.log('尝试使用模拟支付接口...');
  try {
    // 从URL获取参数
    const birthDate = new URLSearchParams(window.location.search).get('birthDate') || '2022-06-21';
    const birthTime = new URLSearchParams(window.location.search).get('birthTime') || '午时 (11:00-13:00)';
    const gender = new URLSearchParams(window.location.search).get('gender') || 'male';
    
    // 构建请求数据
    const requestData = { birthDate, birthTime, gender };
    console.log('发送模拟支付请求，数据:', requestData);
    
    const response = await this.$http.post(`/api/order/mock/pay/${this.resultId}`, requestData);
    if (response.data.code === 200) {
      console.log('获取到新的resultId:', response.data.data.resultId);
      this.resultId = response.data.data.resultId;
      await this.getResult();
    } else {
      console.error('模拟支付失败:', response.data.message);
    }
  } catch (error) {
    console.error('模拟支付失败:', error);
  }
}
*/

// 临时解决方案 - 如果您无法修改前端代码，您可以直接在浏览器控制台中执行以下代码：

/*
// 打开浏览器开发者工具，切换到控制台，粘贴并执行以下代码
(async function() {
  const birthDate = '2022-06-21'; // 更改为您希望使用的日期
  const birthTime = '午时 (11:00-13:00)'; // 更改为您希望使用的时间
  const gender = 'male'; // 更改为您希望使用的性别
  
  // 从URL获取resultId
  const resultId = window.location.pathname.split('/').pop();
  console.log('当前结果ID:', resultId);
  
  // 发送模拟支付请求
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
    }
  } catch (error) {
    console.error('请求出错:', error);
  }
})();
*/

// 在Payment.vue中传递参数到结果页面

/*
// 在支付成功的处理函数中
onPaymentSuccess(response) {
  const resultId = response.data.resultId;
  // 导航到结果页面时，将出生日期、时间和性别作为查询参数传递
  this.$router.push({
    name: 'result',
    params: { id: resultId },
    query: {
      birthDate: this.formData.birthDate,
      birthTime: this.formData.birthTime,
      gender: this.formData.gender
    }
  });
}
*/ 