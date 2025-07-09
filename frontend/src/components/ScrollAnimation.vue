<template>
  <div class="scroll-progress" :style="{ width: scrollWidth }"></div>
</template>

<script>
export default {
  data() {
    return {
      scrollWidth: '0%'
    };
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll);
    this.setupRevealOnScroll();
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll);
  },
  methods: {
    handleScroll() {
      // 计算滚动进度
      const scrollTop = window.scrollY;
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercentage = (scrollTop / scrollHeight) * 100;
      this.scrollWidth = `${scrollPercentage}%`;
      
      // 触发滚动动画
      this.checkRevealElements();
    },
    setupRevealOnScroll() {
      // 给所有需要动画的元素添加reveal类
      const sections = document.querySelectorAll('section');
      sections.forEach(section => {
        const elements = section.querySelectorAll('h2, h3, p, .card-hover, img, form');
        elements.forEach(el => {
          if (!el.classList.contains('reveal')) {
            el.classList.add('reveal');
          }
        });
      });
      
      // 初始检查一次
      this.checkRevealElements();
    },
    checkRevealElements() {
      const reveals = document.querySelectorAll('.reveal');
      
      reveals.forEach(element => {
        const windowHeight = window.innerHeight;
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150; // 元素露出多少像素时触发动画
        
        if (elementTop < windowHeight - elementVisible) {
          element.classList.add('active');
        } else {
          element.classList.remove('active');
        }
      });
    }
  }
};
</script>

<style scoped>
.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(to right, #4f46e5, #8b5cf6);
  z-index: 100;
  transition: width 0.1s ease;
}
</style> 