<template>
  <div class="home-container">
    <van-nav-bar title="八字命理AI人生指导" />
    
    <div class="banner">
      <img src="./assets/banner.png" alt="八字命理AI人生指导" class="banner-img">
      <h2 class="slogan">传统命理 · 现代科技 · 智慧人生</h2>
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
        
        <van-field
          v-model="formData.birthDate"
          readonly
          clickable
          name="birthDate"
          label="出生日期"
          placeholder="点击选择日期"
          @click="showDatePicker = true"
        />
        <van-popup :show="showDatePicker" @update:show="showDatePicker = $event" position="bottom">
          <van-date-picker
            :model-value="[currentDate.getFullYear(), currentDate.getMonth() + 1, currentDate.getDate()]"
            @update:model-value="val => currentDate = new Date(val[0], val[1] - 1, val[2])"
            title="选择出生日期"
            :min-date="new Date(1900, 0, 1)"
            :max-date="new Date()"
            :columns-type="['year', 'month', 'day']"
            swipe-duration="300"
            :item-height="44"
            visible-item-count="5"
            @confirm="onConfirmDate"
            @cancel="showDatePicker = false"
          />
        </van-popup>
        
        <van-field
          v-model="formData.birthTime"
          readonly
          clickable
          name="birthTime"
          label="出生时辰"
          placeholder="点击选择时辰"
          @click="showTimePicker = true"
        />
        <van-popup :show="showTimePicker" @update:show="showTimePicker = $event" position="bottom" style="max-height: 70vh;">
          <div class="time-selector">
            <div class="time-selector-header">
              <van-button size="small" type="default" @click="showTimePicker = false">取消</van-button>
              <div class="time-selector-title">选择出生时辰</div>
              <van-button size="small" type="primary" @click="showTimePicker = false">确定</van-button>
            </div>
            <div class="time-selector-content">
              <van-cell
                v-for="(time, index) in timeData"
                :key="index"
                :title="time.text"
                clickable
                @click="selectTime(time.text)"
                :class="{ 'time-active': formData.birthTime === time.text }"
              />
            </div>
          </div>
        </van-popup>
        
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
      <h3>八字命理AI人生指导系统</h3>
      <p>本系统结合传统八字命理理论与现代人工智能技术，为您提供个性化的人生指导建议。通过分析您的八字命盘和流年大运信息，AI将为您解读人生各方面的发展趋势和潜在机遇。</p>
      
      <h3>使用流程</h3>
      <van-steps direction="vertical" :active="0">
        <van-step>
          <h3>填写信息</h3>
          <p>输入性别、出生年月日时和关注领域</p>
        </van-step>
        <van-step>
          <h3>完成支付</h3>
          <p>支付9.9元获取专业分析</p>
        </van-step>
        <van-step>
          <h3>AI分析</h3>
          <p>系统计算八字并通过AI进行解读</p>
        </van-step>
        <van-step>
          <h3>查看结果</h3>
          <p>获取详细分析报告并可下载PDF</p>
        </van-step>
      </van-steps>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';

const router = useRouter();
const showDatePicker = ref(false);
const showTimePicker = ref(false);
const currentDate = ref(new Date());

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
  focusAreas: []
});

const formatDate = (date) => {
  // 确保月份和日期为两位数
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  return `${date.getFullYear()}-${month}-${day}`;
};

const onConfirmDate = (value) => {
  // 检查value是否为数组，如果不是则使用当前日期
  if (Array.isArray(value)) {
    const [year, month, day] = value;
    // 格式化月份和日期为两位数
    const formattedMonth = month.toString().padStart(2, '0');
    const formattedDay = day.toString().padStart(2, '0');
    formData.birthDate = `${year}-${formattedMonth}-${formattedDay}`;
  } else if (value && typeof value === 'object' && value.getFullYear) {
    // 如果是Date对象，使用格式化函数
    formData.birthDate = formatDate(value);
  } else {
    // 如果value不是数组也不是Date，使用currentDate的值
    formData.birthDate = formatDate(currentDate.value);
  }
  
  // 确保关闭日期选择器并打印调试信息
  console.log('选择的日期:', formData.birthDate);
  showDatePicker.value = false;
};

const selectTime = (time) => {
  formData.birthTime = time;
  showTimePicker.value = false;
  console.log('选择的时辰:', formData.birthTime);
};

const onSubmit = () => {
  // 表单验证
  if (!formData.birthDate) {
    showToast('请选择出生日期');
    return;
  }
  
  if (!formData.birthTime) {
    showToast('请选择出生时辰');
    return;
  }
  
  if (formData.focusAreas.length === 0) {
    showToast('请至少选择一个推算侧重点');
    return;
  }
  
  // 创建订单并跳转到支付页面
  // 实际项目中这里应该调用API创建订单
  router.push({
    path: '/payment',
    query: {
      gender: formData.gender,
      calendarType: formData.calendarType,
      birthDate: formData.birthDate,
      birthTime: formData.birthTime,
      focusAreas: formData.focusAreas.join(',')
    }
  });
};
</script>

<style>
.home-container {
  padding-bottom: 20px;
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

.time-selector {
  background-color: #fff;
  width: 100%;
}

.time-selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid #ebedf0;
}

.time-selector-title {
  font-size: 16px;
  font-weight: 500;
}

.time-selector-content {
  max-height: 60vh;
  overflow-y: auto;
}

.time-active {
  color: #1989fa;
  font-weight: bold;
}
</style>
