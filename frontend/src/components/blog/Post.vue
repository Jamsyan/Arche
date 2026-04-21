<template>
  <div class="post">
    <h2>{{ post.title }}</h2>
    <p>Post content placeholder.</p>
  </div>
</template>

<script setup>
defineProps({ slug: String })
const post = { title: 'Hello Veil', content: 'First post!' }
</script>
