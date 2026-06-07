<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import type { BlogPost, Paragraph } from '@/services/api'

const props = defineProps<{
  post: BlogPost
}>()

const emit = defineEmits<{
  paragraphClick: [paragraph: Paragraph]
}>()

// 有段落列表则用段落，否则 fallback 成整段
const paragraphs = computed(() => {
  if (props.post.paragraphs && props.post.paragraphs.length > 0) {
    return props.post.paragraphs
  }
  // fallback：整篇内容作为一段
  return props.post.content ? [{ index: 1, content: props.post.content }] : []
})

function renderContent(text: string): string {
  // 1. 使用 marked 将 Markdown 渲染为 HTML
  let html = marked.parse(text, { gfm: true }) as string

  // 2. 处理视频嵌入 — 匹配 marked 输出的 <a> 标签
  html = html.replace(
    /<a\s+[^>]*href="((?:https?:\/\/)?(?:www\.)?(?:bilibili\.com|b23\.tv|youtube\.com)[^"]+)"[^>]*>.+?<\/a>/g,
    (_match, url) => {
      let embedUrl = ''
      let hostname = ''
      try {
        const parsed = new URL(
          url.startsWith('http://') || url.startsWith('https://') ? url : `https://${url}`
        )
        hostname = parsed.hostname.toLowerCase()
      } catch {
        return _match
      }

      const isBilibiliHost =
        hostname === 'bilibili.com' ||
        hostname.endsWith('.bilibili.com') ||
        hostname === 'b23.tv' ||
        hostname.endsWith('.b23.tv')
      const isYoutubeHost = hostname === 'youtube.com' || hostname.endsWith('.youtube.com')

      if (isBilibiliHost) {
        const bvMatch = url.match(/BV[\w]+/)
        if (bvMatch) {
          embedUrl = `https://player.bilibili.com/player.html?isOutside=true&bvid=${bvMatch[0]}&autoplay=0&danmaku=0&high_quality=1&no_related=1`
        } else {
          const avMatch = url.match(/video\/(?:av|AV)?(\d+)/)
          if (avMatch) {
            embedUrl = `https://player.bilibili.com/player.html?isOutside=true&aid=${avMatch[1]}&autoplay=0&danmaku=0&high_quality=1&no_related=1`
          }
        }
      } else if (isYoutubeHost) {
        const vMatch = url.match(/(?:watch\?v=|embed\/|shorts\/)([\w-]+)/)
        if (vMatch) {
          embedUrl = `https://www.youtube.com/embed/${vMatch[1]}`
        }
      }
      if (embedUrl) {
        return `<div class="media-block video-block"><iframe src="${embedUrl}" frameborder="0" allowfullscreen></iframe></div>`
      }
      // 不是视频链接，保留原样
      return _match
    }
  )

  // 3. 处理图片 [#N]
  html = html.replace(/\[#(\d+)\]/g, (_match, num) => {
    return `<div class="media-block image-block"><img src="https://picsum.photos/seed/${props.post.id}_${num}/800/450" alt="图片 #${num}" loading="lazy" /></div>`
  })

  return html
}

function handleParagraphClick(para: Paragraph) {
  emit('paragraphClick', para)
}
</script>

<template>
  <article class="post-detail">
    <div
      v-for="para in paragraphs"
      :key="para.index"
      class="content-paragraph"
      @click="handleParagraphClick(para)"
    >
      <span class="paragraph-index">{{ para.index }}</span>
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div class="paragraph-text" v-html="renderContent(para.content)" />
    </div>
  </article>
</template>

<style scoped>
.post-detail {
  font-family: var(--font-serif);
  font-size: 16.5px;
  line-height: 2;
  color: var(--text-primary);
  word-break: break-word;
}

/* ── 段落 ── */
.content-paragraph {
  position: relative;
  padding: 4px 0 4px 32px;
  margin: 0 0 0.6em;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
}

.content-paragraph:hover {
  background: var(--surface-hover-color);
}

/* 段落编号 */
.paragraph-index {
  position: absolute;
  left: 0;
  top: 6px;
  width: 26px;
  text-align: right;
  padding-right: 6px;
  font-family: var(--font-mono, var(--font-sans));
  font-size: 11px;
  color: var(--text-quaternary);
  user-select: none;
  opacity: 0.45;
  transition: opacity var(--transition-fast);
}

.content-paragraph:hover .paragraph-index {
  opacity: 0.85;
}

/* 段落文本 */
.paragraph-text {
  display: block;
}

.paragraph-text :deep(.media-block) {
  margin: 0;
  text-align: center;
}

.paragraph-text :deep(.image-block) {
  margin: 1.5em 0;
}

.paragraph-text :deep(.image-block img) {
  max-width: 100%;
  width: 100%;
  max-width: 720px;
  border-radius: var(--radius-md);
  display: block;
  margin: 0 auto;
}

.paragraph-text :deep(.video-block) {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  margin: 1.5em 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: #000;
}

.paragraph-text :deep(.video-block iframe) {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}

/* ── Markdown 元素样式 ── */
.paragraph-text :deep(h1) {
  font-size: 1.75em;
  font-weight: 700;
  margin: 1.2em 0 0.6em;
  line-height: 1.3;
  color: var(--text-primary);
}

.paragraph-text :deep(h2) {
  font-size: 1.45em;
  font-weight: 700;
  margin: 1.1em 0 0.5em;
  line-height: 1.35;
  color: var(--text-primary);
}

.paragraph-text :deep(h3) {
  font-size: 1.2em;
  font-weight: 600;
  margin: 1em 0 0.45em;
  line-height: 1.4;
  color: var(--text-primary);
}

.paragraph-text :deep(h4) {
  font-size: 1.05em;
  font-weight: 600;
  margin: 0.9em 0 0.4em;
  line-height: 1.45;
  color: var(--text-primary);
}

.paragraph-text :deep(p) {
  margin: 0 0 1em;
}

.paragraph-text :deep(p:last-child) {
  margin-bottom: 0;
}

.paragraph-text :deep(code) {
  font-family: var(--font-mono, 'Fira Code', 'Consolas', monospace);
  font-size: 0.9em;
  padding: 0.2em 0.4em;
  background: var(--surface-hover-color, rgba(128, 128, 128, 0.1));
  border-radius: 3px;
  word-break: break-word;
}

.paragraph-text :deep(pre) {
  background: var(--surface-hover-color, rgba(128, 128, 128, 0.08));
  border-radius: var(--radius-md);
  padding: 1em;
  margin: 0.8em 0;
  overflow-x: auto;
  line-height: 1.6;
}

.paragraph-text :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 0.85em;
  color: inherit;
}

.paragraph-text :deep(ul) {
  margin: 0.5em 0;
  padding-left: 1.5em;
  list-style: disc;
}

.paragraph-text :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
  list-style: decimal;
}

.paragraph-text :deep(li) {
  margin: 0.25em 0;
}

.paragraph-text :deep(blockquote) {
  margin: 0.8em 0;
  padding: 0.5em 1em;
  border-left: 4px solid var(--primary-color, #667eea);
  background: var(--surface-hover-color, rgba(128, 128, 128, 0.05));
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--text-secondary);
}

.paragraph-text :deep(blockquote p) {
  margin: 0.3em 0;
}

.paragraph-text :deep(a) {
  color: var(--primary-color, #667eea);
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: color var(--transition-fast);
}

.paragraph-text :deep(a:hover) {
  color: var(--primary-hover-color, #5a6fd6);
}

.paragraph-text :deep(hr) {
  border: none;
  border-top: 1px solid var(--border-color, rgba(128, 128, 128, 0.2));
  margin: 1.5em 0;
}
</style>
