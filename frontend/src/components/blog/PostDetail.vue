<script setup lang="ts">
import { computed } from 'vue'
import TagList from './TagList.vue'
import { getCoverGradient } from '@/utils/cover'
import type { BlogPost } from '@/services/api'

const props = defineProps<{
  post: BlogPost
}>()

const authorName = computed(() => props.post.author_username || '匿名')
const dateStr = computed(() => props.post.created_at?.slice(0, 10) || '-')

// 渲染内容为 HTML
const renderedContent = computed(() => {
  let html = props.post.content || ''

  // 1. 处理视频嵌入 [title](url)
  html = html.replace(
    /\[([^\]]*)\]\((https?:\/\/(?:www\.)?(?:bilibili\.com|youtube\.com)[^)]+)\)/g,
    (_match, title, url) => {
      let embedUrl = ''
      if (url.includes('bilibili.com')) {
        const bvMatch = url.match(/BV[\w]+/)
        if (bvMatch) {
          embedUrl = `https://player.bilibili.com/player.html?bvid=${bvMatch[0]}&autoplay=0`
        } else {
          const avMatch = url.match(/video\/(\d+)/)
          if (avMatch) {
            embedUrl = `https://player.bilibili.com/player.html?aid=${avMatch[1]}&autoplay=0`
          }
        }
      } else if (url.includes('youtube.com')) {
        const vMatch = url.match(/(?:watch\?v=|embed\/|shorts\/)([\w-]+)/)
        if (vMatch) {
          embedUrl = `https://www.youtube.com/embed/${vMatch[1]}`
        }
      }
      if (embedUrl) {
        return `</p><div class="media-block video-block"><iframe src="${embedUrl}" frameborder="0" allowfullscreen></iframe></div><p>`
      }
      // 不是视频链接，保持原样
      return _match
    }
  )

  // 2. 处理图片 [#N]
  html = html.replace(/\[#(\d+)\]/g, (_match, num) => {
    return `</p><div class="media-block image-block"><img src="https://picsum.photos/seed/${props.post.id}_${num}/800/450" alt="图片 #${num}" loading="lazy" /></div><p>`
  })

  // 3. 处理纯文本中的换行为段落
  // 双换行为段落分隔，单换行为 <br>
  html = html.replace(/\n\n/g, '</p><p>')
  html = html.replace(/\n/g, '<br>')

  return `<p>${html}</p>`
})
</script>

<template>
  <article class="post-detail">
    <!-- 封面 -->
    <div v-if="post.cover_url" class="post-cover">
      <img :src="post.cover_url" :alt="post.title" />
    </div>
    <!-- 没有封面时用默认渐变色 -->
    <div v-else class="post-cover-fallback" :style="{ background: getCoverGradient(post) }">
      <span class="cover-fallback-title">{{ post.title?.charAt(0) || 'P' }}</span>
    </div>

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
    <div class="post-content" v-html="renderedContent" />
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

/* ── 封面 ── */
.post-cover {
  width: 100%;
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: var(--spacing-lg);
}

.post-cover img {
  width: 100%;
  height: auto;
  display: block;
}

.post-cover-fallback {
  width: 100%;
  aspect-ratio: 2/1;
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-fallback-title {
  font-size: 48px;
  font-weight: var(--font-weight-bold);
  color: rgba(255, 255, 255, 0.6);
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
  word-break: break-word;
}

.post-content :deep(p) {
  margin: 0 0 1em;
}

.post-content :deep(p:last-child) {
  margin-bottom: 0;
}

.post-content :deep(.media-block) {
  margin: 0;
  text-align: center;
}

.post-content :deep(.image-block) {
  margin: 1.5em 0;
}

.post-content :deep(.image-block img) {
  max-width: 100%;
  width: 100%;
  max-width: 720px;
  border-radius: var(--radius-md);
  display: block;
  margin: 0 auto;
}

.post-content :deep(.video-block) {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 */
  margin: 1.5em 0;
}

.post-content :deep(.video-block iframe) {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: var(--radius-md);
}
</style>
