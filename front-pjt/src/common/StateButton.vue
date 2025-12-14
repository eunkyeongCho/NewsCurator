<script setup>
import { computed, useAttrs, defineProps, defineEmits, inject } from "vue";
import { useRouter } from "vue-router";

const props = defineProps(['isActive']);
const type = computed(() => props.type || "button");
const size = computed(() => props.size || "md");
const isActive = computed(() => props.isActive || false);
const isDarkMode = inject('isDarkMode');

const router = useRouter();

const buttonSizeClass = computed(() => size.value);
const buttonTypeClass = computed(() => type.value);

const attrs = useAttrs();

const emit = defineEmits(["click"]);

function handleClick() {
  emit("click");
  if (props.to) {
    router.push(props.to);
  }
}
</script>

<template>
  <button
    :class="[
      'toggle-button',
      props.class,
      buttonSizeClass,
      buttonTypeClass,
      { active: props.isActive },
      { 'dark-mode': isDarkMode }
    ]"
    v-bind="attrs"
    @click="handleClick"
  >
    <slot></slot>
  </button>
</template>

<style scoped lang="scss">
.toggle-button {
  white-space: nowrap;
  padding: 10px 20px;
  font-size: 16px;
  border: 1px solid var(--c-border);
  border-radius: 8px;
  background-color: var(--c-card-bg);
  color: var(--c-text);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;

  &.tag {
    background-color: var(--c-gray-100);
    cursor: default;
    border: none;
    font-weight: 600;
  }

  &.active {
    background-color: var(--c-primary);
    color: white;
    box-shadow: 0 2px 10px var(--c-card-shadow);
    transform: scale(1.05);
    transition: all 0.2s ease-in-out;

    &:hover {
      background-color: var(--c-primary-hover);
    }
  }

  &:hover {
    background-color: var(--c-gray-100);
  }

  &.sm {
    padding: 4px 10px;
    font-size: 12px;
  }

  &.md {
    padding: 8px 12px;
    font-size: 14px;
  }

  &:disabled {
    pointer-events: none;
    opacity: 0.6;
  }

  &.dark-mode {
    background-color: var(--c-card-bg);
    color: var(--c-text);
    border-color: var(--c-border);

    &:hover {
      background-color: var(--c-gray-200);
    }

    &.active {
      background-color: var(--c-primary);
      color: white;

      &:hover {
        background-color: var(--c-primary-hover);
      }
    }

    &.tag {
      background-color: var(--c-gray-200);
      color: var(--c-text);
    }
  }
}
</style>
