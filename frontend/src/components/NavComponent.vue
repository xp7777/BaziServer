<template>
  <nav class="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-md border-b border-gray-800" h-20>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-20">
        <!-- Logo -->
        <div class="flex items-center space-x-6">
          <img src="../assets/logo.png" alt="捭阖学宫" class="h-10 w-auto" />
          <span class="text-xl font-bold text-white">捭阖学宫</span>
        </div>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-8">
          <button
            v-for="item in navItems"
            :key="item.id"
            @click="scrollToSection(item.id)"
            class="nav-link text-gray-300 hover:text-white px-3 py-2 text-sm font-medium transition-colors "
          >
            {{ item.label }}
          </button>
        </div>

        <!-- Mobile menu button -->
        <div class="md:hidden">
          <button
            @click="toggleMenu"
            style="color: #000000;"
            class="text-gray-300 hover:text-white p-2 "
          >
            <span v-if="isMenuOpen" class="block w-6 h-6">✕</span>
            <span v-else class="block w-6 h-6">☰</span>
          </button>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <div v-if="isMenuOpen" class="md:hidden">
        <div class="px-2 pt-2 pb-3 space-y-1 bg-black/90">
          <button
            v-for="item in navItems"
            :key="item.id"
            @click="scrollToSection(item.id)"
            style="color: #000000;"
            class="block w-full text-left px-3 py-2 text-gray-300 hover:text-white text-base font-medium transition-colors"
          >
            {{ item.label }}
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  data() {
    return {
      isMenuOpen: false,
      navItems: [
        { id: 'about', label: '关于我们' },
        { id: 'education', label: '国学教育' },
        { id: 'guidance', label: '人生指导' },
        { id: 'courses', label: '在线课程' },
        { id: 'contact', label: '联系我们' }
      ]
    };
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll);
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll);
  },
  methods: {
    scrollToSection(sectionId) {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
      this.isMenuOpen = false;
    },
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
    },
    handleScroll() {
      // 添加滚动时导航栏的效果变化
      const nav = document.querySelector('nav');
      if (window.scrollY > 100) {
        nav.classList.add('scrolled');
      } else {
        nav.classList.remove('scrolled');
      }
    }
  }
};
</script>

<style scoped>
.backdrop-blur-md {
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

nav {
  transition: all 0.3s ease;
}

nav.scrolled {
  background-color: rgba(0, 0, 0, 0.95);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.nav-link {
  position: relative;
  background-color: #000;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: #999999;
  transition: width 0.3s ease;
}

.nav-link:hover::after {
  width: 100%;
}
</style> 