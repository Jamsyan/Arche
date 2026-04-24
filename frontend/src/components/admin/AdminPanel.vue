<template>
  <div class="admin-panel">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.push('/platform')" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <icon-lock class="header-icon" />
        <h1 class="page-title">管理员面板</h1>
      </div>
      <a-tag color="red" size="small">P0 权限</a-tag>
    </div>

    <!-- 系统监控 -->
    <div class="section-header">
      <icon-dashboard class="section-icon" />
      <span>系统监控</span>
      <a-button type="text" size="mini" @click="fetchSummary" :loading="loading">
        <template #icon><icon-refresh /></template>
      </a-button>
    </div>

    <div v-if="summary" class="monitor-grid">
      <div class="monitor-card">
        <div class="monitor-label">CPU 使用率</div>
        <div class="monitor-value">{{ summary.cpu_percent?.toFixed(1) ?? '—' }}%</div>
        <a-progress :percent="summary.cpu_percent ?? 0" size="small" :stroke-width="6" />
      </div>
      <div class="monitor-card">
        <div class="monitor-label">内存</div>
        <div class="monitor-value">{{ summary.memory_used_gb ?? '—' }} / {{ summary.memory_total_gb ?? '—' }} GB</div>
        <a-progress :percent="summary.memory_percent ?? 0" size="small" :stroke-width="6" />
      </div>
      <div class="monitor-card">
        <div class="monitor-label">磁盘</div>
        <div class="monitor-value">{{ summary.disk_used_gb ?? '—' }} / {{ summary.disk_total_gb ?? '—' }} GB</div>
        <a-progress :percent="summary.disk_percent ?? 0" size="small" :stroke-width="6" />
      </div>
      <div class="monitor-card">
        <div class="monitor-label">网络 I/O</div>
        <div class="monitor-value">↑ {{ formatBytes(summary.net_sent) }} / ↓ {{ formatBytes(summary.net_recv) }}</div>
        <div class="monitor-sub">自启动累计</div>
      </div>
      <div class="monitor-card">
        <div class="monitor-label">进程数</div>
        <div class="monitor-value">{{ summary.process_count ?? '—' }}</div>
        <div class="monitor-sub">Python {{ summary.python_version ?? '—' }}</div>
      </div>
      <div class="monitor-card">
        <div class="monitor-label">运行时长</div>
        <div class="monitor-value">{{ summary.uptime ?? '—' }}</div>
        <div class="monitor-sub">{{ summary.platform ?? '—' }}</div>
      </div>
    </div>

    <!-- 进程列表 -->
    <div class="section-header">
      <icon-desktop class="section-icon" />
      <span>资源占用 Top 进程</span>
    </div>

    <a-table
      :data="processes"
      :columns="processColumns"
      row-key="pid"
      :bordered="false"
      :pagination="{ pageSize: 10 }"
      class="process-table"
    />

    <!-- 快捷操作 -->
    <div class="section-header">
      <icon-apps class="section-icon" />
      <span>快捷操作</span>
    </div>

    <div class="quick-actions">
      <a-button type="outline" @click="$router.push('/admin/users')">
        <template #icon><icon-user /></template>
        用户管理
      </a-button>
      <a-button type="outline" @click="$router.push('/admin/oss')">
        <template #icon><icon-storage /></template>
        OSS 管理
      </a-button>
      <a-button type="outline" @click="$router.push('/admin/config')">
        <template #icon><icon-settings /></template>
        配置管理
      </a-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { system } from '../../api'
import {
  IconLock, IconArrowLeft, IconDashboard, IconDesktop,
  IconApps, IconUser, IconStorage, IconRefresh, IconSettings,
} from '@arco-design/web-vue/es/icon'

const loading = ref(false)
const summary = ref(null)
const processes = ref([])

const processColumns = [
  { title: 'PID', dataIndex: 'pid', width: 80 },
  { title: '名称', dataIndex: 'name', width: 160 },
  { title: 'CPU%', dataIndex: 'cpu_percent', width: 80,
    formatter: ({ cellValue }) => cellValue?.toFixed(1) ?? '—' },
  { title: '内存%', dataIndex: 'memory_percent', width: 90,
    formatter: ({ cellValue }) => cellValue?.toFixed(1) ?? '—' },
]

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let v = bytes
  while (v >= 1024 && i < units.length - 1) { v /= 1024; i++ }
  return `${v.toFixed(1)} ${units[i]}`
}

async function fetchSummary() {
  loading.value = true
  try {
    const [summaryData, processData] = await Promise.all([
      system.summary(),
      system.processes({ limit: 20, sort_by: 'cpu_percent' }),
    ])
    if (summaryData) {
      summary.value = summaryData
    }
    if (processData) {
      processes.value = processData.items || []
    }
  } catch (err) {
    Message.error(err.message || '加载系统监控失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => { fetchSummary() })
</script>

<style scoped>
.admin-panel { max-width: 1100px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.header-icon { width: 24px; height: 24px; color: #cf222e; }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }

.section-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600; color: var(--color-text-2);
  margin-bottom: 12px; margin-top: 28px;
}
.section-header:first-child { margin-top: 0; }
.section-icon { width: 16px; height: 16px; color: var(--color-text-4); }

.monitor-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.monitor-card {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.monitor-label { font-size: 12px; color: var(--color-text-4); margin-bottom: 4px; }
.monitor-value { font-size: 22px; font-weight: 700; color: var(--color-text-1); margin-bottom: 8px; }
.monitor-sub { font-size: 12px; color: var(--color-text-4); margin-top: 4px; }

.process-table { border-radius: var(--border-radius-large); overflow: hidden; }

.quick-actions { display: flex; flex-wrap: wrap; gap: 12px; }
.quick-actions .arco-btn { min-width: 140px; justify-content: center; }
</style>
