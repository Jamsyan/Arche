<template>
  <div class="widget widget-full-width">
    <div class="widget-label">Top 进程 (CPU)</div>
    <a-table :data="processes" :columns="columns" row-key="pid"
      :pagination="false" size="small" :bordered="false" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { system } from '../../../api'

const processes = ref([])
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

const columns = [
  { title: 'PID', dataIndex: 'pid', width: 70 },
  { title: '名称', dataIndex: 'name', width: 140 },
  { title: 'CPU%', dataIndex: 'cpu_percent', width: 70, formatter: ({ cellValue }) => cellValue?.toFixed(1) },
  { title: '内存%', dataIndex: 'memory_percent', width: 70, formatter: ({ cellValue }) => cellValue?.toFixed(1) },
]

async function load() {
  try {
    const data = await system.processes({ limit: 10, sort_by: 'cpu_percent' })
    if (data) processes.value = data.items || data || []
  } catch {}
}

onMounted(() => { load(); timer = setInterval(load, 15000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.widget { display: flex; flex-direction: column; gap: 8px; }
.widget-label { font-size: 11px; color: var(--color-text-4); text-transform: uppercase; }
</style>
