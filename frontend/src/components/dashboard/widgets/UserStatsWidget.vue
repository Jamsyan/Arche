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
import { auth } from '../../../api'

const activeCount = ref(0)
const disabledCount = ref(0)
const totalCount = ref(0)
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

async function load() {
  try {
    const [a, d] = await Promise.all([
      auth.listUsers({ page: 1, page_size: 1, status: 'active' }),
      auth.listUsers({ page: 1, page_size: 1, status: 'disabled' }),
    ])
    if (a) activeCount.value = a.total || 0
    if (d) disabledCount.value = d.total || 0
    totalCount.value = activeCount.value + disabledCount.value
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
