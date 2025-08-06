import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import { createPinia } from 'pinia';
import App from './App.vue';
import routes from './router';
import Vant from 'vant';
import 'vant/lib/index.css';
import './App.css'; // 引入全局样式
import axios from 'axios';

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 页面标题和认证守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title;
  }
  
  // 需要认证的路由列表
  const authRequiredRoutes = ['/bazi-service', '/payment', '/result', '/user'];
  
  // 检查是否需要认证
  const requiresAuth = authRequiredRoutes.some(route => to.path.startsWith(route));
  
  if (requiresAuth) {
    const token = localStorage.getItem('userToken');
    const userInfo = localStorage.getItem('userInfo');
    
    if (!token || !userInfo) {
      // 未登录，跳转到登录页
      next('/login');
      return;
    }
  }
  
  next();
});

// 创建Pinia状态管理实例
const pinia = createPinia();

// 创建Vue应用实例
const app = createApp(App);

// 使用Vant UI库
app.use(Vant);

// 使用插件
app.use(router);
app.use(pinia);

// 挂载应用
app.mount('#app');

// 添加请求拦截器，自动携带token
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('userToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);
