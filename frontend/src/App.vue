<template>
  <div class="app-container">
    <router-view />
    <van-tabbar v-model="active" route v-if="showTabbar">
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/user">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';

const active = ref(0);
const route = useRoute();

// 在首页不显示底部导航栏
const showTabbar = computed(() => {
  return route.path !== '/';
});
</script>

<style>
.app-container {
  min-height: 100vh;
}

/* 在非首页时添加底部填充 */
.app-container:not(.home-page) {
  padding-bottom: 50px;
}

/* 全局样式 */
html, body {
  margin: 0;
  padding: 0;
}

/* 添加Tailwind类似的工具类 */
.bg-black {
  background-color: #000;
}

.bg-gray-900 {
  background-color: #111827;
}

.bg-gray-800\/50 {
  background-color: rgba(31, 41, 55, 0.5);
}

.text-white {
  color: #fff;
}

.text-gray-300 {
  color: #d1d5db;
}

.text-gray-400 {
  color: #9ca3af;
}

.text-gray-500 {
  color: #6b7280;
}

.border-gray-700 {
  border-color: #374151;
}

.border-gray-800 {
  border-color: #1f2937;
}

/* 响应式网格 */
@media (min-width: 1024px) {
  .lg\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
  
  .lg\:col-span-2 {
    grid-column: span 2 / span 2;
  }
}

@media (min-width: 768px) {
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .md\:text-4xl {
    font-size: 2.25rem;
    line-height: 2.5rem;
  }
  
  .md\:hidden {
    display: none;
  }
  
  .md\:flex {
    display: flex;
  }
}
</style>
