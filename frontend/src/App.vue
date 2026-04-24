<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import BlogShell from './components/blog/BlogShell.vue'
import PlatformShell from './components/layout/PlatformShell.vue'
import { useAuth } from './router/auth.js'
import { usePluginRegistry } from './stores/pluginRegistry.js'
import { sidebarPlugins, atomicComponents } from './data/plugin-registry-data.js'

const route = useRoute()
const { level, user, isAuthenticated, initAuth, loadUser } = useAuth()
const pluginRegistry = usePluginRegistry()

// 立即注册所有插件（在 setup 阶段）
sidebarPlugins.forEach(item => pluginRegistry.registerSidebar(item))
atomicComponents.forEach(comp => pluginRegistry.registerComponent(comp))

// 根据路由 meta 选择 shell
const currentShell = computed(() => {
  const shell = route.meta?.shell
  if (shell === 'blog') return BlogShell
  return PlatformShell
})

initAuth()
onMounted(async () => {
  await loadUser()
})
</script>

<template>
  <component :is="currentShell" />
</template>
