<template>
  <div class="widget">
    <div class="widget-label">爬虫状态</div>
    <div class="status-badge" :class="statusClass">{{ statusText }}</div>
    <div class="stat-row" v-if="data.active_tasks">活跃任务: <b>{{ data.active_tasks }}</b></div>
    <div class="stat-row" v-if="data.queue_size !== undefined">队列: <b>{{ data.queue_size }}</b></div>
    <div class="stat-row" v-if="data.uptime">运行: {{ data.uptime }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuth } from '../../../router/auth.js'

const { authHeaders } = useAuth()
const data = ref({})
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

const statusText = computed(() => {
  if (!data.value.running) return '已停止'
  return '运行中'
})
const statusClass = computed(() => data.value.running ? 'status-running' : 'status-stopped')

async function fetch() {
  try {
    const res = await fetch('/api/crawler/status', { headers: authHeaders() })
    const d = await res.json()
    if (d.code === 'ok') data.value = d.data || {}
  } catch {}
}

onMounted(() => { fetch(); timer = setInterval(fetch, 15000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.widget { display: flex; flex-direction: column; gap: 6px; }
.widget-label { font-size: 11px; color: var(--color-text-4); text-transform: uppercase; }
.status-badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 13px; font-weight: 600; width: fit-content; }
.status-running { background: rgba(26,127,55,0.12); color: #1a7f37; }
.status-stopped { background: rgba(207,34,46,0.12); color: #cf222e; }
.stat-row { font-size: 12px; color: var(--color-text-3); }
.stat-row b { color: var(--color-text-1); font-weight: 600; }
</style>
