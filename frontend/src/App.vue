<script setup>
import { onMounted } from 'vue'
import BlogShell from './components/blog/BlogShell.vue'
import PlatformShell from './components/platform/PlatformShell.vue'
import { useAuth } from './router/auth.js'

const { level, initAuth, logout } = useAuth()

onMounted(() => {
  // 从 localStorage 恢复认证状态
  initAuth()
})

function handleLogout() {
  logout()
}
</script>

<template>
  <component
    :is="level !== null ? PlatformShell : BlogShell"
    v-if="level !== null"
    :user-level="level"
    @logout="handleLogout"
  />
  <BlogShell v-else />
</template>
