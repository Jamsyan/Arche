<script setup lang="ts">
import { NTag } from 'naive-ui'
import type { BlogPost } from '@/services/api'

defineProps<{
  posts: BlogPost[]
}>()

const emit = defineEmits<{
  open: [post: BlogPost]
}>()
</script>

<template>
  <div class="detail-list">
    <article
      v-for="post in posts"
      :key="post.id"
      class="detail-item card-glass"
      @click="emit('open', post)"
    >
      <h3>{{ post.title }}</h3>
      <p class="excerpt">{{ post.content?.slice(0, 180) || '暂无摘要' }}</p>
      <div class="footer">
        <div class="tags">
          <NTag v-for="tag in (post.tags || []).slice(0, 3)" :key="tag" size="small">{{
            tag
          }}</NTag>
        </div>
        <div class="meta">
          <span>{{ post.author_username || '匿名' }}</span>
          <span>👍 {{ post.likes || 0 }}</span>
          <span>{{ post.created_at?.slice(0, 10) || '-' }}</span>
        </div>
      </div>
    </article>
  </div>
</template>

<style scoped>
.detail-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.detail-item {
  padding: 18px;
  cursor: pointer;
}
h3 {
  margin: 0 0 10px;
}
.excerpt {
  margin: 0 0 12px;
  color: var(--text-secondary);
  line-height: 1.6;
}
.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.tags,
.meta {
  display: flex;
  gap: 8px;
  align-items: center;
}
.meta {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
