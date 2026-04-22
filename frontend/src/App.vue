<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BlogShell from './components/blog/BlogShell.vue'
import PlatformShell from './components/platform/PlatformShell.vue'
import { useAuth } from './router/auth.js'

const route = useRoute()
const { level, initAuth } = useAuth()

const isBlogRoute = computed(() => {
  if (route.path === '/') return true
  if (route.path === '/login' || route.path === '/register') return true
  if (route.path.startsWith('/post/')) return true
  if (route.path === '/404') return true
  return false
})

initAuth()
</script>

<template>
  <component
    :is="isBlogRoute ? BlogShell : PlatformShell"
    :user-level="level ?? 5"
  />
</template>
