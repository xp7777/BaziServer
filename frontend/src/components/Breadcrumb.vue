<template>
  <div class="breadcrumb">
    <template v-for="(item, index) in items" :key="index">
      <router-link 
        v-if="item.to" 
        :to="item.to" 
        class="breadcrumb-item"
      >
        <van-icon v-if="item.icon" :name="item.icon" size="14" />
        {{ item.text }}
      </router-link>
      <span v-else class="breadcrumb-item current">
        <van-icon v-if="item.icon" :name="item.icon" size="14" />
        {{ item.text }}
      </span>
      <van-icon 
        v-if="index < items.length - 1" 
        name="arrow" 
        class="breadcrumb-arrow" 
      />
    </template>
  </div>
</template>

<script>
export default {
  name: 'Breadcrumb',
  props: {
    items: {
      type: Array,
      required: true
    }
  }
};
</script>

<style scoped>
.breadcrumb {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #f7f8fa;
  font-size: 13px;
  overflow-x: auto;
  white-space: nowrap;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #1989fa;
  text-decoration: none;
  flex-shrink: 0;
}

.breadcrumb-item.current {
  color: #323233;
  font-weight: 500;
}

.breadcrumb-arrow {
  margin: 0 8px;
  color: #c8c9cc;
  font-size: 12px;
  flex-shrink: 0;
}
</style>