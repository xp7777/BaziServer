<template>
  <div class="login-container">
    <van-nav-bar
      title="登录/注册"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
    />
    
    <div class="login-form">
      <h2>欢迎使用八字命理AI人生指导</h2>
      <p>请使用手机号登录或注册</p>
      
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="phone"
            name="phone"
            label="手机号码"
            placeholder="请输入手机号码"
            :rules="[{ required: true, message: '请填写手机号码' }]"
          />
          
          <van-field
            v-model="verifyCode"
            center
            clearable
            label="验证码"
            placeholder="请输入验证码"
            :rules="[{ required: true, message: '请填写验证码' }]"
          >
            <template #button>
              <van-button
                size="small"
                type="primary"
                :disabled="isSending"
                @click="sendVerifyCode"
              >
                {{ sendButtonText }}
              </van-button>
            </template>
          </van-field>
        </van-cell-group>
        
        <div style="margin: 16px;">
          <van-button round block type="primary" native-type="submit">
            登录/注册
          </van-button>
        </div>
      </van-form>
      
      <div class="agreement">
        登录/注册即表示您同意
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
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { Toast } from 'vant';

export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter();
    const phone = ref('');
    const verifyCode = ref('');
    const isSending = ref(false);
    const countdown = ref(0);
    const sendButtonText = ref('发送验证码');
    const showAgreementPopup = ref(false);
    const showPrivacyPopup = ref(false);
    
    const onClickLeft = () => {
      router.go(-1);
    };
    
    const startCountdown = () => {
      countdown.value = 60;
      isSending.value = true;
      
      const timer = setInterval(() => {
        countdown.value--;
        sendButtonText.value = `${countdown.value}秒后重发`;
        
        if (countdown.value <= 0) {
          clearInterval(timer);
          isSending.value = false;
          sendButtonText.value = '发送验证码';
        }
      }, 1000);
    };
    
    const sendVerifyCode = () => {
      if (!phone.value) {
        Toast('请输入手机号码');
        return;
      }
      
      if (!/^1[3-9]\d{9}$/.test(phone.value)) {
        Toast('请输入正确的手机号码');
        return;
      }
      
      // 实际项目中这里应该调用API发送验证码
      Toast('验证码已发送');
      startCountdown();
    };
    
    const onSubmit = () => {
      if (!phone.value) {
        Toast('请输入手机号码');
        return;
      }
      
      if (!verifyCode.value) {
        Toast('请输入验证码');
        return;
      }
      
      // 实际项目中这里应该调用API验证登录
      Toast('登录成功');
      
      // 登录成功后跳转到用户中心
      router.push('/user');
    };
    
    const showAgreement = () => {
      showAgreementPopup.value = true;
    };
    
    const showPrivacy = () => {
      showPrivacyPopup.value = true;
    };
    
    return {
      phone,
      verifyCode,
      isSending,
      sendButtonText,
      showAgreementPopup,
      showPrivacyPopup,
      onClickLeft,
      sendVerifyCode,
      onSubmit,
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

.agreement {
  margin-top: 20px;
  font-size: 12px;
  color: #969799;
  text-align: center;
}

.link {
  color: #1989fa;
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
