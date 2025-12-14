<template>
  <div class="news__box">
    <div class="news__box__header" style="padding-bottom: 0;">
      <h2 style="font-size: 1.3rem; font-weight: 700; margin-bottom: 18px;">
        <span style="font-size:1.2em; margin-right:6px;">🔖</span>
        {{ username }}님의 북마크 기사 모아보기
      </h2>
    </div>
    <div class="news__box__cards">
      <router-link
        v-for="article in bookmarks"
        :key="article.id"
        :to="`/news/${article.id}`"
        class="news-card-link"
        style="text-decoration: none; color: inherit;"
      >
        <div class="news-card">
          <div class="news-card__category">{{ article.category }}</div>
          <div class="news-card__meta">
            <span>{{ article.writer }}</span>
            <span>·</span>
            <span>{{ article.write_date?.slice(0, 10) }}</span>
          </div>
          <h3 class="news-card__title">{{ article.title }}</h3>
          <p class="news-card__content">{{ article.content.slice(0, 120) }}...</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const username = ref('');
const bookmarks = ref([]);

onMounted(async () => {
  const res = await axios.get('http://localhost:8000/api/user_bookmark/', { withCredentials: true });
  username.value = res.data.user.username;
  bookmarks.value = res.data.bookmarks;
});
</script>

<style scoped>
.news__box {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 32px 32px 24px 32px;
  margin: 32px auto 0 auto;
  max-width: 900px;
  min-height: 400px;
}
.news__box__header {
  margin-bottom: 0;
}
.news__box__cards {
  display: flex;
  flex-direction: column;
  gap: 32px;
}
.news-card-link {
  display: block;
  transition: box-shadow 0.2s;
  border-radius: 10px;
}
.news-card-link:hover .news-card {
  box-shadow: 0 2px 12px rgba(25, 118, 210, 0.08);
  background: #f7faff;
}
.news-card {
  padding: 24px 0 16px 0;
  border-bottom: 1px solid #eee;
  transition: background 0.2s, box-shadow 0.2s;
}
.news-card__category {
  display: inline-block;
  background: #f5f7fa;
  color: #1976d2;
  font-size: 0.95em;
  font-weight: 600;
  border-radius: 6px;
  padding: 2px 12px;
  margin-bottom: 8px;
}
.news-card__meta {
  color: #888;
  font-size: 0.95em;
  margin-bottom: 4px;
}
.news-card__title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 6px 0 8px 0;
}
.news-card__content {
  color: #444;
  font-size: 1em;
  margin-bottom: 0;
}
</style>