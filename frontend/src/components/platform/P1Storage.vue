<template>
  <div class="storage-page">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.push('/platform')" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <icon-storage class="header-icon" />
        <h1 class="page-title">存储管理</h1>
      </div>
      <a-space>
        <a-button type="text" size="small" @click="refreshStorage" :loading="refreshing">
          <template #icon><icon-refresh /></template>
        </a-button>
        <a-button type="primary" size="small" @click="$router.push('/upload')">
          <template #icon><icon-upload /></template>
          上传文件
        </a-button>
      </a-space>
    </div>

    <!-- 存储概览 -->
    <div class="storage-overview">
      <div class="overview-card local">
        <div class="overview-header">
          <icon-storage class="overview-icon" />
          <span class="overview-title">本地存储</span>
          <a-tag color="green" size="small">已连接</a-tag>
        </div>
        <div class="overview-body">
          <a-progress :percent="storagePercent" size="medium" />
          <div class="overview-stats">
            <span>已用 <b>{{ quota.used_gb ?? 0 }} GB</b></span>
            <span>总量 <b>{{ quota.quota_gb ?? 10 }} GB</b></span>
            <span>文件 <b>{{ quota.file_count ?? 0 }}</b></span>
          </div>
        </div>
      </div>
      <div class="overview-card oss" :class="{ 'oss-disconnected': !globalStats }">
        <div class="overview-header">
          <icon-cloud class="overview-icon" />
          <span class="overview-title">全局存储统计</span>
          <a-tag v-if="globalStats" color="blue" size="small">{{ globalStats.total_files }} 文件</a-tag>
          <a-tag v-else color="gray" size="small">未加载</a-tag>
        </div>
        <div class="overview-body">
          <div v-if="!globalStats" class="oss-disconnect-hint">
            <p>存储统计加载中...</p>
          </div>
          <div v-else>
            <div class="overview-stats">
              <span>总大小 <b>{{ formatBytes(globalStats.total_size) }}</b></span>
              <span>磁盘占用 <b>{{ formatBytes(globalStats.disk_usage) }}</b></span>
            </div>
            <div v-if="globalStats.by_type && Object.keys(globalStats.by_type).length > 0" class="by-type">
              <span v-for="(v, k) in globalStats.by_type" :key="k" class="type-tag">
                {{ k }}: {{ v.count }} 文件
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 我的文件 -->
    <div class="section-header">
      <icon-file class="section-icon" />
      <span>我的文件</span>
    </div>

    <a-table
      :data="myFiles"
      :columns="fileColumns"
      row-key="id"
      :bordered="false"
      :pagination="{ pageSize: 15, showTotal: true }"
      :loading="filesLoading"
      class="file-table"
    >
      <template #name="{ record }">
        <div class="file-name-cell">
          <icon-file class="file-icon" />
          <span class="file-name">{{ record.path?.split('/').pop() || record.path }}</span>
        </div>
      </template>
      <template #size="{ record }">
        {{ formatBytes(record.size) }}
      </template>
      <template #storage_type="{ record }">
        <a-tag :color="record.storage_type === 'local' ? 'green' : 'blue'" size="small">
          {{ record.storage_type }}
        </a-tag>
      </template>
      <template #created_at="{ record }">
        {{ record.created_at ? new Date(record.created_at).toLocaleString('zh-CN') : '-' }}
      </template>
      <template #actions="{ record }">
        <a-space size="small">
          <a-button type="text" size="mini" @click="downloadFile(record)">下载</a-button>
          <a-button type="text" size="mini" status="danger" @click="deleteFile(record)">删除</a-button>
        </a-space>
      </template>
    </a-table>

    <a-empty v-if="!filesLoading && myFiles.length === 0" description="暂无文件，去上传吧" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import {
  IconStorage, IconCloud, IconUpload, IconArrowLeft,
  IconRefresh, IconFile,
} from '@arco-design/web-vue/es/icon'
import { oss } from '../../api'

const refreshing = ref(false)
const filesLoading = ref(false)
const myFiles = ref([])
const quota = ref({})
const globalStats = ref(null)

const storagePercent = computed(() => {
  return quota.value.usage_percent ?? 0
})

const fileColumns = [
  { title: '名称', slotName: 'name', width: 300 },
  { title: '大小', slotName: 'size', width: 100 },
  { title: '类型', slotName: 'storage_type', width: 80 },
  { title: 'MIME', dataIndex: 'mime_type', width: 120, ellipsis: true },
  { title: '上传时间', slotName: 'created_at', width: 160 },
  { title: '操作', slotName: 'actions', width: 120, fixed: 'right' },
]

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let v = bytes
  while (v >= 1024 && i < units.length - 1) { v /= 1024; i++ }
  return `${v.toFixed(1)} ${units[i]}`
}

async function refreshStorage() {
  refreshing.value = true
  try {
    const [quotaData, statsData, filesData] = await Promise.all([
      oss.quota(),
      oss.storageStats({ user_scope: true }),
      oss.myFiles({ limit: 200, offset: 0 }),
    ])

    if (quotaData) quota.value = quotaData
    if (statsData) globalStats.value = statsData
    if (filesData) myFiles.value = filesData.files ?? []
  } catch (err) {
    Message.error(err.message || '加载存储信息失败')
  } finally {
    refreshing.value = false
  }
}

async function downloadFile(file) {
  window.open(`/api/oss/files/${file.id}`, '_blank')
}

async function deleteFile(file) {
  Modal.confirm({
    title: '确认删除',
    content: `确定删除文件 "${file.path?.split('/').pop()}" 吗？`,
    onOk: async () => {
      try {
        await oss.deleteFile(file.id)
        Message.success('删除成功')
        await refreshStorage()
      } catch (err) {
        Message.error(err.message || '删除失败')
      }
    },
  })
}

onMounted(() => { refreshStorage() })
</script>

<style scoped>
.storage-page { max-width: 1100px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.header-icon { width: 24px; height: 24px; color: var(--color-primary); }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }

.storage-overview { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.overview-card {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.overview-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.overview-icon { width: 20px; height: 20px; color: var(--color-primary); }
.overview-title { font-size: 14px; font-weight: 600; flex: 1; }
.overview-stats { display: flex; justify-content: space-between; font-size: 12px; color: var(--color-text-3); margin-top: 8px; }
.overview-stats b { color: var(--color-text-1); }
.by-type { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.type-tag { font-size: 11px; color: var(--color-text-4); background: var(--color-fill-2); padding: 2px 8px; border-radius: 6px; }

.oss-disconnected { opacity: 0.7; }
.oss-disconnect-hint { text-align: center; padding: 24px 0; color: var(--color-text-4); }
.oss-disconnect-hint p { margin-bottom: 12px; }

.section-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600; color: var(--color-text-2);
  margin-bottom: 12px;
}
.section-icon { width: 16px; height: 16px; color: var(--color-text-4); }

.file-table { border-radius: var(--border-radius-large); overflow: hidden; }
.file-name-cell { display: flex; align-items: center; gap: 8px; }
.file-icon { width: 16px; height: 16px; color: var(--color-text-3); flex-shrink: 0; }
.file-name { font-weight: 500; }
</style>
