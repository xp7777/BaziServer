<template>
  <div class="app-container">
    <router-view />
    <van-tabbar v-model="active" route>
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/user">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  name: 'App',
  setup() {
    const active = ref(0);
    return { active };
  }
};
</script>

<style>
.app-container {
  min-height: 100vh;
  padding-bottom: 50px;
}
</style>
