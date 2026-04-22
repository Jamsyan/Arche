<template>
  <div class="widget">
    <div class="widget-label">用户统计</div>
    <div class="stat-row">活跃: <b>{{ activeCount }}</b></div>
    <div class="stat-row">禁用: <b>{{ disabledCount }}</b></div>
    <div class="stat-row">总计: <b>{{ totalCount }}</b></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuth } from '../../../router/auth.js'

const { authHeaders } = useAuth()
const activeCount = ref(0)
const disabledCount = ref(0)
const totalCount = ref(0)
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

async function fetch() {
  try {
    const [activeRes, disabledRes] = await Promise.all([
      fetch('/api/auth/users?page=1&page_size=1&status=active', { headers: authHeaders() }),
      fetch('/api/auth/users?page=1&page_size=1&status=disabled', { headers: authHeaders() }),
    ])
    const a = await activeRes.json()
    const d = await disabledRes.json()
    if (a.code === 'ok') activeCount.value = a.data?.total || 0
    if (d.code === 'ok') disabledCount.value = d.data?.total || 0
    totalCount.value = activeCount.value + disabledCount.value
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
</style>
