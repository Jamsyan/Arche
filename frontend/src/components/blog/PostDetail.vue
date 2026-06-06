<script setup lang="ts">
import { computed } from 'vue'
import TagList from './TagList.vue'
import type { BlogPost } from '@/services/api'

const props = defineProps<{
  post: BlogPost
}>()

const authorName = computed(() => props.post.author_username || '匿名')
const dateStr = computed(() => props.post.created_at?.slice(0, 10) || '-')

const trimmedContent = computed(() => props.post.content?.trimStart() || '')
const firstChar = computed(() => trimmedContent.value.charAt(0) || '')
const restContent = computed(() => trimmedContent.value.slice(1) || '')
</script>

<template>
  <article class="post-detail">
    <!-- 文章头部 -->
    <header class="post-header">
      <div class="header-accent" />
      <div class="post-eyebrow">BLOG</div>
      <h1 class="post-title">{{ post.title }}</h1>
      <div class="post-meta">
        <span class="meta-author">{{ authorName }}</span>
        <span class="meta-dot">·</span>
        <span class="meta-date">{{ dateStr }}</span>
        <span v-if="post.views !== undefined" class="meta-dot">·</span>
        <span v-if="post.views !== undefined" class="meta-views">{{ post.views }} 阅读</span>
      </div>
      <TagList v-if="post.tags && post.tags.length > 0" :tags="post.tags" class="post-tags" />
    </header>

    <!-- 分隔线 -->
    <div class="content-divider" />

    <!-- 正文 -->
    <div class="post-content">
      <span class="drop-cap">{{ firstChar }}</span
      >{{ restContent }}
    </div>
  </article>
</template>

<style scoped>
.post-detail {
  max-width: 720px;
  margin: 0 auto;
  animation: post-enter 0.6s var(--ease-out-smooth) both;
}

@keyframes post-enter {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── 文章头部 ── */
.post-header {
  position: relative;
  padding-top: var(--spacing-xl);
}

.header-accent {
  position: absolute;
  top: 0;
  left: 0;
  width: 48px;
  height: 3px;
  background: var(--primary-color);
  border-radius: 2px;
}

.post-eyebrow {
  font-size: 11px;
  letter-spacing: 0.15em;
  color: var(--text-tertiary);
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-medium);
}

.post-title {
  margin: 0 0 var(--spacing-md);
  font-size: 28px;
  font-weight: var(--font-weight-bold);
  line-height: 1.35;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: var(--spacing-md);
}

.meta-author {
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
}

.meta-dot {
  color: var(--divider-color);
  user-select: none;
}

.post-tags {
  margin-bottom: 0;
}

/* ── 分隔线 ── */
.content-divider {
  height: 1px;
  margin: var(--spacing-xl) 0;
  background: linear-gradient(
    90deg,
    var(--primary-color) 0%,
    var(--divider-color) 30%,
    transparent 100%
  );
  opacity: 0.5;
}

/* ── 正文 ── */
.post-content {
  font-family: var(--font-serif);
  font-size: 16.5px;
  line-height: 2;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.drop-cap {
  float: left;
  font-size: 58px;
  line-height: 0.85;
  font-weight: var(--font-weight-bold);
  color: var(--primary-color);
  margin-right: 12px;
  margin-top: 4px;
  font-family: var(--font-serif);
  letter-spacing: -0.03em;
}
</style>
