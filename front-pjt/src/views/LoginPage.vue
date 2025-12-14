<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="login-title">Welcome Back</h2>
      <p class="login-subtitle">뉴스 추천 서비스에 오신 것을 환영합니다</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label for="username">아이디</label>
          <input 
            type="text" 
            id="username"
            v-model="username" 
            placeholder="아이디를 입력하세요" 
            required 
          />
        </div>
        
        <div class="input-group">
          <label for="password">비밀번호</label>
          <input 
            type="password" 
            id="password"
            v-model="password" 
            placeholder="비밀번호를 입력하세요" 
            required 
          />
        </div>

        <button type="submit" class="login-button">
          로그인
        </button>
      </form>

      <p v-if="error" class="error">{{ error }}</p>

      <p class="signup-link">
        계정이 없으신가요?
        <router-link to="/signup" class="signup-button">회원가입</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import api from '@/axios';
import { useRouter } from 'vue-router';
import emitter from '@/eventBus';
// import axios from 'axios';

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      error: '',
    };
  },
  created() {
    // 로그인 상태 확인
    const token = localStorage.getItem('accessToken');
    if (token) {
      this.$router.push('/news');
    }
  },
  methods: {
    async handleLogin() {
      try {
        const response = await api.post('login/', {
          username: this.username,
          password: this.password,
        });
        if (response.data.access) {
          localStorage.setItem('accessToken', response.data.access);
          localStorage.setItem('refreshToken', response.data.refresh);
          localStorage.setItem('username', this.username);
          localStorage.setItem('userId', response.data.user_id);
          // 로그인 상태 변경 이벤트 발생
          emitter.emit('login-state-changed');
          this.$router.push('/news');
        } else {
          this.error = response.data.message || '로그인 실패';
        }
      } catch (err) {
        this.error = '서버와 연결할 수 없습니다.';
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-title {
  color: #2c3e50;
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
  text-align: center;
}

.login-subtitle {
  color: #666;
  text-align: center;
  margin-bottom: 32px;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  color: #2c3e50;
  font-size: 14px;
  font-weight: 500;
}

.input-group input {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.input-group input:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
}

.login-button {
  background: #4a90e2;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s ease;
  margin-top: 8px;
}

.login-button:hover {
  background: #357abd;
}

.error {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
  margin-top: 16px;
}

.signup-link {
  text-align: center;
  margin-top: 24px;
  color: #666;
  font-size: 14px;
}

.signup-button {
  color: #4a90e2;
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
}

.signup-button:hover {
  text-decoration: underline;
}
</style>
