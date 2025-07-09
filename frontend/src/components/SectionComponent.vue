<template>
  <section :id="id" :class="[background, 'py-20 px-4 sm:px-6 lg:px-8']">
    <div class="max-w-7xl mx-auto">
      <h2 class="text-3xl md:text-4xl font-bold text-white mb-12 text-center">{{ title }}</h2>
      <slot></slot>
    </div>
  </section>
</template>

<script>
export default {
  props: {
    id: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    background: {
      type: String,
      default: 'bg-black'
    }
  }
};
</script>

<style scoped>
/* 可以在这里添加额外的样式 */
</style> 