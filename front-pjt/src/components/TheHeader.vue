<script setup>
import { RouterLink, useRouter } from "vue-router";
import { ref, onMounted, onUnmounted, watch, inject } from "vue";
import emitter from '@/eventBus';
import SearchBar from './SearchBar.vue';
import axios from 'axios';
import NewsCard from '@/components/NewsCard.vue';

const router = useRouter();
const isLoggedIn = ref(false);
const username = ref('');
const showDropdown = ref(false);
const userId = localStorage.getItem('userId');
const userInfo = ref({});
const bookmarks = ref([]);

// 다크 모드 상태 주입
const isDarkMode = inject('isDarkMode');

// 드롭다운 메뉴 외부 클릭 감지를 위한 ref
const dropdownRef = ref(null);

const updateLoginState = () => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    isLoggedIn.value = true;
    username.value = localStorage.getItem('username') || '사용자';
  } else {
    isLoggedIn.value = false;
    username.value = '';
  }
};

// 외부 클릭 감지 함수
const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    showDropdown.value = false;
  }
};

// 라우터 변경 감지
const handleRouteChange = () => {
  showDropdown.value = false;
};

// 다크 모드 토글 함수
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value;
};

// 테마 업데이트 함수
const updateTheme = () => {
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark-mode');
  } else {
    document.documentElement.classList.remove('dark-mode');
  }
};

// 다크 모드 상태 변경 감시
watch(isDarkMode, () => {
  updateTheme();
});

onMounted(() => {
  updateLoginState();
  emitter.on('login-state-changed', updateLoginState);
  // 외부 클릭 이벤트 리스너 추가
  document.addEventListener('click', handleClickOutside);
  // 라우터 변경 이벤트 리스너 추가
  router.beforeEach(handleRouteChange);
  updateTheme(); // 초기 테마 적용
});

onUnmounted(() => {
  emitter.off('login-state-changed', updateLoginState);
  // 이벤트 리스너 제거
  document.removeEventListener('click', handleClickOutside);
  router.beforeEach(handleRouteChange);
});

const refreshPage = (event) => {
  event.preventDefault();
  router.push("/").then(() => {
    window.location.reload();
  });
};

const handleLogout = () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('username');
  localStorage.removeItem('userId');
  isLoggedIn.value = false;
  username.value = '';
  router.push('/');
};

const toggleDropdown = async () => {
  showDropdown.value = !showDropdown.value;
  if (showDropdown.value) {
    const res = await axios.get('http://localhost:8000/api/user_info/', { withCredentials: true });
    userInfo.value = res.data;
    if (res.data.user_id) {
      localStorage.setItem('userId', res.data.user_id);
    }
  }
};

const goToBookmarkList = () => {
  showDropdown.value = false;
  router.push(`/user/${userId}/bookmarks`);
};

onMounted(async () => {
  // 유저 정보
  const userRes = await axios.get(`http://localhost:8000/api/user_info/`, { withCredentials: true });
  username.value = userRes.data.username;
  // 북마크 목록
  const bmRes = await axios.get(`http://localhost:8000/api/${userId}/user_bookmark/`, { withCredentials: true });
  bookmarks.value = bmRes.data.bookmarks;
});
</script>

<template>
  <div class="header__container" :class="{ 'dark-mode': isDarkMode }">
    <header>
      <router-link to="/" @click="refreshPage">
        <span class="logo"> SSAFYNEWS </span>
      </router-link>

      <SearchBar class="search-bar-container" />

      <nav class="menus">
        <router-link to="/news">나만의 뉴스 큐레이팅</router-link>
        <router-link to="/dashboard">대시보드</router-link>
        <div class="theme-toggle-switch" @click="toggleDarkMode" :aria-checked="isDarkMode" role="switch">
          <span class="icon moon" :class="{ active: isDarkMode }">🌙</span>
          <span class="toggle-track">
            <span class="toggle-thumb" :class="{ right: !isDarkMode }"></span>
          </span>
          <span class="icon sun" :class="{ active: !isDarkMode }">☀️</span>
        </div>
        <div v-if="isLoggedIn" class="user-menu" style="position:relative;">
          <span class="username" @click.stop="toggleDropdown">
            {{ username }}님
            <span
              class="dropdown-arrow"
              :class="{ open: showDropdown }"
            >
              {{ showDropdown ? '⏶' : '⏷' }}
            </span>
          </span>
          <div v-if="showDropdown" class="dropdown-menu" ref="dropdownRef">
            <div class="user-info">
              <div class="profile-image-container">
                <img src="../assets/data/profile_img.jpg" alt="프로필" />
              </div>
              <div class="user-details">
                <div class="username">{{ userInfo.username }}님</div>
                <div class="user-email" v-if="userInfo.email">{{ userInfo.email }}</div>
              </div>
            </div>
            <div class="menu-divider"></div>
            <div class="menu-items">
              <div class="menu-item" @click="goToBookmarkList">
                <i class="fas fa-bookmark"></i>
                <span>북마크 목록</span>
              </div>
              <div class="menu-item logout" @click="handleLogout">
                <i class="fas fa-sign-out-alt"></i>
                <span>로그아웃</span>
              </div>
            </div>
          </div>
        </div>
        <router-link v-else to="/login" class="login-btn">로그인</router-link>
      </nav>
    </header>
  </div>
</template>

<style scoped lang="scss">
.header__container {
  background-color: white;
  border-bottom: 1px solid #d4d4d4;
  position: relative;
  z-index: 1000;

  header {
    max-width: 1280px;
    margin: 0 auto;
    color: black;
    height: 64px;
    justify-content: space-between;
    align-items: center;
    display: flex;
    padding: 0 15px;
    gap: 20px;
  }

  .logo {
    font-size: 20px;
    font-weight: 800;
    white-space: nowrap;
  }

  .search-bar-container {
    flex: 0 1 auto;
    width: 300px;
    min-width: auto;
  }

  .menus {
    position: relative;
    display: flex;
    align-items: center;
    gap: 23px;
    white-space: nowrap;
  }

  .user-menu {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-left: 20px;
    position: relative;
  }

  .username {
    color: #4a90e2;
    font-weight: 500;
  }

  .logout-btn {
    background: none;
    border: 1px solid #4a90e2;
    color: #4a90e2;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s ease;

    &:hover {
      background: #4a90e2;
      color: white;
    }
  }

  .login-btn {
    color: #4a90e2;
    text-decoration: none;
    font-weight: 500;
    padding: 6px 12px;
    border: 1px solid #4a90e2;
    border-radius: 4px;
    transition: all 0.3s ease;

    &:hover {
      background: #4a90e2;
      color: white;
    }
  }

  a.router-link-active {
    font-weight: bold;
  }

  .dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    min-width: 240px;
    padding: 16px;
    margin-top: 8px;
    z-index: 1000;
  }

  .user-info {
    display: flex;
    align-items: center;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 12px;
  }

  .profile-image-container {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    overflow: hidden;
    margin-right: 12px;
    background: #e9ecef;
  }

  .profile-image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .profile-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6c757d;
    font-size: 24px;
  }

  .user-details {
    flex: 1;
  }

  .username {
    font-weight: 600;
    color: #212529;
    margin-bottom: 4px;
  }

  .user-email {
    font-size: 0.875rem;
    color: #6c757d;
  }

  .menu-divider {
    height: 1px;
    background: #e9ecef;
    margin: 8px 0;
  }

  .menu-items {
    padding: 4px 0;
  }

  .menu-item {
    display: flex;
    align-items: center;
    padding: 12px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #495057;
  }

  .menu-item:hover {
    background: #f8f9fa;
    color: #228be6;
  }

  .menu-item i {
    width: 20px;
    margin-right: 12px;
    font-size: 1rem;
  }

  .menu-item.logout {
    color: #e03131;
    margin-top: 8px;
  }

  .menu-item.logout:hover {
    background: #fff5f5;
    color: #e03131;
  }

  .dropdown-arrow {
    margin-left: 4px;
    font-size: 1.1em;
    color: #1976d2;
    transition: color 0.2s;
    cursor: pointer;
    user-select: none;
  }

  .dropdown-arrow.open {
    color: #222;
  }
}

.theme-toggle-switch {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
  gap: 10px;
  margin: 0 10px;

  .icon {
    font-size: 1.5rem;
    opacity: 0.5;
    transition: opacity 0.2s;
    &.active {
      opacity: 1;
    }
  }

  .toggle-track {
    width: 56px;
    height: 28px;
    background: #aaa;
    border-radius: 14px;
    position: relative;
    transition: background 0.3s;
    display: flex;
    align-items: center;
  }

  .toggle-thumb {
    position: absolute;
    top: 2px;
    left: 2px;
    width: 24px;
    height: 24px;
    background: #fff;
    border-radius: 50%;
    transition: left 0.3s;
    box-shadow: 0 1px 4px rgba(0,0,0,0.15);
  }
  .toggle-thumb.right {
    left: 30px;
  }
}

// 다크 모드 스타일
.dark-mode {
  background-color: #1a1a1a;
  border-bottom-color: #333;

  header {
    color: #fff;
  }

  .logo {
    color: #fff;
  }

  .username {
    color: #64b5f6;
  }

  .dropdown-menu {
    background: #2d2d2d;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  }

  .user-info {
    background: #333;
  }

  .username {
    color: #fff;
  }

  .user-email {
    color: #aaa;
  }

  .menu-divider {
    background: #444;
  }

  .menu-item {
    color: #ddd;

    &:hover {
      background: #333;
      color: #64b5f6;
    }
  }

  .menu-item.logout {
    color: #ff6b6b;

    &:hover {
      background: #442222;
      color: #ff6b6b;
    }
  }

  .theme-toggle-switch {
    .icon {
      opacity: 1;
    }

    .toggle-track {
      background: #222;
    }

    .toggle-thumb {
      left: 2px !important;
    }
  }

  a {
    color: #fff;

    &:hover {
      color: #64b5f6;
    }
  }

  .login-btn {
    color: #64b5f6;
    border-color: #64b5f6;

    &:hover {
      background: #64b5f6;
      color: #fff;
    }
  }
}
</style>
