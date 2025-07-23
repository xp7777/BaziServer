<template>
  <div class="login-container">
    <van-nav-bar
      title="登录"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
    />
    
    <div class="login-form">
      <h2>欢迎使用八字命理AI人生指导</h2>
      <p>请使用微信登录</p>
      
      <!-- 手机端微信内置浏览器检测 -->
      <div class="wechat-login-section" v-if="isWechatBrowser">
        <div class="wechat-auth-container">
          <div class="wechat-icon">
            <van-icon name="wechat" size="60" color="#07c160" />
          </div>
          <p class="auth-tip">检测到您在微信中打开，可直接授权登录</p>
          <van-button 
            round 
            block 
            type="primary" 
            @click="startWechatPhoneLogin"
            :loading="isPhoneLoading"
            style="background: #07c160; border-color: #07c160;"
          >
            {{ isPhoneLoading ? '正在跳转授权...' : '微信授权登录' }}
          </van-button>
        </div>
      </div>
      
      <!-- PC端二维码登录 -->
      <div class="wechat-login-section" v-else>
        <div class="wechat-qr-container" v-if="showQRCode">
          <div class="qr-title">请使用微信扫描二维码登录</div>
          <div class="qr-code">
            <img v-if="qrCodeImage" :src="qrCodeImage" alt="微信登录二维码" @click="openWechatLogin" style="cursor: pointer;" />
            <div v-else class="loading">正在生成二维码...</div>
          </div>
          <div class="qr-tips">
            <p>1. 使用微信扫描上方二维码</p>
            <p>2. 或者点击二维码在新窗口中登录</p>
            <p>3. 在微信中确认登录</p>
          </div>
          <van-button 
            type="primary" 
            size="small" 
            @click="openWechatLogin"
            style="margin-top: 10px;"
          >
            在新窗口中登录
          </van-button>
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
  </div>
</template>

<script>
import { ref, onUnmounted, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Toast } from 'vant';
import axios from 'axios';

export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter();
    const showQRCode = ref(false);
    const qrCodeImage = ref('');
    const wechatLoginUrl = ref('');
    const isLoading = ref(false);
    const isPhoneLoading = ref(false);
    const loginCheckTimer = ref(null);
    const loginToken = ref('');
    const loginWindow = ref(null);
    const isWechatBrowser = ref(false);
    
    // 返回按钮点击事件
    const onClickLeft = () => {
      router.go(-1);
    };
    
    // 检测是否在微信浏览器中
    const checkWechatBrowser = () => {
      const ua = navigator.userAgent.toLowerCase();
      isWechatBrowser.value = ua.includes('micromessenger');
    };
    
    // 手机端微信网页授权登录
    const startWechatPhoneLogin = async () => {
      try {
        isPhoneLoading.value = true;
        Toast.loading({
          message: '正在跳转微信授权...',
          duration: 0,
          forbidClick: true
        });
        
        // 调用后端API获取微信网页授权URL
        const response = await axios.post('/api/auth/wechatPhone/authorize');
        
        if (response.data.code === 200) {
          // 保存登录token用于轮询
          loginToken.value = response.data.data.state;
          
          // 开始轮询检查登录状态
          startLoginCheck();
          
          Toast.clear();
          Toast.loading({
            message: '正在授权登录...',
            duration: 0,
            forbidClick: true
          });
          
          // 直接跳转到微信授权页面
          window.location.href = response.data.data.authorizeUrl;
          
        } else {
          Toast.fail(response.data.message || '获取授权链接失败');
        }
      } catch (error) {
        console.error('微信网页授权失败:', error);
        Toast.fail('网络错误，请重试');
      } finally {
        isPhoneLoading.value = false;
      }
    };
    
    // PC端微信登录
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
          loginToken.value = response.data.data.token;
          wechatLoginUrl.value = response.data.data.loginUrl;
          qrCodeImage.value = response.data.data.qrCodeImage;
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
    
    const openWechatLogin = () => {
      if (!wechatLoginUrl.value) {
        Toast.fail('请先生成登录二维码');
        return;
      }
      
      // 在新窗口中打开微信登录页面
      const width = 500;
      const height = 600;
      const left = (screen.width - width) / 2;
      const top = (screen.height - height) / 2;
      
      loginWindow.value = window.open(
        wechatLoginUrl.value,
        'wechatLogin',
        `width=${width},height=${height},left=${left},top=${top},scrollbars=yes,resizable=yes`
      );
      
      // 监听弹窗关闭
      const checkClosed = setInterval(() => {
        if (loginWindow.value && loginWindow.value.closed) {
          clearInterval(checkClosed);
          console.log('登录窗口已关闭');
        }
      }, 1000);
    };
    
    // 轮询检查登录状态
    const startLoginCheck = () => {
      if (loginCheckTimer.value) {
        clearInterval(loginCheckTimer.value);
      }
      
      loginCheckTimer.value = setInterval(async () => {
        if (!loginToken.value) {
          console.log('loginToken为空，停止轮询');
          clearInterval(loginCheckTimer.value);
          return;
        }
        
        try {
          const response = await axios.get(`/api/auth/wechat/check/${loginToken.value}`);
          
          if (response.data.code === 200) {
            const { status, userInfo, token } = response.data.data;
            
            if (status === 'success') {
              // 登录成功
              clearInterval(loginCheckTimer.value);
              
              console.log('登录成功，保存用户信息:', { userInfo, token });
              
              // 保存用户信息和token
              localStorage.setItem('userToken', token);
              localStorage.setItem('userInfo', JSON.stringify(userInfo));
              
              Toast.clear();
              Toast.success('登录成功');
              
              // 统一跳转到八字服务页面
              setTimeout(() => {
                router.push('/bazi-service');
              }, 1000);
            } else if (status === 'expired') {
              // 二维码过期
              clearInterval(loginCheckTimer.value);
              Toast.clear();
              Toast.fail('授权已过期，请重新登录');
              isPhoneLoading.value = false;
            }
          }
        } catch (error) {
          console.error('检查登录状态失败:', error);
        }
      }, 1000);
    };
    
    const checkLoginStatusOnce = async () => {
      try {
        const response = await axios.get(`/api/auth/wechat/check/${loginToken.value}`);
        
        if (response.data.code === 200) {
          const { status, userInfo, token } = response.data.data;
          
          if (status === 'success') {
            // 保存用户信息和token
            localStorage.setItem('userToken', token);
            localStorage.setItem('userInfo', JSON.stringify(userInfo));
            
            Toast.clear();
            Toast.success('登录成功');
            
            // PC端也跳转到八字服务页面
            setTimeout(() => {
              router.push('/bazi-service');
            }, 1000);
          }
        }
      } catch (error) {
        console.error('检查登录状态失败:', error);
      }
    };

    // 监听来自弹窗的消息（只处理PC端弹窗消息）
    const handleMessage = (event) => {
      console.log('收到弹窗消息:', event);
      
      // 只处理PC端弹窗消息，手机端不处理
      if (isWechatBrowser.value) {
        console.log('手机端忽略弹窗消息');
        return;
      }
      
      // 检查消息类型
      if (event.data && event.data.type === 'WECHAT_LOGIN_RESULT') {
        console.log('收到微信登录结果:', event.data);
        
        if (event.data.success) {
          console.log('PC端微信登录成功，停止轮询');
          // 登录成功，停止轮询
          if (loginCheckTimer.value) {
            clearInterval(loginCheckTimer.value);
            loginCheckTimer.value = null;
          }
          
          // 关闭登录窗口
          if (loginWindow.value && !loginWindow.value.closed) {
            loginWindow.value.close();
          }
          
          Toast.success('登录成功，正在跳转...');
          
          // PC端立即检查一次登录状态
          checkLoginStatusOnce();
        } else {
          console.log('微信登录失败:', event.data.message);
          Toast.fail(event.data.message || '登录失败');
        }
      }
    };

    onMounted(() => {
      // 检测微信浏览器
      checkWechatBrowser();
      
      // 处理微信授权回调
      handleWechatCallback();
      
      // 添加消息监听（只在PC端生效）
      window.addEventListener('message', handleMessage);
    });
    
    const showAgreement = () => {
      // 显示用户协议
    };
    
    const showPrivacy = () => {
      // 显示隐私政策
    };

    onMounted(() => {
      // 检测微信浏览器
      checkWechatBrowser();
      
      // 处理微信授权回调
      handleWechatCallback();
      
      window.addEventListener('message', handleMessage);
    });
    
    // 组件卸载时清理定时器和事件监听
    onUnmounted(() => {
      if (loginCheckTimer.value) {
        clearInterval(loginCheckTimer.value);
      }
      if (loginWindow.value && !loginWindow.value.closed) {
        loginWindow.value.close();
      }
      window.removeEventListener('message', handleMessage);
    });
    
    // 处理微信授权回调
    const handleWechatCallback = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const wechatSuccess = urlParams.get('wechat_success');
      const state = urlParams.get('state');
      
      if (wechatSuccess === 'true' && state) {
        console.log('检测到微信授权成功回调:', { state });
        
        // 设置登录token
        loginToken.value = state;
        
        // 清除所有现有的Toast，然后显示处理中提示
        Toast.clear();
        
        // 使用更稳定的Toast配置
        const loadingToast = Toast.loading({
          message: '正在处理授权信息...',
          duration: 0,
          forbidClick: true,
          overlay: true,
          loadingType: 'spinner'
        });
        
        // 开始轮询检查登录状态
        startLoginCheck();
        
        // 清理URL参数，避免重复处理
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
      }
    };

    return {
      showQRCode,
      qrCodeImage,
      isLoading,
      isPhoneLoading,
      isWechatBrowser,
      onClickLeft,
      startWechatLogin,
      startWechatPhoneLogin,
      openWechatLogin,
      showAgreement,
      showPrivacy,
      handleWechatCallback
    };
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-form {
  padding: 20px;
  text-align: center;
}

.login-form h2 {
  color: white;
  margin-bottom: 10px;
}

.login-form p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 30px;
}

.wechat-login-section {
  background: white;
  border-radius: 15px;
  padding: 30px 20px;
  margin-bottom: 20px;
}

.qr-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
}

.qr-code {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  margin-bottom: 20px;
}

.qr-code img {
  width: 200px;
  height: 200px;
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: transform 0.2s;
}

.qr-code img:hover {
  transform: scale(1.05);
}

.loading {
  color: #666;
  font-size: 14px;
}

.qr-tips {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.qr-tips p {
  margin: 5px 0;
  color: #666;
}

.login-buttons {
  margin-top: 20px;
}

.agreement {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  line-height: 1.5;
}

.link {
  color: #4fc3f7;
  text-decoration: underline;
  cursor: pointer;
}

.wechat-auth-container {
  background: white;
  border-radius: 15px;
  padding: 40px 20px;
  margin-bottom: 20px;
  text-align: center;
}

.wechat-icon {
  margin-bottom: 20px;
}

.auth-tip {
  color: #666;
  font-size: 16px;
  margin-bottom: 30px;
  line-height: 1.5;
}
</style>
