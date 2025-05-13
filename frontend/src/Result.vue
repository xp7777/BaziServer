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
          <template v-if="focusAreas.includes('health')">
            <div class="analysis-section">
              <h3>身体健康</h3>
              <p>{{ aiAnalysis.health }}</p>
            </div>
          </template>
          
          <template v-if="focusAreas.includes('wealth')">
            <div class="analysis-section">
              <h3>财运分析</h3>
              <p>{{ aiAnalysis.wealth }}</p>
            </div>
          </template>
          
          <template v-if="focusAreas.includes('career')">
            <div class="analysis-section">
              <h3>事业发展</h3>
              <p>{{ aiAnalysis.career }}</p>
            </div>
          </template>
          
          <template v-if="focusAreas.includes('relationship')">
            <div class="analysis-section">
              <h3>婚姻感情</h3>
              <p>{{ aiAnalysis.relationship }}</p>
            </div>
          </template>
          
          <template v-if="focusAreas.includes('children')">
            <div class="analysis-section">
              <h3>子女缘分</h3>
              <p>{{ aiAnalysis.children }}</p>
            </div>
          </template>
          
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
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showToast } from 'vant';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import axios from 'axios';
import http from './api/http'; // 导入配置好的http实例

const route = useRoute();
const router = useRouter();
const resultId = route.params.id || route.query.resultId;
const activeTab = ref(0);

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
    showToast('正在测试API连接...');
    // 使用配置好的http实例
    const response = await http.get('/');
    console.log('API根路径响应:', response.data);
    showToast('API连接成功');
    return true;
  } catch (error) {
    console.error('API连接测试失败:', error);
    showToast('API连接失败，请检查后端服务');
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
    showToast('缺少结果ID，无法获取分析结果');
    return;
  }
  
  try {
    console.log('调用API获取结果:', `/api/bazi/result/${finalResultId}`);
    
    // 显示加载提示，提醒用户需要等待
    showToast({
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
      showToast('分析结果加载成功');
    } else if (response.data.code === 202) {
      // 服务器接受了请求但还在处理中（异步分析）
      console.log('分析正在进行中，等待时间:', response.data.data.waitTime || '未知');
      
      // 显示清晰的等待提示，告知用户确切的等待情况
      showToast({
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
      
      // 启动轮询，每15秒查询一次直到分析完成
      // 增加轮询间隔，减少服务器压力
      const pollInterval = setInterval(async () => {
        try {
          console.log('轮询查询分析结果...');
          const pollResponse = await http.get(`/api/bazi/result/${finalResultId}`);
          
          if (pollResponse.data.code === 200) {
            // 分析完成，更新数据
            baziData.value = pollResponse.data.data.baziChart;
            aiAnalysis.value = pollResponse.data.data.aiAnalysis;
            focusAreas.value = pollResponse.data.data.focusAreas;
            showToast('分析结果加载成功！您的八字命盘解析已完成');
            clearInterval(pollInterval); // 停止轮询
            
            // 自动切换到AI分析结果标签
            activeTab.value = 1;
          } else if (pollResponse.data.code !== 202) {
            // 如果返回其他错误码，停止轮询
            console.error('轮询时发生错误:', pollResponse.data.message);
            showToast(`查询错误: ${pollResponse.data.message}`);
            clearInterval(pollInterval); // 停止轮询
          } else {
            // 仍在分析中，更新等待时间
            const waitTime = pollResponse.data.data.waitTime || 0;
            const remainingTime = Math.max(0, 60 - waitTime);  // 假设总时间为60秒
            
            showToast({
              message: `AI正在专注分析中(${Math.round(waitTime/60*100)}%)，预计还需${remainingTime}秒完成...`,
              duration: 5000,
              position: 'middle'
            });
            console.log('仍在分析中，已等待:', waitTime, '秒');
          }
        } catch (err) {
          console.error('轮询时出错:', err);
          clearInterval(pollInterval); // 出错也停止轮询
        }
      }, 15000); // 每15秒查询一次，减少服务器压力
      
      // 设置最大轮询时间，防止无限轮询
      setTimeout(() => {
        if (pollInterval) {
          clearInterval(pollInterval);
          console.log('超过最大轮询时间，停止轮询');
          
          // 显示一个友好的提示，询问用户是否要继续等待
          showDialog({
            title: '分析耗时较长',
            message: '您的八字命理分析正在进行中，但耗时较长。您可以选择继续等待或稍后再查看结果。',
            showCancelButton: true,
            confirmButtonText: '继续等待',
            cancelButtonText: '稍后查看',
            theme: 'round-button',
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
      showToast(response.data.message || '获取分析结果失败');
    }
  } catch (error) {
    console.error('获取分析结果出错:', error);
    console.error('错误详情:', error.response ? error.response.data : '无响应数据');
    showToast('获取分析结果失败，请稍后重试');
    
    // 备选方案：如果ID以"RES"开头，尝试模拟支付再获取结果
    if (finalResultId.startsWith('RES')) {
      try {
        console.log('尝试使用模拟支付接口...');
        
        // 显示加载提示
        showToast({
          message: '正在模拟支付并进行八字分析，请耐心等待30-60秒...',
          duration: 10000,
          position: 'middle'
        });
        
        const orderId = finalResultId.replace('RES', '');
        const mockPaymentResponse = await http.post(`/api/order/mock/pay/${orderId}`);
        
        if (mockPaymentResponse.data.code === 200 && mockPaymentResponse.data.data.resultId) {
          const newResultId = mockPaymentResponse.data.data.resultId;
          console.log('获取到新的resultId:', newResultId);
          
          const retryResponse = await http.get(`/api/bazi/result/${newResultId}`);
          if (retryResponse.data.code === 200) {
            baziData.value = retryResponse.data.data.baziChart;
            aiAnalysis.value = retryResponse.data.data.aiAnalysis;
            focusAreas.value = retryResponse.data.data.focusAreas;
            showToast('分析结果加载成功');
            return;
          }
        }
      } catch (mockError) {
        console.error('模拟支付失败:', mockError);
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
  showToast({
    message: '正在生成PDF，请稍候...',
    duration: 5000,
    position: 'middle'
  });
  
  if (!resultId) {
    showToast('缺少结果ID，无法生成PDF');
    return;
  }
  
  try {
    // 调用后端API生成并下载PDF
    console.log('调用API下载PDF:', `/api/bazi/pdf/${resultId}`);
    
    // 检测是否在微信环境中
    const isWeixinBrowser = /MicroMessenger/i.test(navigator.userAgent);
    console.log('是否在微信环境:', isWeixinBrowser);
    
    if (isWeixinBrowser) {
      // 微信环境使用直接打开链接的方式，返回JSON包含URL
      const response = await http.get(`/api/bazi/pdf/${resultId}`);
      
      if (response.data.code === 200 && response.data.data?.url) {
        // 在新窗口打开URL
        window.open(response.data.data.url, '_blank');
        showToast('PDF生成成功，请点击右上角菜单在浏览器中打开以下载');
        return;
      } else if (response.data.code === 302 && response.data.data?.url) {
        // 处理重定向
        window.open(response.data.data.url, '_blank');
        showToast('PDF生成成功，请点击右上角菜单在浏览器中打开以下载');
        return;
      } else {
        showToast(response.data.message || 'PDF已生成，请在浏览器中查看');
        return;
      }
    }
    
    // 非微信环境使用Blob下载
    // 由于文件下载需要处理二进制数据，使用特殊配置
    const response = await http.get(`/api/bazi/pdf/${resultId}`, {
      responseType: 'blob', // 设置响应类型为二进制数据
    }).catch(error => {
      // 直接处理错误，因为有些响应可能是JSON格式的错误消息
      if (error.response) {
        // 如果是JSON错误，尝试转换并显示
        if (error.response.headers['content-type']?.includes('application/json')) {
          return error.response;
        }
      }
      throw error; // 其他错误重新抛出
    });
    
    // 检查响应状态
    if (response.status === 200) {
      // 检查返回的内容类型来确定是PDF还是JSON数据
      const contentType = response.headers['content-type'];
      
      if (contentType?.includes('application/pdf')) {
        // 创建Blob对象
        const blob = new Blob([response.data], { type: 'application/pdf' });
        
        // 创建下载链接
        const url = window.URL.createObjectURL(blob);
        
        // 判断移动设备，可能不支持下载
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        if (isMobile) {
          // 移动设备上优先打开PDF预览
          window.open(url, '_blank');
          showToast('PDF已打开，请使用浏览器的分享/保存功能下载');
        } else {
          // 桌面设备上使用标准下载方式
          const link = document.createElement('a');
          link.href = url;
          link.download = `八字命理分析_${resultId}.pdf`;
          
          // 模拟点击下载
          document.body.appendChild(link);
          link.click();
          
          // 清理
          setTimeout(() => {
            window.URL.revokeObjectURL(url);
            document.body.removeChild(link);
          }, 100);
        }
        
        showToast('PDF下载成功！');
        return;
      }
      
      // 处理JSON响应（可能是URL链接）
      if (contentType?.includes('application/json')) {
        // 解析JSON响应
        const reader = new FileReader();
        reader.onload = function() {
          try {
            const jsonResponse = JSON.parse(reader.result);
            console.log('API响应(JSON):', jsonResponse);
            
            // 检查是否有URL
            if (jsonResponse.code === 200 && jsonResponse.data?.url) {
              // 在新窗口打开URL
              window.open(jsonResponse.data.url, '_blank');
              showToast('PDF生成成功，正在打开...');
            } else if (jsonResponse.code === 302 && jsonResponse.data?.url) {
              // 处理重定向
              window.open(jsonResponse.data.url, '_blank');
              showToast('PDF生成成功，正在打开...');
            } else {
              // 显示其他成功消息
              showToast(jsonResponse.message || 'PDF操作成功');
            }
          } catch (e) {
            console.error('解析JSON响应出错:', e);
            showToast('处理PDF响应时出错');
          }
        };
        reader.readAsText(response.data);
        return;
      }
    }
    
    // 处理其他情况
    showToast('PDF生成过程中出现异常，请重试');
    console.error('未知的PDF响应:', response);
    
  } catch (error) {
    console.error('下载PDF出错:', error);
    showToast('下载PDF失败: ' + (error.message || '未知错误'));
  }
};

const shareResult = () => {
  showToast('分享功能开发中');
};

const reloadBaziData = async () => {
  showToast('正在重新加载数据...');
  
  try {
    // 测试模拟支付接口以获取分析结果
    if (!resultId) {
      showToast('缺少结果ID');
      return;
    }
    
    // 首先尝试使用模拟支付接口
    try {
      console.log('尝试使用模拟支付接口...');
      
      // 显示加载提示
      showToast({
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
          showToast('数据加载成功');
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
      showToast('数据加载成功');
    } else {
      showToast(response.data.message || '加载失败');
    }
  } catch (error) {
    console.error('重新加载失败:', error);
    showToast('加载失败: ' + (error.message || '未知错误'));
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
</style>
