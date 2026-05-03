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
  <div class="card-grid">
    <article
      v-for="post in posts"
      :key="post.id"
      class="card-item card-glass"
      @click="emit('open', post)"
    >
      <h3>{{ post.title }}</h3>
      <p>{{ post.content?.slice(0, 120) || '暂无摘要' }}</p>
      <div class="tags">
        <NTag v-for="tag in (post.tags || []).slice(0, 3)" :key="tag" size="small">{{ tag }}</NTag>
      </div>
      <div class="meta">{{ post.created_at?.slice(0, 10) || '-' }}</div>
    </article>
  </div>
</template>

<style scoped>
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.card-item {
  padding: 16px;
  cursor: pointer;
}
h3 {
  margin: 0 0 10px;
  font-size: 18px;
}
p {
  margin: 0 0 12px;
  color: var(--text-secondary);
  line-height: 1.6;
  min-height: 66px;
}
.tags {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.meta {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
