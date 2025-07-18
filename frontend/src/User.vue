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
      <van-cell title="历史查询记录" is-link @click="toggleHistoryList" />
      <van-cell title="我的订单" is-link @click="toggleOrderList" />
    </van-cell-group>
    
    <!-- 历史查询记录 -->
    <van-cell-group inset title="历史查询记录" v-if="isLoggedIn && showHistoryList">
      <van-loading v-if="loading" type="spinner" vertical>加载中...</van-loading>
      
      <template v-else>
        <van-cell
          v-for="item in historyList"
          :key="item.id"
          :title="`${item.date} ${item.gender === 'male' ? '男' : '女'}`"
          :value="formatFocusAreas(item.focusAreas)"
          is-link
          @click="viewResult(item.id)"
        >
          <template #label>
            <span>{{ item.birthDate || '未知出生日期' }}</span>
          </template>
        </van-cell>
        
        <div class="empty-history" v-if="historyList.length === 0">
          <van-empty description="暂无查询记录" />
          <van-button type="primary" block @click="goToHome">立即测算</van-button>
        </div>
      </template>
    </van-cell-group>
    
    <!-- 我的订单 -->
    <van-cell-group inset title="我的订单" v-if="isLoggedIn && showOrderList">
      <van-loading v-if="loading" type="spinner" vertical>加载中...</van-loading>
      
      <template v-else>
        <van-cell
          v-for="order in orderList"
          :key="order.id"
          :title="`${order.date} ${order.orderType}`"
          :value="`¥${order.amount}`"
          is-link
          @click="viewOrder(order.id, order.resultId)"
        >
          <template #label>
            <span>{{ order.status }} · {{ order.payTime }}</span>
          </template>
        </van-cell>
        
        <div class="empty-history" v-if="orderList.length === 0">
          <van-empty description="暂无订单记录" />
          <van-button type="primary" block @click="goToHome">立即测算</van-button>
        </div>
      </template>
    </van-cell-group>
    
    <van-cell-group inset title="账号设置" v-if="isLoggedIn">
      <van-cell title="退出登录" @click="logout" />
    </van-cell-group>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Toast } from 'vant';
import axios from 'axios';

export default {
  name: 'UserPage',
  setup() {
    const router = useRouter();
    
    // 从 localStorage 获取用户信息
    const userInfo = ref({});
    
    // 历史记录和订单数据
    const historyList = ref([]);
    const orderList = ref([]);
    const loading = ref(false);
    
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
    
    // 获取历史记录
    const loadHistoryRecords = async () => {
      if (!isLoggedIn.value) return;
      
      loading.value = true;
      try {
        const token = localStorage.getItem('userToken');
        const response = await axios.get('/api/bazi/history', {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (response.data.code === 200) {
          historyList.value = response.data.data.map(item => ({
            id: item.resultId,
            date: formatDate(item.createdAt),
            focusAreas: item.focusAreas || [],
            gender: item.gender || '',
            birthDate: item.birthDate || ''
          }));
          console.log('历史记录加载成功:', historyList.value);
        } else {
          console.error('获取历史记录失败:', response.data.message);
        }
      } catch (error) {
        console.error('获取历史记录出错:', error);
      } finally {
        loading.value = false;
      }
    };
    
    // 获取订单列表
    const loadOrders = async () => {
      if (!isLoggedIn.value) return;
      
      loading.value = true;
      try {
        const token = localStorage.getItem('userToken');
        const response = await axios.get('/api/order/my', {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (response.data.code === 200) {
          orderList.value = response.data.data.map(order => ({
            id: order._id,
            resultId: order.resultId,
            date: formatDate(order.createdAt),
            amount: (order.amount || 0).toFixed(2),
            status: formatOrderStatus(order.status),
            orderType: formatOrderType(order.orderType),
            payTime: order.payTime ? formatDate(order.payTime) : '未支付'
          }));
          console.log('订单列表加载成功:', orderList.value);
        } else {
          console.error('获取订单列表失败:', response.data.message);
        }
      } catch (error) {
        console.error('获取订单列表出错:', error);
      } finally {
        loading.value = false;
      }
    };
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '未知日期';
      
      try {
        let date;
        
        // 如果是 MongoDB 的日期对象格式
        if (typeof dateString === 'object' && dateString.$date) {
          date = new Date(dateString.$date);
        } else {
          date = new Date(dateString);
        }
        
        // 检查日期是否有效
        if (isNaN(date.getTime())) {
          console.warn('无效日期:', dateString);
          return '未知日期';
        }
        
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      } catch (e) {
        console.error('日期格式化错误:', e, dateString);
        return '未知日期';
      }
    };
    
    // 格式化订单状态
    const formatOrderStatus = (status) => {
      const statusMap = {
        'pending': '待支付',
        'paid': '已支付',
        'completed': '已完成',
        'cancelled': '已取消'
      };
      return statusMap[status] || status;
    };
    
    // 格式化订单类型
    const formatOrderType = (type) => {
      const typeMap = {
        'analysis': '八字分析',
        'followup': '深度追问',
        'yearly': '年运分析'
      };
      return typeMap[type] || type;
    };
    
    const formatFocusAreas = (areas) => {
      if (!areas || !Array.isArray(areas)) return '';
      
      const areaNames = {
        'health': '健康',
        'wealth': '财运',
        'career': '事业',
        'relationship': '感情',
        'children': '子女',
        'personality': '性格',
        'yearly': '年运'
      };
      
      return areas.map(area => areaNames[area] || area).join('、');
    };
    
    onMounted(() => {
      loadUserInfo();
      if (isLoggedIn.value) {
        loadHistoryRecords();
        loadOrders();
      }
    });
    
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
      
      // 显示订单列表
      showOrderList.value = true;
      showHistoryList.value = false;
    };
    
    const viewResult = (resultId) => {
      router.push(`/result/${resultId}`);
    };
    
    const viewOrder = (orderId, resultId) => {
      if (resultId) {
        // 如果有结果ID，跳转到结果页面
        router.push(`/result/${resultId}`);
      } else {
        // 否则跳转到订单详情页面
        Toast('订单详情功能开发中');
      }
    };
    
    const logout = () => {
      // 清除本地存储
      localStorage.removeItem('userToken');
      localStorage.removeItem('userInfo');
      userInfo.value = {};
      historyList.value = [];
      orderList.value = [];
      Toast('退出成功');
      // 跳转到登录页面
      router.push('/login');
    };
    
    // 控制显示哪个列表
    const showHistoryList = ref(true);
    const showOrderList = ref(false);
    
    const toggleHistoryList = () => {
      showHistoryList.value = true;
      showOrderList.value = false;
    };
    
    const toggleOrderList = () => {
      showHistoryList.value = false;
      showOrderList.value = true;
    };
    
    return {
      userInfo,
      isLoggedIn,
      historyList,
      orderList,
      loading,
      showHistoryList,
      showOrderList,
      formatFocusAreas,
      goToLogin,
      goToHome,
      goToHistory,
      goToOrders,
      viewResult,
      viewOrder,
      logout,
      toggleHistoryList,
      toggleOrderList
    };
  }
};
</script>

<style scoped>
.user-container {
  padding-bottom: 20px;
  min-height: 100vh;
  background-color: #f7f8fa;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
  background-color: #1989fa;
  margin-bottom: 12px;
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

.van-loading {
  padding: 20px 0;
  display: flex;
  justify-content: center;
}
</style>
