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
          <img v-if="qrCodeUrl && qrCodeUrl.startsWith('data:')" :src="qrCodeUrl" alt="支付二维码" />
          <iframe v-else-if="qrCodeUrl" :src="qrCodeUrl" frameborder="0" width="200" height="200"></iframe>
          <div v-else class="qrcode-placeholder">
            <p>正在加载支付二维码...</p>
          </div>
        </div>
        <p>支付金额: ¥9.90</p>
        <van-button type="primary" block @click="checkPaymentStatus">
          我已完成支付
        </van-button>
        <van-button plain block @click="showQRCode = false" style="margin-top: 10px">
          取消
        </van-button>
      </div>
    </van-popup>
  </div>
</template>

<script>
import { ref, onMounted, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Toast } from 'vant';
import axios from 'axios';

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
    const orderId = ref('');
    const createTime = ref(new Date().toLocaleString());
    const paymentMethod = ref('wechat');
    const showQRCode = ref(false);
    const qrCodeUrl = ref('');
    const isProcessing = ref(false);
    
    onMounted(async () => {
      // 调用API创建订单
      try {
        Toast.loading({
          message: '正在创建订单...',
          duration: 0,
          forbidClick: true
        });
        
        // 调用订单创建API
        const response = await axios.post('/api/order/create/simple', {
          gender,
          birthDate,
          birthTime,
          birthPlace,
          livingPlace,
          focusAreas: focusAreas || [],
          calendarType: calendarType || 'solar'
        });
        
        if (response.data.code === 200) {
          orderId.value = response.data.data.orderId;
          createTime.value = new Date().toLocaleString();
          Toast.success('订单创建成功');
          console.log('订单创建成功', orderId.value);
        } else {
          Toast.fail(response.data.message || '创建订单失败');
        }
      } catch (error) {
        console.error('创建订单失败:', error);
        Toast.fail('创建订单失败，请重试');
      }
    });
    
    const onClickLeft = () => {
      router.go(-1);
    };
    
    const onPayment = () => {
      // 检查订单ID
      if (!orderId.value) {
        Toast.fail('订单尚未创建，请刷新页面重试');
        return;
      }
      
      // 根据支付方式获取真实二维码
      Toast.loading({
        message: '正在获取支付二维码...',
        duration: 0,
        forbidClick: true
      });
      
      // 创建真实支付订单并获取支付二维码
      const createPayment = async () => {
        try {
          const paymentData = {
            paymentMethod: paymentMethod.value,
            birthDate,
            birthTime,
            gender,
            focusAreas,
            calendarType,
            birthPlace,
            livingPlace
          };
          
          // 调用真实支付API
          const response = await axios.post(`/api/order/create/payment/${orderId.value}`, paymentData);
          
          if (response.data.code === 200) {
            Toast.clear();
            
            // 解析支付二维码返回数据
            if (response.data.data.qr_image) {
              // 直接使用Base64二维码图片
              qrCodeUrl.value = response.data.data.qr_image;
              showQRCode.value = true;
            } else if (response.data.data.code_url) {
              // 生成二维码图片
              qrCodeUrl.value = response.data.data.code_url;
              showQRCode.value = true;
            } else if (response.data.data.pay_url) {
              // 支付宝URL
              window.open(response.data.data.pay_url, '_blank');
            } else {
              Toast.fail('未获取到支付二维码');
            }
          } else {
            Toast.fail(response.data.message || '获取支付二维码失败');
          }
        } catch (error) {
          console.error('获取支付二维码出错:', error);
          Toast.fail('获取支付二维码失败');
        }
      };
      
      createPayment();
    };
    
    const onPaymentSuccess = async () => {
      if (isProcessing.value) {
        return false;
      }
      
      isProcessing.value = true;
      Toast.loading({
        message: '正在查询支付结果...',
        duration: 0,
        forbidClick: true
      });
      
      try {
        // 查询支付结果API
        console.log('查询支付结果:', orderId.value);
        
        // 增加重试次数，微信支付状态更新可能有延迟
        let retryCount = 0;
        const maxRetries = 3;
        let response;
        let paymentSuccess = false;
        
        // 重试查询支付状态
        while (retryCount < maxRetries && !paymentSuccess) {
          response = await axios.get(`/api/order/query/${orderId.value}`);
          console.log(`支付查询响应 (尝试 ${retryCount + 1}/${maxRetries}):`, response.data);
          
          if (response.data.code === 200 && response.data.data.status === 'paid') {
            paymentSuccess = true;
            break;
          }
          
          // 如果查询失败，等待2秒后重试
          if (!paymentSuccess) {
            await new Promise(resolve => setTimeout(resolve, 2000));
            retryCount++;
          }
        }
        
        // 如果重试后仍未成功，尝试手动更新接口
        if (!paymentSuccess) {
          console.log('查询支付状态失败，尝试手动更新订单状态');
          response = await axios.get(`/api/order/manual_update/${orderId.value}`);
          console.log('手动更新响应:', response.data);
          paymentSuccess = (response.data.code === 200 && response.data.data.status === 'paid');
        }
        
        if (paymentSuccess) {
          Toast.success('支付成功');
          showQRCode.value = false;
          
          // 使用服务器返回的resultId
          const resultId = response.data.data.resultId;
          
          if (!resultId) {
            console.error('服务器未返回有效的resultId');
            // 生成默认结果ID并尝试手动更新
            const defaultResultId = 'RES' + orderId.value.replace(/^BZ/, '');
            console.log('使用默认结果ID:', defaultResultId);
            
            try {
              // 尝试手动更新获取结果ID
              const manualResponse = await axios.get(`/api/order/manual_update/${orderId.value}`);
              console.log('手动更新响应:', manualResponse.data);
              
              if (manualResponse.data.code === 200 && manualResponse.data.data.resultId) {
                // 使用手动更新返回的resultId
                const updatedResultId = manualResponse.data.data.resultId;
                console.log('手动更新成功，获取到结果ID:', updatedResultId);
                
                // 继续处理计算和分析
                await processBaziCalculation(updatedResultId);
                
                // 跳转到结果页面
                redirectToResultPage(updatedResultId);
                return;
              } else {
                Toast.fail('无法获取有效的结果ID，将使用默认ID');
                await processBaziCalculation(defaultResultId);
                redirectToResultPage(defaultResultId);
                return;
              }
            } catch (manualError) {
              console.error('手动更新失败:', manualError);
              Toast.fail('获取结果ID失败，使用默认ID');
              await processBaziCalculation(defaultResultId);
              redirectToResultPage(defaultResultId);
              return;
            }
          }
          
          console.log('获取到结果ID:', resultId);
          
          // 请求立即计算完整的命盘数据
          await processBaziCalculation(resultId);
          
          // 跳转到结果页面
          redirectToResultPage(resultId);
        } else {
          Toast.fail(response?.data?.message || '支付处理失败');
          isProcessing.value = false;
        }
      } catch (error) {
        console.error('支付处理出错:', error);
        
        // 错误处理：尝试构造默认结果ID
        Toast.clear();
        Toast.fail('支付处理出错，将使用默认结果ID');
        
        // 构造默认结果ID
        const defaultResultId = 'RES' + orderId.value.replace(/^BZ/, '');
        console.log('使用默认结果ID:', defaultResultId);
        
        // 尝试计算和跳转
        await processBaziCalculation(defaultResultId);
        
        // 即使出错也跳转到结果页面，使用默认结果ID
        redirectToResultPage(defaultResultId);
      } finally {
        isProcessing.value = false;
      }
    };
    
    // 提取八字计算过程为独立函数
    const processBaziCalculation = async (resultId) => {
      try {
        Toast.loading({
          message: '正在生成八字命盘...',
          duration: 0,
          forbidClick: true
        });
        
        // 获取基础URL，确保在不同环境下都能正确请求API
        const baseUrl = process.env.VUE_APP_API_URL || window.location.origin;
        console.log('使用API基础URL:', baseUrl);
        
        // 添加重试机制
        let retryCount = 0;
        const maxRetries = 3;
        let updateSuccess = false;
        
        while (retryCount < maxRetries && !updateSuccess) {
          try {
            // 修改：使用正确的update API端点
            console.log(`正在请求更新八字数据 (尝试 ${retryCount + 1}/${maxRetries}):`, resultId);
            const updateResponse = await axios.post(`${baseUrl}/api/bazi/update/${resultId}`, {
              birthDate,
              birthTime,
              gender,
              calendarType,
              birthPlace,
              livingPlace,
              focusAreas,
              forceRecalculate: true,        // 强制重新计算基础数据
              generateShenshaData: true,     // 生成神煞数据
              generateDayunData: true,       // 生成大运数据 
              generateLiunianData: true,     // 生成流年数据
              useDeepseekAPI: true           // 使用DeepSeek API进行分析
            });
            
            console.log('八字数据更新响应:', updateResponse.data);
            
            if (updateResponse.data.code === 200) {
              updateSuccess = true;
              Toast.success('命盘数据生成中');
              
              // 确保延迟足够长，以便后端完成八字数据处理
              setTimeout(async () => {
                try {
                  console.log('正在请求八字深度分析:', resultId);
                  const analyzeResponse = await axios.post(`${baseUrl}/api/bazi/analyze/${resultId}`, {
                    useDeepseekAPI: true
                  });
                  console.log('八字深度分析响应:', analyzeResponse.data);
                  Toast.success('命盘分析已开始');
                } catch (analyzeError) {
                  console.error('深度分析请求失败:', analyzeError);
                  // 即使分析请求失败，也继续流程，不阻止用户查看结果
                  Toast.fail('命盘深度分析请求失败，但可以继续查看基础结果');
                }
              }, 3000); // 延长等待时间到3秒
              
              break; // 成功后跳出循环
            } else {
              console.error('八字数据更新失败:', updateResponse.data.message);
              // 失败后重试
              await new Promise(resolve => setTimeout(resolve, 1000));
              retryCount++;
            }
          } catch (error) {
            console.error(`更新请求失败 (尝试 ${retryCount + 1}/${maxRetries}):`, error);
            
            // 如果是404错误，可能是结果记录还未创建，尝试手动更新订单状态
            if (error.response && error.response.status === 404) {
              console.log('结果记录不存在，尝试手动更新订单状态');
              try {
                const manualResponse = await axios.get(`${baseUrl}/api/order/manual_update/${orderId.value}`);
                console.log('手动更新响应:', manualResponse.data);
                
                if (manualResponse.data.code === 200 && manualResponse.data.data.resultId) {
                  // 使用手动更新返回的resultId
                  const updatedResultId = manualResponse.data.data.resultId;
                  console.log('手动更新成功，获取到新的结果ID:', updatedResultId);
                  
                  // 更新当前使用的resultId
                  resultId = updatedResultId;
                }
              } catch (manualError) {
                console.error('手动更新失败:', manualError);
              }
            }
            
            // 失败后重试
            await new Promise(resolve => setTimeout(resolve, 1000));
            retryCount++;
          }
        }
        
        if (!updateSuccess) {
          Toast.fail('命盘计算请求失败，请稍后在结果页面刷新重试');
          console.error('达到最大重试次数，八字数据更新失败');
        }
      } catch (calcError) {
        console.error('命盘计算请求失败:', calcError);
        Toast.fail('命盘计算请求失败，但您仍可以查看结果页面');
      }
    };
    
    // 添加结果页面跳转函数
    const redirectToResultPage = (resultId) => {
      // 延迟跳转，给用户体验更好的过渡
      setTimeout(() => {
        router.push({
          path: `/result/${resultId}`,
          query: {
            birthDate,
            birthTime,
            gender,
            birthPlace,
            livingPlace,
            originalOrderId: orderId.value // 传递原始订单ID
          }
        });
      }, 1000);
    };
    
    const checkPaymentStatus = async () => {
      if (isProcessing.value) return;
      
      isProcessing.value = true;
      Toast.loading({
        message: '正在查询支付状态...',
        duration: 0,
        forbidClick: true
      });
      
      try {
        const response = await axios.get(`/api/order/query/${orderId.value}`);
        console.log('支付状态查询响应:', response.data);
        
        if (response.data.code === 200 && response.data.data.status === 'paid') {
          // 支付成功，继续处理
          onPaymentSuccess();
        } else {
          Toast.fail('未检测到支付完成，请确认支付或稍后再试');
          isProcessing.value = false;
        }
      } catch (error) {
        console.error('查询支付状态失败:', error);
        Toast.fail('查询支付状态失败');
        isProcessing.value = false;
      }
    };
    
    // 添加轮询支付状态的方法
    let paymentStatusInterval = null;
    
    const startPaymentStatusPolling = () => {
      // 每5秒查询一次支付状态
      paymentStatusInterval = setInterval(async () => {
        try {
          const response = await axios.get(`/api/order/query/${orderId.value}`);
          console.log('轮询支付状态:', response.data);
          
          if (response.data.code === 200 && response.data.data.status === 'paid') {
            // 支付成功，停止轮询并处理
            clearInterval(paymentStatusInterval);
            onPaymentSuccess();
          }
        } catch (error) {
          console.error('轮询支付状态失败:', error);
        }
      }, 5000);
    };
    
    // 在显示二维码时开始轮询，在组件销毁时清除轮询
    watch(showQRCode, (newVal) => {
      if (newVal) {
        startPaymentStatusPolling();
      } else if (paymentStatusInterval) {
        clearInterval(paymentStatusInterval);
      }
    });
    
    onUnmounted(() => {
      if (paymentStatusInterval) {
        clearInterval(paymentStatusInterval);
      }
    });

    return {
      orderId,
      createTime,
      paymentMethod,
      showQRCode,
      qrCodeUrl,
      isProcessing,
      onClickLeft,
      onPayment,
      onPaymentSuccess,
      checkPaymentStatus
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
