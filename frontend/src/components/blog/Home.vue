<template>
  <div class="home">
    <h2>Latest Posts</h2>
    <p v-if="loading">Loading...</p>
    <ul v-else>
      <li v-for="post in posts" :key="post.id">
        <router-link :to="`/post/${post.slug}`">{{ post.title }}</router-link>
        <p>{{ post.excerpt }}</p>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const posts = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await fetch('/api/blog/posts')
    posts.value = await res.json()
  } finally {
    loading.value = false
  }
})
</script>
