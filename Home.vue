<template>
  <div class="home-container">
    <van-nav-bar title="八字命理AI人生指导" />
    
    <div class="banner">
      <img src="../assets/banner.png" alt="八字命理AI人生指导" class="banner-img">
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
          readonly
          clickable
          name="birthDate"
          :value="formData.birthDate"
          label="出生日期"
          placeholder="点击选择日期"
          @click="showDatePicker = true"
        />
        <van-popup v-model:show="showDatePicker" position="bottom">
          <van-datetime-picker
            v-model="currentDate"
            type="date"
            title="选择出生日期"
            :min-date="new Date(1900, 0, 1)"
            :max-date="new Date()"
            @confirm="onConfirmDate"
            @cancel="showDatePicker = false"
          />
        </van-popup>
        
        <van-field
          readonly
          clickable
          name="birthTime"
          :value="formData.birthTime"
          label="出生时辰"
          placeholder="点击选择时辰"
          @click="showTimePicker = true"
        />
        <van-popup v-model:show="showTimePicker" position="bottom">
          <van-picker
            show-toolbar
            title="选择出生时辰"
            :columns="timeColumns"
            @confirm="onConfirmTime"
            @cancel="showTimePicker = false"
          />
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

<script>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';

export default {
  name: 'HomePage',
  setup() {
    const router = useRouter();
    const showDatePicker = ref(false);
    const showTimePicker = ref(false);
    const currentDate = ref(new Date());
    
    const timeColumns = [
      '子时 (23:00-01:00)',
      '丑时 (01:00-03:00)',
      '寅时 (03:00-05:00)',
      '卯时 (05:00-07:00)',
      '辰时 (07:00-09:00)',
      '巳时 (09:00-11:00)',
      '午时 (11:00-13:00)',
      '未时 (13:00-15:00)',
      '申时 (15:00-17:00)',
      '酉时 (17:00-19:00)',
      '戌时 (19:00-21:00)',
      '亥时 (21:00-23:00)'
    ];
    
    const formData = reactive({
      gender: 'male',
      calendarType: 'solar',
      birthDate: '',
      birthTime: '',
      focusAreas: []
    });
    
    const onConfirmDate = (value) => {
      formData.birthDate = `${value.getFullYear()}-${value.getMonth() + 1}-${value.getDate()}`;
      showDatePicker.value = false;
    };
    
    const onConfirmTime = (value) => {
      formData.birthTime = value;
      showTimePicker.value = false;
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
    
    return {
      formData,
      showDatePicker,
      showTimePicker,
      currentDate,
      timeColumns,
      onConfirmDate,
      onConfirmTime,
      onSubmit
    };
  }
};
</script>

<style scoped>
.home-container {
  padding-bottom: 20px;
}

.banner {
  text-align: center;
  padding: 20px 0;
  background-color: #f2f3f5;
}

.banner-img {
  width: 80%;
  max-width: 300px;
  margin-bottom: 10px;
}

.slogan {
  font-size: 16px;
  color: #323233;
  margin: 0;
}

.intro-section {
  padding: 20px 16px;
}

.intro-section h3 {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #323233;
}

.intro-section p {
  margin: 0;
  font-size: 14px;
  color: #646566;
  line-height: 1.5;
}
</style>
