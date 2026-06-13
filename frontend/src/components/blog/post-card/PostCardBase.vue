<script setup lang="ts">
import { computed } from 'vue'
import type { BlogPost } from '@/services/api'
import { getCoverGradient } from '@/utils/cover'
import { buildExcerptFallback } from './utils'

const props = defineProps<{
  post: BlogPost
}>()

const emit = defineEmits<{
  open: [post: BlogPost]
}>()

const coverStyle = computed(() => {
  const url = props.post.cover_url
  if (url) {
    return {
      backgroundImage: `url(${url})`,
      backgroundSize: 'cover' as const,
      backgroundPosition: 'center' as const
    }
  }
  return { background: getCoverGradient(props.post) }
})

const excerpt = computed(() => {
  const abstract = props.post.introduction?.abstract
  if (abstract) return abstract.slice(0, 120)
  return buildExcerptFallback(props.post)
})

function handleClick() {
  emit('open', props.post)
}
</script>

<template>
  <article class="pc-base" @click="handleClick">
    <!-- 封面区插槽，默认使用渐变色占位 -->
    <div class="pc-cover-area">
      <slot name="cover">
        <div class="pc-cover-fallback" :style="coverStyle" />
      </slot>
    </div>

    <!-- 内容区插槽，默认显示标题 + 摘要 -->
    <div class="pc-content-area">
      <slot name="content">
        <h4 class="pc-title">{{ post.title }}</h4>
        <p v-if="excerpt" class="pc-excerpt">{{ excerpt }}</p>
      </slot>
    </div>

    <!-- 底部插槽 -->
    <div class="pc-actions-area">
      <slot name="actions" />
    </div>
  </article>
</template>

<style scoped>
/* ── 通用 ── */
.pc-base {
  cursor: pointer;
  font-family: var(--font-sans);
  transition:
    transform var(--ease-out-smooth),
    box-shadow var(--ease-out-smooth);
  touch-action: manipulation;
}
.pc-base:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* ── 封面区 ── */
.pc-cover-area {
  line-height: 0;
}

.pc-cover-fallback {
  width: 100%;
  height: 100%;
  min-height: 100px;
  background-size: cover;
  background-position: center;
}

/* ── 内容区 ── */
.pc-content-area {
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pc-title {
  margin: 0;
  font-size: 16px;
  font-weight: var(--font-weight-semibold);
  line-height: 1.4;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pc-excerpt {
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ── 底部区 ── */
.pc-actions-area {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  border-top: 1px solid var(--border-color);
}
</style>
