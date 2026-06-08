<script setup lang="ts">
/**
 * HeroCarousel — 博客首页 3D 卡片轮播。
 *
 * 基于 ArCarousel3D 通用组件，注入博客文章的封面/标题/作者渲染。
 */
import ArCarousel3D from '@/components/ui/ArCarousel3D.vue'
import { getCoverGradient } from '@/utils/cover'
import type { BlogPost } from '@/services/api'

const props = withDefaults(
  defineProps<{
    posts: BlogPost[]
    interval?: number
  }>(),
  { interval: 12000 }
)
const emit = defineEmits<{
  open: [post: BlogPost]
}>()

function coverStyle(post: BlogPost) {
  if (post.cover_url) {
    return {
      backgroundImage: `url(${post.cover_url})`,
      backgroundSize: 'cover' as const,
      backgroundPosition: 'center' as const
    }
  }
  return { background: getCoverGradient(post) }
}

function handleSelect(post: BlogPost) {
  if (post.id.startsWith('demo-')) return
  emit('open', post)
}
</script>

<template>
  <ArCarousel3D :items="posts" :interval="interval" @select="handleSelect">
    <template #card="{ item: post, showOverlay }">
      <div class="card-cover" :style="coverStyle(post)">
        <div class="card-shine" />
      </div>
      <div v-if="showOverlay" class="card-overlay">
        <div class="overlay-content">
          <span class="overlay-author">{{ post.author_username || '匿名' }}</span>
          <h3 class="overlay-title">{{ post.title }}</h3>
        </div>
      </div>
    </template>
  </ArCarousel3D>
</template>

<style scoped>
.card-cover {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  border-radius: inherit;
}

.card-shine {
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

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 50%, rgba(26, 24, 23, 0.75) 100%);
  display: flex;
  align-items: flex-end;
  padding: var(--spacing-lg);
  pointer-events: none;
}

.overlay-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.overlay-author {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
  font-weight: var(--font-weight-medium);
}

.overlay-title {
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
</style>
