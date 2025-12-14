<script setup>
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import { computed, inject } from "vue";

const props = defineProps(['data']);
const isDarkMode = inject('isDarkMode');

const { formatDate } = useDate();
const date = computed(() => formatDate(props.data.write_date));
</script>

<template>
  <div class="card" :class="{ 'dark-mode': isDarkMode }">
    <div class="card__header">
      <StateButton type="state" size="sm" disabled>{{
        props.data.category
      }}</StateButton>
      <span class="card__header-item">{{ props.data.writer }}</span>
      <span class="card__header-item">· {{ date }}</span>
    </div>
    <RouterLink :to="{ name: 'newsDetail', params: { id: props.data.id } }">
      <h2 class="title">{{ props.data.title }}</h2>
      <p class="description">{{ props.data.content }}</p>
    </RouterLink>
    <div class="stats">
      <span>❤️ {{ props.data.likes || 0 }}</span>
      <span>👀 {{ props.data.views || 0 }}</span>
      <a :href="props.data.url">📄</a>
    </div>

    <div class="tags">
      <StateButton
        v-for="(tag, index) in props.data.keywords"
        :key="index"
        type="tag"
        size="sm"
      >
        #{{ tag }}
      </StateButton>
    </div>
  </div>
</template>

<style scoped lang="scss">
.card {
  background-color: var(--c-card-bg);
  width: 80%;
  padding: 20px;
  margin-bottom: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px var(--c-card-shadow);
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    box-shadow: 0 2px 12px var(--c-card-shadow);
    background: var(--c-gray-100);
  }

  a {
    text-decoration: none;
    color: inherit;
  }

  &__header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
    color: var(--c-text-secondary);
    &-item {
      font-weight: normal;
    }
  }

  .title {
    margin: 12px 0;
    font-size: 22px;
    font-weight: bold;
    color: var(--c-text);
  }

  .description {
    font-size: 1rem;
    width: 90%;
    color: var(--c-text-secondary);
    margin: 15px 0;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.3;
  }

  .stats {
    display: flex;
    gap: 15px;
    font-size: 0.9rem;
    color: var(--c-text-secondary);
    margin-bottom: 15px;
    align-items: center;

    a {
      color: var(--c-primary);
      text-decoration: none;
      
      &:hover {
        color: var(--c-primary-hover);
      }
    }
  }

  .tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    padding-bottom: 40px;
    border-bottom: 1px solid var(--c-border);
  }

  &.dark-mode {
    background-color: var(--c-card-bg);
    box-shadow: 0 2px 8px var(--c-card-shadow);

    &:hover {
      background-color: var(--c-gray-200);
      box-shadow: 0 2px 12px var(--c-card-shadow);
    }

    .title {
      color: var(--c-text);
    }

    .description {
      color: var(--c-text-secondary);
    }

    .stats {
      color: var(--c-text-secondary);
    }

    .tags {
      border-bottom-color: var(--c-border);
    }
  }
}
</style>
