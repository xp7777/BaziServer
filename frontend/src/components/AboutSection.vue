<template>
  <div class="grid lg:grid-cols-2 gap-12 items-center">
    <div>
      <p class="text-lg text-gray-300 leading-relaxed mb-8">
        捭阖学宫是一家专注于鬼谷子文化传播与教育的学术机构，
        致力于将古老智慧与现代生活相结合，为当代人提供系统化的国学教育与人生指导。
      </p>
      <p class="text-lg text-gray-300 leading-relaxed mb-8">
        我们的宗旨是"传承智慧，启发未来"，通过深入浅出的教学方式，
        帮助学员理解并运用鬼谷子的纵横捭阖之术，在现代社会中游刃有余。
      </p>
    </div>
    
    <div class="relative">
      <img 
        src="../assets/banner2.png" 
        alt="捭阖学宫" 
        class="w-full rounded-lg shadow-2xl"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent rounded-lg"></div>
    </div>
    
    <div class="lg:col-span-2 mt-8">
      <h3 class="text-2xl font-semibold text-white mb-8 text-center">我们的特色</h3>
      <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div v-for="(feature, index) in features" :key="index" class="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
          <h4 class="text-lg font-semibold text-white mb-3">{{ feature.title }}</h4>
          <p class="text-gray-400">{{ feature.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      features: [
        {
          title: '古今融合',
          description: '将传统智慧与现代科技相结合，创新教学方式'
        },
        {
          title: '系统教学',
          description: '从入门到精通，提供完整的学习体系与成长路径'
        },
        {
          title: '实战应用',
          description: '注重实际运用，解决现实生活中的实际问题'
        },
        {
          title: '个性化指导',
          description: '根据个人特点与需求，提供量身定制的学习计划'
        }
      ]
    };
  }
};
</script>

<style scoped>
/* 可以在这里添加额外的样式 */
</style> 