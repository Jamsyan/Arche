<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { NCard, NGrid, NGi, NProgress, NDataTable, NTag, useMessage } from 'naive-ui'
import {
  getSystemSummaryApi,
  getProcessesApi,
  type SystemSummary,
  type ProcessInfo
} from '@/services/api'

const message = useMessage()

const summary = ref<SystemSummary>({ cpu_usage: 0, memory_usage: 0, disk_usage: 0 })
const processes = ref<ProcessInfo[]>([])
const loading = ref(false)

const processColumns = [
  { title: 'PID', key: 'pid', width: 80 },
  { title: '进程名', key: 'name', ellipsis: true },
  {
    title: 'CPU %',
    key: 'cpu_percent',
    width: 120,
    render: (row: ProcessInfo) =>
      h(
        NTag,
        { size: 'small', type: row.cpu_percent > 50 ? 'error' : 'default' },
        {
          default: () => `${row.cpu_percent.toFixed(1)}%`
        }
      )
  },
  {
    title: '内存 %',
    key: 'memory_percent',
    width: 120,
    render: (row: ProcessInfo) =>
      h(
        NTag,
        { size: 'small', type: row.memory_percent > 50 ? 'error' : 'default' },
        {
          default: () => `${row.memory_percent.toFixed(1)}%`
        }
      )
  }
]

const summaryCards = [
  { label: 'CPU 使用率', key: 'cpu_usage' as const, color: '#9a5a2f' },
  { label: '内存使用率', key: 'memory_usage' as const, color: '#b8743d' },
  { label: '磁盘使用率', key: 'disk_usage' as const, color: '#6f3f22' }
]

const fetchData = async () => {
  loading.value = true
  try {
    const [summaryRes, processesRes] = await Promise.all([
      getSystemSummaryApi({ silent: true, skipAuthLogout: true }),
      getProcessesApi({ limit: 30 }, { silent: true, skipAuthLogout: true })
    ])
    summary.value = summaryRes
    processes.value = processesRes || []
  } catch {
    message.error('获取系统监控数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="system-monitor-page">
    <NCard class="monitor-card">
      <template #header>
        <h2>系统监控</h2>
      </template>

      <NGrid :cols="3" :x-gap="12" :y-gap="12">
        <NGi v-for="card in summaryCards" :key="card.key">
          <div class="metric-card">
            <div class="metric-label">{{ card.label }}</div>
            <NProgress
              type="line"
              :percentage="Math.round(summary[card.key])"
              :color="card.color"
              :height="10"
              :border-radius="5"
              :fill-border-radius="5"
              indicator-placement="inside"
              class="metric-progress"
            />
            <div class="metric-value">{{ Math.round(summary[card.key]) }}%</div>
          </div>
        </NGi>
      </NGrid>

      <div v-if="processes.length > 0" class="processes-section">
        <h3 class="section-title">进程列表</h3>
        <NDataTable
          :columns="processColumns"
          :data="processes"
          :loading="loading"
          size="small"
          striped
          :bordered="false"
        />
      </div>
      <div v-else class="processes-empty">
        <p>暂无进程数据</p>
      </div>
    </NCard>
  </div>
</template>

<style scoped>
.system-monitor-page {
  max-width: 100%;
}

.monitor-card h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.metric-card {
  background: rgba(255, 248, 236, 0.52);
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.metric-value {
  font-size: 13px;
  color: var(--text-tertiary);
  text-align: right;
}

.section-title {
  margin: 20px 0 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.processes-empty {
  text-align: center;
  padding: 40px 0;
  color: var(--text-tertiary);
}
</style>

<style>
.n-data-table {
  --n-th-color: rgba(255, 248, 236, 0.52) !important;
  --n-td-color: rgba(255, 248, 236, 0.52) !important;
  --n-td-color-hover: rgba(154, 90, 47, 0.04) !important;
  --n-border-color: rgba(130, 95, 65, 0.1) !important;
}
</style>
