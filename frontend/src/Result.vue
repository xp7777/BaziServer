<template>
  <div class="result-container">
    <van-nav-bar
      title="八字分析结果"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
    />
    
    <div class="result-header">
      <h2>您的八字命盘分析</h2>
      <p>基于您的出生信息，AI为您提供的个性化人生指导</p>
    </div>
    
    <van-tabs v-model="activeTab" sticky>
      <van-tab title="命盘信息">
        <div class="bazi-chart">
          <h3>八字命盘</h3>
          <van-grid :column-num="4" :border="false">
            <van-grid-item>
              <template #default>
                <div class="pillar">
                  <div class="stem">{{ baziData.yearPillar.heavenlyStem }}</div>
                  <div class="branch">{{ baziData.yearPillar.earthlyBranch }}</div>
                  <div class="label">年柱</div>
                </div>
              </template>
            </van-grid-item>
            <van-grid-item>
              <template #default>
                <div class="pillar">
                  <div class="stem">{{ baziData.monthPillar.heavenlyStem }}</div>
                  <div class="branch">{{ baziData.monthPillar.earthlyBranch }}</div>
                  <div class="label">月柱</div>
                </div>
              </template>
            </van-grid-item>
            <van-grid-item>
              <template #default>
                <div class="pillar">
                  <div class="stem">{{ baziData.dayPillar.heavenlyStem }}</div>
                  <div class="branch">{{ baziData.dayPillar.earthlyBranch }}</div>
                  <div class="label">日柱</div>
                </div>
              </template>
            </van-grid-item>
            <van-grid-item>
              <template #default>
                <div class="pillar">
                  <div class="stem">{{ baziData.hourPillar.heavenlyStem }}</div>
                  <div class="branch">{{ baziData.hourPillar.earthlyBranch }}</div>
                  <div class="label">时柱</div>
                </div>
              </template>
            </van-grid-item>
          </van-grid>
          
          <h3>五行分布</h3>
          <div class="five-elements">
            <div class="element" v-for="(value, element) in baziData.fiveElements" :key="element">
              <div class="element-name">{{ getElementName(element) }}</div>
              <div class="element-value">{{ value }}</div>
            </div>
          </div>
          
          <h3>大运流年</h3>
          <div class="flowing-years">
            <van-steps direction="horizontal" :active="2">
              <van-step v-for="(year, index) in baziData.flowingYears.slice(0, 5)" :key="index">
                {{ year.year }}年<br>
                {{ year.heavenlyStem }}{{ year.earthlyBranch }}
              </van-step>
            </van-steps>
          </div>
        </div>
      </van-tab>
      
      <van-tab title="AI分析结果">
        <div class="ai-analysis">
          <div v-if="userAge < 0" class="age-notice">
            <van-notice-bar
              color="#1989fa"
              background="#ecf9ff"
              left-icon="info-o"
            >
              此分析针对未来出生的宝宝，重点关注性格特点、天赋才能和健康发展趋势。
            </van-notice-bar>
          </div>
          <div v-else-if="userAge < 6" class="age-notice">
            <van-notice-bar
              color="#1989fa"
              background="#ecf9ff"
              left-icon="info-o"
            >
              此分析针对婴幼儿({{userAge}}岁)，重点关注性格特点、天赋才能和健康发展趋势。
            </van-notice-bar>
          </div>
          <div v-else-if="userAge < 18" class="age-notice">
            <van-notice-bar
              color="#1989fa"
              background="#ecf9ff"
              left-icon="info-o"
            >
              此分析针对未成年人({{userAge}}岁)，重点关注性格特点、学业发展和健康状况。
            </van-notice-bar>
          </div>
          
          <div class="analysis-section">
            <h3>身体健康</h3>
            <p>{{ aiAnalysis.health }}</p>
          </div>
          
          <div v-if="userAge < 18 && userAge >= 0" class="analysis-section">
            <h3>学业发展</h3>
            <p>{{ getAnalysisContent('学业发展') }}</p>
          </div>
          
          <div class="analysis-section">
            <h3>性格特点</h3>
            <p>{{ getAnalysisContent('性格特点') }}</p>
          </div>
          
          <div v-if="userAge >= 18 && focusAreas.includes('wealth')" class="analysis-section">
            <h3>财运分析</h3>
            <p>{{ aiAnalysis.wealth }}</p>
          </div>
          
          <div v-if="userAge >= 18 && focusAreas.includes('career')" class="analysis-section">
            <h3>事业发展</h3>
            <p>{{ aiAnalysis.career }}</p>
          </div>
          
          <div v-if="userAge >= 18 && focusAreas.includes('relationship')" class="analysis-section">
            <h3>婚姻感情</h3>
            <p>{{ aiAnalysis.relationship }}</p>
          </div>
          
          <div v-if="userAge >= 18 && focusAreas.includes('children')" class="analysis-section">
            <h3>子女缘分</h3>
            <p>{{ aiAnalysis.children }}</p>
          </div>
          
          <div class="analysis-section">
            <h3>未来发展</h3>
            <p>{{ getAnalysisContent('未来发展') || aiAnalysis.overall }}</p>
          </div>
          
          <div class="analysis-section">
            <h3>综合建议</h3>
            <p>{{ aiAnalysis.overall }}</p>
          </div>
        </div>
      </van-tab>
    </van-tabs>
    
    <div class="action-buttons">
      <van-button type="primary" block @click="downloadPDF">
        下载PDF报告
      </van-button>
      <van-button plain type="primary" block style="margin-top: 10px;" @click="shareResult">
        分享结果
      </van-button>
      
      <!-- 调试按钮 -->
      <van-button plain type="warning" 
                  block 
                  style="margin-top: 10px;" 
                  @click="reloadBaziData">
        重新加载分析数据
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Toast, Dialog } from 'vant';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import axios from 'axios';
import http from './api/http'; // 导入配置好的http实例

const route = useRoute();
const router = useRouter();
const resultId = route.params.id || route.query.resultId;
const activeTab = ref(0);

// 用户年龄，从URL参数或localStorage获取
const userAge = ref(parseInt(route.query.age) || parseInt(localStorage.getItem('userAge')) || null);

// 从分析文本中提取特定部分内容
const getAnalysisContent = (sectionName) => {
  try {
    // 处理健康分析文本，尝试提取学业、性格等内容
    if (aiAnalysis.value.health) {
      const healthText = aiAnalysis.value.health;
      
      // 查找各部分的标记
      const academicMatch = healthText.match(new RegExp(`###\\s*${sectionName}([\\s\\S]*?)(?=###|$)`, 'i'));
      if (academicMatch && academicMatch[1]) {
        return academicMatch[1].trim();
      }
      
      // 如果是未来发展，尝试从overall中提取
      if (sectionName === '未来发展' && aiAnalysis.value.overall) {
        const futureMatch = aiAnalysis.value.overall.match(/未来(\d+)年[：:]([\s\S]*?)(?=（本分析|$)/i);
        if (futureMatch && futureMatch[2]) {
          return futureMatch[2].trim();
        }
      }
    }
    
    // 如果没有找到对应部分或提取失败，返回空字符串
    return '';
  } catch (e) {
    console.error(`提取${sectionName}内容时出错:`, e);
    return '';
  }
};

// 模拟数据，作为API调用失败时的备用数据
const focusAreas = ref(['health', 'wealth', 'career', 'relationship']);

// 备用数据，只在API调用失败时使用
const baziData = ref({
  yearPillar: {
    heavenlyStem: '甲',
    earthlyBranch: '子',
    element: '水'
  },
  monthPillar: {
    heavenlyStem: '丙',
    earthlyBranch: '寅',
    element: '木'
  },
  dayPillar: {
    heavenlyStem: '戊',
    earthlyBranch: '午',
    element: '火'
  },
  hourPillar: {
    heavenlyStem: '庚',
    earthlyBranch: '申',
    element: '金'
  },
  fiveElements: {
    wood: 2,
    fire: 2,
    earth: 1,
    metal: 2,
    water: 1
  },
  flowingYears: [
    {
      year: 2025,
      heavenlyStem: '乙',
      earthlyBranch: '丑',
      element: '土'
    },
    {
      year: 2026,
      heavenlyStem: '丙',
      earthlyBranch: '寅',
      element: '木'
    },
    {
      year: 2027,
      heavenlyStem: '丁',
      earthlyBranch: '卯',
      element: '木'
    },
    {
      year: 2028,
      heavenlyStem: '戊',
      earthlyBranch: '辰',
      element: '土'
    },
    {
      year: 2029,
      heavenlyStem: '己',
      earthlyBranch: '巳',
      element: '火'
    }
  ]
});

// 备用分析数据，只在API调用失败时使用
const aiAnalysis = ref({
  health: '您的八字中火土较旺，木水偏弱。从健康角度看，您需要注意心脑血管系统和消化系统的保养。建议平时多喝水，保持规律作息，避免过度劳累和情绪波动。2025-2026年间需特别注意肝胆健康，可适当增加绿色蔬菜的摄入，定期体检。',
  wealth: '您的财运在2025年有明显上升趋势，特别是在春夏季节。八字中金水相生，适合从事金融、贸易、水利相关行业。投资方面，稳健为主，可考虑分散投资组合。2027年有意外财运，但需谨慎对待，避免投机性强的项目。',
  career: '您的事业宫位较为稳定，具有较强的组织能力和执行力。2025-2026年是事业发展的关键期，有升职或转行的机会。建议提升专业技能，扩展人脉关系。您适合在团队中担任协调或管理角色，发挥沟通才能。',
  relationship: '您的八字中日柱为戊午，感情态度较为务实。2025年下半年至2026年上半年是感情发展的良好时期。已婚者需注意与伴侣的沟通，避免因工作忙碌而忽略家庭。单身者有机会通过社交活动或朋友介绍认识合适的对象。',
  children: '您的子女宫位较为温和，与子女关系和谐。教育方面，建议采用引导式而非强制式的方法，尊重子女的兴趣发展。2026-2027年是子女发展的重要阶段，可能需要您更多的关注和支持。',
  overall: '综合分析您的八字，2025-2027年是您人生的一个上升期，各方面都有良好发展。建议把握这段时间，在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。您的人生态度积极乐观，具有较强的适应能力和抗压能力，这将帮助您度过人生中的各种挑战。'
});

const testApiConnection = async () => {
  try {
    Toast.loading('正在测试API连接...');
    // 使用配置好的http实例
    const response = await http.get('/');
    console.log('API根路径响应:', response.data);
    Toast.success('API连接成功');
    return true;
  } catch (error) {
    console.error('API连接测试失败:', error);
    Toast.fail('API连接失败，请检查后端服务');
    return false;
  }
};

onMounted(async () => {
  // 先测试API连接
  const isApiConnected = await testApiConnection();
  if (!isApiConnected) {
    console.warn('API连接失败，将使用模拟数据');
    return;
  }
  
  console.log('结果页面加载，ID:', resultId);
  
  // 如果没有resultId，尝试从本地存储获取
  const localResultId = localStorage.getItem('resultId');
  if (!resultId && localResultId) {
    console.log('从本地存储获取ID:', localResultId);
  }
  
  const finalResultId = resultId || localResultId;
  
  if (!finalResultId) {
    console.error('缺少结果ID，无法获取分析结果');
    Toast.fail('缺少结果ID，无法获取分析结果');
    return;
  }
  
  try {
    console.log('调用API获取结果:', `/api/bazi/result/${finalResultId}`);
    
    // 显示加载提示，提醒用户需要等待
    Toast.loading({
      message: '正在调用AI进行八字分析，请耐心等待30-60秒...',
      duration: 10000,
      position: 'middle'
    });
    
    // 使用配置好的http实例
    const response = await http.get(`/api/bazi/result/${finalResultId}`);
    
    console.log('API响应:', response.status, response.data);
    
    if (response.data.code === 200) {
      console.log('获取成功，更新数据');
      // 确保从API获取数据并更新视图
      baziData.value = response.data.data.baziChart;
      aiAnalysis.value = response.data.data.aiAnalysis;
      focusAreas.value = response.data.data.focusAreas;
      
      Toast.success('分析结果加载成功');
    } else if (response.data.code === 202) {
      // 服务器接受了请求但还在处理中（异步分析）
      console.log('分析正在进行中，等待时间:', response.data.data.waitTime || '未知');
      
      // 显示清晰的等待提示，告知用户确切的等待情况
      Toast.loading({
        message: `AI正在专注分析您的八字命盘，已经分析了${response.data.data.waitTime || 0}秒，完整分析需要30-60秒，请稍候...`,
        duration: 8000,
        position: 'middle'
      });
      
      // 预先显示部分数据
      if (response.data.data.baziChart) {
        baziData.value = response.data.data.baziChart;
      }
      if (response.data.data.aiAnalysis) {
        aiAnalysis.value = response.data.data.aiAnalysis;
      }
      if (response.data.data.focusAreas) {
        focusAreas.value = response.data.data.focusAreas;
      }
      
      // 创建轮询定时器引用
      const pollInterval = ref(null);
      const maxPollTimeout = ref(null);
      
      // 启动轮询，每15秒查询一次直到分析完成
      pollInterval.value = setInterval(async () => {
        try {
          console.log('轮询查询分析结果...');
          const pollResponse = await http.get(`/api/bazi/result/${finalResultId}`);
          
          // 添加更详细的日志
          console.log(`轮询响应状态码: ${pollResponse.status}, 响应code: ${pollResponse.data.code}`);
          
          // 首先检查是否有分析结果
          const hasAnalysis = pollResponse.data.data && 
                              pollResponse.data.data.aiAnalysis && 
                              Object.values(pollResponse.data.data.aiAnalysis).some(v => v);
          
          if (pollResponse.data.code === 200 || hasAnalysis) {
            // 分析完成，更新数据
            console.log('分析已完成，更新数据');
            baziData.value = pollResponse.data.data.baziChart;
            aiAnalysis.value = pollResponse.data.data.aiAnalysis;
            focusAreas.value = pollResponse.data.data.focusAreas;
            Toast.success('分析结果加载成功！您的八字命盘解析已完成');
            
            // 清除所有定时器
            if (pollInterval.value) {
              clearInterval(pollInterval.value);
              pollInterval.value = null;
            }
            if (maxPollTimeout.value) {
              clearTimeout(maxPollTimeout.value);
              maxPollTimeout.value = null;
            }
            
            // 自动切换到AI分析结果标签
            activeTab.value = 1;
          } else if (pollResponse.data.code !== 202) {
            // 如果返回其他错误码，停止轮询
            console.error('轮询时发生错误:', pollResponse.data.message);
            Toast.fail(`查询错误: ${pollResponse.data.message}`);
            
            // 清除所有定时器
            if (pollInterval.value) {
              clearInterval(pollInterval.value);
              pollInterval.value = null;
            }
            if (maxPollTimeout.value) {
              clearTimeout(maxPollTimeout.value);
              maxPollTimeout.value = null;
            }
          } else {
            // 仍在分析中，更新等待时间
            const waitTime = pollResponse.data.data.waitTime || 0;
            const remainingTime = Math.max(0, 60 - waitTime);  // 假设总时间为60秒
            
            Toast.loading({
              message: `AI正在专注分析中(${Math.round(waitTime/60*100)}%)，预计还需${remainingTime}秒完成...`,
              duration: 5000,
              position: 'middle'
            });
            console.log('仍在分析中，已等待:', waitTime, '秒');
          }
        } catch (err) {
          console.error('轮询时出错:', err);
          // 出错也停止轮询并清除定时器
          if (pollInterval.value) {
            clearInterval(pollInterval.value);
            pollInterval.value = null;
          }
        }
      }, 15000); // 每15秒查询一次，减少服务器压力
      
      // 设置最大轮询时间，防止无限轮询
      maxPollTimeout.value = setTimeout(() => {
        if (pollInterval.value) {
          clearInterval(pollInterval.value);
          pollInterval.value = null;
          console.log('超过最大轮询时间，停止轮询');
          
          // 显示一个友好的提示，询问用户是否要继续等待
          Dialog.confirm({
            title: '分析耗时较长',
            message: '您的八字命理分析正在进行中，但耗时较长。您可以选择继续等待或稍后再查看结果。',
            confirmButtonText: '继续等待',
            cancelButtonText: '稍后查看',
          }).then(() => {
            // 用户选择继续等待，重新启动轮询
            window.location.reload();
          }).catch(() => {
            // 用户选择稍后查看，可以先返回首页
            router.push('/');
          });
        }
      }, 180000); // 最多轮询3分钟
    } else {
      console.error('API返回错误:', response.data.message);
      Toast.fail(response.data.message || '获取分析结果失败');
    }
  } catch (error) {
    console.error('获取分析结果出错:', error);
    console.error('错误详情:', error.response ? error.response.data : '无响应数据');
    Toast.fail('获取分析结果失败，请稍后重试');
    
    // 备选方案：如果ID以"RES"开头，尝试模拟支付再获取结果
    if (finalResultId.startsWith('RES')) {
      try {
        console.log('尝试使用模拟支付接口...');
        
        // 显示加载提示
        Toast.loading({
          message: '正在模拟支付并进行八字分析，请耐心等待30-60秒...',
          duration: 20000,  // 增加等待时间
          position: 'middle'
        });
        
        const orderId = finalResultId.replace('RES', '');
        
        // 从URL查询参数中获取出生日期和时间
        const urlParams = new URLSearchParams(window.location.search);
        const birthDate = urlParams.get('birthDate') || '2023-06-06'; // 使用默认值
        const birthTime = urlParams.get('birthTime') || '辰时 (07:00-09:00)'; // 使用默认值
        const gender = urlParams.get('gender') || 'male'; // 使用默认值
        
        // 验证日期格式
        let validBirthDate = birthDate;
        try {
          // 检查日期格式是否正确
          const dateParts = birthDate.split('-');
          if (dateParts.length === 3) {
            const year = parseInt(dateParts[0]);
            const month = parseInt(dateParts[1]);
            const day = parseInt(dateParts[2]);
            
            // 验证年份在合理范围内
            if (year < 1900 || year > 2100) {
              console.warn(`出生年份 ${year} 超出推荐范围(1900-2100)，使用默认值`);
              validBirthDate = '2000-01-01';
            }
          } else {
            console.warn(`日期格式错误: ${birthDate}，使用默认值`);
            validBirthDate = '2000-01-01';
          }
        } catch (e) {
          console.error('日期验证错误:', e);
          validBirthDate = '2000-01-01';
        }
        
        console.log('模拟支付使用参数:', { birthDate: validBirthDate, birthTime, gender });
        
        // 添加参数到URL
        const mockPaymentUrl = `/api/order/mock/pay/${orderId}?birthDate=${encodeURIComponent(validBirthDate)}&birthTime=${encodeURIComponent(birthTime)}&gender=${encodeURIComponent(gender)}`;
        
        // 尝试最多3次请求
        let retryCount = 0;
        let mockPaymentResponse = null;
        
        while (retryCount < 3) {
          try {
            console.log(`尝试请求模拟支付 (${retryCount + 1}/3)...`);
            mockPaymentResponse = await http.post(mockPaymentUrl);
            
            // 如果成功，跳出循环
            if (mockPaymentResponse && mockPaymentResponse.data && mockPaymentResponse.data.code === 200) {
              break;
            }
            
            // 如果失败但有响应，记录错误
            console.error('模拟支付请求失败:', mockPaymentResponse?.data);
            
            // 等待一秒后重试
            await new Promise(resolve => setTimeout(resolve, 1000));
            retryCount++;
          } catch (retryError) {
            console.error(`模拟支付请求出错 (尝试 ${retryCount + 1}/3):`, retryError);
            
            // 等待一秒后重试
            await new Promise(resolve => setTimeout(resolve, 1000));
            retryCount++;
          }
        }
        
        // 检查是否成功获取响应
        if (mockPaymentResponse && mockPaymentResponse.data && mockPaymentResponse.data.code === 200 && mockPaymentResponse.data.data && mockPaymentResponse.data.data.resultId) {
          const newResultId = mockPaymentResponse.data.data.resultId;
          console.log('获取到新的resultId:', newResultId);
          
          // 等待2秒，让服务器有时间处理结果
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          // 尝试最多3次获取结果
          let resultRetryCount = 0;
          let resultSuccess = false;
          
          while (resultRetryCount < 3 && !resultSuccess) {
            try {
              console.log(`尝试获取结果 (${resultRetryCount + 1}/3)...`);
              const retryResponse = await http.get(`/api/bazi/result/${newResultId}`);
              
              if (retryResponse.data.code === 200) {
                baziData.value = retryResponse.data.data.baziChart;
                aiAnalysis.value = retryResponse.data.data.aiAnalysis;
                focusAreas.value = retryResponse.data.data.focusAreas;
                Toast.success('分析结果加载成功');
                resultSuccess = true;
                break;
              } else if (retryResponse.data.code === 202) {
                // 结果正在处理中，等待更长时间再重试
                console.log('结果正在处理中，等待...');
                await new Promise(resolve => setTimeout(resolve, 3000));
              } else {
                console.error('获取结果失败:', retryResponse.data);
                await new Promise(resolve => setTimeout(resolve, 1000));
              }
            } catch (resultError) {
              console.error(`获取结果出错 (尝试 ${resultRetryCount + 1}/3):`, resultError);
              await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
            resultRetryCount++;
          }
          
          if (resultSuccess) {
            return; // 成功获取结果，退出函数
          }
        }
        
        // 如果所有尝试都失败，显示错误提示
        Toast.fail('无法获取分析结果，请稍后刷新页面重试');
      } catch (mockError) {
        console.error('模拟支付失败:', mockError);
        Toast.fail('模拟支付失败，请稍后重试');
      }
    }
  }
});

const getElementName = (element) => {
  const elementNames = {
    wood: '木',
    fire: '火',
    earth: '土',
    metal: '金',
    water: '水'
  };
  return elementNames[element] || element;
};

const onClickLeft = () => {
  router.push('/');
};

const downloadPDF = async () => {
  Toast.loading({
    message: '正在生成并下载PDF报告...',
    duration: 5000,
    position: 'middle'
  });
  
  if (!resultId) {
    Toast.fail('缺少结果ID，无法生成报告');
    return;
  }
  
  // 使用流式下载模式
  await downloadPDFAsStream();
};

// 新增直接流下载函数
const downloadPDFAsStream = async () => {
  Toast.loading({
    message: '正在生成PDF并下载报告...',
    duration: 0,
    position: 'middle',
    forbidClick: true
  });
  
  if (!resultId) {
    Toast.clear();
    Toast.fail('缺少结果ID，无法下载报告');
    return;
  }
  
  try {
    console.log('直接下载报告, 结果ID:', resultId);
    
    // 请求PDF文件流，添加随机参数避免缓存
    const response = await fetch(`/api/bazi/pdf/${resultId}?mode=stream&_=${Date.now()}`);
    
    // 检查错误
    if (!response.ok) {
      let errorMsg = '下载失败';
      try {
        const errorData = await response.json();
        errorMsg = errorData.message || errorMsg;
      } catch (e) {
        // 如果不是JSON格式的错误，尝试获取文本错误信息
        try {
          const errorText = await response.text();
          if (errorText) {
            errorMsg = `下载失败: ${errorText.substring(0, 100)}`;
          }
        } catch (textError) {
          // 如果无法获取文本，使用HTTP状态码
          errorMsg = `下载失败: HTTP错误 ${response.status}`;
        }
      }
      throw new Error(errorMsg);
    }
    
    // 检查内容类型
    const contentType = response.headers.get('content-type');
    if (!contentType || contentType.indexOf('application/pdf') === -1) {
      // 如果返回的不是PDF，尝试解析错误信息
      let errorMsg = '服务器返回的不是PDF文件';
      try {
        const errorData = await response.text();
        errorMsg = `错误: ${errorData.substring(0, 200)}`;
      } catch (e) {
        // 保持默认错误信息
      }
      throw new Error(errorMsg);
    }
    
    // 转换为Blob对象
    const blob = await response.blob();
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `八字命理分析_${resultId}.pdf`;
    
    // 触发下载
    document.body.appendChild(a);
    a.click();
    
    // 清理
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    Toast.clear();
    Toast.success('报告下载成功');
  } catch (error) {
    console.error('直接下载PDF出错:', error);
    Toast.clear();
    Toast.fail(error.message || '下载失败，请稍后重试');
    
    // 如果直接下载失败，提示用户使用本地PDF生成
    Dialog.confirm({
      title: 'PDF下载失败',
      message: '服务器生成PDF失败，是否要使用浏览器生成PDF文件？注意：本地生成的PDF格式可能不如服务器生成的完善。',
      confirmButtonText: '使用本地生成',
      cancelButtonText: '取消',
    }).then(() => {
      // 用户选择使用本地生成
      generatePDFLocally();
    }).catch(() => {
      // 用户取消
      console.log('用户取消本地PDF生成');
    });
  }
};

// 本地生成PDF的函数
const generatePDFLocally = async () => {
  console.log('使用客户端jsPDF库生成PDF');
  
  // 获取内容元素
  const element = document.querySelector('.result-container');
  if (!element) {
    throw new Error('找不到要转换的内容元素');
  }
  
  Toast.loading({
    message: '正在捕获页面内容...',
    duration: 5000
  });
  
  try {
    // 使用html2canvas捕获内容
    const canvas = await html2canvas(element, {
      scale: 1,
      useCORS: true,
      logging: false,
      windowWidth: document.documentElement.offsetWidth,
      windowHeight: document.documentElement.offsetHeight,
    });
    
    Toast.loading({
      message: '正在生成PDF文件...',
      duration: 5000
    });
        
    // 创建PDF文档
    const pdf = new jsPDF('p', 'mm', 'a4');
        
    // 计算尺寸和比例
    const imgData = canvas.toDataURL('image/png');
    const imgWidth = 210; // A4宽度，单位mm
    const pageHeight = 297; // A4高度，单位mm
    const imgHeight = canvas.height * imgWidth / canvas.width;
    let heightLeft = imgHeight;
    let position = 0;
          
    // 添加首页
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;
    
    // 如果内容超过一页，添加更多页
    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }
    
    // 添加页脚
    const pageCount = pdf.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);
      pdf.setFontSize(10);
      pdf.setTextColor(150);
      pdf.text(`八字命理AI分析报告 - 页 ${i} / ${pageCount}`, pdf.internal.pageSize.getWidth() / 2, pdf.internal.pageSize.getHeight() - 10, { align: 'center' });
    }
    
    // 保存PDF
    pdf.save(`八字命理分析_${resultId}.pdf`);
    
    return true;
  } catch (error) {
    console.error('本地PDF生成错误:', error);
    throw error;
  }
};

const shareResult = () => {
  Toast.success('分享功能开发中');
};

const reloadBaziData = async () => {
  Toast.loading('正在重新加载数据...');
  
  try {
    // 测试模拟支付接口以获取分析结果
    if (!resultId) {
      Toast.fail('缺少结果ID');
      return;
    }
    
    // 首先尝试使用模拟支付接口
    try {
      console.log('尝试使用模拟支付接口...');
      
      // 显示加载提示
      Toast.loading({
        message: '正在重新分析八字，请耐心等待30-60秒...',
        duration: 10000,
        position: 'middle'
      });
      
      const mockPaymentResponse = await http.post(`/api/order/mock/pay/${resultId.replace('RES', '')}`);
      console.log('模拟支付响应:', mockPaymentResponse.data);
      
      if (mockPaymentResponse.data.code === 200 && mockPaymentResponse.data.data.resultId) {
        // 使用返回的resultId重新加载数据
        const newResultId = mockPaymentResponse.data.data.resultId;
        console.log('获取到新的resultId:', newResultId);
        
        const response = await http.get(`/api/bazi/result/${newResultId}`);
        if (response.data.code === 200) {
          baziData.value = response.data.data.baziChart;
          aiAnalysis.value = response.data.data.aiAnalysis;
          focusAreas.value = response.data.data.focusAreas;
          Toast.success('数据加载成功');
          return;
        }
      }
    } catch (mockError) {
      console.warn('模拟支付失败，尝试直接获取结果:', mockError);
    }
    
    // 如果模拟支付失败，尝试直接获取结果
    const response = await http.get(`/api/bazi/result/${resultId}`);
    
    if (response.data.code === 200) {
      baziData.value = response.data.data.baziChart;
      aiAnalysis.value = response.data.data.aiAnalysis;
      focusAreas.value = response.data.data.focusAreas;
      Toast.success('数据加载成功');
    } else {
      Toast.fail(response.data.message || '加载失败');
    }
  } catch (error) {
    console.error('重新加载失败:', error);
    Toast.fail('加载失败: ' + (error.message || '未知错误'));
  }
};
</script>

<style scoped>
.result-container {
  padding-bottom: 20px;
}

.result-header {
  text-align: center;
  padding: 20px 0;
  background-color: #f2f3f5;
}

.result-header h2 {
  margin: 0;
  font-size: 20px;
  color: #323233;
}

.result-header p {
  margin: 10px 0 0;
  font-size: 14px;
  color: #969799;
}

.bazi-chart {
  padding: 20px 16px;
}

.bazi-chart h3 {
  margin: 20px 0 10px;
  color: #323233;
}

.pillar {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stem {
  width: 40px;
  height: 40px;
  line-height: 40px;
  text-align: center;
  background-color: #1989fa;
  color: white;
  border-radius: 4px;
  margin-bottom: 5px;
}

.branch {
  width: 40px;
  height: 40px;
  line-height: 40px;
  text-align: center;
  background-color: #07c160;
  color: white;
  border-radius: 4px;
  margin-bottom: 5px;
}

.label {
  font-size: 12px;
  color: #646566;
}

.five-elements {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
}

.element {
  text-align: center;
  flex: 1;
}

.element-name {
  font-size: 14px;
  color: #323233;
}

.element-value {
  font-size: 18px;
  font-weight: bold;
  color: #1989fa;
  margin-top: 5px;
}

.flowing-years {
  margin: 20px 0;
}

.ai-analysis {
  padding: 20px 16px;
}

.analysis-section {
  margin-bottom: 20px;
}

.analysis-section h3 {
  margin: 0 0 10px;
  color: #323233;
}

.analysis-section p {
  margin: 0;
  font-size: 14px;
  color: #646566;
  line-height: 1.6;
}

.action-buttons {
  padding: 20px 16px;
}

.age-notice {
  margin-bottom: 20px;
}
</style>
