<script setup lang="ts">
import { computed } from 'vue'
import { NIcon } from 'naive-ui'
import { EyeOutline, HeartOutline } from '@vicons/ionicons5'
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

const hasRealCover = computed(() => !!props.post.cover_url)

const displayCoverUrl = computed(() => props.post.cover_url || '')

const shortExcerpt = computed(() => {
  const text = props.post.introduction?.abstract ?? ''
  return text.slice(0, 50)
})

const excerpt = computed(() => {
  const text = props.post.introduction?.abstract ?? ''
  return text.slice(0, 120)
})

const authorName = computed(() => props.post.author_username || '匿名')
const authorDisplay = computed(() => `@ ${authorName.value}`)

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
  <PostCardBase :post="post" class="post-card-grid" @open="$emit('open', $event)">
    <template #cover>
      <div class="grid-cover-wrap">
        <div v-if="displayCoverUrl" class="grid-cover">
          <img :src="displayCoverUrl" alt="" class="grid-cover-img" loading="lazy" />
        </div>
        <!-- 统计数据（右下角） -->
        <div class="grid-cover-stats">
          <span class="grid-stat-item">
            <NIcon size="12"><EyeOutline /></NIcon>
            {{ post.views ?? 0 }}
          </span>
          <span class="grid-stat-item">
            <NIcon size="12"><HeartOutline /></NIcon>
            {{ post.likes ?? 0 }}
          </span>
        </div>
      </div>
    </template>

    <template #content>
      <h4 :class="['grid-title', { 'grid-title--compact': hasRealCover }]">
        {{ post.title }}
      </h4>
      <p v-if="hasRealCover && shortExcerpt" class="grid-excerpt grid-excerpt--compact">
        {{ shortExcerpt }}
      </p>
      <p v-if="!hasRealCover" class="grid-excerpt grid-excerpt--expanded">{{ excerpt }}</p>
      <div v-if="displayTags.length > 0" class="grid-tags">
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
      <div class="grid-footer">
        <span class="grid-badge">博主</span>
        <span class="grid-author">{{ authorDisplay }}</span>
        <span class="grid-sep">·</span>
        <span class="grid-time">{{ displayDate }}</span>
      </div>
    </template>

    <template #actions />
  </PostCardBase>
</template>

<style scoped>
.post-card-grid {
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

.post-card-grid:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* ── 封面区 ── */
.grid-cover-wrap {
  position: relative;
  line-height: 0;
}

.grid-cover {
  width: 100%;
  overflow: hidden;
}

.grid-cover-img {
  width: 100%;
  height: auto;
  display: block;
  max-height: 260px;
  object-fit: cover;
}

/* 统计数据（左下角） */
.grid-cover-stats {
  position: absolute;
  bottom: 6px;
  left: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  pointer-events: none;
  z-index: 1;
}

.grid-stat-item {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  font-weight: var(--font-weight-semibold);
  color: #fff;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

/* ── 内容区 ── */
:deep(.pc-content-area) {
  padding: var(--spacing-sm) var(--spacing-md);
  gap: 6px;
  flex: 1;
}

.grid-title {
  margin: 0;
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
  line-height: 1.45;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.grid-title--compact {
  -webkit-line-clamp: 1;
}

.grid-excerpt {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-tertiary);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.grid-excerpt--compact {
  -webkit-line-clamp: 1;
}

.grid-excerpt--expanded {
  -webkit-line-clamp: 4;
  font-size: 13px;
  line-height: 1.55;
}

.grid-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.grid-footer {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  line-height: 18px;
  color: var(--text-tertiary);
  margin-top: auto;
  padding-top: 6px;
  border-top: 1px solid var(--border-color);
}

.grid-badge {
  font-size: 11px;
  font-weight: var(--font-weight-semibold);
  color: var(--primary-color);
  line-height: 18px;
}

.grid-author {
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
  font-size: 12px;
  letter-spacing: 0.01em;
}

.grid-time {
  color: var(--text-quaternary);
}

.grid-sep {
  color: var(--text-quaternary, rgba(26, 24, 23, 0.18));
}
</style>
