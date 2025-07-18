<template>
  <div class="login-container">
    <van-nav-bar
      title="微信登录"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
    />
    
    <div class="login-form">
      <h2>欢迎使用八字命理AI人生指导</h2>
      <p>请使用微信登录</p>
      
      <div class="wechat-login-section">
        <div class="wechat-qr-container" v-if="showQRCode">
          <div class="qr-title">请使用微信扫描二维码登录</div>
          <div class="qr-code">
            <img :src="qrCodeUrl" alt="微信登录二维码" v-if="qrCodeUrl" />
            <van-loading v-else>生成二维码中...</van-loading>
          </div>
          <div class="qr-tips">
            <p>1. 打开微信扫一扫</p>
            <p>2. 扫描上方二维码</p>
            <p>3. 在微信中确认登录</p>
          </div>
        </div>
        
        <div class="login-buttons">
          <van-button 
            round 
            block 
            type="primary" 
            @click="startWechatLogin"
            :loading="isLoading"
          >
            {{ isLoading ? '正在生成登录二维码...' : '微信登录' }}
          </van-button>
        </div>
      </div>
      
      <div class="agreement">
        登录即表示您同意
        <span class="link" @click="showAgreement">《用户协议》</span>
        和
        <span class="link" @click="showPrivacy">《隐私政策》</span>
      </div>
    </div>
    
    <van-popup v-model:show="showAgreementPopup" round position="bottom" style="height: 70%">
      <div class="popup-content">
        <h3>用户协议</h3>
        <p>这里是用户协议内容...</p>
        <van-button type="primary" block @click="showAgreementPopup = false">
          我已阅读并同意
        </van-button>
      </div>
    </van-popup>
    
    <van-popup v-model:show="showPrivacyPopup" round position="bottom" style="height: 70%">
      <div class="popup-content">
        <h3>隐私政策</h3>
        <p>这里是隐私政策内容...</p>
        <van-button type="primary" block @click="showPrivacyPopup = false">
          我已阅读并同意
        </van-button>
      </div>
    </van-popup>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { Toast } from 'vant';
import axios from 'axios';

export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter();
    const showQRCode = ref(false);
    const qrCodeUrl = ref('');
    const isLoading = ref(false);
    const showAgreementPopup = ref(false);
    const showPrivacyPopup = ref(false);
    const loginCheckTimer = ref(null);
    const loginToken = ref('');
    
    const onClickLeft = () => {
      router.go(-1);
    };
    
    const startWechatLogin = async () => {
      try {
        isLoading.value = true;
        Toast.loading({
          message: '正在生成登录二维码...',
          duration: 0,
          forbidClick: true
        });
        
        // 调用后端API生成微信登录二维码
        const response = await axios.post('/api/auth/wechat/qrcode');
        
        if (response.data.code === 200) {
          qrCodeUrl.value = response.data.data.qrCodeUrl;
          loginToken.value = response.data.data.token;
          showQRCode.value = true;
          
          Toast.clear();
          Toast.success('二维码生成成功，请扫码登录');
          
          // 开始轮询检查登录状态
          startLoginCheck();
        } else {
          Toast.fail(response.data.message || '生成登录二维码失败');
        }
      } catch (error) {
        console.error('生成微信登录二维码失败:', error);
        Toast.fail('网络错误，请重试');
      } finally {
        isLoading.value = false;
      }
    };
    
    const startLoginCheck = () => {
      loginCheckTimer.value = setInterval(async () => {
        try {
          const response = await axios.get(`/api/auth/wechat/check/${loginToken.value}`);
          
          if (response.data.code === 200) {
            const { status, userInfo, token } = response.data.data;
            
            if (status === 'success') {
              // 登录成功
              clearInterval(loginCheckTimer.value);
              
              // 保存用户信息和token
              localStorage.setItem('userToken', token);
              localStorage.setItem('userInfo', JSON.stringify(userInfo));
              
              Toast.success('登录成功');
              
              // 跳转到用户中心或返回上一页
              router.push('/user');
            } else if (status === 'expired') {
              // 二维码过期
              clearInterval(loginCheckTimer.value);
              Toast.fail('二维码已过期，请重新获取');
              showQRCode.value = false;
            }
          }
        } catch (error) {
          console.error('检查登录状态失败:', error);
        }
      }, 2000); // 每2秒检查一次
    };
    
    const showAgreement = () => {
      showAgreementPopup.value = true;
    };
    
    const showPrivacy = () => {
      showPrivacyPopup.value = true;
    };
    
    // 组件卸载时清理定时器
    onUnmounted(() => {
      if (loginCheckTimer.value) {
        clearInterval(loginCheckTimer.value);
      }
    });
    
    return {
      showQRCode,
      qrCodeUrl,
      isLoading,
      showAgreementPopup,
      showPrivacyPopup,
      onClickLeft,
      startWechatLogin,
      showAgreement,
      showPrivacy
    };
  }
};
</script>

<style scoped>
.login-container {
  padding-bottom: 20px;
}

.login-form {
  padding: 30px 16px;
  text-align: center;
}

.login-form h2 {
  margin: 0 0 10px;
  font-size: 20px;
  color: #323233;
}

.login-form p {
  margin: 0 0 30px;
  font-size: 14px;
  color: #969799;
}

.wechat-login-section {
  margin: 30px 0;
}

.wechat-qr-container {
  margin: 20px 0;
}

.qr-title {
  font-size: 16px;
  color: #323233;
  margin-bottom: 20px;
}

.qr-code {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px 0;
  min-height: 200px;
}

.qr-code img {
  width: 200px;
  height: 200px;
  border: 1px solid #eee;
}

.qr-tips {
  margin-top: 20px;
  font-size: 14px;
  color: #969799;
}

.qr-tips p {
  margin: 5px 0;
}

.login-buttons {
  margin: 20px 0;
}

.agreement {
  margin-top: 20px;
  font-size: 12px;
  color: #969799;
  text-align: center;
}

.link {
  color: #1989fa;
  cursor: pointer;
}

.popup-content {
  padding: 20px;
}

.popup-content h3 {
  text-align: center;
  margin-bottom: 20px;
}

.popup-content p {
  margin-bottom: 30px;
  line-height: 1.6;
}
</style>
