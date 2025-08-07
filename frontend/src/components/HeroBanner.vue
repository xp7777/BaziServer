<template>
  <section class="relative h-screen overflow-hidden">
    <!-- Preload critical images -->
    <link 
      v-for="(banner, index) in banners" 
      :key="`preload-${index}`"
      rel="preload" 
      :href="banner.webp" 
      as="image"
      v-if="index < 2"
    >
    
    <!-- Background Images with lazy loading -->
    <div 
      v-for="(banner, index) in banners" 
      :key="index"
      class="absolute inset-0 bg-cover bg-center transition-opacity duration-1500"
      :style="{ 
        backgroundImage: `url(${banner.webp}), url(${banner.fallback})`,
        opacity: index === currentBanner ? 1 : 0,
        transform: index === currentBanner ? 'scale(1)' : 'scale(1.1)',
        transition: 'opacity 1.5s ease, transform 10s ease'
      }"
    >
    </div>
    
    <!-- Overlay gradient -->
    <div class="absolute inset-0 bg-gradient-to-b from-black/30 via-black/50 to-black/70"></div>
    
    <!-- Content -->
    <div class="relative z-10 h-full flex items-center justify-center text-center">
      <div class="max-w-4xl mx-auto px-4">
        <transition name="fade" mode="out-in">
          <div :key="currentBanner" class="animate-fadeIn">
            <h1 
              class="hero-title text-5xl md:text-7xl font-bold text-white mb-6 animate-slideInDown"
              style="text-shadow: 0 2px 4px rgba(0,0,0,0.5)"
            >
              {{ banners[currentBanner].title }}
            </h1>
            <p 
              class="text-xl md:text-2xl text-gray-200 mb-8 animate-slideInUp"
              style="text-shadow: 0 1px 2px rgba(0,0,0,0.5)"
            >
              {{ banners[currentBanner].subtitle }}
            </p>
            <button
              @click="scrollToAbout"
              class="button-cls bg-gray-800/80 hover:bg-gray-700/80 text-white px-8 py-3 rounded-lg text-lg font-medium transition-all duration-300 backdrop-blur-sm border border-gray-600 animate-fadeIn hover:scale-105"
            >
              探索智慧之门
            </button>
          </div>
        </transition>
      </div>
    </div>
    
    <!-- Loading indicator -->
    <div 
      v-if="!allImagesLoaded"
      class="absolute inset-0 flex items-center justify-center bg-black/50 z-20"
    >
      <div class="text-white text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p>正在加载...</p>
      </div>
    </div>
    
    <!-- Banner Indicators -->
    <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex space-x-3 z-50">
      <button
        v-for="(banner, index) in banners"
        :key="index"
        @click.stop="setCurrentBanner(index)"
        class="w-3 h-3 rounded-full transition-all duration-300 cursor-pointer hover:scale-125"
        :class="index === currentBanner ? 'bg-white scale-125' : 'bg-white/50 hover:bg-white/75'"
        :aria-label="`切换到幻灯片 ${index + 1}`"
      >
      </button>
    </div>
    
    <!-- Progress bar -->
    <div class="absolute bottom-0 left-0 w-full h-1 bg-black/20 z-50">
      <div 
        class="h-full bg-white/80 transition-all duration-5000 ease-linear"
        :style="{ width: `${((currentBanner + 1) / banners.length) * 100}%` }"
      ></div>
    </div>
  </section>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue';

// 优化的图片导入
import banner1Webp from '../assets/optimized/banner1.webp';
import banner1Jpg from '../assets/optimized/banner1.jpeg';
import banner1Fallback from '../assets/banner1.png';

import banner2Webp from '../assets/optimized/banner2.webp';
import banner2Jpg from '../assets/optimized/banner2.jpeg';
import banner2Fallback from '../assets/banner2.png';

import banner3Webp from '../assets/optimized/banner3.webp';
import banner3Jpg from '../assets/optimized/banner3.jpeg';
import banner3Fallback from '../assets/banner3.png';

import banner4Webp from '../assets/optimized/banner4.webp';
import banner4Jpg from '../assets/optimized/banner4.jpeg';
import banner4Fallback from '../assets/banner4.png';

// 占位符图片（极小尺寸）- 移除这些不存在的引用
// import banner1Placeholder from '../assets/optimized/banner1-placeholder.jpg';
// import banner2Placeholder from '../assets/optimized/banner2-placeholder.jpg';
// import banner3Placeholder from '../assets/optimized/banner3-placeholder.jpg';
// import banner4Placeholder from '../assets/optimized/banner4-placeholder.jpg';

export default {
  setup() {
    const currentBanner = ref(0);
    const loadedImages = ref([false, false, false, false]);
    let timer = null;
    let preloadTimer = null;

    const banners = [
      { 
        webp: banner1Webp, 
        jpg: banner1Jpg,
        fallback: banner1Fallback,
        // placeholder: banner1Placeholder, 移除
        title: '鬼谷文化', 
        subtitle: '纵横捭阖，古今通达' 
      },
      { 
        webp: banner2Webp, 
        jpg: banner2Jpg,
        fallback: banner2Fallback,
        // placeholder: banner2Placeholder, 移除
        title: '法天象地', 
        subtitle: '国学指引，人生赋能' 
      },
      { 
        webp: banner3Webp, 
        jpg: banner3Jpg,
        fallback: banner3Fallback,
        // placeholder: banner3Placeholder, 移除
        title: '国学传承', 
        subtitle: '强者风范，生生不息' 
      },
      { 
        webp: banner4Webp, 
        jpg: banner4Jpg,
        fallback: banner4Fallback,
        // placeholder: banner4Placeholder, 移除
        title: '道家智慧', 
        subtitle: '天人合一，道法自然' 
      }
    ];

    const allImagesLoaded = computed(() => 
      loadedImages.value.every(loaded => loaded)
    );

    const setCurrentBanner = (index) => {
      currentBanner.value = index;
      resetTimer();
    };

    const scrollToAbout = () => {
      document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' });
    };

    const preloadImage = (src) => {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = resolve;
        img.onerror = reject;
        img.src = src;
      });
    };

    const loadImages = async () => {
      console.log('开始预加载图片...');
      
      const loadPromises = banners.map(async (banner, index) => {
        try {
          // 优先加载WebP格式
          await preloadImage(banner.webp);
          loadedImages.value[index] = true;
          console.log(`图片 ${index + 1} 加载完成`);
        } catch (error) {
          console.warn(`WebP加载失败，使用回退格式: ${error}`);
          try {
            await preloadImage(banner.jpg);
            loadedImages.value[index] = true;
          } catch (fallbackError) {
            console.warn(`JPG加载失败，使用原始PNG: ${fallbackError}`);
            await preloadImage(banner.fallback);
            loadedImages.value[index] = true;
          }
        }
      });

      await Promise.all(loadPromises);
      console.log('所有图片加载完成');
    };

    const resetTimer = () => {
      if (timer) clearInterval(timer);
      timer = setInterval(() => {
        currentBanner.value = (currentBanner.value + 1) % banners.length;
      }, 5000);
    };

    // 智能预加载策略
    const smartPreload = () => {
      // 预加载当前和下一张图片
      const nextIndex = (currentBanner.value + 1) % banners.length;
      
      [currentBanner.value, nextIndex].forEach(index => {
        if (!loadedImages.value[index]) {
          preloadImage(banners[index].webp).catch(() => {
            preloadImage(banners[index].jpg);
          });
        }
      });
    };

    onMounted(async () => {
      console.log('HeroBanner组件挂载');
      
      // 开始加载图片
      await loadImages();
      
      // 启动轮播
      resetTimer();
      
      // 智能预加载
      preloadTimer = setInterval(smartPreload, 2000);
      
      // 监听页面可见性变化
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
          if (timer) clearInterval(timer);
        } else {
          resetTimer();
        }
      });
    });

    onUnmounted(() => {
      if (timer) clearInterval(timer);
      if (preloadTimer) clearInterval(preloadTimer);
    });

    return {
      currentBanner,
      banners,
      loadedImages,
      allImagesLoaded,
      setCurrentBanner,
      scrollToAbout
    };
  }
};
</script>

<style scoped>
/* 优化动画 */
.animate-fadeIn {
  animation: fadeIn 0.6s ease-out;
}

.animate-slideInDown {
  animation: slideInDown 0.8s ease-out;
}

.animate-slideInUp {
  animation: slideInUp 0.8s ease-out 0.2s both;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 背景图片缩放动画 */
.bg-cover {
  will-change: transform;
}

/* 加载动画 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .text-xl {
    font-size: 1.125rem;
  }
}

/* 性能优化 */
.bg-cover {
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
}
</style>