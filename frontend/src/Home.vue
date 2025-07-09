<template>
  <div class="min-h-screen bg-black text-white smooth-scroll">
    <div class="scroll-progress"></div>
    <nav-component></nav-component>
    <hero-banner></hero-banner>
    
    <section-component id="about" title="关于捭阖学宫" background="bg-gray-900">
      <about-section></about-section>
    </section-component>
    
    <section-component id="education" title="国学文化教育" background="bg-black">
      <div class="grid lg:grid-cols-3 gap-8">
        <div class="card-hover bg-gray-800/50 p-8 rounded-lg border border-gray-700" v-for="(item, index) in educationItems" :key="index">
          <h3 class="text-xl font-semibold text-white mb-4">{{ item.title }}</h3>
          <p class="text-gray-300 mb-4">
            {{ item.description }}
          </p>
          <button class="text-gray-400 hover:text-white transition-colors">
            了解更多 →
          </button>
        </div>
      </div>
    </section-component>
    
    <section-component id="guidance" title="人生指导" background="bg-gray-900">
      <div class="text-center max-w-4xl mx-auto">
        <p class="text-lg text-gray-300 leading-relaxed mb-8">
          融合人工智能和传统文化天文历法、易经等传统智慧，
          提供人生方向规划与问题解决方案，让古老智慧为现代人生赋能。
        </p>
        <div class="bg-gray-800/50 p-8 rounded-lg border border-gray-700 mb-8">
          <h3 class="text-xl font-semibold text-white mb-4">进入专业服务</h3>
          <p class="text-gray-400 mb-6">
            涵盖人生事业生活各方面，包括个人居住环境、穿衣打扮等的全面指导！
          </p>
          <button class="bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded-lg transition-colors" @click="goToBaziService">
            点击进入
          </button>
        </div>
      </div>
    </section-component>
    
    <section-component id="courses" title="在线课程体系" background="bg-black">
      <div class="grid lg:grid-cols-2 gap-12 items-center">
        <div>
          <p class="text-lg text-gray-300 leading-relaxed mb-8">
            从入门到进阶，每周末晚上上课、包括互动答疑、作业点评、智慧沙龙，
            打造"线上私塾"式沉浸体验，助你轻松学懂国学。
          </p>
          
          <div class="space-y-6">
            <div v-for="(course, index) in courses" :key="index" class="card-hover bg-gray-800/50 p-6 rounded-lg border border-gray-700">
              <h3 class="text-white font-semibold mb-2">{{ course.title }}</h3>
              <p class="text-gray-400 text-sm mb-3">
                {{ course.description }}
              </p>
              <div class="flex items-center justify-between">
                <span class="text-gray-500 text-sm">{{ course.duration }}</span>
                <button class="text-gray-400 hover:text-white transition-colors text-sm">
                  查看详情
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="relative">
          <img 
            src="./assets/banner4.png" 
            alt="山中讲学图" 
            class="w-full rounded-lg shadow-2xl"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent rounded-lg"></div>
        </div>
      </div>
    </section-component>
    
    <section-component id="contact" title="联系我们" background="bg-gray-900">
      <div class="grid lg:grid-cols-2 gap-12">
        <div>
          <h3 class="text-xl font-semibold text-white mb-6">联系方式</h3>
          <div class="space-y-4">
            <div class="flex items-center space-x-3">
              <span class="text-gray-400">官方微信：</span>
              <span class="text-white">guiguziwenhua</span>
            </div>
            <div class="flex items-center space-x-3">
              <span class="text-gray-400">客服邮箱：</span>
              <span class="text-white">83309928@qq.com</span>
            </div>
            <div class="flex items-center space-x-3">
              <span class="text-gray-400">合作电话：</span>
              <span class="text-white">400-666-8888</span>
            </div>
          </div>
        </div>
        
        <div>
          <h3 class="text-xl font-semibold text-white mb-6">意见建议</h3>
          <form class="space-y-4" @submit.prevent="submitForm">
            <input
              type="text"
              v-model="contactForm.name"
              placeholder="您的姓名"
              class="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-gray-500 transition-colors"
            />
            <input
              type="email"
              v-model="contactForm.email"
              placeholder="您的邮箱"
              class="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-gray-500 transition-colors"
            />
            <textarea
              v-model="contactForm.message"
              placeholder="您的问题或建议"
              rows="4"
              class="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-gray-500 transition-colors"
            ></textarea>
            <button
              type="submit"
              class="w-full bg-gray-700 hover:bg-gray-600 text-white py-3 rounded-lg transition-colors"
            >
              发送消息
            </button>
          </form>
        </div>
      </div>
    </section-component>
    
    <footer class="bg-black border-t border-gray-800 py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <p class="text-gray-500">
          © 2025 捭阖学宫 | 传承智慧 · 启发未来
        </p>
      </div>
    </footer>
    
    <back-to-top></back-to-top>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import NavComponent from './components/NavComponent.vue';
import HeroBanner from './components/HeroBanner.vue';
import SectionComponent from './components/SectionComponent.vue';
import AboutSection from './components/AboutSection.vue';
import BackToTop from './components/BackToTop.vue';

export default {
  components: {
    NavComponent,
    HeroBanner,
    SectionComponent,
    AboutSection,
    BackToTop
  },
  setup() {
    const router = useRouter();
    
    const educationItems = [
      {
        title: '经典研读',
        description: '深入学习《易经》《道德经》《鬼谷子》《孙子兵法》等国学经典，领悟古圣先贤的智慧精髓。'
      },
      {
        title: '思维训练',
        description: '融合现代思维训练方法，提升逻辑思维、战略思维和创新思维能力，培养全面的智慧素养。'
      },
      {
        title: '领导力提升',
        description: '结合鬼谷子纵横术和现代管理学，打造系统化的领导力培养体系，助力个人成长。'
      }
    ];
    
    const courses = [
      {
        title: '基础入门课程',
        description: '国学基础知识、经典导读、文化背景介绍',
        duration: '12课时'
      },
      {
        title: '进阶提升课程',
        description: '深度解析经典、实战应用、案例分析',
        duration: '108课时'
      },
      {
        title: '高级班课程',
        description: '一对一指导、根据个人资质和能力，分科进行深度研修',
        duration: '360课时'
      }
    ];
    
    const contactForm = reactive({
      name: '',
      email: '',
      message: ''
    });
    
    const submitForm = () => {
      // 表单提交逻辑
      console.log('提交表单:', contactForm);
      // 清空表单
      contactForm.name = '';
      contactForm.email = '';
      contactForm.message = '';
    };
    
    const goToBaziService = () => {
      // 导航到八字命理服务页面
      router.push('/bazi-service');
    };
    
    return {
      educationItems,
      courses,
      contactForm,
      submitForm,
      goToBaziService
    };
  }
};
</script>

<style>
.smooth-scroll {
  scroll-behavior: smooth;
}

.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(to right, #4f46e5, #8b5cf6);
  z-index: 100;
  width: var(--scroll-width, 0%);
}

.card-hover {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
}
</style>
