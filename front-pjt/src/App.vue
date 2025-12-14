<script setup>
import { useRoute } from "vue-router";
import TheHeader from "./components/TheHeader.vue";
import TheFooter from "./components/TheFooter.vue";
import { onMounted, ref, watch, provide } from 'vue';

const route = useRoute();
const isDarkMode = ref(localStorage.getItem('darkMode') === 'true');

// 다크 모드 상태 제공
provide('isDarkMode', isDarkMode);

// 다크 모드 상태 변경 감시
watch(isDarkMode, (newValue) => {
  if (newValue) {
    document.documentElement.classList.add('dark-mode');
  } else {
    document.documentElement.classList.remove('dark-mode');
  }
  localStorage.setItem('darkMode', newValue);
});

// 초기 다크 모드 상태 적용
onMounted(() => {
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark-mode');
  }
});
</script>

<template>
  <div class="app" :class="{ 'dark-mode': isDarkMode }">
    <TheHeader />
    <main>
      <RouterView />
    </main>
    <TheFooter v-if="route.path !== '/login' && route.path !== '/register'" />
  </div>
</template>

<style lang="scss">
:root {
  --c-bg: #ffffff;
  --c-text: #1a1a1a;
  --c-text-secondary: #666666;
  --c-border: #e5e5e5;
  --c-card-bg: #ffffff;
  --c-card-shadow: rgba(0, 0, 0, 0.1);
  --c-primary: #4a90e2;
  --c-primary-hover: #357abd;
  --c-error: #e53935;
  --c-success: #43a047;
  --c-warning: #ffa000;
  --c-gray-100: #f8f9fa;
  --c-gray-200: #e9ecef;
  --c-gray-300: #dee2e6;
  --c-gray-400: #ced4da;
  --c-gray-500: #adb5bd;
  --c-gray-600: #6c757d;
}

.dark-mode {
  --c-bg: #1a1a1a;
  --c-text: #ffffff;
  --c-text-secondary: #b3b3b3;
  --c-border: #333333;
  --c-card-bg: #2d2d2d;
  --c-card-shadow: rgba(0, 0, 0, 0.3);
  --c-primary: #64b5f6;
  --c-primary-hover: #42a5f5;
  --c-error: #ef5350;
  --c-success: #66bb6a;
  --c-warning: #ffb74d;
  --c-gray-100: #2d2d2d;
  --c-gray-200: #333333;
  --c-gray-300: #404040;
  --c-gray-400: #4d4d4d;
  --c-gray-500: #666666;
  --c-gray-600: #808080;
}

.app {
  min-height: 100vh;
  background-color: var(--c-bg);
  color: var(--c-text);
  transition: background-color 0.3s ease, color 0.3s ease;
}

main {
  max-width: 1280px;
  min-width: 360px;
  min-height: 100vh;
  margin: 0 auto;
  padding: 50px 15px;
  background-color: var(--c-bg);
  transition: background-color 0.3s ease;
}

// 다크 모드에서의 공통 스타일
.dark-mode {
  .box {
    background-color: var(--c-card-bg);
    border-color: var(--c-border);
    box-shadow: 0 2px 8px var(--c-card-shadow);
  }

  input, textarea, select {
    background-color: var(--c-gray-100);
    color: var(--c-text);
    border-color: var(--c-border);

    &::placeholder {
      color: var(--c-gray-500);
    }
  }

  button {
    &:not(.theme-toggle) {
      background-color: var(--c-gray-200);
      color: var(--c-text);
      border-color: var(--c-border);

      &:hover {
        background-color: var(--c-gray-300);
      }
    }
  }

  a {
    color: var(--c-primary);

    &:hover {
      color: var(--c-primary-hover);
    }
  }
}
</style>
