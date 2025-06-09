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
          <div v-if="baziData && baziData.yearPillar && baziData.monthPillar && baziData.dayPillar && baziData.hourPillar" class="four-pillars">
            <!-- 年柱 -->
            <div class="pillar">
              <div class="stem">{{ baziData.yearPillar.heavenlyStem }}</div>
              <div class="branch">{{ baziData.yearPillar.earthlyBranch }}</div>
              <div class="label">年柱</div>
              <div class="nayin">{{ baziData.yearPillar.naYin }}</div>
              <div class="shishen">{{ baziData.yearPillar.shiShen }}</div>
              <div class="wangshuai">{{ baziData.yearPillar.wangShuai }}</div>
            </div>
            
            <!-- 月柱 -->
            <div class="pillar">
              <div class="stem">{{ baziData.monthPillar.heavenlyStem }}</div>
              <div class="branch">{{ baziData.monthPillar.earthlyBranch }}</div>
              <div class="label">月柱</div>
              <div class="nayin">{{ baziData.monthPillar.naYin }}</div>
              <div class="shishen">{{ baziData.monthPillar.shiShen }}</div>
              <div class="wangshuai">{{ baziData.monthPillar.wangShuai }}</div>
            </div>
            
            <!-- 日柱 -->
            <div class="pillar">
              <div class="stem">{{ baziData.dayPillar.heavenlyStem }}</div>
              <div class="branch">{{ baziData.dayPillar.earthlyBranch }}</div>
              <div class="label">日柱</div>
              <div class="nayin">{{ baziData.dayPillar.naYin }}</div>
              <div class="shishen">{{ baziData.dayPillar.shiShen }}</div>
              <div class="wangshuai">{{ baziData.dayPillar.wangShuai }}</div>
            </div>
            
            <!-- 时柱 -->
            <div class="pillar">
              <div class="stem">{{ baziData.hourPillar.heavenlyStem }}</div>
              <div class="branch">{{ baziData.hourPillar.earthlyBranch }}</div>
              <div class="label">时柱</div>
              <div class="nayin">{{ baziData.hourPillar.naYin }}</div>
              <div class="shishen">{{ baziData.hourPillar.shiShen }}</div>
              <div class="wangshuai">{{ baziData.hourPillar.wangShuai }}</div>
            </div>
          </div>
          <div v-else class="error-message">
            <van-empty description="八字数据加载失败，请重试" />
            <van-button type="primary" size="small" @click="reloadBaziData">重新加载</van-button>
          </div>
          
          <h3>五行分布</h3>
          <div class="five-elements" v-if="baziData && baziData.fiveElements">
            <div class="element" v-for="(value, element) in baziData.fiveElements" :key="element">
              <div class="element-name">{{ getElementName(element) }}</div>
              <div class="element-value">{{ value }}</div>
            </div>
          </div>
          <div class="five-elements" v-else>
            <div class="element" v-for="element in ['wood', 'fire', 'earth', 'metal', 'water']" :key="element">
              <div class="element-name">{{ getElementName(element) }}</div>
              <div class="element-value">--</div>
            </div>
          </div>
          
          <!-- 添加神煞显示 -->
          <h3>神煞信息</h3>
          <div class="shen-sha-info" v-if="baziData && baziData.shenSha">
            <div class="shen-sha-content">
              <div class="shen-sha-item">
                <span class="label">日冲</span>
                <span class="value">{{ baziData.shenSha.dayChong }}</span>
              </div>
              <div class="shen-sha-item">
                <span class="label">值神</span>
                <span class="value">{{ baziData.shenSha.zhiShen }}</span>
              </div>
              <div class="shen-sha-item">
                <span class="label">喜神</span>
                <span class="value">{{ baziData.shenSha.xiShen }}</span>
              </div>
              <div class="shen-sha-item">
                <span class="label">福神</span>
                <span class="value">{{ baziData.shenSha.fuShen }}</span>
              </div>
              <div class="shen-sha-item">
                <span class="label">财神</span>
                <span class="value">{{ baziData.shenSha.caiShen }}</span>
              </div>
            </div>
            
            <!-- 本命神煞 -->
            <div class="ben-ming-sha" v-if="baziData.shenSha.benMing.length > 0">
              <h4>本命神煞</h4>
              <div class="ben-ming-list">
                <span v-for="(sha, index) in baziData.shenSha.benMing" :key="index" class="ben-ming-item">
                  {{ sha }}
                </span>
              </div>
            </div>
          </div>
          <div class="shen-sha-info" v-else>
            <van-cell-group inset>
              <van-cell title="神煞信息" value="暂无数据" />
            </van-cell-group>
          </div>
          
          <!-- 添加大运显示 -->
          <h3>大运信息</h3>
          <div class="da-yun-info" v-if="baziData && baziData.daYun">
            <div class="qi-yun-info">
              <p>起运年龄: {{ baziData.daYun.startAge }}岁</p>
              <p>起运年份: {{ baziData.daYun.startYear }}年</p>
              <p>大运顺序: {{ baziData.daYun.isForward ? '顺行' : '逆行' }}</p>
            </div>
            
            <!-- 大运列表 -->
            <div class="da-yun-table">
              <table class="custom-table">
                <thead>
                  <tr>
                    <th>年龄</th>
                    <th>年份</th>
                    <th>天干</th>
                    <th>地支</th>
                    <th>纳音</th>
                    <th>吉凶</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(yun, index) in baziData.daYun.daYunList" :key="index">
                    <td>{{ yun.startAge }}-{{ yun.endAge }}</td>
                    <td>{{ yun.startYear }}-{{ yun.endYear }}</td>
                    <td>{{ yun.heavenlyStem }}</td>
                    <td>{{ yun.earthlyBranch }}</td>
                    <td>{{ yun.naYin }}</td>
                    <td>{{ yun.jiXiong }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="da-yun-info" v-else>
            <van-cell-group inset>
              <van-cell title="大运信息" value="暂无数据" />
            </van-cell-group>
          </div>
          
          <h3>流年信息</h3>
          <div class="liu-nian-info" v-if="baziData && baziData.flowingYears && baziData.flowingYears.length">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>年份</th>
                  <th>年龄</th>
                  <th>天干</th>
                  <th>地支</th>
                  <th>五行</th>
                  <th>神煞</th>
                  <th>吉凶</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(year, index) in baziData.flowingYears" :key="index">
                  <td>{{ year.year }}</td>
                  <td>{{ year.age }}</td>
                  <td>{{ year.heavenlyStem }}</td>
                  <td>{{ year.earthlyBranch }}</td>
                  <td>{{ getElementName(year.ganElement) }}/{{ getElementName(year.zhiElement) }}</td>
                  <td>{{ year.shenSha && Array.isArray(year.shenSha) ? year.shenSha.join(', ') : '无' }}</td>
                  <td>{{ year.jiXiong || '未知' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="liu-nian-info" v-else>
            <van-empty description="流年数据暂无" />
          </div>
        </div>
      </van-tab>
      
      <van-tab title="AI分析结果">
        <div class="ai-analysis">
          <div v-if="userAge !== null && userAge < 0" class="age-notice">
            <van-notice-bar
              color="#1989fa"
              background="#ecf9ff"
              left-icon="info-o"
            >
              此分析针对未来出生的宝宝，重点关注性格特点、天赋才能和健康发展趋势。
            </van-notice-bar>
          </div>
          <div v-else-if="userAge !== null && userAge < 6" class="age-notice">
            <van-notice-bar
              color="#1989fa"
              background="#ecf9ff"
              left-icon="info-o"
            >
              此分析针对婴幼儿({{userAge}}岁)，重点关注性格特点、天赋才能和健康发展趋势。
            </van-notice-bar>
          </div>
          <div v-else-if="userAge !== null && userAge < 18" class="age-notice">
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
          
          <div class="analysis-section">
            <h3>性格特点</h3>
            <p>{{ aiAnalysis.personality || getAnalysisContent('性格特点') }}</p>
          </div>
          
          <!-- 学业分析（对所有年龄段显示，但侧重点不同） -->
          <div class="analysis-section">
            <h3>学业分析</h3>
            <p>{{ aiAnalysis.education || getAnalysisContent('学业分析') }}</p>
          </div>
          
          <!-- 父母情况（所有年龄段都显示） -->
          <div class="analysis-section">
            <h3>父母情况</h3>
            <p>{{ aiAnalysis.parents || '暂无父母情况分析' }}</p>
          </div>
          
          <!-- 人际关系（所有年龄段都显示） -->
          <div class="analysis-section">
            <h3>人际关系</h3>
            <p>{{ aiAnalysis.social || '暂无人际关系分析' }}</p>
          </div>
          
          <!-- 财运分析（18岁以上显示，或者标注为未来发展） -->
          <div class="analysis-section">
            <h3>{{ userAge !== null && userAge >= 18 ? '财运分析' : '未来财运发展' }}</h3>
            <p>{{ aiAnalysis.wealth }}</p>
          </div>
          
          <!-- 事业发展（18岁以上显示，或者标注为未来发展） -->
          <div class="analysis-section">
            <h3>{{ userAge !== null && userAge >= 18 ? '事业发展' : '未来事业发展' }}</h3>
            <p>{{ aiAnalysis.career }}</p>
          </div>
          
          <!-- 婚姻感情（18岁以上显示，或者标注为未来发展） -->
          <div class="analysis-section">
            <h3>{{ userAge !== null && userAge >= 18 ? '婚姻感情' : '未来感情发展' }}</h3>
            <p>{{ aiAnalysis.relationship }}</p>
          </div>
          
          <!-- 子女情况（18岁以上显示，或者标注为未来发展） -->
          <div class="analysis-section">
            <h3>{{ userAge !== null && userAge >= 18 ? '子女情况' : '未来子女缘分' }}</h3>
            <p>{{ aiAnalysis.children }}</p>
          </div>
          
          <!-- 近五年运势（所有年龄段都显示） -->
          <div class="analysis-section">
            <h3>近五年运势</h3>
            <p>{{ aiAnalysis.future || getAnalysisContent('近五年运势') || aiAnalysis.overall }}</p>
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
      
      <!-- 本地生成PDF按钮 -->
      <van-button plain type="info" 
                  block 
                  style="margin-top: 10px;" 
                  @click="handleLocalPDFGeneration">
        本地生成PDF
      </van-button>
      
      <!-- 调试按钮 -->
      <van-button plain type="warning" 
                  block 
                  style="margin-top: 10px;" 
                  @click="reloadBaziData">
        重新加载分析数据
      </van-button>
    </div>
    
    <!-- 添加追问部分 -->
    <div class="followup-section" v-if="baziData && !loading">
      <h2 class="section-title">深度分析</h2>
      <p class="section-desc">选择您感兴趣的领域，进行深度分析</p>
      
      <div class="followup-options">
        <div 
          v-for="option in followupOptions" 
          :key="option.id" 
          class="followup-option" 
          :class="{ 'paid': option.paid }"
          @click="selectFollowupOption(option)"
        >
          <div class="option-content">
            <span class="option-name">{{ option.name }}</span>
            <span class="option-status" v-if="option.paid">已解锁</span>
            <span class="option-status" v-else>￥9.9</span>
          </div>
        </div>
      </div>
      
      <!-- 已支付的追问分析结果展示 -->
      <div v-if="currentFollowup && currentFollowup.paid" class="followup-result">
        <h3>{{ currentFollowup.name }}分析</h3>
        <div class="analysis-content">
          {{ followupAnalysis[currentFollowup.id] || '暂无分析结果' }}
        </div>
      </div>
    </div>
    
    <!-- 追问支付对话框 -->
    <van-dialog
      v-model:show="showFollowupDialog"
      title="深度分析"
      confirm-button-text="支付 ￥9.9"
      @confirm="payForFollowup"
      :before-close="() => !isLoadingFollowup"
    >
      <div class="followup-dialog-content">
        <p>您选择了「{{ currentFollowup?.name }}」深度分析</p>
        <p>支付后，AI将根据您的八字和流年运势，为您提供专业的命理分析</p>
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Toast, Dialog } from 'vant';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const resultId = ref(route.params.id || route.query.resultId);
const activeTab = ref(0);
const loading = ref(false);

// 用户年龄，从URL参数或localStorage获取
const userAge = ref(null);
// 尝试从URL参数获取年龄
if (route.query.age && !isNaN(parseInt(route.query.age))) {
  userAge.value = parseInt(route.query.age);
} 
// 如果URL参数中没有年龄，尝试从localStorage获取
else if (localStorage.getItem('userAge') && !isNaN(parseInt(localStorage.getItem('userAge')))) {
  userAge.value = parseInt(localStorage.getItem('userAge'));
}
// 记录用户年龄到控制台，便于调试
console.log('用户年龄:', userAge.value);

// 从分析文本中提取特定部分内容
const getAnalysisContent = (sectionName) => {
  try {
    // 如果是性格特点或学业发展，直接从对应字段获取
    if (sectionName === '性格特点' && aiAnalysis.value.personality) {
      return aiAnalysis.value.personality;
    }
    
    if (sectionName === '学业发展' && aiAnalysis.value.education) {
      return aiAnalysis.value.education;
    }
    
    // 处理健康分析文本，尝试提取学业、性格等内容
    if (aiAnalysis.value.health) {
      const healthText = aiAnalysis.value.health;
      
      // 查找各部分的标记
      const sectionMatch = healthText.match(new RegExp(`###\\s*${sectionName}([\\s\\S]*?)(?=###|$)`, 'i'));
      if (sectionMatch && sectionMatch[1]) {
        return sectionMatch[1].trim();
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

// 修改数据初始化
const focusAreas = ref([]);
const analysisResult = ref({});

// 初始化八字数据
const baziData = ref({
  yearPillar: { 
    heavenlyStem: '', 
    earthlyBranch: '',
    naYin: '',
    shiShen: '',
    wangShuai: ''
  },
  monthPillar: { 
    heavenlyStem: '', 
    earthlyBranch: '',
    naYin: '',
    shiShen: '',
    wangShuai: ''
  },
  dayPillar: { 
    heavenlyStem: '', 
    earthlyBranch: '',
    naYin: '',
    shiShen: '',
    wangShuai: ''
  },
  hourPillar: { 
    heavenlyStem: '', 
    earthlyBranch: '',
    naYin: '',
    shiShen: '',
    wangShuai: ''
  },
  fiveElements: {},
  flowingYears: [],
  shenSha: {
    dayChong: '',
    zhiShen: '',
    xiShen: '',
    fuShen: '',
    caiShen: '',
    benMing: [],
    yearGan: [],
    yearZhi: [],
    dayGan: [],
    dayZhi: []
  },
  daYun: {
    startAge: 0,
    startYear: 0,
    isForward: true,
    daYunList: []
  },
  birthDate: null,
  birthTime: null,
  gender: null
});

// 初始化分析数据
const aiAnalysis = ref({
  health: '',
  wealth: '',
  career: '',
  relationship: '',
  children: '',
  overall: '',
  personality: '',
  education: '',
  parents: '',
  social: '',
  future: ''
});

const testApiConnection = async () => {
  try {
    Toast.loading('正在测试API连接...');
    // 使用配置好的http实例
    const response = await axios.get('/');
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
    loading.value = false;
    return;
  }
  
  console.log('结果页面加载，URL参数中的ID:', resultId.value);
  
  // 如果没有resultId，尝试从本地存储获取
  const localResultId = localStorage.getItem('resultId');
  if (!resultId.value && localResultId) {
    console.log('从本地存储获取ID:', localResultId);
    // 更新resultId为从本地存储获取的值
    resultId.value = localResultId;
  }
  
  // 确保resultId是字符串类型，不是布尔值或其他数据类型
  if (resultId.value === true || resultId.value === false) {
    console.error('resultId不应该是布尔值:', resultId.value);
    resultId.value = localResultId || route.query.resultId || '';
  }
  
  console.log('最终使用的resultId:', resultId.value);
  
  // 如果resultId为空或无效，显示错误并尝试从URL查询参数获取
  if (!resultId.value) {
    console.error('缺少结果ID，无法获取分析结果');
    
    // 尝试从URL查询参数获取备选ID
    const urlResultId = route.query.resultId;
    if (urlResultId) {
      console.log('从URL查询参数获取备选ID:', urlResultId);
      resultId.value = urlResultId;
    } else {
      Toast.fail('缺少结果ID，无法获取分析结果');
      loading.value = false;
      return;
    }
  }
  
  // 存储确认的resultId到本地存储
  localStorage.setItem('resultId', resultId.value);
  
  // 显示加载提示
  Toast.loading({
    message: '正在加载八字分析结果，请稍候...',
    duration: 0,
    forbidClick: true
  });
  
  // 调用getBaziResult函数获取结果
  await getBaziResult();
  
  // 关闭加载提示
  Toast.clear();
});

const getElementName = (element) => {
  if (!element) return '--';
  
  const elementNames = {
    'wood': '木',
    'fire': '火',
    'earth': '土',
    'metal': '金',
    'water': '水',
    '木': '木',
    '火': '火',
    '土': '土',
    '金': '金',
    '水': '水'
  };
  
  return elementNames[element] || element;
};

const onClickLeft = () => {
  router.push('/');
};

// 修改后的直接流下载函数，适应后端始终返回文件流
const downloadPDFAsStream = async () => {
  Toast.loading({
    message: '正在生成PDF并下载报告...',
    duration: 0,
    position: 'middle',
    forbidClick: true
  });
  
  if (!resultId.value) {
    Toast.clear();
    Toast.fail('缺少结果ID，无法下载报告');
    return false;
  }
  
  try {
    console.log('直接下载报告, 结果ID:', resultId.value);
    
    // 创建下载链接，添加时间戳避免缓存问题
    const timestamp = new Date().getTime();
    const downloadUrl = `/api/bazi/pdf/${resultId.value}?t=${timestamp}`;
    console.log('下载URL:', downloadUrl);
    
    // 使用fetch API获取文件流
    const response = await fetch(downloadUrl, {
      method: 'GET',
      cache: 'no-cache',
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
    
    // 检查错误
    if (!response.ok) {
      let errorMsg = `下载失败: HTTP错误 ${response.status}`;
      try {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          errorMsg = errorData.message || errorMsg;
        } else {
          // 如果不是JSON格式的错误，尝试获取文本错误信息
          const errorText = await response.text();
          if (errorText) {
            errorMsg = `下载失败: ${errorText.substring(0, 100)}`;
          }
        }
      } catch (e) {
        console.error('解析错误响应失败:', e);
      }
      throw new Error(errorMsg);
    }
    
    // 检查内容类型
    const contentType = response.headers.get('content-type');
    const disposition = response.headers.get('content-disposition');
    
    console.log('响应内容类型:', contentType);
    console.log('响应内容处置:', disposition);
    
    // 确定文件名和扩展名
    let filename = `八字命理分析_${resultId.value}.pdf`;
    if (disposition && disposition.includes('filename=')) {
      const filenameMatch = disposition.match(/filename=["']?([^"']+)["']?/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    }
    
    // 确定文件类型
    const fileExtension = contentType && contentType.includes('html') ? 'html' : 'pdf';
    if (!filename.endsWith(fileExtension)) {
      filename = `八字命理分析_${resultId.value}.${fileExtension}`;
    }
    
    // 转换为Blob对象
    const blob = await response.blob();
    
    // 检查Blob大小 - 注意：当浏览器接管下载时，可能会导致blob.size为0
    // 因此，如果有Content-Disposition头部，我们应该认为下载已经开始
    const isDownloadStarted = disposition && disposition.includes('attachment');
    if (blob.size === 0 && !isDownloadStarted) {
      throw new Error('下载的文件为空');
    }
    
    // 对于小文件，我们可以验证文件内容
    // 但对于大文件或浏览器接管的下载，跳过验证
    if (blob.size > 0 && blob.size < 1024*1024 && contentType && contentType.includes('pdf')) {
      try {
        // 读取文件头部以验证是否为有效的PDF
        const fileReader = new FileReader();
        const headerPromise = new Promise((resolve, reject) => {
          fileReader.onloadend = (e) => resolve(e.target.result);
          fileReader.onerror = (e) => reject(e);
        });
        fileReader.readAsArrayBuffer(blob.slice(0, 5));
        
        const header = await headerPromise;
        const headerView = new Uint8Array(header);
        const headerString = String.fromCharCode.apply(null, headerView);
        
        if (!headerString.startsWith('%PDF')) {
          console.error('无效的PDF文件头:', headerString);
          throw new Error('下载的不是有效的PDF文件');
        }
      } catch (e) {
        console.error('验证PDF文件失败:', e);
        // 如果是浏览器接管下载导致的验证失败，我们不抛出错误
        if (!isDownloadStarted) {
          throw new Error('验证PDF文件失败: ' + e.message);
        } else {
          console.warn('浏览器接管了下载，跳过PDF验证');
        }
      }
    }
    
    // 如果浏览器已经接管下载（通过Content-Disposition头部），
    // 我们不需要手动创建下载链接
    if (!isDownloadStarted) {
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      
      // 触发下载
      document.body.appendChild(a);
      a.click();
      
      // 清理
      setTimeout(() => {
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }, 100);
    }
    
    Toast.clear();
    Toast.success('报告下载成功');
    return true;
  } catch (error) {
    console.error('直接下载PDF出错:', error);
    Toast.clear();
    
    // 检查是否是因为浏览器已经接管了下载而导致的错误
    if (error.message && (
        error.message.includes('下载的文件为空') || 
        error.message.includes('验证PDF文件失败')
      )) {
      // 如果是这类错误，可能是浏览器已经开始下载，我们不显示错误
      console.log('可能是浏览器已经接管了下载，不显示错误');
      Toast.success('报告下载已开始，请等待浏览器完成下载');
      return true;
    }
    
    // 显示错误信息
    Toast.fail(error.message || '下载失败，请稍后重试');
    return false;
  }
};

// 修改主下载函数，添加重试逻辑
const downloadPDF = async () => {
  Toast.loading({
    message: '正在生成并下载PDF报告...',
    duration: 5000,
    position: 'middle'
  });
  
  if (!resultId.value) {
    Toast.fail('缺少结果ID，无法生成报告');
    return;
  }
  
  // 最多尝试3次下载
  let attempts = 0;
  let success = false;
  
  while (attempts < 3 && !success) {
    attempts++;
    
    if (attempts > 1) {
      console.log(`尝试第${attempts}次下载...`);
      Toast.loading({
        message: `尝试第${attempts}次下载...`,
        duration: 2000
      });
      // 在重试之前等待一段时间
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // 使用流式下载模式，并处理返回值
    success = await downloadPDFAsStream();
    
    // 如果流式下载成功，直接返回，不再尝试其他方法
    if (success === true) {
      return;
    }
  }
  
  // 如果多次尝试后仍然失败，提示用户
  if (!success) {
    Toast.clear();
    Dialog.alert({
      title: 'PDF下载失败',
      message: '下载PDF报告失败，请稍后再试。如果问题持续存在，请联系客服。',
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
    pdf.save(`八字命理分析_${resultId.value}.pdf`);
    
    return true;
  } catch (error) {
    console.error('本地PDF生成错误:', error);
    throw error;
  }
};

const shareResult = () => {
  Toast.success('分享功能开发中');
};

// 处理本地PDF生成
const handleLocalPDFGeneration = async () => {
  try {
    Toast.loading({
      message: '正在本地生成PDF...',
      duration: 0,
      forbidClick: true
    });
    
    await generatePDFLocally();
    
    Toast.clear();
    Toast.success('本地PDF生成成功');
  } catch (error) {
    console.error('本地PDF生成失败:', error);
    Toast.clear();
    Toast.fail('本地PDF生成失败: ' + (error.message || '未知错误'));
  }
};

const reloadBaziData = async () => {
  Toast.loading('正在重新加载数据...');
  
  try {
    if (!resultId.value) {
      Toast.fail('缺少结果ID');
      return;
    }
    
    // 获取URL参数
    const urlParams = new URLSearchParams(window.location.search);
    
    // 尝试使用模拟支付接口
    try {
      console.log('尝试使用模拟支付接口...');
      
      // 显示加载提示
      Toast.loading({
        message: '正在分析八字，AI处理通常需要30-60秒，请耐心等待...',
        duration: 0,
        position: 'middle',
        forbidClick: true
      });
      
      // 准备请求数据
      const requestData = {
        birthDate: baziData.value.birthDate || urlParams.get('birthDate'),
        birthTime: baziData.value.birthTime || urlParams.get('birthTime'),
        gender: baziData.value.gender || urlParams.get('gender')
      };
      
      console.log('请求数据:', requestData);
      
      // 发送模拟支付请求
      const mockPaymentResponse = await axios.post(`/api/order/mock/pay/${resultId.value}`, requestData);
      console.log('模拟支付响应:', mockPaymentResponse.data);
      
      if (mockPaymentResponse.data.code === 200) {
        // 使用返回的resultId重新加载数据
        if (mockPaymentResponse.data.data && mockPaymentResponse.data.data.resultId) {
          const newResultId = mockPaymentResponse.data.data.resultId;
          console.log('获取到新的resultId:', newResultId);
          
          // 更新全局的resultId变量
          resultId.value = newResultId;
          // 还需要更新本地存储中的resultId
          localStorage.setItem('resultId', newResultId);
          
          const response = await axios.get(`/api/bazi/result/${newResultId}`);
          if (response.data.code === 200) {
            // 更新八字数据，使用空值合并运算符确保数据存在
            baziData.value = {
              yearPillar: response.data.data.baziChart?.yearPillar || null,
              monthPillar: response.data.data.baziChart?.monthPillar || null,
              dayPillar: response.data.data.baziChart?.dayPillar || null,
              hourPillar: response.data.data.baziChart?.hourPillar || null,
              fiveElements: response.data.data.baziChart?.fiveElements || null,
              flowingYears: response.data.data.baziChart?.flowingYears || [],
              shenSha: response.data.data.baziChart?.shenSha || {
                dayChong: "",
                zhiShen: "",
                pengZuGan: "",
                pengZuZhi: "",
                xiShen: "",
                fuShen: "",
                caiShen: "",
                benMing: [],
                yearGan: [],
                yearZhi: [],
                dayGan: [],
                dayZhi: []
              },
              daYun: response.data.data.baziChart?.daYun || {
                startAge: 1,
                startYear: new Date().getFullYear() + 1,
                isForward: true,
                daYunList: []
              },
              birthDate: response.data.data.baziChart?.birthDate || null,
              birthTime: response.data.data.baziChart?.birthTime || null,
              gender: response.data.data.baziChart?.gender || null
            };
            
            // 更新AI分析结果
            aiAnalysis.value = {
              health: response.data.data.aiAnalysis?.health || '',
              wealth: response.data.data.aiAnalysis?.wealth || '',
              career: response.data.data.aiAnalysis?.career || '',
              relationship: response.data.data.aiAnalysis?.relationship || '',
              children: response.data.data.aiAnalysis?.children || '',
              overall: response.data.data.aiAnalysis?.overall || '',
              personality: response.data.data.aiAnalysis?.personality || '',
              education: response.data.data.aiAnalysis?.education || '',
              parents: response.data.data.aiAnalysis?.parents || '',
              social: response.data.data.aiAnalysis?.social || '',
              future: response.data.data.aiAnalysis?.future || ''
            };
            
            Toast.success('数据加载成功');
            return;
          }
        } else {
          console.error('响应中缺少resultId');
          Toast.fail('响应格式不正确');
        }
      }
    } catch (mockError) {
      console.error('模拟支付失败:', mockError);
      Toast.fail('重新加载失败: ' + (mockError.message || '未知错误'));
      return;
    }
    
    // 如果模拟支付失败，尝试直接获取结果
    const response = await axios.get(`/api/bazi/result/${resultId.value}`);
    
    if (response.data.code === 200) {
      // 更新八字数据，使用空值合并运算符确保数据存在
      baziData.value = {
        yearPillar: response.data.data.baziChart?.yearPillar || null,
        monthPillar: response.data.data.baziChart?.monthPillar || null,
        dayPillar: response.data.data.baziChart?.dayPillar || null,
        hourPillar: response.data.data.baziChart?.hourPillar || null,
        fiveElements: response.data.data.baziChart?.fiveElements || null,
        flowingYears: response.data.data.baziChart?.flowingYears || [],
        shenSha: response.data.data.baziChart?.shenSha || {
          dayChong: "",
          zhiShen: "",
          pengZuGan: "",
          pengZuZhi: "",
          xiShen: "",
          fuShen: "",
          caiShen: "",
          benMing: [],
          yearGan: [],
          yearZhi: [],
          dayGan: [],
          dayZhi: []
        },
        daYun: response.data.data.baziChart?.daYun || {
          startAge: 1,
          startYear: new Date().getFullYear() + 1,
          isForward: true,
          daYunList: []
        },
        birthDate: response.data.data.baziChart?.birthDate || null,
        birthTime: response.data.data.baziChart?.birthTime || null,
        gender: response.data.data.baziChart?.gender || null
      };
      
      // 更新AI分析结果
      aiAnalysis.value = {
        health: response.data.data.aiAnalysis?.health || '',
        wealth: response.data.data.aiAnalysis?.wealth || '',
        career: response.data.data.aiAnalysis?.career || '',
        relationship: response.data.data.aiAnalysis?.relationship || '',
        children: response.data.data.aiAnalysis?.children || '',
        overall: response.data.data.aiAnalysis?.overall || '',
        personality: response.data.data.aiAnalysis?.personality || '',
        education: response.data.data.aiAnalysis?.education || '',
        parents: response.data.data.aiAnalysis?.parents || '',
        social: response.data.data.aiAnalysis?.social || '',
        future: response.data.data.aiAnalysis?.future || ''
      };
      
      Toast.success('数据加载成功');
    } else {
      Toast.fail(response.data.message || '加载失败');
    }
  } catch (error) {
    console.error('重新加载失败:', error);
    Toast.fail('加载失败: ' + (error.message || '未知错误'));
  }
};

// 追问相关状态
const followupOptions = ref([
  { id: 'marriage', name: '婚姻感情', selected: false, paid: false },
  { id: 'career', name: '事业财运', selected: false, paid: false },
  { id: 'children', name: '子女情况', selected: false, paid: false },
  { id: 'parents', name: '父母情况', selected: false, paid: false },
  { id: 'health', name: '身体健康', selected: false, paid: false },
  { id: 'education', name: '学业', selected: false, paid: false },
  { id: 'relationship', name: '人际关系', selected: false, paid: false },
  { id: 'fiveYears', name: '近五年运势', selected: false, paid: false }
]);

const currentFollowup = ref(null);
const showFollowupDialog = ref(false);
const followupAnalysis = ref({});
const isLoadingFollowup = ref(false);

// 选择追问选项
const selectFollowupOption = (option) => {
  // 如果已经支付过，直接显示结果
  if (option.paid) {
    // 显示已支付的分析结果
    currentFollowup.value = option;
    return;
  }
  
  // 否则设置当前选择的追问选项
  currentFollowup.value = option;
  showFollowupDialog.value = true;
};

// 支付追问费用
const payForFollowup = async () => {
  if (!currentFollowup.value) return;
  
  try {
    isLoadingFollowup.value = true;
    Toast.loading({
      message: '处理中...',
      forbidClick: true,
      duration: 0
    });
    
    // 获取URL参数
    const urlParams = new URLSearchParams(window.location.search);
    
    // 创建追问订单
    const orderResponse = await axios.post('/api/order/create/followup', {
      resultId: resultId.value,
      area: currentFollowup.value.id
    });
    
    if (orderResponse.data.code === 200) {
      const followupOrderId = orderResponse.data.data.orderId;
      console.log('追问订单创建成功:', followupOrderId);
      
      // 模拟支付
      const paymentResponse = await axios.post(`/api/order/mock/pay/${followupOrderId}`, {
        birthDate: baziData.value?.birthDate || urlParams.get('birthDate'),
        birthTime: baziData.value?.birthTime || urlParams.get('birthTime'),
        gender: baziData.value?.gender || urlParams.get('gender'),
        area: currentFollowup.value.id,
        resultId: resultId.value
      });
      
      if (paymentResponse.data.code === 200) {
        console.log('追问支付成功:', paymentResponse.data);
        
        // 获取并保存新的resultId（如果有的话）
        if (paymentResponse.data.data && paymentResponse.data.data.resultId) {
          const newResultId = paymentResponse.data.data.resultId;
          console.log('获取到新的resultId:', newResultId);
          // 更新全局的resultId变量
          resultId.value = newResultId;
          // 还需要更新本地存储中的resultId
          localStorage.setItem('resultId', newResultId);
        }
        
        // 获取追问分析结果
        await getFollowupAnalysis(currentFollowup.value.id);
        
        // 标记为已支付
        const index = followupOptions.value.findIndex(o => o.id === currentFollowup.value.id);
        if (index !== -1) {
          followupOptions.value[index].paid = true;
        }
        
        showFollowupDialog.value = false;
        Toast.success('分析完成');
      } else {
        Toast.fail('支付失败');
      }
    } else {
      Toast.fail('创建订单失败');
    }
  } catch (error) {
    console.error('追问支付过程出错:', error);
    Toast.fail('处理失败，请重试');
  } finally {
    isLoadingFollowup.value = false;
    Toast.clear();
  }
};

// 获取追问分析结果
const getFollowupAnalysis = async (area) => {
  loading.value = true;
  try {
    const response = await axios.get(`/api/bazi/followup/${resultId.value}/${area}`);
    
    if (response.data.code === 200) {
      console.log('获取追问分析成功:', response.data);
      followupAnalysis.value[area] = response.data.data.analysis;
      return response.data.data.analysis;
    } else {
      console.error('获取追问分析失败:', response.data);
      return null;
    }
  } catch (error) {
    console.error('获取追问分析出错:', error);
    return null;
  } finally {
    loading.value = false;
  }
};

// 检查已支付的追问
const checkPaidFollowups = async () => {
  try {
    const response = await axios.get(`/api/bazi/followup/list/${resultId.value}`);
    
    if (response.data.code === 200 && response.data.data.followups) {
      const paidFollowups = response.data.data.followups;
      
      // 更新已支付的追问选项
      followupOptions.value = followupOptions.value.map(option => {
        const isPaid = paidFollowups.some(f => f.area === option.id);
        if (isPaid) {
          // 如果已支付，获取分析结果
          getFollowupAnalysis(option.id);
        }
        return { ...option, paid: isPaid };
      });
    }
  } catch (error) {
    console.error('检查已支付追问出错:', error);
  }
};

// 修改getBaziResult函数
const getBaziResult = async () => {
  loading.value = true;
  try {
    console.log('获取八字分析结果，ID:', resultId.value);
    const response = await axios.get(`/api/bazi/result/${resultId.value}`);
    console.log('八字分析结果:', response.data);
    
    if (response.data.code === 200 && response.data.data) {
      // 更新八字数据，使用深度合并确保数据结构完整
      if (response.data.data.baziChart) {
        baziData.value = {
          yearPillar: response.data.data.baziChart.yearPillar || baziData.value.yearPillar,
          monthPillar: response.data.data.baziChart.monthPillar || baziData.value.monthPillar,
          dayPillar: response.data.data.baziChart.dayPillar || baziData.value.dayPillar,
          hourPillar: response.data.data.baziChart.hourPillar || baziData.value.hourPillar,
          fiveElements: response.data.data.baziChart.fiveElements || baziData.value.fiveElements,
          flowingYears: response.data.data.baziChart.flowingYears || [],
          shenSha: response.data.data.baziChart.shenSha || baziData.value.shenSha,
          daYun: response.data.data.baziChart.daYun || baziData.value.daYun,
          birthDate: response.data.data.baziChart.birthDate || null,
          birthTime: response.data.data.baziChart.birthTime || null,
          gender: response.data.data.baziChart.gender || null
        };
      } else {
        console.warn('响应中缺少baziChart数据');
        Toast.fail('数据格式不正确');
      }
      
      // 更新AI分析结果
      if (response.data.data.aiAnalysis) {
        aiAnalysis.value = {
          health: response.data.data.aiAnalysis.health || '',
          wealth: response.data.data.aiAnalysis.wealth || '',
          career: response.data.data.aiAnalysis.career || '',
          relationship: response.data.data.aiAnalysis.relationship || '',
          children: response.data.data.aiAnalysis.children || '',
          overall: response.data.data.aiAnalysis.overall || '',
          personality: response.data.data.aiAnalysis.personality || '',
          education: response.data.data.aiAnalysis.education || '',
          parents: response.data.data.aiAnalysis.parents || '',
          social: response.data.data.aiAnalysis.social || '',
          future: response.data.data.aiAnalysis.future || ''
        };
      }
      
      // 初始化追问选项
      initFollowupOptions();
      
      // 加载已支付的追问分析结果
      await loadFollowupResults();
      
      Toast.success('分析结果加载成功');
    } else {
      console.error('获取八字分析结果失败:', response.data.message);
      Toast.fail(response.data.message || '获取分析结果失败');
    }
  } catch (error) {
    console.error('获取八字分析结果出错:', error);
    Toast.fail('获取分析结果失败，请稍后再试');
  } finally {
    loading.value = false;
  }
};

// 添加缺失的函数
// 初始化追问选项
const initFollowupOptions = () => {
  // 根据用户年龄调整追问选项
  if (userAge.value !== null) {
    if (userAge.value < 6) {
      // 为婴幼儿调整选项
      followupOptions.value = followupOptions.value.filter(option => 
        ['health', 'personality', 'education', 'parents'].includes(option.id)
      );
    } else if (userAge.value < 18) {
      // 为未成年人调整选项
      followupOptions.value = followupOptions.value.filter(option => 
        !['marriage', 'career'].includes(option.id)
      );
    }
  }
  
  console.log('初始化追问选项完成:', followupOptions.value);
};

// 加载已支付的追问分析结果
const loadFollowupResults = async () => {
  try {
    // 检查是否有结果ID
    if (!resultId.value) {
      console.warn('缺少结果ID，无法加载追问分析');
      return;
    }
    
    // 调用API获取已支付的追问列表
    const response = await axios.get(`/api/bazi/followup/list/${resultId.value}`);
    
    if (response.data.code === 200 && response.data.data.followups) {
      const paidFollowups = response.data.data.followups;
      
      // 更新已支付的追问选项
      followupOptions.value = followupOptions.value.map(option => {
        const isPaid = paidFollowups.some(f => f.area === option.id);
        if (isPaid) {
          // 如果已支付，获取分析结果
          getFollowupAnalysis(option.id);
        }
        return { ...option, paid: isPaid };
      });
      
      console.log('已加载追问分析结果:', paidFollowups);
    }
  } catch (error) {
    console.error('加载追问分析结果出错:', error);
    // 出错时不显示错误提示，静默失败
  }
};

// 解析八字数据
const parseBaZiData = (data) => {
  if (!data) return null;
  
  return {
    yearPillar: data.yearPillar || { heavenlyStem: '未知', earthlyBranch: '未知' },
    monthPillar: data.monthPillar || { heavenlyStem: '未知', earthlyBranch: '未知' },
    dayPillar: data.dayPillar || { heavenlyStem: '未知', earthlyBranch: '未知' },
    hourPillar: data.hourPillar || { heavenlyStem: '未知', earthlyBranch: '未知' },
    shenSha: data.shenSha || {
      dayChong: '未知',
      zhiShen: '未知',
      pengZuGan: '未知',
      pengZuZhi: '未知',
      xiShen: '未知',
      fuShen: '未知',
      caiShen: '未知',
      benMing: [],
      yearGan: [],
      yearZhi: [],
      dayGan: [],
      dayZhi: []
    },
    daYun: data.daYun || {
      startAge: 0,
      startYear: 0,
      isForward: true,
      daYunList: []
    },
    flowingYears: data.flowingYears || []
  };
};

// 在mounted或created钩子中调用
onMounted(async () => {
  // ... existing code ...
  
  try {
    // 修改为正确的API端点
    const response = await axios.get(`/api/bazi/result/${resultId.value}`);
    if (response.data.code === 200) {
      const analysisData = response.data.data;
      // 解析八字数据
      const baziData = parseBaZiData(analysisData.baziChart);
      
      // 更新状态
      analysisResult.value = {
        ...analysisData,
        baziData
      };
      
      // 初始化完成
      loading.value = false;
    }
  } catch (error) {
    console.error('加载分析结果失败:', error);
    loading.value = false;
  }
});
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

.four-pillars {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
}

.pillar {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f5f7fa;
  padding: 10px;
  border-radius: 8px;
  width: 80px;
}

.stem, .branch {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  margin: 4px 0;
  border-radius: 4px;
}

.stem {
  background: #1989fa;
  color: white;
}

.branch {
  background: #07c160;
  color: white;
}

.label {
  font-size: 12px;
  color: #646566;
  margin-top: 4px;
}

.nayin, .shishen, .wangshuai {
  font-size: 12px;
  color: #323233;
  margin-top: 4px;
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

.shen-sha-info {
  margin-bottom: 20px;
}

.da-yun-info {
  margin-bottom: 20px;
}

.qi-yun-info {
  margin: 0 0 10px;
  font-size: 14px;
  color: #646566;
}

.da-yun-table {
  margin-top: 10px;
}

.placeholder {
  background-color: #f2f3f5;
  color: #969799;
}

/* 追问部分样式 */
.followup-section {
  margin-top: 20px;
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.section-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
}

.followup-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.followup-option {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.followup-option:hover {
  background-color: #e8f0fe;
}

.followup-option.paid {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
}

.option-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.option-name {
  font-size: 15px;
  font-weight: 500;
}

.option-status {
  font-size: 13px;
  color: #ff6b00;
}

.followup-option.paid .option-status {
  color: #52c41a;
}

.followup-result {
  margin-top: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #1989fa;
}

.followup-result h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #333;
}

.analysis-content {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
}

.followup-dialog-content {
  padding: 15px;
  text-align: center;
}

/* 添加表格样式 */
.custom-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  margin: 10px 0;
  background-color: #fff;
  color: #323233;
  font-size: 14px;
}

.custom-table th,
.custom-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #ebedf0;
  text-align: center;
}

.custom-table th {
  font-weight: 500;
  background-color: #f7f8fa;
  color: #646566;
}

.custom-table tr:hover {
  background-color: #f2f3f5;
}
</style>
