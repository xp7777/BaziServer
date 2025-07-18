<template>
  <div class="home-container">
    <van-nav-bar title="八字命理人生指导" />
    
    <div class="banner">
      <img src="./assets/banner11.png" alt="八字命理AI人生指导" class="banner-img">
      <h2 class="slogan">传统文化 · 现代科技 · 智慧人生</h2>
    </div>
    
    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field name="gender" label="性别">
          <template #input>
            <van-radio-group v-model="formData.gender" direction="horizontal">
              <van-radio name="male">男</van-radio>
              <van-radio name="female">女</van-radio>
            </van-radio-group>
          </template>
        </van-field>
        
        <van-field name="calendarType" label="历法选择">
          <template #input>
            <van-radio-group v-model="formData.calendarType" direction="horizontal">
              <van-radio name="solar">公历</van-radio>
              <van-radio name="lunar">农历</van-radio>
            </van-radio-group>
          </template>
        </van-field>
        
        <van-field name="birthDate" label="出生日期">
          <template #input>
            <input 
              type="date" 
              v-model="formData.birthDate"
              min="1900-01-01" 
              max="2100-12-31"
              class="native-date-picker"
            />
          </template>
        </van-field>
        
        <van-field name="birthTime" label="出生时辰">
          <template #input>
            <select v-model="formData.birthTime" class="native-time-picker">
              <option value="">请选择时辰</option>
              <option 
                v-for="(time, index) in timeData"
                :key="index"
                :value="time.text"
              >
                {{ time.text }}
              </option>
            </select>
          </template>
        </van-field>
        
        <van-field 
          v-model="formData.birthPlace" 
          name="birthPlace" 
          label="出生地" 
          placeholder="请输入出生地（如：北京市海淀区）"
          :rules="[{ required: true, message: '请填写出生地' }]"
        />
        
        <van-field 
          v-model="formData.livingPlace" 
          name="livingPlace" 
          label="居住地" 
          placeholder="请输入当前居住地（如：上海市浦东新区）"
          :rules="[{ required: true, message: '请填写居住地' }]"
        />
        
        <van-field name="focusAreas" label="推算侧重点">
          <template #input>
            <van-checkbox-group v-model="formData.focusAreas" direction="horizontal">
              <van-checkbox name="health">身体健康</van-checkbox>
              <van-checkbox name="wealth">财运</van-checkbox>
              <van-checkbox name="career">事业</van-checkbox>
              <van-checkbox name="relationship">婚姻感情</van-checkbox>
              <van-checkbox name="children">子女</van-checkbox>
            </van-checkbox-group>
          </template>
        </van-field>
      </van-cell-group>
      
      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit">
          提交并支付 (9.9元)
        </van-button>
      </div>
    </van-form>
    
    <div class="intro-section">
      <h3>人生规划指导系统</h3>
      <p>本系统结合传统国学理论与现代科技，为您提供个性化的人生指导建议。通过分析您的个人信息，为您解读人生各方面的发展趋势和潜在机遇，规划好您的人生之路。</p>
      
      <h3>使用流程</h3>
      <van-steps direction="vertical" :active="0">
        <van-step>
          <h3>填写信息</h3>
          <p>输入性别、出生年月日时、出生地、居住地和重点关注领域</p>
        </van-step>
        <van-step>
          <h3>完成支付</h3>
          <p>支付9.9元获取专业分析</p>
        </van-step>
        <van-step>
          <h3>等待分析结果</h3>
          <p>系统进行计算分析，并进行解读</p>
        </van-step>
        <van-step>
          <h3>查看结果</h3>
          <p>获取详细分析报告并可下载PDF</p>
        </van-step>
      </van-steps>
      <p style="text-align: center;">如果有问题，请加V guiguziwenhua 解决。</p>
    </div>
    
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Toast } from 'vant';

const router = useRouter();

// 重新定义时辰数据为正确的格式
const timeData = [
  { text: '子时 (23:00-01:00)' },
  { text: '丑时 (01:00-03:00)' },
  { text: '寅时 (03:00-05:00)' },
  { text: '卯时 (05:00-07:00)' },
  { text: '辰时 (07:00-09:00)' },
  { text: '巳时 (09:00-11:00)' },
  { text: '午时 (11:00-13:00)' },
  { text: '未时 (13:00-15:00)' },
  { text: '申时 (15:00-17:00)' },
  { text: '酉时 (17:00-19:00)' },
  { text: '戌时 (19:00-21:00)' },
  { text: '亥时 (21:00-23:00)' }
];

const formData = reactive({
  gender: 'male',
  calendarType: 'solar',
  birthDate: '',
  birthTime: '',
  birthPlace: '',
  livingPlace: '',
  focusAreas: []
});

// 检查登录状态
const checkLoginStatus = () => {
  const token = localStorage.getItem('userToken');
  const userInfo = localStorage.getItem('userInfo');
  
  if (!token || !userInfo) {
    Toast.fail('请先登录');
    router.push('/login');
    return false;
  }
  return true;
};

const onSubmit = () => {
  // 首先检查登录状态
  if (!checkLoginStatus()) {
    return;
  }
  
  // 表单验证
  if (!formData.birthDate) {
    Toast.fail('请选择出生日期');
    return;
  }
  
  if (!formData.birthTime) {
    Toast.fail('请选择出生时辰');
    return;
  }
  
  if (!formData.birthPlace) {
    Toast.fail('请填写出生地');
    return;
  }
  
  if (!formData.livingPlace) {
    Toast.fail('请填写居住地');
    return;
  }
  
  if (formData.focusAreas.length === 0) {
    Toast.fail('请至少选择一个推算侧重点');
    return;
  }
  
  // 创建订单并跳转到支付页面
  console.log('提交数据:', formData);
  router.push({
    path: '/payment',
    query: {
      gender: formData.gender,
      calendarType: formData.calendarType,
      birthDate: formData.birthDate,
      birthTime: formData.birthTime,
      birthPlace: formData.birthPlace,
      livingPlace: formData.livingPlace,
      focusAreas: formData.focusAreas.join(',')
    }
  });
};

// 组件挂载时检查登录状态
onMounted(() => {
  checkLoginStatus();
});
</script>

<style>
.home-container {
  padding-bottom: 20px;
  background-color: #ffffff; /* 添加白色背景 */
  min-height: 100vh; /* 确保全屏白色 */
}

.banner {
  text-align: center;
  padding: 20px 15px;
  background-color: #f7f8fa;
}

.banner-img {
  width: 100%;
  max-width: 300px;
  border-radius: 8px;
}

.slogan {
  margin-top: 10px;
  font-size: 16px;
  color: #666;
}

.intro-section {
  padding: 20px 16px;
  background-color: #fff;
  margin-top: 20px;
}

.intro-section h3 {
  margin-bottom: 10px;
  font-size: 18px;
  color: #323233;
}

.intro-section p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 20px;
}

.native-date-picker,
.native-time-picker {
  width: 100%;
  height: 24px;
  border: none;
  padding: 0;
  background-color: transparent;
}

</style> 
