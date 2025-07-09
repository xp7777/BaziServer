<template>
  <section :id="id" :class="[background, 'py-20 px-4 sm:px-6 lg:px-8']">
    <div class="max-w-7xl mx-auto">
      <h2 class="text-3xl md:text-4xl font-bold text-white mb-12 text-center reveal">{{ title }}</h2>
      <div class="reveal">
        <slot></slot>
      </div>
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
  },
  mounted() {
    // 确保该组件被观察到
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
        }
      });
    }, { threshold: 0.1 });
    
    const revealElements = this.$el.querySelectorAll('.reveal');
    revealElements.forEach(el => {
      observer.observe(el);
    });
  }
};
</script>

<style scoped>
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: all 1s ease;
}

.reveal.active {
  opacity: 1;
  transform: translateY(0);
}
</style> 