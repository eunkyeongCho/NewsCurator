<template>
  <div class="signup-container">
    <div class="signup-box">
      <h2 class="title">회원가입</h2>
      <p class="subtitle">뉴스 데이터 분석 서비스에 오신 것을 환영합니다</p>
      
      <form @submit.prevent="handleSignup" class="signup-form">
        <div class="form-group">
          <label for="username">아이디</label>
          <div class="input-wrapper">
            <i class="fas fa-user"></i>
            <input 
              id="username"
              type="text" 
              v-model="username" 
              placeholder="아이디를 입력하세요" 
              required 
              :class="{ 'error-input': !success && message }"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">비밀번호</label>
          <div class="input-wrapper">
            <i class="fas fa-lock"></i>
            <input 
              id="password"
              type="password" 
              v-model="password" 
              placeholder="비밀번호를 입력하세요" 
              required 
              :class="{ 'error-input': !success && message }"
            />
          </div>
        </div>

        <button type="submit" class="signup-button" :disabled="isLoading">
          <span v-if="!isLoading">회원가입</span>
          <span v-else class="loading-spinner"></span>
        </button>

        <div class="message-box" v-if="message" :class="{ error: !success, success: success }">
          <i :class="success ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'"></i>
          {{ message }}
        </div>
      </form>

      <div class="login-link">
        이미 계정이 있으신가요? 
        <router-link to="/login">로그인하기</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/axios';

export default {
  name: 'Signup',
  data() {
    return {
      username: '',
      password: '',
      message: '',
      success: false,
      isLoading: false,
    };
  },
  methods: {
    async handleSignup() {
      this.isLoading = true;
      try {
        const response = await api.post('account/register/', {
          username: this.username,
          password: this.password,
        });

        this.message = response.data.message;
        this.success = true;

        // 성공하면 로그인 페이지로 이동
        setTimeout(() => {
          this.$router.push('/');
        }, 1500);
      } catch (err) {
        this.success = false;
        if (err.response && err.response.data.message) {
          this.message = err.response.data.message;
        } else {
          this.message = '회원가입 중 오류가 발생했습니다.';
        }
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped>
.signup-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.signup-box {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.title {
  color: #2c3e50;
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 10px;
  text-align: center;
}

.subtitle {
  color: #7f8c8d;
  text-align: center;
  margin-bottom: 30px;
  font-size: 14px;
}

.signup-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #2c3e50;
  font-size: 14px;
  font-weight: 500;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper i {
  position: absolute;
  left: 12px;
  color: #95a5a6;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.input-wrapper input:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.input-wrapper input.error-input {
  border-color: #e74c3c;
}

.signup-button {
  background: #3498db;
  color: white;
  border: none;
  padding: 14px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
}

.signup-button:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
}

.signup-button:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #ffffff;
  border-top: 3px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.message-box {
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.message-box.error {
  background: #fde8e8;
  color: #e74c3c;
  border: 1px solid #fad2d2;
}

.message-box.success {
  background: #e8f8e8;
  color: #27ae60;
  border: 1px solid #d2fad2;
}

.login-link {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #7f8c8d;
}

.login-link a {
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
  margin-left: 5px;
}

.login-link a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .signup-box {
    padding: 30px 20px;
  }

  .title {
    font-size: 24px;
  }

  .input-wrapper input {
    padding: 10px 10px 10px 35px;
  }
}
</style>
