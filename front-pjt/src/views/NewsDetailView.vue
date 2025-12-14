<script setup>
import { ref, onMounted, watch } from "vue";
import ContentBox from "@/common/ContentBox.vue";
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import router from "@/router";
import LeftArrow from "@/components/icon/LeftArrow.svg";
import ArticlePreview from "@/components/ArticlePreview.vue";
import axios from 'axios';
import { useRoute } from "vue-router";
import ArticleChatbot from '@/components/ArticleChatbot.vue';

const props = defineProps({
  id: {
    type: [String, Number],
    required: true,
  },
});

const route = useRoute();
const news = ref();
const relatedNews = ref(null);

const { formatDate } = useDate();

const liked = ref(false);
const likeCount = ref(0);
const isAnimating = ref(false);
const isBookmarkAnimating = ref(false);
const isBookmarked = ref(false);

const handleLike = async () => {
  try {
    const response = await axios.post(`http://localhost:8000/api/articles/${props.id}/like/`);
    if (response.status === 201) {
      liked.value = true;
      likeCount.value++;
      isAnimating.value = true;
      setTimeout(() => {
        isAnimating.value = false;
      }, 600);
    } else if (response.status === 204) {
      liked.value = false;
      likeCount.value--;
      isAnimating.value = true;
      setTimeout(() => {
        isAnimating.value = false;
      }, 600);
    }
  } catch (error) {
    console.error('Error toggling like:', error);
  }
};

const handleBookmark = async () => {
  try {
    const response = await axios.post(`http://localhost:8000/api/articles/${props.id}/bookmark/`);
    if (response.status === 201) {
      isBookmarked.value = true;
      isBookmarkAnimating.value = true;
      setTimeout(() => {
        isBookmarkAnimating.value = false;
      }, 600);
    } else if (response.status === 204) {
      isBookmarked.value = false;
      isBookmarkAnimating.value = true;
      setTimeout(() => {
        isBookmarkAnimating.value = false;
      }, 600);
    }
  } catch (error) {
    console.error('Error toggling bookmark:', error);
  }
};

const fetchNewsData = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/api/articles/${props.id}/`);
    news.value = response.data.article;
    relatedNews.value = response.data.related_articles;
    likeCount.value = news.value.likes || 0;
    liked.value = news.value.is_like;
    isBookmarked.value = news.value.is_bookmarked;
  } catch (error) {
    console.error('Error fetching news detail:', error);
  }
};

// props.id가 변경될 때마다 데이터를 다시 불러옵니다
watch(() => props.id, () => {
  fetchNewsData();
});

onMounted(() => {
  fetchNewsData();
});

</script>

<template>
  <button @click="() => router.back()" class="back-btn"><LeftArrow /></button>
  <div v-if="news" class="news-detail">
    <div class="article__container">
      <ContentBox>
        <div class="article">
          <div class="article__header">
            <StateButton type="state" size="sm" isActive disabled>{{
              news?.category
            }}</StateButton>
            <h2 class="article__header-title">{{ news?.title }}</h2>
            <div class="article__header-writer">
              <span>{{ news.writer }}</span>
              <span> 🕒 {{ formatDate(news.write_date) }}</span>
            </div>
          </div>

          <p class="article__content">{{ news?.content }}</p>

          <div class="article__tags">
            <StateButton
              v-for="(tag, index) in news.keywords"
              :key="index"
              type="tag"
              size="sm"
            >
              #{{ tag }}
            </StateButton>
          </div>

          <div class="article__content__footer">
            <div class="article__content__emoji">
              <span class="emoji-btn">
                <span v-if="liked"> ❤️ </span> <span v-else>🤍</span
                >{{ likeCount }}
              </span>
              <div class="emoji-btn">
                <span class="content__emoji-eye"> 👀 </span
                >{{ news?.views }}
              </div>

              <a :href="news.url">📄</a>
            </div>
            <div style="display: flex; gap: 12px; position: relative;">
              <button class="emoji-btn" @click="handleLike">
                <span>{{ liked ? "❤️" : "🤍" }} 좋아요</span>
              </button>
              <button class="emoji-btn" @click="handleBookmark">
                <span :style="{ color: isBookmarked ? '#f4b400' : '#888' }">
                  {{ isBookmarked ? "🔖" : "📑" }}
                </span>
                북마크
              </button>
              <!-- 좋아요 애니메이션 -->
              <transition name="heart-float">
                <span v-if="isAnimating" class="floating-heart">
                  {{ liked ? "❤️" : "🤍" }}
                </span>
              </transition>
              <!-- 북마크 애니메이션 -->
              <transition name="bookmark-float">
                <span v-if="isBookmarkAnimating" class="floating-bookmark">
                  {{ isBookmarked ? "🔖" : "📑" }}
                </span>
              </transition>
            </div>
          </div>
        </div>
      </ContentBox>
    </div>

    <ContentBox class="sidebar">
      <h1 class="sidebar__title">📰 관련 기사</h1>
      <div v-for="(article, index) in relatedNews" :key="index">
        <ArticlePreview :to="`/news/${article.id}`" :news="article" />
      </div>
    </ContentBox>

    <!-- 챗봇 컴포넌트 추가 -->
    
  </div>
  <div>
    <ArticleChatbot v-if="news" :articleId="news.id" />
  </div>
</template>

<style scoped lang="scss">
.back-btn {
  margin-bottom: 10px;
}

.news-detail {
  display: flex;
  gap: 20px;

  @media (max-width: 800px) {
    flex-direction: column;
  }

  .article__container {
    flex: 2;
    display: flex;
    flex-direction: column;
    gap: 50px;
  }

  .sidebar {
    flex: 1;
    &__title {
      font-weight: 700;
      font-size: 18px;
      margin-bottom: 20px;
    }
  }

  .article {
    font-size: 1rem;
    padding: 20px;
    &__header {
      color: #888;
      font-size: 0.9rem;
      margin-bottom: 10px;
      &-title {
        margin: 12px 0;
        font-size: 1.6rem;
        font-weight: bold;
        color: var(--c-text);
      }
      &-writer {
        display: flex;
        gap: 10px;
      }
    }

    &__content {
      margin: 16px 0;
      line-height: 1.6;
      color: var(--c-text);

      &__footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 30px;
      }

      &__emoji {
        color: #888;
        font-size: 16px;
        display: flex;
        gap: 30px;
        align-items: center;
        &-eye {
          font-size: 17px;
        }
      }
    }

    &__tags {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 15px;
    }
  }

  .emoji-btn {
    display: flex;
    align-items: center;
    font-size: 15px;
    color: #888;
  }

  .floating-heart {
    position: absolute;
    font-size: 24px;
    color: red;
    animation: heartFloat 0.6s ease-out forwards;
  }

  .floating-bookmark {
    position: absolute;
    font-size: 24px;
    color: #f4b400;
    animation: bookmarkFloat 0.6s ease-out forwards;
  }

  @keyframes heartFloat {
    0% {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    50% {
      opacity: 0.8;
      transform: translateY(-20px) scale(1.2);
    }
    100% {
      opacity: 0;
      transform: translateY(-40px) scale(0.8);
    }
  }

  @keyframes bookmarkFloat {
    0% {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    50% {
      opacity: 0.8;
      transform: translateY(-20px) scale(1.2);
    }
    100% {
      opacity: 0;
      transform: translateY(-40px) scale(0.8);
    }
  }
}
</style>
