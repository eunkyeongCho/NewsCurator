<script setup>
import { ref, onMounted, computed, watch } from "vue";
import ContentBox from "@/common/ContentBox.vue";
import NewsCard from "@/components/NewsCard.vue";
import { tabs } from "@/assets/data/tabs";
import PaginationButton from "@/common/PaginationButton.vue";
import StateButton from "@/common/StateButton.vue";
import axios from 'axios';
import { useRoute } from 'vue-router';
import { inject } from 'vue';

const newsList = ref([]);
const sortBy = ref("latest");
const activeTab = ref(tabs[0].id);
const currentPage = ref(1);
const itemsPerPage = 5;
const route = useRoute();
const userId = route.params.userId;
const username = ref('');
const bookmarks = ref([]);
const isDarkMode = inject('isDarkMode');

const fetchNews = async (sort = 'latest') => {
  try {
    const url = sort === 'recommend' 
      ? 'http://localhost:8000/api/articles/recommend/'
      : 'http://localhost:8000/api/articles/';
    const response = await axios.get(url);
    newsList.value = response.data;
  } catch (error) {
    console.error('Error fetching news:', error);
  }
};

// sortBy가 변경될 때마다 데이터를 다시 불러옵니다
watch(sortBy, (newSort) => {
  fetchNews(newSort);
  currentPage.value = 1; // 정렬 변경시 첫 페이지로 이동
});

onMounted(() => {
  fetchNews();
});

onMounted(async () => {
  const userRes = await axios.get(`http://localhost:8000/api/${userId}/user_info/`, { withCredentials: true });
  username.value = userRes.data.username;
  const bmRes = await axios.get(`http://localhost:8000/api/${userId}/user_bookmark/`, { withCredentials: true });
  bookmarks.value = bmRes.data.bookmarks;
});

const filteredNewsList = computed(() => {
  const selectedTab = tabs.find(tab => tab.id === activeTab.value);
  const categoryValue = selectedTab?.value || "";

  let filtered = categoryValue
    ? newsList.value.filter(news => news.category === categoryValue)
    : newsList.value;

  // 추천순은 백엔드에서 정렬된 데이터를 받아오므로 클라이언트에서 정렬하지 않음
  if (sortBy.value === "latest") {
    filtered = [...filtered].sort((a, b) => new Date(b.write_date) - new Date(a.write_date));
  } else if (sortBy.value === "views") {
    filtered = [...filtered].sort((a, b) => b.views - a.views);
  }

  // 페이지네이션 적용
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  return filtered.slice(startIndex, endIndex);
});

const totalPages = computed(() => {
  const selectedTab = tabs.find(tab => tab.id === activeTab.value);
  const categoryValue = selectedTab?.value || "";
  const filtered = categoryValue
    ? newsList.value.filter(news => news.category === categoryValue)
    : newsList.value;
  return Math.ceil(filtered.length / itemsPerPage);
});

// 페이지네이션에 표시할 페이지 범위 계산
const paginationRange = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  
  // 전체 페이지가 10개 이하면 모든 페이지 표시
  if (total <= 10) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  // 현재 페이지 주변의 페이지 계산
  let start = Math.max(1, current - 4);
  let end = Math.min(total, current + 4);

  // 시작과 끝 페이지 조정
  if (start === 1) {
    end = Math.min(10, total);
  } else if (end === total) {
    start = Math.max(1, total - 9);
  }

  return Array.from({ length: end - start + 1 }, (_, i) => start + i);
});
</script>

<template>
  <div class="news">
    <div class="news__intro-card" :class="{ 'dark-mode': isDarkMode }">
      <h1 class="news__title">
        <span class="news__emoji">🤖</span>
        <span class="news__title-text">AI 맞춤 추천 뉴스</span>
      </h1>
      <p class="news__description">
        당신이 원하는 뉴스, <span class="point">이제 AI가 직접 추천</span>해드립니다!<br />
        <span class="point">나만의 취향</span>을 기반으로, 맞춤형 뉴스만 쏙쏙 골라주는<br />
        뉴스 큐레이팅 서비스 <strong class="point">SSAFYNEWS</strong>에 빠져보세요.<br />
        <span class="sub">AI 챗봇과 기사에 대해 대화하며 궁금한 점을 물어보고,<br />
        한눈에 보기 쉬운 <span class="point">대시보드</span>로 나의 뉴스 소비 패턴도 확인할 수 있습니다.</span>
      </p>
    </div>
    <ContentBox class="news__tabs">
      <StateButton
        v-for="tab in tabs"
        :key="tab.id"
        type="state"
        :is-active="activeTab === tab.id"
        @click="() => {
        activeTab = tab.id;
        currentPage = 1;
        }"
      >
        {{ tab.label }}
      </StateButton>
    </ContentBox>
    <ContentBox class="news__box">
      <div class="news__box__title-container">
        <div class="filters__container">
          <select class="filters" v-model="sortBy">
            <option value="latest">최신순</option>
            <option value="recommend">추천순</option>
            <option value="views">조회순</option>
          </select>
        </div>
      </div>

      <div class="news__box__cards" v-for="news in filteredNewsList" :key="news.id">
        <NewsCard :data="news" />
      </div>

      <div class="pagination">
        <button 
          class="pagination__button"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          이전
        </button>
        <button 
          v-for="page in paginationRange" 
          :key="page"
          class="pagination__button"
          :class="{ 'pagination__button--active': currentPage === page }"
          @click="currentPage = page"
        >
          {{ page }}
        </button>
        <button 
          class="pagination__button"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          다음
        </button>
      </div>
    </ContentBox>
  </div>
</template>

<style scoped lang="scss">
.news {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 30px;

  &__intro-card {
    background: var(--c-card-bg);
    border-radius: 18px;
    box-shadow: 0 2px 16px var(--c-card-shadow);
    padding: 28px 24px 24px 24px;
    margin: 0 auto 24px auto;
    max-width: 900px;
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    animation: fadeIn 0.7s;
    min-height: unset;
    transition: all 0.3s ease;

    &.dark-mode {
      background: var(--c-card-bg);
      box-shadow: 0 2px 16px var(--c-card-shadow);

      .news__title-text {
        color: var(--c-primary);
      }

      .news__description {
        color: var(--c-text);

        .point {
          color: var(--c-primary);
        }

        .sub {
          color: var(--c-text-secondary);
        }
      }
    }
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px);}
    to { opacity: 1; transform: none;}
  }

  &__title {
    font-size: 2rem;
    font-weight: 800;
    color: var(--c-primary);
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }

  &__emoji {
    font-size: 2.2rem;
    margin-right: 4px;
  }

  &__title-text {
    color: var(--c-primary);
    letter-spacing: -1px;
  }

  &__description {
    color: var(--c-text);
    font-size: 1.13rem;
    line-height: 1.7;
    margin-bottom: 0;

    .point {
      color: var(--c-primary);
      font-weight: 700;
    }

    .sub {
      color: var(--c-text-secondary);
      font-size: 1.01em;
    }
  }

  &__tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 12px 30px !important;
  }

  &__box {
    padding: 30px !important;

    &__noti {
      color: #666666;
      font-size: 12px;
      padding: 5px 10px;
    }

    &__title-container {
      position: relative;
      display: flex;
      align-items: center;
    }

    &__title {
      font-weight: 700;
      font-size: 21px;
      cursor: pointer;

      &-username {
        font-weight: 400;
        padding: 3px;
        border-bottom: 2px solid #272c97;
      }
      &-icon {
        font-size: 15px;
      }
    }

    &__subtitle-loggedin {
      font-weight: 400;
      padding: 10px 0 0 10px;
      color: #575757;
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
      text-decoration: underline;
    }

    &__title-container:hover .news__box__subtitle-loggedin {
      opacity: 1;
    }

    .filters__container {
      position: absolute;
      right: 0;
    }

    &__cards {
      margin-top: 30px;
      margin-left: 30px;
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 30px;

  &__button {
    padding: 8px 16px;
    border: 1px solid #e2e2e2;
    border-radius: 4px;
    background-color: white;
    cursor: pointer;
    transition: all 0.2s;

    &:hover:not(:disabled) {
      background-color: #f5f5f5;
    }

    &:disabled {
      cursor: not-allowed;
      opacity: 0.5;
    }

    &--active {
      background-color: #272c97;
      color: white;
      border-color: #272c97;
    }
  }
}

@media (max-width: 600px) {
  .news__intro-card {
    padding: 22px 8px 18px 8px;
    font-size: 0.98rem;
  }
  .news__title {
    font-size: 1.2rem;
  }
}
</style>
