<script setup lang="ts">
import { computed } from 'vue'

/**
 * ArAvatar — 全局统一用户头像组件
 *
 * - 默认显示 PersonCircleOutline SVG 图标（直接渲染，无 NIcon 底部间隙）
 * - 有 avatarUrl 时显示图片
 * - 总是可点击
 * - 统一底色和大小
 */

const props = withDefaults(
  defineProps<{
    username?: string
    avatarUrl?: string
    size?: number
    clickable?: boolean
  }>(),
  { size: 30, clickable: true }
)

const emit = defineEmits<{
  click: [e: MouseEvent]
}>()

const style = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  cursor: props.clickable ? 'pointer' : 'default'
}))

function handleClick(e: MouseEvent) {
  if (props.clickable) emit('click', e)
}
</script>

<template>
  <div class="ar-avatar" :style="style" :title="username" @click="handleClick">
    <img v-if="avatarUrl" :src="avatarUrl" :alt="username || '头像'" class="ar-avatar__img" />
    <svg v-else class="ar-avatar__svg" viewBox="0 0 512 512" fill="currentColor">
      <path
        d="M258.9 48C141.92 46.42 46.42 141.92 48 258.9c1.56 112.19 92.91 203.54 205.1 205.1c117 1.6 212.48-93.9 210.88-210.88C462.44 140.91 371.09 49.56 258.9 48zm126.42 327.25a4 4 0 0 1-6.14-.32a124.27 124.27 0 0 0-32.35-29.59C321.37 329 289.11 320 256 320s-65.37 9-90.83 25.34a124.24 124.24 0 0 0-32.35 29.58a4 4 0 0 1-6.14.32A175.32 175.32 0 0 1 80 259c-1.63-97.31 78.22-178.76 175.57-179S432 158.81 432 256a175.32 175.32 0 0 1-46.68 119.25z"
      />
      <path
        d="M256 144c-19.72 0-37.55 7.39-50.22 20.82s-19 32-17.57 51.93C191.11 256 221.52 288 256 288s64.83-32 67.79-71.24c1.48-19.74-4.8-38.14-17.68-51.82C293.39 151.44 275.59 144 256 144z"
      />
    </svg>
  </div>
</template>

<style scoped>
.ar-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--primary-light-color);
  color: var(--primary-color);
  flex-shrink: 0;
  overflow: hidden;
  transition: opacity 0.15s ease;
}
.ar-avatar:hover {
  opacity: 0.8;
}
.ar-avatar__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}
.ar-avatar__svg {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
