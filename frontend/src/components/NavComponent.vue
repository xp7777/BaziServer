<template>
  <nav class="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-md border-b border-gray-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <div class="flex items-center space-x-3">
          <img src="../assets/logo.png" alt="捭阖学宫" class="h-10 w-auto" />
          <span class="text-xl font-bold text-white">捭阖学宫</span>
        </div>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-8">
          <button
            v-for="item in navItems"
            :key="item.id"
            @click="scrollToSection(item.id)"
            class="nav-link text-gray-300 hover:text-white px-3 py-2 text-sm font-medium transition-colors"
          >
            {{ item.label }}
          </button>
        </div>

        <!-- Mobile menu button -->
        <div class="md:hidden">
          <button
            @click="toggleMenu"
            class="text-gray-300 hover:text-white p-2"
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
    }
  }
};
</script>

<style scoped>
.backdrop-blur-md {
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
</style> 