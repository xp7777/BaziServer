import React from 'react';
import Navigation from './components/Navigation';
import HeroBanner from './components/HeroBanner';
import Section from './components/Section';
import AboutSection from './components/AboutSection';
import BackToTop from './components/BackToTop';
import { ScrollProgress, FadeInWhenVisible, StaggerContainer, StaggerItem } from './components/Animations';
import banner4 from './assets/banner4.png';
import './App.css';

function App() {
  return (
    <div className="min-h-screen bg-black text-white smooth-scroll">
      <ScrollProgress />
      <Navigation />
      <HeroBanner />
      
      <Section id="about" title="关于捭阖学宫" background="bg-gray-900">
        <AboutSection />
      </Section>
      
      <Section id="education" title="国学文化教育" background="bg-black">
        <StaggerContainer>
          <div className="grid lg:grid-cols-3 gap-8">
            <StaggerItem>
              <div className="card-hover bg-gray-800/50 p-8 rounded-lg border border-gray-700">
                <h3 className="text-xl font-semibold text-white mb-4">经典研读</h3>
                <p className="text-gray-300 mb-4">
                  深入学习《易经》《道德经》《鬼谷子》《孙子兵法》等国学经典，
                  领悟古圣先贤的智慧精髓。
                </p>
                <button className="text-gray-400 hover:text-white transition-colors">
                  了解更多 →
                </button>
              </div>
            </StaggerItem>
            
            <StaggerItem>
              <div className="card-hover bg-gray-800/50 p-8 rounded-lg border border-gray-700">
                <h3 className="text-xl font-semibold text-white mb-4">思维训练</h3>
                <p className="text-gray-300 mb-4">
                  融合现代思维训练方法，提升逻辑思维、战略思维和创新思维能力，
                  培养全面的智慧素养。
                </p>
                <button className="text-gray-400 hover:text-white transition-colors">
                  了解更多 →
                </button>
              </div>
            </StaggerItem>
            
            <StaggerItem>
              <div className="card-hover bg-gray-800/50 p-8 rounded-lg border border-gray-700">
                <h3 className="text-xl font-semibold text-white mb-4">领导力提升</h3>
                <p className="text-gray-300 mb-4">
                  结合鬼谷子纵横术和现代管理学，打造系统化的领导力培养体系，
                  助力个人成长。
                </p>
                <button className="text-gray-400 hover:text-white transition-colors">
                  了解更多 →
                </button>
              </div>
            </StaggerItem>
          </div>
        </StaggerContainer>
      </Section>
      
      <Section id="guidance" title="人生指导" background="bg-gray-900">
        <FadeInWhenVisible>
          <div className="text-center max-w-4xl mx-auto">
            <p className="text-lg text-gray-300 leading-relaxed mb-8">
              融合人工智能和传统文化天文历法、易经等传统智慧，
              提供人生方向规划与问题解决方案，让古老智慧为现代人生赋能。
            </p>
            <div className="bg-gray-800/50 p-8 rounded-lg border border-gray-700 mb-8">
              <h3 className="text-xl font-semibold text-white mb-4">进入专业服务</h3>
              <p className="text-gray-400 mb-6">
              个性化的人生指导服务，包括命理分析、风水咨询、 人生规划等专业内容！
              </p>
              <button className="bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded-lg transition-colors">
                点击进入
              </button>
            </div>
          </div>
        </FadeInWhenVisible>
      </Section>
      
      <Section id="courses" title="在线课程体系" background="bg-black">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <FadeInWhenVisible>
            <div>
              <p className="text-lg text-gray-300 leading-relaxed mb-8">
                从入门到进阶，每周末晚上上课、包括互动答疑、作业点评、智慧沙龙，
                打造"线上私塾"式沉浸体验，助你轻松学懂国学。
              </p>
              
              <StaggerContainer>
                <div className="space-y-6">
                  <StaggerItem>
                    <div className="card-hover bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                      <h3 className="text-white font-semibold mb-2">基础入门课程</h3>
                      <p className="text-gray-400 text-sm mb-3">
                        国学基础知识、经典导读、文化背景介绍
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-500 text-sm">12课时</span>
                        <button className="text-gray-400 hover:text-white transition-colors text-sm">
                          查看详情
                        </button>
                      </div>
                    </div>
                  </StaggerItem>
                  
                  <StaggerItem>
                    <div className="card-hover bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                      <h3 className="text-white font-semibold mb-2">进阶提升课程</h3>
                      <p className="text-gray-400 text-sm mb-3">
                        深度解析经典、实战应用、案例分析
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-500 text-sm">108课时</span>
                        <button className="text-gray-400 hover:text-white transition-colors text-sm">
                          查看详情
                        </button>
                      </div>
                    </div>
                  </StaggerItem>
                  
                  <StaggerItem>
                    <div className="card-hover bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                      <h3 className="text-white font-semibold mb-2">高级班课程</h3>
                      <p className="text-gray-400 text-sm mb-3">
                        一对一指导、根据个人资质和能力，分科进行深度研修
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-500 text-sm">360课时</span>
                        <button className="text-gray-400 hover:text-white transition-colors text-sm">
                          查看详情
                        </button>
                      </div>
                    </div>
                  </StaggerItem>
                </div>
              </StaggerContainer>
            </div>
          </FadeInWhenVisible>
          
          <FadeInWhenVisible delay={0.3}>
            <div className="relative">
              <img 
                src={banner4} 
                alt="山中讲学图" 
                className="w-full rounded-lg shadow-2xl"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent rounded-lg" />
            </div>
          </FadeInWhenVisible>
        </div>
      </Section>
      
      <Section id="contact" title="联系我们" background="bg-gray-900">
        <div className="grid lg:grid-cols-2 gap-12">
          <FadeInWhenVisible>
            <div>
              <h3 className="text-xl font-semibold text-white mb-6">联系方式</h3>
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <span className="text-gray-400">官方微信：</span>
                  <span className="text-white">guiguziwenhua</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-gray-400">客服邮箱：</span>
                  <span className="text-white">83309928@qq.com</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-gray-400">合作电话：</span>
                  <span className="text-white">400-666-8888</span>
                </div>
              </div>
            </div>
          </FadeInWhenVisible>
          
          <FadeInWhenVisible delay={0.3}>
            <div>
              <h3 className="text-xl font-semibold text-white mb-6">意见建议</h3>
              <form className="space-y-4">
                <input
                  type="text"
                  placeholder="您的姓名"
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-gray-500 transition-colors"
                />
                <input
                  type="email"
                  placeholder="您的邮箱"
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-gray-500 transition-colors"
                />
                <textarea
                  placeholder="您的问题或建议"
                  rows="4"
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-gray-500 transition-colors"
                ></textarea>
                <button
                  type="submit"
                  className="w-full bg-gray-700 hover:bg-gray-600 text-white py-3 rounded-lg transition-colors"
                >
                  发送消息
                </button>
              </form>
            </div>
          </FadeInWhenVisible>
        </div>
      </Section>
      
      <footer className="bg-black border-t border-gray-800 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-500">
            © 2025 捭阖学宫 | 传承智慧 · 启发未来
          </p>
        </div>
      </footer>
      
      <BackToTop />
    </div>
  );
}

export default App;

