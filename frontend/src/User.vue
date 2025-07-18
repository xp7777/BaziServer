<template>
  <div class="user-container">
    <van-nav-bar title="个人中心" />
    
    <div class="user-info">
      <div class="avatar">
        <van-image
          round
          width="80"
          height="80"
          :src="userInfo.avatar || 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'"
        />
      </div>
      <div class="user-name">{{ userInfo.nickname || '未登录' }}</div>
      <div class="login-action" v-if="!isLoggedIn">
        <van-button type="primary" size="small" @click="goToLogin">登录/注册</van-button>
      </div>
    </div>
    
    <van-cell-group inset title="我的服务">
      <van-cell title="历史查询记录" is-link @click="goToHistory" />
      <van-cell title="我的订单" is-link @click="goToOrders" />
    </van-cell-group>
    
    <van-cell-group inset title="历史查询记录" v-if="isLoggedIn && historyList.length > 0">
      <van-cell
        v-for="item in historyList"
        :key="item.id"
        :title="item.date"
        :value="formatFocusAreas(item.focusAreas)"
        is-link
        @click="viewResult(item.id)"
      />
    </van-cell-group>
    
    <div class="empty-history" v-if="isLoggedIn && historyList.length === 0">
      <van-empty description="暂无查询记录" />
      <van-button type="primary" block @click="goToHome">立即测算</van-button>
    </div>
    
    <van-cell-group inset title="账号设置" v-if="isLoggedIn">
      <van-cell title="退出登录" @click="logout" />
    </van-cell-group>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Toast } from 'vant';

export default {
  name: 'UserPage',
  setup() {
    const router = useRouter();
    
    // 从 localStorage 获取用户信息
    const userInfo = ref({});
    
    const isLoggedIn = computed(() => {
      return !!userInfo.value.openid || !!localStorage.getItem('userToken');
    });
    
    // 获取用户信息
    const loadUserInfo = () => {
      const savedUserInfo = localStorage.getItem('userInfo');
      if (savedUserInfo) {
        try {
          userInfo.value = JSON.parse(savedUserInfo);
        } catch (error) {
          console.error('解析用户信息失败:', error);
          userInfo.value = {};
        }
      }
    };
    
    onMounted(() => {
      loadUserInfo();
    });
    
    // 模拟历史记录数据，实际项目中应该从API获取
    const historyList = ref([
      {
        id: 'RES1649823456',
        date: '2025-04-10',
        focusAreas: ['health', 'wealth', 'career']
      },
      {
        id: 'RES1649823789',
        date: '2025-03-25',
        focusAreas: ['relationship', 'children']
      }
    ]);
    
    const formatFocusAreas = (areas) => {
      const areaNames = {
        health: '健康',
        wealth: '财运',
        career: '事业',
        relationship: '感情',
        children: '子女'
      };
      
      return areas.map(area => areaNames[area] || area).join('、');
    };
    
    const goToLogin = () => {
      router.push('/login');
    };
    
    const goToHome = () => {
      router.push('/');
    };
    
    const goToHistory = () => {
      if (!isLoggedIn.value) {
        Toast('请先登录');
        goToLogin();
        return;
      }
      
      // 已经在历史记录页面，无需跳转
    };
    
    const goToOrders = () => {
      if (!isLoggedIn.value) {
        Toast('请先登录');
        goToLogin();
        return;
      }
      
      Toast('订单功能开发中');
    };
    
    const viewResult = (resultId) => {
      router.push(`/result/${resultId}`);
    };
    
    const logout = () => {
      // 清除本地存储
      localStorage.removeItem('userToken');
      localStorage.removeItem('userInfo');
      userInfo.value = {};
      Toast('退出成功');
      // 跳转到登录页面
      router.push('/login');
    };
    
    return {
      userInfo,
      isLoggedIn,
      historyList,
      formatFocusAreas,
      goToLogin,
      goToHome,
      goToHistory,
      goToOrders,
      viewResult,
      logout
    };
  }
};
</script>

<style scoped>
.user-container {
  padding-bottom: 20px;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
  background-color: #1989fa;
}

.avatar {
  margin-bottom: 10px;
}

.user-name {
  color: white;
  font-size: 18px;
  margin-bottom: 10px;
}

.login-action {
  margin-top: 10px;
}

.empty-history {
  padding: 20px 16px;
}
</style>
