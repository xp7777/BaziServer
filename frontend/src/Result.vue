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
    
    <van-tabs v-model:active="activeTab" sticky>
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showToast } from 'vant';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

const route = useRoute();
const router = useRouter();
const resultId = route.params.id;
const activeTab = ref(0);

// 模拟数据，实际项目中应该从API获取
const focusAreas = ref(['health', 'wealth', 'career', 'relationship']);

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

const aiAnalysis = ref({
  health: '您的八字中火土较旺，木水偏弱。从健康角度看，您需要注意心脑血管系统和消化系统的保养。建议平时多喝水，保持规律作息，避免过度劳累和情绪波动。2025-2026年间需特别注意肝胆健康，可适当增加绿色蔬菜的摄入，定期体检。',
  wealth: '您的财运在2025年有明显上升趋势，特别是在春夏季节。八字中金水相生，适合从事金融、贸易、水利相关行业。投资方面，稳健为主，可考虑分散投资组合。2027年有意外财运，但需谨慎对待，避免投机性强的项目。',
  career: '您的事业宫位较为稳定，具有较强的组织能力和执行力。2025-2026年是事业发展的关键期，有升职或转行的机会。建议提升专业技能，扩展人脉关系。您适合在团队中担任协调或管理角色，发挥沟通才能。',
  relationship: '您的八字中日柱为戊午，感情态度较为务实。2025年下半年至2026年上半年是感情发展的良好时期。已婚者需注意与伴侣的沟通，避免因工作忙碌而忽略家庭。单身者有机会通过社交活动或朋友介绍认识合适的对象。',
  children: '您的子女宫位较为温和，与子女关系和谐。教育方面，建议采用引导式而非强制式的方法，尊重子女的兴趣发展。2026-2027年是子女发展的重要阶段，可能需要您更多的关注和支持。',
  overall: '综合分析您的八字，2025-2027年是您人生的一个上升期，各方面都有良好发展。建议把握这段时间，在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。您的人生态度积极乐观，具有较强的适应能力和抗压能力，这将帮助您度过人生中的各种挑战。'
});

onMounted(() => {
  // 实际项目中这里应该调用API获取分析结果
  console.log('获取分析结果', resultId);
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

const downloadPDF = () => {
  showToast('正在生成PDF，请稍候...');
  
  // 实际项目中应该调用后端API下载PDF
  // 这里仅做前端演示
  setTimeout(() => {
    showToast('PDF生成成功，开始下载');
  }, 1500);
};

const shareResult = () => {
  showToast('分享功能开发中');
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
