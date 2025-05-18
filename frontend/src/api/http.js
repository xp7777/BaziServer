import axios from 'axios';

// 创建一个axios实例
const http = axios.create({
  baseURL: 'http://localhost:5000', // 后端API基础URL
  timeout: 60000, // 请求超时时间增加到60秒，适应DeepSeek API响应时间
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器 - 添加token
http.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      // 确保token格式正确，不要添加Bearer前缀（后端可能已经处理）
      config.headers['Authorization'] = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
    }
    return config;
  },
  error => {
    console.error('请求拦截器错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
http.interceptors.response.use(
  response => {
    // 正常响应处理
    return response;
  },
  error => {
    console.error('API请求错误:', error);
    
    // 根据错误状态码处理特殊情况
    if (error.response) {
      const status = error.response.status;
      const errorMessage = error.response.data?.message || '未知错误';
      
      switch (status) {
        case 401:
          console.log('未授权，请重新登录');
          // 可以在这里处理登出逻辑或跳转到登录页
          localStorage.removeItem('token'); // 清除无效的token
          break;
        case 404:
          console.log(`请求的资源不存在: ${errorMessage}`);
          break;
        case 500:
          console.log(`服务器错误: ${errorMessage}`);
          break;
        default:
          console.log(`未知错误(${status}): ${errorMessage}`);
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      if (error.code === 'ECONNABORTED') {
        console.log(`请求超时: 服务器处理时间超过了${http.defaults.timeout/1000}秒，这可能是因为AI分析需要更长时间`);
      } else {
      console.log('服务器未响应，请检查网络连接或后端服务是否运行');
      }
    } else {
      // 设置请求时发生错误
      console.log(`请求配置错误: ${error.message}`);
    }
    
    return Promise.reject(error);
  }
);

export default http; 