<template>
  <div class="cloud-artifacts">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <a-space>
        <a-select v-model="filterJobId" placeholder="按训练任务过滤" style="width: 240px" allow-clear>
          <a-option v-for="job in jobs" :key="job.id" :value="job.id">
            {{ job.name }}
          </a-option>
        </a-select>
        <a-select v-model="filterType" placeholder="按类型过滤" style="width: 160px" allow-clear>
          <a-option value="checkpoint">模型 checkpoint</a-option>
          <a-option value="log">日志文件</a-option>
          <a-option value="config">配置文件</a-option>
          <a-option value="result">结果文件</a-option>
          <a-option value="other">其他</a-option>
        </a-select>
      </a-space>
    </div>

    <!-- 统计卡片 -->
    <div class="status-row">
      <div class="status-card">
        <div class="status-num">{{ stats.total ?? 0 }}</div>
        <div class="status-label">总制品数</div>
      </div>
      <div class="status-card s-checkpoint">
        <div class="status-num">{{ stats.byType?.checkpoint ?? 0 }}</div>
        <div class="status-label">模型 checkpoint</div>
      </div>
      <div class="status-card s-log">
        <div class="status-num">{{ stats.byType?.log ?? 0 }}</div>
        <div class="status-label">日志文件</div>
      </div>
      <div class="status-card s-storage">
        <div class="status-num">{{ formatBytes(stats.totalSize ?? 0) }}</div>
        <div class="status-label">总大小</div>
      </div>
    </div>

    <!-- 制品列表 -->
    <a-table
      :data="artifacts"
      :columns="artifactColumns"
      row-key="id"
      :bordered="false"
      :pagination="pagination"
      class="artifact-table"
      @page-change="onPageChange"
    >
      <template #name="{ record }">
        <div class="artifact-item">
          <component :is="typeIcon(record.artifact_type)" class="artifact-icon" :color="typeColor(record.artifact_type)" />
          <div class="artifact-info">
            <span class="artifact-name">{{ record.name }}</span>
            <span class="artifact-path">{{ record.path }}</span>
          </div>
          <a-tag size="small" :color="storageColor(record.storage_location)">{{ storageLabel(record.storage_location) }}</a-tag>
        </div>
      </template>
      <template #type="{ record }">
        <a-tag :color="typeColor(record.artifact_type)" size="small">{{ typeLabel(record.artifact_type) }}</a-tag>
      </template>
      <template #size="{ record }">
        <span class="size-text">{{ formatBytes(record.size_bytes) }}</span>
      </template>
      <template #job="{ record }">
        <span v-if="record.job" class="job-name">{{ record.job.name }}</span>
        <span v-else class="job-none">-</span>
      </template>
      <template #created_at="{ record }">
        <span class="time-text">{{ formatTime(record.created_at) }}</span>
      </template>
      <template #actions="{ record }">
        <a-space size="small">
          <a-button size="mini" @click="downloadArtifact(record)">
            <template #icon><icon-download /></template>
            下载
          </a-button>
          <a-popconfirm
            content="确定要删除这个制品吗？删除后不可恢复。"
            @ok="deleteArtifact(record)"
          >
            <a-button size="mini" status="danger">
              <template #icon><icon-delete /></template>
              删除
            </a-button>
          </a-popconfirm>
        </a-space>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useAuth } from '../../router/auth.js'
import {
  IconRefresh, IconFile, IconStorage,
  IconSettings, IconDownload, IconDelete,
} from '@arco-design/web-vue/es/icon'

const { authHeaders } = useAuth()
const refreshing = ref(false)
const artifacts = ref([])
const jobs = ref([])
const stats = ref({ total: 0, byType: {}, totalSize: 0 })
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const pagination = { showTotal: true, pageSize: 20 }

// 筛选条件
const filterJobId = ref(undefined)
const filterType = ref(undefined)

const TYPE_INFO = {
  checkpoint: { label: '模型 checkpoint', color: 'purple', icon: IconDatabase },
  log: { label: '日志文件', color: 'gray', icon: IconFileText },
  config: { label: '配置文件', color: 'blue', icon: IconSettings },
  result: { label: '结果文件', color: 'green', icon: IconFile },
  other: { label: '其他', color: 'orange', icon: IconFile },
}

const STORAGE_INFO = {
  minio: { label: '本地存储', color: 'blue' },
  aliyun: { label: '阿里云 OSS', color: 'orange' },
}

function typeIcon(type) { return TYPE_INFO[type]?.icon ?? IconFile }
function typeColor(type) { return TYPE_INFO[type]?.color ?? 'gray' }
function typeLabel(type) { return TYPE_INFO[type]?.label ?? type }

function storageColor(location) { return STORAGE_INFO[location]?.color ?? 'gray' }
function storageLabel(location) { return STORAGE_INFO[location]?.label ?? location }

const artifactColumns = [
  { title: '名称/路径', slotName: 'name', width: 400 },
  { title: '类型', slotName: 'type', width: 120 },
  { title: '大小', slotName: 'size', width: 100 },
  { title: '所属任务', slotName: 'job', width: 180 },
  { title: '创建时间', slotName: 'created_at', width: 180 },
  { title: '操作', slotName: 'actions', width: 160, fixed: 'right' },
]

// 工具函数
function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`
}

function formatTime(timeStr) {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 获取任务列表（用于筛选）
async function fetchJobs() {
  try {
    const res = await fetch('/api/cloud/jobs?page_size=100', { headers: authHeaders() })
    const data = await res.json()
    if (data.code === 'ok') {
      jobs.value = data.data.items || []
    }
  } catch (e) {
    console.error('获取任务列表失败', e)
  }
}

async function fetchArtifacts() {
  refreshing.value = true
  try {
    const params = new URLSearchParams({
      page: page.value,
      page_size: pageSize.value,
    })
    if (filterJobId.value) params.append('job_id', filterJobId.value)
    if (filterType.value) params.append('artifact_type', filterType.value)

    const res = await fetch(`/api/cloud/artifacts?${params}`, { headers: authHeaders() })
    const data = await res.json()
    if (data.code === 'ok') {
      artifacts.value = data.data.items || []
      total.value = data.data.total || 0
      pagination.total = total.value

      // 统计类型和大小
      const byType = {}
      let totalSize = 0
      artifacts.value.forEach(art => {
        byType[art.artifact_type] = (byType[art.artifact_type] || 0) + 1
        totalSize += art.size_bytes || 0
      })
      stats.value = {
        total: total.value,
        byType,
        totalSize,
      }
    }
  } catch {
    Message.error('加载制品列表失败')
  } finally {
    refreshing.value = false
  }
}

function onPageChange(p) {
  page.value = p
  fetchArtifacts()
}

// 筛选条件变化时重新加载
watch([filterJobId, filterType], () => {
  page.value = 1
  fetchArtifacts()
})

async function downloadArtifact(artifact) {
  try {
    const res = await fetch(`/api/cloud/artifacts/${artifact.id}/download`, { headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') {
      // 打开下载链接
      window.open(result.data.download_url, '_blank')
      Message.success('已开始下载')
    } else {
      Message.error(result.message || '获取下载链接失败')
    }
  } catch {
    Message.error('网络错误')
  }
}

async function deleteArtifact(artifact) {
  try {
    const res = await fetch(`/api/cloud/artifacts/${artifact.id}`, { method: 'DELETE', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') {
      Message.success('制品已删除')
      await fetchArtifacts()
    } else {
      Message.error(result.message)
    }
  } catch {
    Message.error('网络错误')
  }
}

onMounted(() => {
  fetchJobs()
  fetchArtifacts()
})
</script>

<style scoped>
.cloud-artifacts {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
}

/* 筛选栏 */
.filter-bar {
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

/* 统计卡片行 */
.status-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.status-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
  transition: all 0.2s ease;
}

.status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.status-card .status-num {
  font-size: 32px;
  font-weight: 700;
  color: #1d2129;
  line-height: 1;
  margin-bottom: 8px;
}

.status-card.s-checkpoint .status-num { color: #722ed1; }
.status-card.s-log .status-num { color: #4e5969; }
.status-card.s-storage .status-num { color: #00b42a; }

.status-label {
  font-size: 13px;
  color: #86909c;
}

/* 制品表格 */
.artifact-table {
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.7);
}

.artifact-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.artifact-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.artifact-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.artifact-name {
  font-weight: 500;
  color: #1d2129;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.artifact-path {
  font-size: 12px;
  color: #86909c;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'SF Mono', monospace;
}

.size-text {
  font-size: 13px;
  color: #4e5969;
}

.job-name {
  font-size: 13px;
  color: #165dff;
}

.job-none {
  font-size: 13px;
  color: #86909c;
}

.time-text {
  font-size: 13px;
  color: #4e5969;
}
</style>
