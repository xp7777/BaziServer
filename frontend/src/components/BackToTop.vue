<template>
  <button 
    @click="scrollToTop" 
    class="fixed bottom-6 right-6 bg-gray-800 hover:bg-gray-700 text-white p-3 rounded-full shadow-lg transition-all duration-300 z-50"
    :class="{ 'opacity-0 pointer-events-none': !showButton, 'opacity-100': showButton }"
  >
    <svg xmlns="http://www.w3.org/2000/svg" style="color: #000000;" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
    </svg>
  </button>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';

export default {
  setup() {
    const showButton = ref(false);
    
    const checkScroll = () => {
      showButton.value = window.scrollY > 300;
    };
    
    const scrollToTop = () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    };
    
    onMounted(() => {
      window.addEventListener('scroll', checkScroll);
    });
    
    onUnmounted(() => {
      window.removeEventListener('scroll', checkScroll);
    });
    
    return {
      showButton,
      scrollToTop
    };
  }
};
</script>

<style scoped>
button {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

button:hover {
  transform: translateY(-3px);
}
</style> 