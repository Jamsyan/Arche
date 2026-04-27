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
  <div class="compact-list">
    <div
      v-for="post in posts"
      :key="post.id"
      class="compact-item card-glass"
      @click="emit('open', post)"
    >
      <div class="left">
        <h3>{{ post.title }}</h3>
        <div class="meta">
          <NTag v-for="tag in (post.tags || []).slice(0, 2)" :key="tag" size="small">{{
            tag
          }}</NTag>
        </div>
      </div>
      <div class="right">{{ post.created_at?.slice(0, 10) || '-' }}</div>
    </div>
  </div>
</template>

<style scoped>
.compact-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.compact-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
}
.left h3 {
  margin: 0 0 8px;
  font-size: 16px;
}
.meta {
  display: flex;
  gap: 8px;
}
.right {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
