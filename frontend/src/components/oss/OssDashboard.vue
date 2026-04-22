<template>
  <div class="oss-dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">总文件数</div>
        <div class="stat-value">{{ stats.total_files }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">总存储</div>
        <div class="stat-value">{{ formatBytes(stats.total_size) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">磁盘占用</div>
        <div class="stat-value">{{ formatBytes(stats.disk_usage) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">配额用户数</div>
        <div class="stat-value">{{ stats.total_users }}</div>
      </div>
    </div>

    <!-- 存储类型分布 -->
    <a-card :bordered="false" title="按存储类型分布" style="margin-top: 16px" class="glass-card">
      <div v-if="Object.keys(stats.by_type || {}).length === 0" class="empty-hint">
        暂无数据
      </div>
      <div v-else class="type-grid">
        <div v-for="(v, k) in stats.by_type" :key="k" class="type-item">
          <span class="type-label">{{ k }}</span>
          <span class="type-value">{{ v.count }} 文件 / {{ formatBytes(v.size) }}</span>
        </div>
      </div>
    </a-card>

    <!-- Top 用户 -->
    <a-card :bordered="false" title="存储用量 Top 用户" style="margin-top: 16px" class="glass-card">
      <a-table
        :data="topUsers"
        :columns="topColumns"
        :pagination="false"
        :loading="loading"
      />
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useAuth } from '../../router/auth.js'

const { authHeaders } = useAuth()
const stats = ref({
  total_files: 0,
  total_size: 0,
  disk_usage: 0,
  total_users: 0,
  by_type: {},
})
const topUsers = ref([])
const loading = ref(false)

const topColumns = [
  { title: '用户 ID', dataIndex: 'user_id', width: 300, ellipsis: true },
  {
    title: '存储用量',
    dataIndex: 'total_bytes',
    width: 150,
    formatter: ({ cellValue }) => formatBytes(cellValue),
  },
  { title: '文件数', dataIndex: 'file_count', width: 100 },
]

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let v = bytes
  while (v >= 1024 && i < units.length - 1) { v /= 1024; i++ }
  return `${v.toFixed(1)} ${units[i]}`
}

async function loadData() {
  loading.value = true
  try {
    const [statsRes, topRes] = await Promise.all([
      fetch('/api/oss/admin/stats', { headers: authHeaders() }),
      fetch('/api/oss/admin/stats/top-users?limit=10', { headers: authHeaders() }),
    ])
    const statsData = await statsRes.json()
    const topData = await topRes.json()

    if (statsData.code === 'ok') stats.value = statsData.data
    if (topData.code === 'ok') topUsers.value = topData.data.users || []
  } catch {
    Message.error('加载统计失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadData() })
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.stat-card {
  background: rgba(255,255,255,0.75);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: var(--border-radius-large);
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.stat-label { font-size: 12px; color: var(--color-text-4); }
.stat-value { font-size: 28px; font-weight: 700; color: var(--color-text-1); margin-top: 4px; }

.glass-card {
  background: rgba(255,255,255,0.75) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(0,0,0,0.06) !important;
  border-radius: var(--border-radius-large) !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03) !important;
}
.empty-hint { text-align: center; padding: 24px; color: var(--color-text-4); }
.type-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.type-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 12px; background: var(--color-fill-1); border-radius: 8px;
}
.type-label { font-weight: 600; color: var(--color-text-2); }
.type-value { font-size: 12px; color: var(--color-text-3); }

@media (max-width: 900px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
