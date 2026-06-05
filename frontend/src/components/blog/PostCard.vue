<script setup lang="ts">
import { computed } from 'vue'
import { NIcon } from 'naive-ui'
import { HeartOutline, BookmarkOutline, ChatbubbleOutline } from '@vicons/ionicons5'
import ArTag from '@/components/ui/ArTag.vue'
import type { BlogPost } from '@/services/api'

type Layout = 'grid' | 'list' | 'compact'

const props = withDefaults(
  defineProps<{
    post: BlogPost
    layout?: Layout
    showCover?: boolean
    showExcerpt?: boolean
    showActions?: boolean
  }>(),
  {
    layout: 'grid',
    showCover: false,
    showExcerpt: true,
    showActions: false
  }
)

const emit = defineEmits<{
  open: [post: BlogPost]
}>()

const TAG_COLORS = ['red', 'blue', 'yellow', 'green', 'default'] as const

const authorName = computed(() => props.post.author_username || '匿名')
const coverUrl = computed(
  () => `https://picsum.photos/seed/${encodeURIComponent(props.post.slug || props.post.id)}/400/300`
)
const dateStr = computed(() => props.post.created_at?.slice(0, 10) || '-')
const excerpt = computed(() => props.post.content?.slice(0, 150) || '')
const displayTags = computed(() => (props.post.tags || []).slice(0, 3))

function tagColor(index: number) {
  return TAG_COLORS[index % TAG_COLORS.length]!
}

function handleClick() {
  emit('open', props.post)
}
</script>

<template>
  <article
    :class="['post-card', `post-card--${layout}`, { 'has-cover': showCover && layout === 'grid' }]"
    @click="handleClick"
  >
    <!-- Grid 封面 -->
    <div v-if="showCover && layout === 'grid'" class="card-cover">
      <img :src="coverUrl" :alt="post.title" class="cover-image" loading="lazy" />
      <div class="cover-overlay">
        <span class="cover-count">{{ post.views || 0 }} 阅读</span>
      </div>
    </div>

    <!-- List 封面（左侧小图） -->
    <div v-if="showCover && layout === 'list'" class="list-cover">
      <img :src="coverUrl" :alt="post.title" class="list-cover-image" loading="lazy" />
    </div>

    <!-- 正文 -->
    <div class="card-body">
      <div v-if="layout === 'grid'" class="card-meta-top">
        <span class="meta-author">{{ authorName }}</span>
        <span class="meta-date">{{ dateStr }}</span>
      </div>

      <h4 class="card-title">{{ post.title }}</h4>

      <p v-if="showExcerpt && layout !== 'compact'" class="card-excerpt">
        {{ excerpt }}
      </p>

      <div class="card-footer">
        <div class="card-tags">
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

        <!-- List / Compact 元信息 -->
        <div v-if="layout !== 'grid'" class="meta-row">
          <span class="meta-author">{{ authorName }}</span>
          <span class="meta-sep">·</span>
          <span class="meta-date">{{ dateStr }}</span>
        </div>
      </div>
    </div>

    <!-- 交互栏 -->
    <footer v-if="showActions" class="card-actions">
      <span class="action-item">
        <NIcon size="15"><HeartOutline /></NIcon>
        <em>{{ post.likes || 0 }}</em>
      </span>
      <span class="action-item">
        <NIcon size="15"><BookmarkOutline /></NIcon>
      </span>
      <span class="action-item">
        <NIcon size="15"><ChatbubbleOutline /></NIcon>
      </span>
    </footer>
  </article>
</template>

<style scoped>
.post-card {
  cursor: pointer;
  font-family: var(--font-sans);
  transition:
    transform var(--ease-out-smooth),
    box-shadow var(--ease-out-smooth);
  touch-action: manipulation;
}

.post-card:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* ── Grid ── */
.post-card--grid {
  display: flex;
  flex-direction: column;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.post-card--grid:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.post-card--grid .card-body {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: var(--spacing-sm);
}

/* ── List ── */
.post-card--list {
  display: flex;
  gap: var(--spacing-lg);
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  padding: var(--spacing-lg);
}

.post-card--list:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.post-card--list .card-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* ── Compact ── */
.post-card--compact {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: var(--surface-color);
}

.post-card--compact:hover {
  border-color: var(--primary-color);
  background: var(--primary-light-color);
}

.post-card--compact .card-body {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex: 1;
  min-width: 0;
}

.post-card--compact .card-footer {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

/* ── 封面 ── */
.card-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background: var(--surface-inset-color);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 60%, rgba(26, 24, 23, 0.6) 100%);
  display: flex;
  align-items: flex-end;
  padding: var(--spacing-sm) var(--spacing-md);
}

.cover-count {
  font-size: 12px;
  color: #fff;
}

/* List 封面 */
.list-cover {
  width: 120px;
  height: 90px;
  flex-shrink: 0;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--surface-inset-color);
}

.list-cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* ── 标题 ── */
.card-title {
  margin: 0;
  font-size: 17px;
  font-weight: var(--font-weight-semibold);
  line-height: 1.4;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-card--list .card-title {
  font-size: 18px;
}

.post-card--compact .card-title {
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  -webkit-line-clamp: 1;
  white-space: nowrap;
  text-overflow: ellipsis;
}

/* ── 元信息 ── */
.card-meta-top {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 12px;
  color: var(--text-tertiary);
}

.meta-author {
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
}

.meta-date {
  color: var(--text-tertiary);
}

.meta-sep {
  color: var(--text-quaternary, rgba(26, 24, 23, 0.18));
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  white-space: nowrap;
}

/* ── 摘要 ── */
.card-excerpt {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ── 底部区域 ── */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
  margin-top: auto;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  min-width: 0;
}

/* ── 交互栏 ── */
.card-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

.action-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

.action-item em {
  font-style: normal;
}
</style>
