<script setup>
import { Bar, Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import ContentBox from "@/common/ContentBox.vue";
import { ref, onMounted, inject, computed } from "vue";
import ArticlePreview from "@/components/ArticlePreview.vue";
import api from '@/axios';

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

const props = defineProps();

const categoryData = ref({
  labels: [],
  datasets: [
    {
      data: [],
      backgroundColor: [],
    },
  ],
});
const categories = ref([]);
const favoriteArticles = ref([]);

const keywordData = ref({
  labels: [],
  datasets: [
    {
      label: "키워드 빈도수",
      data: [],
      backgroundColor: "#C7E4B8",
    },
  ],
});

const readData = ref({
  labels: [],
  datasets: [
    {
      label: "읽은 기사 수",
      data: [],
      backgroundColor: "#DBB8E4",
    },
  ],
});

const options = {
  plugins: {
    legend: {
      display: true,
      position: "right",
      labels: {
        padding: 15,
        boxWidth: 20,
        font: {
          size: 14,
        },
      },
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          const label = context.label || "";
          const value = context.raw;
          return `${label}: ${value}개`;
        },
      },
    },
    layout: {
      padding: {
        right: 40,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        min: 0,
        max: 1,
      },
    },
  },
};

const isDarkMode = inject('isDarkMode');

const chartTextColor = computed(() => isDarkMode.value ? '#fff' : '#333');
const chartGridColor = computed(() => isDarkMode.value ? '#444' : '#e0e0e0');
const chartTooltipBg = computed(() => isDarkMode.value ? '#222' : '#fff');
const chartTooltipColor = computed(() => isDarkMode.value ? '#fff' : '#333');

const barOptions = computed(() => ({
  indexAxis: "y",
  scales: {
    x: {
      beginAtZero: true,
      ticks: { color: chartTextColor.value },
      grid: { color: chartGridColor.value }
    },
    y: {
      ticks: { color: chartTextColor.value },
      grid: { color: chartGridColor.value }
    }
  },
  plugins: {
    legend: { display: false, labels: { color: chartTextColor.value } },
    tooltip: {
      backgroundColor: chartTooltipBg.value,
      titleColor: chartTooltipColor.value,
      bodyColor: chartTooltipColor.value,
      borderColor: chartGridColor.value,
      borderWidth: 1,
    }
  }
}));

const readBarOptions = computed(() => ({
  indexAxis: "x",
  scales: {
    x: {
      ticks: { color: chartTextColor.value },
      grid: { color: chartGridColor.value }
    },
    y: {
      beginAtZero: true,
      ticks: { color: chartTextColor.value, stepSize: 1 },
      grid: { color: chartGridColor.value }
    }
  },
  plugins: {
    legend: { display: false, labels: { color: chartTextColor.value } },
    tooltip: {
      backgroundColor: chartTooltipBg.value,
      titleColor: chartTooltipColor.value,
      bodyColor: chartTooltipColor.value,
      borderColor: chartGridColor.value,
      borderWidth: 1,
      callbacks: {
        label: (context) => `읽은 기사: ${context.raw}개`
      }
    }
  }
}));

const newsList = ref([]);
const sortBy = ref("latest");
const relatedNews = ref(null);

const getUserIdFromToken = () => {
  const token = localStorage.getItem('accessToken');
  if (!token) return null;
  
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    const payload = JSON.parse(jsonPayload);
    return payload.user_id;
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};

// 날짜 포맷팅 함수
const formatDate = (date) => {
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${month}-${day}`;
};

// 주간 읽은 기사 데이터 처리 함수
const processWeeklyReadData = (weeklyData) => {
  const today = new Date();
  const dates = [];
  const counts = [];
  
  // 최근 7일 날짜 생성
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD 형식
    dates.push(formatDate(date));
    
    // 해당 날짜의 데이터 찾기
    const dayData = weeklyData.find(item => item.day === dateStr);
    counts.push(dayData ? dayData.count : 0);
  }
  
  readData.value = {
    labels: dates,
    datasets: [{
      label: "읽은 기사 수",
      data: counts,
      backgroundColor: "#DBB8E4",
    }]
  };
};

const doughnutOptions = computed(() => ({
  plugins: {
    legend: {
      display: true,
      position: "right",
      labels: {
        padding: 15,
        boxWidth: 20,
        font: { size: 14 },
        color: chartTextColor.value
      }
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          const label = context.label || "";
          const value = context.raw;
          return `${label}: ${value}개`;
        },
      },
    },
    layout: {
      padding: { right: 40 },
    },
  },
}));

onMounted(async () => {
  try {
    const userId = getUserIdFromToken();
    if (!userId) {
      console.error('User ID not found in token');
      return;
    }
    const response = await api.get(`${userId}/dashboard/`);
    
    // 주간 읽은 기사 데이터 처리
    if (response.data.weekly_read_count) {
      processWeeklyReadData(response.data.weekly_read_count);
    }
    
    // 카테고리 데이터 설정
    const categoryColors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
    categoryData.value = {
      labels: response.data.top_categories.map(cat => cat.category),
      datasets: [{
        data: response.data.top_categories.map(cat => cat.count),
        backgroundColor: categoryColors.slice(0, response.data.top_categories.length)
      }]
    };
    categories.value = response.data.top_categories.map((cat, index) => [cat.category, cat.count]);

    // 키워드 데이터 설정
    if (response.data.top_keywords && response.data.top_keywords.length > 0) {
      keywordData.value = {
        labels: response.data.top_keywords.map(kw => kw.keyword),
        datasets: [{
          label: "키워드 빈도수",
          data: response.data.top_keywords.map(kw => kw.score),
          backgroundColor: "#C7E4B8"
        }]
      };
    }

    // 좋아요 누른 기사 설정
    favoriteArticles.value = response.data.liked_articles;
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
  }
});
</script>

<template>
  <div class="dashboard">
    <div class="dashboard__intro-card" :class="{ 'dark-mode': isDarkMode }">
      <h1 class="dashboard__title">
        <span class="dashboard__emoji">📊</span>
        <span class="dashboard__title-text">DASHBOARD</span>
      </h1>
      <p class="dashboard__description">
        <span class="point">방문 기록</span> 및 <span class="point">좋아요 데이터</span>를 기반으로<br />
        <span class="point">나의 관심 분야</span>를 확인하고,<br />
        관심 분야에 맞는 <span class="point">추천 기사</span>를 받아보세요.<br />
        <span class="sub">여러분의 취업 여정의 <span class="point">로드맵</span>을 제공합니다.</span>
      </p>
    </div>
    <div class="layout">
      <ContentBox class="category">
        <h1>🐤 나의 관심 카테고리</h1>
        <p class="card_description">
          내가 주로 읽은 기사들을 분석하여 정치, 경제, 문화 등 가장 관심 있는
          뉴스 카테고리를 한눈에 보여드립니다.
        </p>
        <div class="category__chart">
          <Doughnut :data="categoryData" :options="doughnutOptions" />
          <div class="category__labels">
            <span
              v-for="(category, index) in categories"
              :key="index"
              :style="{
                borderColor: categoryData.datasets[0].backgroundColor[index],
                color: categoryData.datasets[0].backgroundColor[index],
              }"
              class="category__label"
            >
              {{ index + 1 }}순위: {{ category[0] }} ({{ category[1] }}개)
            </span>
          </div>
        </div>
      </ContentBox>

      <ContentBox class="keyword">
        <h1>⭐️ 주요 키워드</h1>
        <p class="card_description">
          내가 관심있게 본 뉴스 기사들에서 가장 많이 등장한 핵심 키워드를
          추출하여 현재 나의 주요 관심사를 보여드립니다.
        </p>
        <Bar :data="keywordData" :options="barOptions" />
      </ContentBox>
    </div>
    <div class="layout">
      <ContentBox>
        <h1>📰 주간 읽은 기사</h1>
        <p class="card_description">
          최근 일주일 동안 하루에 몇 개의 기사를 읽었는지 그래프로 확인하며 나의
          뉴스 소비 패턴을 분석합니다.
        </p>
        <Bar :data="readData" :options="readBarOptions" />
      </ContentBox>

      <ContentBox class="like-news">
        <h1>❤️ 좋아요 누른 기사</h1>
        <p class="card_description">
          내가 좋아요를 누른 기사들의 목록을 한곳에서 모아보고 다시 찾아볼 수
          있습니다.
        </p>
        <div v-for="(article, index) in favoriteArticles" :key="index">
          <ArticlePreview :to="`/news/${article.id}`" :news="article" />
        </div>
      </ContentBox>
    </div>
  </div>
</template>

<style scoped lang="scss">
.title {
  margin: 0;
  font-size: 25px;
}
.subtitle {
  font-weight: 500;
  margin-bottom: 40px;
}
.like-news {
  overflow-y: auto;
  box-sizing: border-box;
}
.dashboard {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card_description {
  margin: 10px;
}

.layout {
  display: flex;
  gap: 20px;
  > * {
    height: 450px;
  }

  @media (max-width: 768px) {
    flex-direction: column;
  }
}
.category {
  &__chart {
    height: 300px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    padding-bottom: 30px;
  }
  &__label {
    border: 1px solid;
    padding: 3px 5px;
    border-radius: 10px;
    margin-right: 10px;
  }
}

h1 {
  margin-bottom: 20px;
}

.dashboard__intro-card {
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

    .dashboard__title-text {
      color: var(--c-primary);
    }

    .dashboard__description {
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
.dashboard__title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--c-primary);
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
.dashboard__emoji {
  font-size: 2.2rem;
  margin-right: 4px;
}
.dashboard__title-text {
  color: var(--c-primary);
  letter-spacing: -1px;
}
.dashboard__description {
  color: var(--c-text);
  font-size: 1.13rem;
  line-height: 1.7;
  margin-bottom: 0;
}
.dashboard__description .point {
  color: var(--c-primary);
  font-weight: 700;
}
.dashboard__description .sub {
  color: var(--c-text-secondary);
  font-size: 1.01em;
}
@media (max-width: 600px) {
  .dashboard__intro-card {
    padding: 22px 8px 18px 8px;
    font-size: 0.98rem;
  }
  .dashboard__title {
    font-size: 1.2rem;
  }
}
.dark-mode .category__label {
  color: #fff !important;
}
</style>
