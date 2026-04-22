<template>
  <div class="widget">
    <div class="widget-label">训练任务</div>
    <div class="stat-row">总计: <b>{{ stats.total || 0 }}</b></div>
    <div class="stat-row" v-if="stats.by_status">
      <span v-for="(count, status) in stats.by_status" :key="status" class="status-tag">{{ status }}: {{ count }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuth } from '../../../router/auth.js'

const { authHeaders } = useAuth()
const stats = ref({})
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

async function fetch() {
  try {
    const res = await fetch('/api/cloud/jobs?page=1&page_size=1', { headers: authHeaders() })
    const d = await res.json()
    if (d.code === 'ok') {
      stats.value = { total: d.data?.total || 0 }
    }
  } catch {}
}

onMounted(() => { fetch(); timer = setInterval(fetch, 30000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.widget { display: flex; flex-direction: column; gap: 6px; }
.widget-label { font-size: 11px; color: var(--color-text-4); text-transform: uppercase; }
.stat-row { font-size: 12px; color: var(--color-text-3); }
.stat-row b { color: var(--color-text-1); font-weight: 600; }
.status-tag { display: inline-block; background: var(--color-fill-1); padding: 1px 6px; border-radius: 4px; margin-right: 4px; font-size: 11px; }
</style>
