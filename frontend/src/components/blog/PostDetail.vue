<script setup lang="ts">
import { computed } from 'vue'
import { NIcon } from 'naive-ui'
import { HeartOutline } from '@vicons/ionicons5'
import ArDivider from '@/components/ui/ArDivider.vue'
import TagList from './TagList.vue'
import type { BlogPost } from '@/services/api'

const props = defineProps<{
  post: BlogPost
}>()

const emit = defineEmits<{
  like: []
  favorite: []
}>()

const authorName = computed(() => props.post.author_username || '匿名')
const dateStr = computed(() => props.post.created_at?.slice(0, 10) || '-')
</script>

<template>
  <article class="post-detail">
    <h1 class="post-title">{{ post.title }}</h1>

    <div class="post-meta">
      <span class="meta-author">{{ authorName }}</span>
      <span class="meta-dot">·</span>
      <span class="meta-date">{{ dateStr }}</span>
      <span v-if="post.views !== undefined" class="meta-dot">·</span>
      <span v-if="post.views !== undefined" class="meta-views">{{ post.views }} 阅读</span>
    </div>

    <TagList v-if="post.tags && post.tags.length > 0" :tags="post.tags" class="post-tags" />

    <ArDivider />

    <div class="post-content">{{ post.content }}</div>

    <ArDivider />

    <div class="post-actions">
      <button class="action-btn" @click="emit('like')">
        <NIcon size="18">
          <HeartOutline />
        </NIcon>
        <span>{{ post.likes || 0 }}</span>
      </button>
      <button class="action-btn" @click="emit('favorite')">
        <NIcon size="18">
          <HeartOutline />
        </NIcon>
        <span>收藏</span>
      </button>
    </div>
  </article>
</template>

<style scoped>
.post-detail {
  max-width: 720px;
  margin: 0 auto;
  font-family: var(--font-sans);
}

.post-title {
  margin: 0 0 var(--spacing-md);
  font-size: 26px;
  font-weight: var(--font-weight-bold);
  line-height: 1.3;
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
  margin-bottom: var(--spacing-md);
}

.post-content {
  font-size: 15px;
  line-height: 1.9;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.post-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-full);
  background: var(--surface-color);
  color: var(--text-secondary);
  font-family: var(--font-sans);
  font-size: 13px;
  cursor: pointer;
  transition:
    background-color var(--transition-fast),
    border-color var(--transition-fast),
    color var(--transition-fast);
  touch-action: manipulation;
}

.action-btn:hover {
  background: var(--primary-light-color);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.action-btn:active {
  transform: scale(0.96);
}
</style>
