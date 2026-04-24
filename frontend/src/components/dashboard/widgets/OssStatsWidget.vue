<template>
  <div class="widget">
    <div class="widget-label">存储统计</div>
    <div class="stat-row">文件: <b>{{ stats.total_files || 0 }}</b></div>
    <div class="stat-row">总量: <b>{{ formatBytes(stats.total_size) }}</b></div>
    <div class="stat-row">用户: <b>{{ stats.total_users || 0 }}</b></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { oss } from '../../../api'

const stats = ref({})
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0, v = bytes
  while (v >= 1024 && i < units.length - 1) { v /= 1024; i++ }
  return `${v.toFixed(1)} ${units[i]}`
}

async function load() {
  try {
    const d = await oss.adminStats()
    if (d) stats.value = d || {}
  } catch {}
}

onMounted(() => { load(); timer = setInterval(load, 30000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.widget { display: flex; flex-direction: column; gap: 6px; }
.widget-label { font-size: 11px; color: var(--color-text-4); text-transform: uppercase; }
.stat-row { font-size: 12px; color: var(--color-text-3); }
.stat-row b { color: var(--color-text-1); font-weight: 600; }
</style>
