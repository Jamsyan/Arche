<template>
  <div class="widget widget-full-width">
    <div class="widget-label">存储 Top 用户</div>
    <a-table :data="users" :columns="columns" row-key="user_id"
      :pagination="false" size="small" :bordered="false" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuth } from '../../../router/auth.js'

const { authHeaders } = useAuth()
const users = ref([])
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0, v = bytes
  while (v >= 1024 && i < units.length - 1) { v /= 1024; i++ }
  return `${v.toFixed(1)} ${units[i]}`
}

const columns = [
  { title: '用户', dataIndex: 'user_id', width: 280 },
  { title: '文件数', dataIndex: 'file_count', width: 80 },
  { title: '用量', width: 120, formatter: ({ record }) => formatBytes(record.total_size) },
]

async function fetch() {
  try {
    const res = await fetch('/api/oss/admin/stats/top-users?limit=10', { headers: authHeaders() })
    const d = await res.json()
    if (d.code === 'ok') users.value = d.data?.users || []
  } catch {}
}

onMounted(() => { fetch(); timer = setInterval(fetch, 30000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.widget { display: flex; flex-direction: column; gap: 8px; }
.widget-label { font-size: 11px; color: var(--color-text-4); text-transform: uppercase; }
</style>
