<script setup lang="ts">
import ArCarousel3D from '@/components/ui/ArCarousel3D.vue'
import PostCardHero from './PostCardHero.vue'
import type { BlogPost } from '@/services/api'

withDefaults(
  defineProps<{
    posts: BlogPost[]
    interval?: number
  }>(),
  { interval: 12000 }
)

const emit = defineEmits<{
  open: [post: BlogPost]
}>()

function handleSelect(post: BlogPost) {
  if (post.id.startsWith('demo-')) return
  emit('open', post)
}
</script>

<template>
  <ArCarousel3D :items="posts" :interval="interval" @select="handleSelect">
    <template #card="{ item: post, showOverlay }">
      <PostCardHero :post="post" :show-overlay="showOverlay" @open="emit('open', post)" />
    </template>
  </ArCarousel3D>
</template>
