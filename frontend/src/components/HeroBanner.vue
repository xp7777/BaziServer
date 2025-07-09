<template>
  <section class="relative h-screen overflow-hidden">
    <!-- Background Images -->
    <div 
      v-for="(banner, index) in banners" 
      :key="index"
      class="absolute inset-0 bg-cover bg-center transition-opacity duration-1500"
      :style="{ 
        backgroundImage: `url(${banner.image})`,
        opacity: index === currentBanner ? 1 : 0
      }"
    ></div>
    
    <!-- Overlay -->
    <div class="absolute inset-0 bg-black/50"></div>
    
    <!-- Content -->
    <div class="relative z-10 h-full flex items-center justify-center text-center">
      <div class="max-w-4xl mx-auto px-4">
        <transition name="fade" mode="out-in">
          <div :key="currentBanner">
            <h1 class="hero-title text-5xl md:text-7xl font-bold text-white mb-6">
              {{ banners[currentBanner].title }}
            </h1>
            <p class="text-xl md:text-2xl text-gray-300 mb-8">
              {{ banners[currentBanner].subtitle }}
            </p>
            <button
              @click="scrollToAbout"
              class="bg-gray-800/80 hover:bg-gray-700/80 text-white px-8 py-3 rounded-lg text-lg font-medium transition-all duration-300 backdrop-blur-sm border border-gray-600"
            >
              探索智慧之门
            </button>
          </div>
        </transition>
      </div>
    </div>
    
    <!-- Banner Indicators -->
    <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex space-x-2">
      <button
        v-for="(_, index) in banners"
        :key="index"
        @click="setCurrentBanner(index)"
        class="w-3 h-3 rounded-full transition-all duration-300"
        :class="index === currentBanner ? 'bg-white' : 'bg-white/50'"
      ></button>
    </div>
  </section>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import banner1 from '../assets/banner1.png';
import banner2 from '../assets/banner2.png';
import banner3 from '../assets/banner3.png';
import banner4 from '../assets/banner4.png';

export default {
  setup() {
    const currentBanner = ref(0);
    let timer = null;
    
    const banners = [
      { image: banner1, title: '鬼谷文化', subtitle: '纵横捭阖，古今通达' },
      { image: banner2, title: '法天象地', subtitle: '国学指引，人生赋能' },
      { image: banner3, title: '国学传承', subtitle: '强者风范，生生不息' },
      { image: banner4, title: '道家智慧', subtitle: '天人合一，道法自然' }
    ];
    
    const setCurrentBanner = (index) => {
      currentBanner.value = index;
    };
    
    const scrollToAbout = () => {
      document.getElementById('about').scrollIntoView({ behavior: 'smooth' });
    };
    
    onMounted(() => {
      timer = setInterval(() => {
        currentBanner.value = (currentBanner.value + 1) % banners.length;
      }, 5000);
    });
    
    onUnmounted(() => {
      clearInterval(timer);
    });
    
    return {
      currentBanner,
      banners,
      setCurrentBanner,
      scrollToAbout
    };
  }
};
</script>

<style scoped>
.transition-opacity {
  transition: opacity 1.5s ease;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 1s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.backdrop-blur-sm {
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
</style> 