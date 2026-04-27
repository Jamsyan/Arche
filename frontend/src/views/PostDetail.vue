<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { NTag } from 'naive-ui'
import { getPostBySlugApi, type BlogPost } from '@/services/api'

const route = useRoute()
const post = ref<BlogPost | null>(null)

onMounted(async () => {
  post.value = await getPostBySlugApi(String(route.params.slug || ''))
})
</script>

<template>
  <article v-if="post" class="post-detail card-glass">
    <h1>{{ post.title }}</h1>
    <div class="meta">
      <span>{{ post.author_username || '匿名' }}</span>
      <span>{{ post.created_at?.slice(0, 10) || '-' }}</span>
    </div>
    <div class="tags">
      <NTag v-for="tag in post.tags || []" :key="tag">{{ tag }}</NTag>
    </div>
    <pre class="content">{{ post.content }}</pre>
  </article>
</template>

<style scoped>
.post-detail {
  padding: 20px;
}
h1 {
  margin: 0 0 10px;
}
.meta {
  display: flex;
  gap: 12px;
  color: var(--text-tertiary);
  margin-bottom: 12px;
}
.tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.content {
  white-space: pre-wrap;
  font-family: inherit;
  color: var(--text-primary);
  line-height: 1.7;
}
</style>
