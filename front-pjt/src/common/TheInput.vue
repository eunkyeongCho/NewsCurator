<script setup>
import { ref, computed, useAttrs, defineProps, inject } from "vue";

defineOptions({
  inheritAttrs: false,
});

const props = defineProps();
const wrapperClass = computed(() => props.wrapperClass || "");
const value = computed(() => props.value || "");
const modelValue = ref("");
const isDarkMode = inject('isDarkMode');

const attrs = useAttrs();

const errorClass = computed(() => {
  return props.error ? "error" : "";
});
</script>

<template>
  <div :class="['input-box', wrapperClass, errorClass, { 'dark-mode': isDarkMode }]">
    <input type="text" v-model="modelValue" v-bind="attrs" />
  </div>
  <p class="error-msg">{{ props.error }}</p>
</template>

<style scoped lang="scss">
.input-box {
  width: 100%;
  padding: 5px 8px;
  border: 1px solid var(--c-border);
  border-radius: 8px;
  display: flex;
  align-items: center;
  background-color: var(--c-card-bg);
  transition: all 0.3s ease;

  &.error {
    border-color: var(--c-error);
  }

  input {
    width: 100%;
    border: none;
    outline: none;
    background-color: transparent;
    color: var(--c-text);
    padding: 6px;

    &::placeholder {
      color: var(--c-gray-500);
    }

    &:disabled::placeholder {
      color: var(--c-text);
    }
  }

  &.dark-mode {
    background-color: var(--c-gray-100);
    border-color: var(--c-border);

    input {
      color: var(--c-text);

      &::placeholder {
        color: var(--c-gray-500);
      }
    }
  }
}

.error-msg {
  position: absolute;
  color: var(--c-error);
  margin: 5px 0 0 5px;
  font-size: 12px;
}
</style>
