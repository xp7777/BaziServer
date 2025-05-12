import Home from './Home.vue';
import Login from './Login.vue';
import User from './User.vue';
import Payment from './Payment.vue';
import Result from './Result.vue';

const routes = [
  { 
    path: '/', 
    component: Home,
    meta: { title: '八字命理AI人生指导' }
  },
  { 
    path: '/login', 
    component: Login,
    meta: { title: '用户登录' }
  },
  { 
    path: '/user', 
    component: User,
    meta: { title: '个人中心' }
  },
  { 
    path: '/payment', 
    component: Payment,
    meta: { title: '订单支付' }
  },
  { 
    path: '/result/:id', 
    component: Result,
    meta: { title: '分析结果' }
  }
];

export default routes; 