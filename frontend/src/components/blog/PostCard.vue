<script setup lang="ts">
import { computed } from 'vue'
import { NIcon } from 'naive-ui'
import { HeartOutline, BookmarkOutline, ChatbubbleOutline } from '@vicons/ionicons5'
import ArTag from '@/components/ui/ArTag.vue'
import { getCoverGradient } from '@/utils/cover'
import type { BlogPost } from '@/services/api'

type PostCardMode = 'showcase' | 'media' | 'feed' | 'stack' | 'cover'

const props = withDefaults(
  defineProps<{
    post: BlogPost
    mode?: PostCardMode
    /** showcase 模式下是否显示文字叠加层 */
    showOverlay?: boolean
    /** media 模式下是否显示底部分享/点赞栏 */
    showActions?: boolean
    /** stack 模式下左侧标签内容（作者名等） */
    label?: string
    /** cover 模式下观看进度 (0-100) */
    metaProgress?: number
    /** cover 模式下阅读时长文字 */
    metaDuration?: string
  }>(),
  {
    mode: 'media',
    showOverlay: true,
    showActions: false
  }
)

const emit = defineEmits<{
  open: [post: BlogPost]
}>()

const TAG_COLORS = ['red', 'blue', 'yellow', 'green', 'default'] as const

const authorName = computed(() => props.post.author_username || '匿名')
const dateStr = computed(() => props.post.created_at?.slice(0, 10) || '-')

const coverStyle = computed(() => {
  if (props.post.cover_url) {
    return {
      backgroundImage: `url(${props.post.cover_url})`,
      backgroundSize: 'cover' as const,
      backgroundPosition: 'center' as const
    }
  }
  return { background: getCoverGradient(props.post) }
})

function stripHtml(html: string): string {
  const el = document.createElement('div')
  el.innerHTML = html
  return el.textContent || ''
}

const excerpt = computed(() => {
  const text = props.post.content ? stripHtml(props.post.content) : ''
  return text.slice(0, 120) || ''
})
const displayTags = computed(() => (props.post.tags || []).slice(0, 3))

function tagColor(index: number) {
  return TAG_COLORS[index % TAG_COLORS.length]!
}

function handleClick() {
  emit('open', props.post)
}
</script>

<template>
  <article :class="['post-card', `post-card--${mode}`]" @click="handleClick">
    <!-- ═══ showcase: 全出血封面 + 叠加文字 ═══ -->
    <template v-if="mode === 'showcase'">
      <div class="sc-cover" :style="coverStyle">
        <div class="sc-shine" />
      </div>
      <div v-if="showOverlay" class="sc-overlay">
        <div class="sc-overlay-body">
          <span class="sc-author">{{ authorName }}</span>
          <h3 class="sc-title">{{ post.title }}</h3>
        </div>
      </div>
    </template>

    <!-- ═══ media: 封面(<img> 自然宽高比) + 内容卡片 ═══ -->
    <template v-if="mode === 'media'">
      <!-- 有封面 → <img> 保留原始比例，瀑布流下自然产生高矮节奏 -->
      <div v-if="post.cover_url" class="md-cover">
        <img :src="post.cover_url" alt="" class="md-cover-img" loading="lazy" />
      </div>
      <!-- 无封面 → 渐变色占位，固定比例 -->
      <div v-else class="md-cover md-cover--fallback" :style="coverStyle" />

      <div class="md-body">
        <h4 class="md-title">{{ post.title }}</h4>
        <p class="md-excerpt">{{ excerpt }}</p>
        <div class="md-footer">
          <div class="md-meta">
            <span class="md-author">{{ authorName }}</span>
            <span class="md-sep">·</span>
            <span class="md-date">{{ dateStr }}</span>
          </div>
          <div v-if="displayTags.length > 0" class="md-tags">
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
        </div>
      </div>

      <footer v-if="showActions" class="md-actions">
        <span class="action-item">
          <NIcon size="14"><HeartOutline /></NIcon>
          <em>{{ post.likes || 0 }}</em>
        </span>
        <span class="action-item">
          <NIcon size="14"><BookmarkOutline /></NIcon>
        </span>
        <span class="action-item">
          <NIcon size="14"><ChatbubbleOutline /></NIcon>
        </span>
      </footer>
    </template>

    <!-- ═══ feed: 紧凑型（极小缩略图 / 纯文字） ═══ -->
    <template v-if="mode === 'feed'">
      <div v-if="post.cover_url" class="fd-thumb" :style="coverStyle" />
      <div class="fd-body">
        <h4 class="fd-title">{{ post.title }}</h4>
        <div class="fd-meta">
          <span>{{ authorName }}</span>
          <span class="fd-sep">·</span>
          <span>{{ dateStr }}</span>
        </div>
      </div>
    </template>

    <!-- ═══ stack: 紧凑堆叠卡（标签 + 贴面封面 + 标题底栏） ═══ -->
    <template v-if="mode === 'stack'">
      <div class="sk-body">
        <div class="sk-label">
          <span class="sk-label-text">{{ label || authorName }}</span>
        </div>
        <div class="sk-cover" :style="coverStyle">
          <div class="sk-cover-shine" />
        </div>
      </div>
      <div class="sk-title-bar">
        <span class="sk-title">{{ post.title }}</span>
      </div>
    </template>

    <!-- ═══ cover: 全封面 + 信息浮层 ═══ -->
    <template v-if="mode === 'cover'">
      <div class="cv-card" :style="coverStyle">
        <!-- 顶部：左→右渐变，标题 + @作者 -->
        <div class="cv-top-overlay">
          <span class="cv-title">{{ post.title }}</span>
          <span class="cv-author">@{{ authorName }}</span>
        </div>
        <!-- 底部：进度 + 时长 -->
        <div class="cv-bottom-overlay">
          <span v-if="metaProgress != null" class="cv-progress"> 已读 {{ metaProgress }}% </span>
          <span v-if="metaDuration" class="cv-duration">{{ metaDuration }}</span>
        </div>
      </div>
    </template>
  </article>
</template>

<style scoped>
/* ── 通用 ── */
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

/* ══════════ SHOWCASE ══════════ */
.post-card--showcase {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: inherit;
}

.sc-cover {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  border-radius: inherit;
}

.sc-shine {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.08) 0%,
    transparent 40%,
    transparent 60%,
    rgba(255, 255, 255, 0.03) 100%
  );
  pointer-events: none;
}

.sc-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 50%, rgba(26, 24, 23, 0.75) 100%);
  display: flex;
  align-items: flex-end;
  padding: var(--spacing-lg);
  pointer-events: none;
}

.sc-overlay-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sc-author {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
  font-weight: var(--font-weight-medium);
}

.sc-title {
  margin: 0;
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: #fff;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

/* ══════════ MEDIA ══════════ */
.post-card--media {
  display: flex;
  flex-direction: column;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.post-card--media:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.md-cover {
  width: 100%;
  overflow: hidden;
  line-height: 0;
}

.md-cover-img {
  width: 100%;
  height: auto;
  display: block;
  animation: md-img-in 0.4s var(--ease-out-smooth) both;
}

@keyframes md-img-in {
  from {
    opacity: 0;
    transform: scale(1.02);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.md-cover--fallback {
  aspect-ratio: 16 / 9;
  background-size: cover;
  background-position: center;
}

.md-body {
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

/* 底部区域：作者信息 + 标签，自然推到底部 */
.md-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 4px;
}

.md-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-quaternary);
}

.md-author {
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
}

.md-date {
  color: var(--text-tertiary);
}

.md-sep {
  color: var(--text-quaternary, rgba(26, 24, 23, 0.18));
}

.md-title {
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

.md-excerpt {
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.md-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.md-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
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

/* ══════════ FEED ══════════ */
.post-card--feed {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: var(--surface-color);
}

.post-card--feed:hover {
  border-color: var(--primary-color);
  background: var(--primary-light-color);
}

.fd-thumb {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background-size: cover;
  background-position: center;
}

.fd-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.fd-title {
  margin: 0;
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  line-height: 1.4;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fd-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.fd-sep {
  color: var(--text-quaternary, rgba(26, 24, 23, 0.18));
}

/* ══════════ STACK ══════════ */
.post-card--stack {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--surface-strong-color);
}

.sk-body {
  flex: 1;
  display: flex;
  min-height: 0;
}

/* ── 左侧标签（竖排文字，宽可通过 --sk-label-w 覆写） ── */
.sk-label {
  width: var(--sk-label-w, 38px);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  writing-mode: vertical-rl;
  text-orientation: upright;
  background: var(--surface-inset-color);
}

.sk-label-text {
  font-size: 11px;
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  letter-spacing: 2px;
}

/* ── 封面（"贴上去"的层次感） ── */
.sk-cover {
  flex: 1;
  background-size: cover;
  background-position: center;
  position: relative;
  /* 右边上下圆角与卡片对齐 */
  border-top-right-radius: inherit;
  border-bottom-right-radius: inherit;
  /* 左边上下独立小圆角 */
  border-top-left-radius: 5px;
  border-bottom-left-radius: 5px;
  /* 阴影产生"照片贴在表面"的深度感 */
  box-shadow:
    -1px 0 6px rgba(26, 24, 23, 0.06),
    2px 2px 8px rgba(26, 24, 23, 0.1);
}

.sk-cover-shine {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, transparent 50%);
  pointer-events: none;
}

/* ── 底部标题栏（紧凑贴合） ── */
.sk-title-bar {
  padding: var(--sk-title-pad, 8px 10px);
  background: var(--surface-color);
}

.sk-title {
  font-size: var(--sk-title-size, 12px);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  letter-spacing: -0.01em;
}

/* 深色模式适配 */
:global(.dark) .sk-label {
  background: rgba(42, 39, 36, 0.72);
}

:global(.dark) .sk-cover {
  box-shadow:
    -1px 0 6px rgba(0, 0, 0, 0.15),
    2px 2px 8px rgba(0, 0, 0, 0.2);
}

:global(.dark) .sk-title-bar {
  background: rgba(26, 24, 23, 0.88);
}

/* ══════════ COVER ══════════ */
.post-card--cover {
  width: 100%;
  height: 100%;
  border-radius: inherit;
  overflow: hidden;
}

.cv-card {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
}

/* ── 顶部 overlay：左→右渐隐 ── */
.cv-top-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 6px 10px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  background: linear-gradient(
    to right,
    rgba(26, 24, 23, 0.5) 0%,
    rgba(26, 24, 23, 0.18) 50%,
    transparent 100%
  );
  pointer-events: none;
  min-height: 32px;
}

.cv-title {
  font-size: 13px;
  font-weight: var(--font-weight-semibold);
  color: #fff;
  line-height: 1.3;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.35);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  max-width: 72%;
  flex-shrink: 1;
}

.cv-author {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.88);
  white-space: nowrap;
  flex-shrink: 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* ── 底部 overlay：下→上渐隐 ── */
.cv-bottom-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 7px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to top, rgba(26, 24, 23, 0.55) 0%, transparent 100%);
  pointer-events: none;
  min-height: 32px;
}

.cv-progress {
  font-size: 11px;
  font-weight: var(--font-weight-medium);
  color: #fff;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
  font-variant-numeric: tabular-nums;
}

.cv-duration {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* 深色模式 */
:global(.dark) .cv-top-overlay {
  background: linear-gradient(
    to right,
    rgba(0, 0, 0, 0.55) 0%,
    rgba(0, 0, 0, 0.2) 55%,
    transparent 100%
  );
}

:global(.dark) .cv-bottom-overlay {
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6) 0%, transparent 100%);
}
</style>
