<template>
  <div class="search-bar" :class="{ 'is-focused': isFocused, 'dark-mode': isDarkMode }">
    <div class="search-bar__input-group">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="검색어를 입력하세요"
        @focus="isFocused = true"
        @blur="handleBlur"
        @keyup.enter="handleSearch"
        ref="searchInput"
      >
      <button @click="handleSearch">
        <span>🔍</span>
      </button>
    </div>
    
    <!-- 검색창 포커스시 나타나는 드롭다운 -->
    <div v-if="isFocused" class="search-bar__dropdown">
      <div class="search-bar__filters">
        <select v-model="selectedCategory" @change="handleSearch">
          <option value="">전체 카테고리</option>
          <option v-for="tab in tabs" :key="tab.id" :value="tab.value">
            {{ tab.label }}
          </option>
        </select>
        
        <select v-model="sortBy" @change="handleSearch">
          <option value="">관련도순</option>
          <option value="date">최신순</option>
          <option value="views">조회순</option>
        </select>
      </div>

      <div v-if="loading" class="search-bar__loading">
        검색 중...
      </div>
      <div v-else-if="isSearched" class="search-bar__results">
        <div v-if="total > 0" class="search-bar__info">
          총 {{ total }}개의 검색결과
        </div>
        <div v-else class="search-bar__no-results">
          검색 결과가 없습니다.
        </div>

        <div class="search-bar__result-list">
          <RouterLink 
            v-for="result in results" 
            :key="result.id"
            :to="{ name: 'newsDetail', params: { id: result.id }}" 
            class="search-bar__result-item"
          >
            <div class="search-bar__result-category">{{ result.category }}</div>
            <h3 class="search-bar__result-title" v-html="result.title"></h3>
            <p class="search-bar__result-preview" v-html="result.content_preview"></p>
            <div class="search-bar__result-meta">
              <span>{{ result.writer }}</span>
              <span>{{ formatDate(result.write_date) }}</span>
              <span>👀 {{ result.views }}</span>
            </div>
          </RouterLink>
        </div>

        <div v-if="total > pageSize" class="search-bar__more">
          <button @click="handleShowMore">더보기 ({{ currentPage }}/{{ totalPages }})</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, inject } from 'vue';
import { useDate } from '@/composables/useDate';
import { tabs } from '@/assets/data/tabs';
import axios from 'axios';

const { formatDate } = useDate();

const isDarkMode = inject('isDarkMode');

// 상태 관리
const searchQuery = ref('');
const selectedCategory = ref('');
const sortBy = ref('');
const currentPage = ref(1);
const pageSize = 5;
const isFocused = ref(false);
const searchInput = ref(null);

const results = ref([]);
const total = ref(0);
const loading = ref(false);
const isSearched = ref(false);

// 계산된 속성
const totalPages = computed(() => Math.ceil(total.value / pageSize));

// 검색 함수
const handleSearch = async (resetPage = true) => {
  if (!searchQuery.value.trim() && !isSearched.value) return;
  
  if (resetPage) currentPage.value = 1;
  loading.value = true;
  isSearched.value = true;

  try {
    // 먼저 인덱스 재생성
    await axios.post('http://localhost:8000/api/index/all/');
    
    // 그 다음 검색 실행
    const response = await axios.get('http://localhost:8000/api/search/', {
      params: {
        q: searchQuery.value,
        category: selectedCategory.value,
        sort: sortBy.value,
        page: currentPage.value,
        size: pageSize
      }
    });
    console.log(response.data);
    if (resetPage) {
      results.value = response.data.results;
    } else {
      results.value = [...results.value, ...response.data.results];
    }
    total.value = response.data.total;
  } catch (error) {
    console.error('검색 중 오류 발생:', error);
  } finally {
    loading.value = false;
  }
};

// 더보기
const handleShowMore = (event) => {
  event.stopPropagation();  // 이벤트 버블링 방지
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    handleSearch(false);
  }
};

// 포커스 아웃 처리
const handleBlur = (event) => {
  // 더보기 버튼 클릭시에는 닫지 않도록 처리
  if (event.relatedTarget?.closest('.search-bar__more')) {
    return;
  }
  
  // 드롭다운 내부 클릭시에는 닫지 않도록 지연
  setTimeout(() => {
    if (!document.activeElement?.closest('.search-bar')) {
      isFocused.value = false;
    }
  }, 200);
};

// 클릭 이벤트 핸들러
const handleClickOutside = (event) => {
  const searchBar = document.querySelector('.search-bar');
  if (searchBar && !searchBar.contains(event.target)) {
    isFocused.value = false;
  }
};

// 이벤트 리스너 등록/해제
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped lang="scss">
.search-bar {
  position: relative;
  width: 100%;
  z-index: 1000;

  &__input-group {
    display: flex;
    align-items: center;
    background-color: var(--c-card-bg);
    border: 1px solid var(--c-border);
    border-radius: 4px;
    overflow: hidden;
    transition: all 0.3s ease;

    input {
      flex: 1;
      padding: 8px 12px;
      border: none;
      font-size: 13px;
      outline: none;
      width: 100%;
      background-color: var(--c-card-bg);
      color: var(--c-text);

      &::placeholder {
        color: var(--c-text-secondary);
        font-size: 13px;
      }
    }

    button {
      padding: 8px 12px;
      background: none;
      border: none;
      cursor: pointer;
      font-size: 14px;
      color: var(--c-text-secondary);
      transition: all 0.3s ease;
      
      &:hover {
        background-color: var(--c-hover);
      }
    }
  }

  &.is-focused &__input-group {
    border-color: var(--c-primary);
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }

  &__dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--c-card-bg);
    border: 1px solid var(--c-primary);
    border-top: none;
    border-bottom-left-radius: 4px;
    border-bottom-right-radius: 4px;
    box-shadow: 0 2px 4px var(--c-card-shadow);
    max-height: 400px;
    overflow-y: auto;
  }

  &__filters {
    display: flex;
    gap: 10px;
    padding: 10px;
    border-bottom: 1px solid var(--c-border);

    select {
      padding: 5px;
      border: 1px solid var(--c-border);
      border-radius: 4px;
      font-size: 12px;
      background-color: var(--c-card-bg);
      color: var(--c-text);
      cursor: pointer;

      &:focus {
        outline: none;
        border-color: var(--c-primary);
      }
    }
  }

  &__loading {
    padding: 20px;
    text-align: center;
    color: var(--c-text-secondary);
  }

  &__info {
    padding: 10px;
    color: var(--c-text-secondary);
    font-size: 12px;
    border-bottom: 1px solid var(--c-border);
  }

  &__no-results {
    padding: 20px;
    text-align: center;
    color: var(--c-text-secondary);
  }

  &__result-list {
    padding: 10px;
  }

  &__result-item {
    display: block;
    padding: 10px;
    text-decoration: none;
    color: var(--c-text);
    border-radius: 4px;
    transition: all 0.3s ease;

    &:hover {
      background-color: var(--c-hover);
    }
  }

  &__result-category {
    display: inline-block;
    padding: 2px 6px;
    background-color: var(--c-hover);
    border-radius: 4px;
    font-size: 11px;
    margin-bottom: 4px;
    color: var(--c-text);
  }

  &__result-title {
    font-size: 14px;
    margin: 0 0 4px;
    color: var(--c-text);

    :deep(em) {
      background-color: #ffe066 !important;
      color: #222 !important;
      border-radius: 3px;
      padding: 0 2px;
      font-style: normal;
      font-weight: 700;
      transition: background 0.2s, color 0.2s;
    }
  }

  &__result-preview {
    font-size: 12px;
    color: var(--c-text-secondary);
    margin: 0 0 4px;
    line-height: 1.4;

    :deep(em) {
      background-color: #ffe066 !important;
      color: #222 !important;
      border-radius: 3px;
      padding: 0 2px;
      font-style: normal;
      font-weight: 700;
      transition: background 0.2s, color 0.2s;
    }
  }

  &__result-meta {
    display: flex;
    gap: 10px;
    font-size: 11px;
    color: var(--c-text-secondary);
  }

  &__more {
    padding: 10px;
    text-align: center;
    border-top: 1px solid var(--c-border);

    button {
      padding: 6px 12px;
      background: none;
      border: 1px solid var(--c-primary);
      color: var(--c-primary);
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        background-color: var(--c-primary);
        color: white;
      }
    }
  }

  &.dark-mode {
    .search-bar__input-group {
      background-color: var(--c-card-bg);
      border-color: var(--c-border);

      input {
        background-color: var(--c-card-bg);
        color: var(--c-text);

        &::placeholder {
          color: var(--c-text-secondary);
        }
      }

      button {
        color: var(--c-text-secondary);

        &:hover {
          background-color: var(--c-hover);
        }
      }
    }

    .search-bar__dropdown {
      background-color: var(--c-card-bg);
      border-color: var(--c-primary);
      box-shadow: 0 2px 4px var(--c-card-shadow);
    }

    .search-bar__filters select {
      background-color: var(--c-card-bg);
      color: var(--c-text);
      border-color: var(--c-border);

      &:focus {
        border-color: var(--c-primary);
      }
    }

    .search-bar__result-item {
      color: var(--c-text);

      &:hover {
        background-color: var(--c-hover);
      }
    }

    .search-bar__result-category {
      background-color: var(--c-hover);
      color: var(--c-text);
    }

    .search-bar__result-title {
      color: var(--c-text);

      :deep(em) {
        background-color: #ffe066 !important;
        color: #222 !important;
        border-radius: 3px;
        padding: 0 2px;
        font-style: normal;
        font-weight: 700;
        transition: background 0.2s, color 0.2s;
      }
    }

    .search-bar__result-preview {
      color: var(--c-text-secondary);

      :deep(em) {
        background-color: #ffe066 !important;
        color: #222 !important;
        border-radius: 3px;
        padding: 0 2px;
        font-style: normal;
        font-weight: 700;
        transition: background 0.2s, color 0.2s;
      }
    }

    .search-bar__result-meta {
      color: var(--c-text-secondary);
    }
  }
}
</style> 