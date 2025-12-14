<script setup>
import { inject } from 'vue';

const isDarkMode = inject('isDarkMode');
</script>

<template>
  <div class="box" :class="{ 'dark-mode': isDarkMode }">
    <slot />
  </div>
</template>

<style scoped lang="scss">
.box {
  background-color: var(--c-card-bg);
  border: 1px solid var(--c-border);
  border-radius: 10px;
  box-shadow: 0 2px 8px var(--c-card-shadow);
  width: 100%;
  padding: 20px;
  transition: all 0.3s ease;
}

.dark-mode {
  background-color: var(--c-card-bg);
  border-color: var(--c-border);
  box-shadow: 0 2px 8px var(--c-card-shadow);
}
</style>
