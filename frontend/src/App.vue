<script setup>
import { ref, onMounted } from 'vue'
import BlogShell from './components/blog/BlogShell.vue'
import PlatformShell from './components/platform/PlatformShell.vue'
import { useAuth } from './router/auth.js'

const { isAuthenticated, role, loadUser } = useAuth()

onMounted(async () => {
  await loadUser()
})
</script>

<template>
  <BlogShell v-if="!isAuthenticated" />
  <PlatformShell v-else :role="role" />
</template>
