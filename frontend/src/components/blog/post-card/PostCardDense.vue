<script setup lang="ts">
import { computed } from 'vue'
import ArTag from '@/components/ui/ArTag.vue'
import PostCardBase from './PostCardBase.vue'
import type { BlogPost } from '@/services/api'

const props = defineProps<{
  post: BlogPost
}>()

defineEmits<{
  open: [post: BlogPost]
}>()

const TAG_COLORS = ['red', 'blue', 'yellow', 'green', 'default'] as const

const displayTags = computed(() => (props.post.tags || []).slice(0, 3))

function tagColor(index: number) {
  return TAG_COLORS[index % TAG_COLORS.length]!
}

const authorDisplay = computed(() => `@ ${props.post.author_username || '匿名'}`)

/** 摘要为空时，用帖子元信息作为替代展示 */
function buildExcerptFallback(post: BlogPost): string {
  const parts: string[] = []
  const intro = post.introduction
  if (intro?.difficulty_level) parts.push(intro.difficulty_level)
  if (post.category_id) parts.push(post.category_id)
  if (parts.length > 0) return parts.join(' · ')
  return ''
}

const shortExcerpt = computed(() => {
  const abstract = props.post.introduction?.abstract
  if (abstract) return abstract.slice(0, 50)
  return buildExcerptFallback(props.post)
})

/** 日期格式化：今年 → "04-01"，往年 → "2025-04-01" */
function formatDate(dateStr: string): string {
  if (!dateStr || dateStr === '-') return '-'
  const date = new Date(dateStr)
  const now = new Date()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  if (date.getFullYear() === now.getFullYear()) {
    return `${month}-${day}`
  }
  return `${date.getFullYear()}-${month}-${day}`
}

const displayDate = computed(() => formatDate(props.post.created_at || ''))
</script>

<template>
  <PostCardBase :post="post" class="post-card-dense" @open="$emit('open', $event)">
    <template #content>
      <h4 class="dense-title">{{ post.title }}</h4>
      <p v-if="shortExcerpt" class="dense-excerpt">{{ shortExcerpt }}</p>
      <div class="dense-meta">
        <span class="dense-author">
          <span class="dense-badge">博主</span>
          {{ authorDisplay }}
        </span>
        <span class="dense-sep">·</span>
        <span class="dense-time">{{ displayDate }}</span>
        <span class="dense-sep">·</span>
        <span class="dense-likes">♥ {{ post.likes || 0 }}</span>
      </div>
      <div v-if="displayTags.length > 0" class="dense-tags">
        <ArTag
          v-for="(tag, i) in displayTags"
          :key="tag"
          :color="tagColor(i)"
          size="sm"
          type="light"
        >
          {{ tag }}
        </ArTag>
      </div>
    </template>

    <template #cover />
    <template #actions />
  </PostCardBase>
</template>

<style scoped>
.post-card-dense {
  display: flex;
  flex-direction: column;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition:
    transform 0.2s var(--ease-out-smooth),
    box-shadow 0.2s var(--ease-out-smooth);
}

.post-card-dense:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

:deep(.pc-content-area) {
  padding: var(--spacing-md);
  gap: 6px;
}

.dense-title {
  margin: 0;
  font-size: 15px;
  font-weight: var(--font-weight-semibold);
  line-height: 1.4;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dense-excerpt {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dense-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  line-height: 18px;
  color: var(--text-tertiary);
  flex-wrap: wrap;
}

.dense-author {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
}

.dense-badge {
  font-size: 11px;
  font-weight: var(--font-weight-semibold);
  line-height: 18px;
  color: var(--primary-color);
}

.dense-time {
  color: var(--text-quaternary);
}

.dense-likes {
  color: var(--text-tertiary);
}

.dense-sep {
  color: var(--text-quaternary, rgba(26, 24, 23, 0.18));
}

.dense-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-top: 2px;
}
</style>
