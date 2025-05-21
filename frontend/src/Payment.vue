<template>
  <div class="payment-container">
    <van-nav-bar
      title="订单支付"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
    />
    
    <van-card
      title="八字命理AI人生指导"
      desc="个性化人生指导建议"
      price="9.90"
      currency="¥"
    >
      <template #tags>
        <van-tag plain type="primary">专业分析</van-tag>
        <van-tag plain type="success">AI解读</van-tag>
        <van-tag plain type="warning">PDF报告</van-tag>
      </template>
    </van-card>
    
    <van-cell-group inset title="订单信息">
      <van-cell title="订单编号" :value="orderId" />
      <van-cell title="创建时间" :value="createTime" />
      <van-cell title="支付金额" value="¥9.90" />
    </van-cell-group>
    
    <van-cell-group inset title="选择支付方式">
      <van-cell clickable @click="paymentMethod = 'wechat'">
        <template #title>
          <div class="payment-method">
            <van-icon name="wechat" color="#07C160" size="24" />
            <span class="payment-name">微信支付</span>
          </div>
        </template>
        <template #right-icon>
          <van-radio :name="'wechat'" :checked="paymentMethod === 'wechat'" />
        </template>
      </van-cell>
      
      <van-cell clickable @click="paymentMethod = 'alipay'">
        <template #title>
          <div class="payment-method">
            <van-icon name="alipay" color="#1677FF" size="24" />
            <span class="payment-name">支付宝</span>
          </div>
        </template>
        <template #right-icon>
          <van-radio :name="'alipay'" :checked="paymentMethod === 'alipay'" />
        </template>
      </van-cell>
    </van-cell-group>
    
    <div class="payment-action">
      <van-button round block type="primary" @click="onPayment">
        立即支付
      </van-button>
    </div>
    
    <van-popup :show="showQRCode" @update:show="showQRCode = $event" round>
      <div class="qrcode-container">
        <h3>请扫码支付</h3>
        <div class="qrcode">
          <iframe v-if="qrCodeUrl" :src="qrCodeUrl" frameborder="0" width="200" height="200"></iframe>
          <div v-else class="qrcode-placeholder">
            <p>正在加载支付二维码...</p>
          </div>
        </div>
        <p>支付金额: ¥9.90</p>
        <van-button type="primary" block @click="onPaymentSuccess">
          支付完成
        </van-button>
      </div>
    </van-popup>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Toast } from 'vant';

export default {
  name: 'PaymentPage',
  setup() {
    const route = useRoute();
    const router = useRouter();
    
    // 从路由参数获取订单信息
    const gender = route.query.gender;
    const calendarType = route.query.calendarType;
    const birthDate = route.query.birthDate;
    const birthTime = route.query.birthTime;
    const birthPlace = route.query.birthPlace;
    const livingPlace = route.query.livingPlace;
    const focusAreas = route.query.focusAreas?.split(',') || [];
    
    // 支付相关状态
    const orderId = ref('BZ' + Date.now().toString());
    const createTime = ref(new Date().toLocaleString());
    const paymentMethod = ref('wechat');
    const showQRCode = ref(false);
    const qrCodeUrl = ref('');
    
    onMounted(() => {
      // 实际项目中这里应该调用API创建订单
      console.log('订单创建成功', {
        gender,
        calendarType,
        birthDate,
        birthTime,
        birthPlace,
        livingPlace,
        focusAreas
      });
    });
    
    const onClickLeft = () => {
      router.go(-1);
    };
    
    const onPayment = () => {
      // 根据支付方式显示不同的二维码
      if (paymentMethod.value === 'wechat') {
        // 使用本地HTML文件作为微信支付二维码
        qrCodeUrl.value = '/images/wechat-qrcode.html';
      } else {
        // 使用本地HTML文件作为支付宝二维码
        qrCodeUrl.value = '/images/alipay-qrcode.html';
      }
      
      showQRCode.value = true;
      
      // 实际项目中这里应该调用API获取支付二维码
      console.log('发起支付请求', {
        orderId: orderId.value,
        paymentMethod: paymentMethod.value
      });

      // 由于我们只是演示，记录一下二维码URL
      console.log(`使用${paymentMethod.value}支付，二维码URL:`, qrCodeUrl.value);
    };
    
    const onPaymentSuccess = () => {
      Toast.success('支付成功');
      showQRCode.value = false;
      
      // 模拟支付成功后的结果ID
      const resultId = 'RES' + Date.now().toString();
      
      // 跳转到结果页面
      router.push(`/result/${resultId}`);
    };
    
    return {
      orderId,
      createTime,
      paymentMethod,
      showQRCode,
      qrCodeUrl,
      onClickLeft,
      onPayment,
      onPaymentSuccess
    };
  }
};
</script>

<style scoped>
.payment-container {
  padding-bottom: 20px;
}

.payment-method {
  display: flex;
  align-items: center;
}

.payment-name {
  margin-left: 10px;
}

.payment-action {
  padding: 20px 16px;
}

.qrcode-container {
  padding: 20px;
  text-align: center;
  width: 280px;
}

.qrcode {
  width: 200px;
  height: 200px;
  margin: 20px auto;
  background-color: #f2f3f5;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ebedf0;
  border-radius: 4px;
  overflow: hidden;
}

.qrcode iframe {
  border: none;
  width: 100%;
  height: 100%;
}

.qrcode img {
  max-width: 100%;
  max-height: 100%;
}

.qrcode-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #969799;
}
</style>
