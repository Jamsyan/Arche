<script setup lang="ts">
import PostCardBase from './PostCardBase.vue'
import type { BlogPost } from '@/services/api'

defineProps<{
  post: BlogPost
  metaProgress?: number
  metaDuration?: string
}>()

defineEmits<{
  open: [post: BlogPost]
}>()
</script>

<template>
  <PostCardBase :post="post" class="post-card-cover" @open="$emit('open', $event)">
    <template #cover>
      <div
        class="cover-card"
        :style="{
          backgroundImage: post.cover_url ? `url(${post.cover_url})` : undefined
        }"
      >
        <!-- 顶部：左→右渐变，标题 + @作者 -->
        <div class="cover-top-overlay">
          <span class="cover-title">{{ post.title }}</span>
          <span class="cover-author">@{{ post.author_username || '匿名' }}</span>
        </div>
        <!-- 底部：进度 + 时长 -->
        <div class="cover-bottom-overlay">
          <span v-if="metaProgress != null" class="cover-progress"> 已读 {{ metaProgress }}% </span>
          <span v-if="metaDuration" class="cover-duration">{{ metaDuration }}</span>
        </div>
      </div>
    </template>

    <template #content />
    <template #actions />
  </PostCardBase>
</template>

<style scoped>
.post-card-cover {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.cover-card {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
  border-radius: inherit;
}

/* ── 顶部 overlay：左→右渐隐 ── */
.cover-top-overlay {
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

.cover-title {
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

.cover-author {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.88);
  white-space: nowrap;
  flex-shrink: 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* ── 底部 overlay：下→上渐隐 ── */
.cover-bottom-overlay {
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

.cover-progress {
  font-size: 11px;
  font-weight: var(--font-weight-medium);
  color: #fff;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
  font-variant-numeric: tabular-nums;
}

.cover-duration {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* 深色模式 */
:global(.dark) .cover-top-overlay {
  background: linear-gradient(
    to right,
    rgba(0, 0, 0, 0.55) 0%,
    rgba(0, 0, 0, 0.2) 55%,
    transparent 100%
  );
}

:global(.dark) .cover-bottom-overlay {
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6) 0%, transparent 100%);
}
</style>
