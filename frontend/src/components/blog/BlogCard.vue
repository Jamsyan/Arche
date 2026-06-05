<script setup lang="ts">
import { computed } from 'vue'
import { NIcon, NTag } from 'naive-ui'
import {
  PersonOutline,
  HeartOutline,
  BookmarkOutline,
  ShareSocialOutline,
  FlameOutline
} from '@vicons/ionicons5'
import type { BlogPost } from '@/services/api'

const props = withDefaults(
  defineProps<{
    post: BlogPost
    layout?: 'grid' | 'list' | 'compact'
    showCover?: boolean
    showExcerpt?: boolean
    showMeta?: boolean
    showActions?: boolean
    coverHeight?: number
  }>(),
  {
    layout: 'grid',
    showCover: false,
    showExcerpt: true,
    showMeta: true,
    showActions: false,
    coverHeight: 152
  }
)

const emit = defineEmits<{
  open: [post: BlogPost]
}>()

const authorName = computed(() => props.post.author_username || '匿名')
const coverUrl = computed(
  () => `https://picsum.photos/seed/${encodeURIComponent(props.post.slug || props.post.id)}/280/360`
)
const dateStr = computed(() => props.post.created_at?.slice(0, 10) || '-')
const excerpt = computed(() => props.post.content?.slice(0, 120) || '暂无摘要')
const firstTag = computed(() => (props.post.tags || [])[0] || '日志')
const shareCount = computed(() => Math.max(1, Math.round((props.post.views || 0) / 18)))
const favoriteCount = computed(() => Math.max(1, Math.round((props.post.likes || 0) * 0.65)))
const displayTags = computed(() => (props.post.tags || []).slice(0, 3))
</script>

<template>
  <article
    class="blog-card"
    :class="[`blog-card--${layout}`, { 'has-cover': showCover }]"
    :style="showCover && layout === 'grid' ? { '--cover-height': `${coverHeight}px` } : undefined"
    @click="emit('open', post)"
  >
    <!-- Grid 封面区域 -->
    <div v-if="layout === 'grid' && showCover" class="card-cover">
      <img
        class="cover-image"
        :src="coverUrl"
        :alt="`${post.title} 封面`"
        width="120"
        height="152"
        loading="lazy"
      />
      <div class="cover-overlay">
        <span class="cover-tag">{{ firstTag }}</span>
        <span class="cover-date">{{ dateStr }}</span>
      </div>
    </div>

    <!-- 正文区域 -->
    <div class="card-body">
      <!-- 作者行（grid 布局） -->
      <div v-if="layout === 'grid' && showMeta" class="card-author">
        <span class="author-avatar">
          <NIcon size="14" aria-hidden="true">
            <PersonOutline />
          </NIcon>
        </span>
        <span class="author-name">@{{ authorName }}</span>
      </div>

      <!-- 标题 -->
      <h4 class="card-title">{{ post.title }}</h4>

      <!-- 摘要 -->
      <p v-if="showExcerpt && layout !== 'compact'" class="card-excerpt">{{ excerpt }}</p>

      <!-- 标签（list / compact 布局） -->
      <div v-if="layout !== 'grid' && displayTags.length > 0" class="card-tags">
        <NTag v-for="tag in displayTags" :key="tag" size="small">{{ tag }}</NTag>
      </div>

      <!-- 元信息 -->
      <div v-if="showMeta" class="card-meta">
        <span v-if="layout === 'list'">{{ authorName }}</span>
        <span v-if="layout === 'list'">👍 {{ post.likes || 0 }}</span>
        <span v-if="layout === 'list'">👁 {{ post.views || 0 }}</span>
        <span>{{ dateStr }}</span>
      </div>
    </div>

    <!-- 交互芯片（grid 布局） -->
    <footer v-if="layout === 'grid' && showActions" class="card-actions">
      <span class="action-chip" title="点赞">
        <NIcon size="16"><HeartOutline /></NIcon>
        <em>{{ post.likes || 0 }}</em>
      </span>
      <span class="action-chip" title="收藏">
        <NIcon size="16"><BookmarkOutline /></NIcon>
        <em>{{ favoriteCount }}</em>
      </span>
      <span class="action-chip" title="分享">
        <NIcon size="16"><ShareSocialOutline /></NIcon>
        <em>{{ shareCount }}</em>
      </span>
      <span class="action-chip action-chip--hot" title="热度">
        <NIcon size="16"><FlameOutline /></NIcon>
        <em>{{ post.views || 0 }}</em>
      </span>
    </footer>
  </article>
</template>

<style scoped>
.blog-card {
  cursor: pointer;
  touch-action: manipulation;
}

/* ── Grid 布局 ── */
.blog-card--grid {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-glass);
  padding: 14px;
  display: grid;
  grid-template-rows: auto 24px minmax(0, 1fr) 52px;
  gap: 10px;
  min-height: 286px;
  isolation: isolate;
  position: relative;
  transition:
    box-shadow 0.28s ease,
    border-color 0.28s ease;
}

.blog-card--grid::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid color-mix(in srgb, var(--primary-color) 24%, transparent);
  box-shadow: 0 10px 22px var(--paper-shadow-color);
  opacity: 0;
  transition:
    opacity 0.28s ease,
    transform 0.28s ease;
  pointer-events: none;
  z-index: -1;
}

.blog-card--grid:hover {
  border-color: color-mix(in srgb, var(--primary-color) 34%, transparent);
  box-shadow: 0 12px 24px color-mix(in srgb, #432d1c 16%, transparent);
}

.blog-card--grid:hover::after {
  opacity: 1;
  transform: translateY(-3px);
}

/* Grid 有封面时调整行布局 */
.blog-card--grid.has-cover {
  grid-template-rows: auto 24px minmax(0, 1fr) 52px;
}

/* ── 封面 ── */
.card-cover {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--surface-color);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px;
  min-height: var(--cover-height, 152px);
}

.cover-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px;
  background: linear-gradient(
    180deg,
    rgba(15, 23, 42, 0.1) 0%,
    rgba(15, 23, 42, 0.32) 62%,
    rgba(15, 23, 42, 0.5) 100%
  );
}

.cover-tag {
  align-self: flex-start;
  font-size: 11px;
  color: var(--text-on-primary, #fff);
  background: rgba(15, 23, 42, 0.32);
  border-radius: 999px;
  padding: 2px 8px;
}

.cover-date {
  align-self: flex-end;
  font-size: 11px;
  color: var(--text-on-primary, #fff);
}

/* ── 正文 ── */
.card-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.blog-card--grid .card-body {
  flex: 1;
  min-height: 152px;
}

.blog-card--grid.has-cover .card-body {
  min-height: auto;
}

/* ── 作者行 ── */
.card-author {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 24px;
  min-width: 0;
  margin-bottom: 6px;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--primary-light-color);
  border: 1px solid color-mix(in srgb, var(--primary-color) 24%, transparent);
  color: color-mix(in srgb, var(--primary-pressed-color) 65%, transparent);
  flex-shrink: 0;
}

.author-name {
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
}

/* ── 标题 ── */
.card-title {
  margin: 0;
  font-size: 17px;
  line-height: 1.35;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.blog-card--list .card-title {
  font-size: 18px;
  -webkit-line-clamp: 2;
}

.blog-card--compact .card-title {
  font-size: 14px;
  font-weight: 500;
  -webkit-line-clamp: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── 摘要 ── */
.card-excerpt {
  margin: 10px 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 13px;
}

.blog-card--grid .card-excerpt {
  margin: 14px 0 0;
  line-height: 22px;
  font-weight: 500;
  background: var(--primary-light-color);
  border-left: 3px solid color-mix(in srgb, var(--primary-color) 34%, transparent);
  border-radius: 8px;
  padding: 10px 10px 10px 12px;
  font-family: 'PingFang SC', 'Microsoft YaHei UI', 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
  overflow: hidden;
  max-height: calc(22px * 3 + 20px);
}

.blog-card--list .card-excerpt {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* ── 标签 ── */
.card-tags {
  display: flex;
  gap: 8px;
  margin: 8px 0 0;
  flex-wrap: wrap;
}

.blog-card--compact .card-tags {
  margin: 0 0 0 10px;
}

/* ── 元信息 ── */
.card-meta {
  font-size: 12px;
  color: var(--text-tertiary);
}

.blog-card--grid .card-meta {
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 12px;
  align-items: center;
}

.blog-card--list .card-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 8px;
  font-size: 13px;
}

.blog-card--compact .card-meta {
  flex-shrink: 0;
}

/* ── List 布局 ── */
.blog-card--list {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-glass);
  padding: 18px;
  transition:
    box-shadow 0.28s ease,
    border-color 0.28s ease;
}

.blog-card--list:hover {
  border-color: color-mix(in srgb, var(--primary-color) 34%, transparent);
  box-shadow: 0 12px 24px color-mix(in srgb, #432d1c 16%, transparent);
}

/* ── Compact 布局 ── */
.blog-card--compact {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease;
}

.blog-card--compact:hover {
  background: color-mix(in srgb, var(--primary-color) 4%, transparent);
  border-color: color-mix(in srgb, var(--primary-color) 24%, transparent);
}

.blog-card--compact .card-body {
  display: flex;
  flex-direction: row;
  align-items: center;
  min-width: 0;
  flex: 1;
  gap: 10px;
}

/* ── 交互芯片 ── */
.card-actions {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  min-width: 0;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.action-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 3px 6px;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--surface-color);
  color: var(--text-secondary);
  line-height: 1;
  min-width: 0;
}

.action-chip em {
  font-style: normal;
  font-size: 11px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.action-chip--hot {
  color: var(--primary-color);
  border-color: color-mix(in srgb, var(--primary-color) 24%, transparent);
  background: var(--primary-light-color);
}

/* ── 统计数字等宽 ── */
.blog-card--grid .card-meta span,
.blog-card--list .card-meta span {
  font-variant-numeric: tabular-nums;
}
</style>
