<script setup lang="ts">
import PostCardBase from './PostCardBase.vue'
import type { BlogPost } from '@/services/api'

defineProps<{
  post: BlogPost
  showOverlay?: boolean
}>()

defineEmits<{
  open: [post: BlogPost]
}>()
</script>

<template>
  <PostCardBase :post="post" class="post-card-hero" @open="$emit('open', $event)">
    <template #cover>
      <div class="hero-cover" :style="{ backgroundImage: `url(${post.cover_url})` }">
        <div class="hero-shine" />
        <div v-if="showOverlay" class="hero-overlay">
          <div class="hero-overlay-body">
            <h3 class="hero-title">{{ post.title }}</h3>
            <span class="hero-author">@{{ post.author_username || '匿名' }}</span>
          </div>
        </div>
      </div>
    </template>
    <template #content />
    <template #actions />
  </PostCardBase>
</template>

<style scoped>
.post-card-hero {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: inherit;
}

.hero-cover {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  border-radius: inherit;
}

.hero-shine {
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

.hero-overlay {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 32px var(--spacing-lg) var(--spacing-lg);
  background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.55) 100%);
  pointer-events: none;
}

.hero-overlay-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hero-title {
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

.hero-author {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: var(--font-weight-medium);
}
</style>
