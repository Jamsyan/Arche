<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { NButton, NGrid, NGi, useMessage } from 'naive-ui'
import ProTable from '@/components/ProTable.vue'
import {
  getOssAdminStatsApi,
  getOssAdminFilesApi,
  getOssAdminTopUsersApi,
  deleteOssAdminFileApi,
  type OSSAdminStats,
  type OSSFile,
  type OSSTopUser
} from '@/services/api'

const message = useMessage()

const stats = ref<OSSAdminStats>({ total_files: 0, total_size: 0, total_users: 0 })
const topUsers = ref<OSSTopUser[]>([])
const loading = ref(false)

const formatBytes = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

const statCards = [
  { label: '文件总数', value: () => stats.value.total_files, color: '#9a5a2f' },
  { label: '总存储', value: () => formatBytes(stats.value.total_size), color: '#b8743d' },
  { label: '用户数', value: () => stats.value.total_users, color: '#6f3f22' }
]

const fileColumns = [
  { title: '文件名', key: 'path', ellipsis: true },
  { title: 'MIME', key: 'mime_type', width: 120 },
  { title: '大小', key: 'size', width: 100, render: (row: OSSFile) => formatBytes(row.size) },
  { title: '存储', key: 'storage_type', width: 80 },
  {
    title: '私有',
    key: 'is_private',
    width: 60,
    render: (row: OSSFile) => (row.is_private ? '是' : '否')
  },
  { title: '上传时间', key: 'created_at', width: 160 },
  {
    title: '操作',
    key: 'actions',
    width: 80,
    render: (row: OSSFile) =>
      h(
        NButton,
        { size: 'tiny', type: 'error', quaternary: true, onClick: () => handleDeleteFile(row) },
        { default: () => '删除' }
      )
  }
]

const topUserColumns = [
  { title: '用户', key: 'username' },
  { title: '文件数', key: 'file_count', width: 100 },
  {
    title: '存储量',
    key: 'total_size',
    width: 120,
    render: (row: OSSTopUser) => formatBytes(row.total_size)
  }
]

const handleDeleteFile = async (file: OSSFile) => {
  try {
    await deleteOssAdminFileApi(file.id, { silent: true })
    message.success('已删除')
  } catch {
    message.error('删除失败')
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const [statsRes, topRes] = await Promise.all([
      getOssAdminStatsApi({ silent: true, skipAuthLogout: true }),
      getOssAdminTopUsersApi({ silent: true, skipAuthLogout: true })
    ])
    stats.value = statsRes
    topUsers.value = topRes || []
  } catch {
    // 静默
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="oss-admin-page">
    <div class="page-heading">
      <h2>OSS 存储管理</h2>
    </div>

    <NGrid :cols="3" :x-gap="12" :y-gap="12" class="stats-grid">
      <NGi v-for="card in statCards" :key="card.label">
        <div class="section-card stat-card">
          <div class="stat-label">{{ card.label }}</div>
          <div class="stat-value">{{ card.value() }}</div>
        </div>
      </NGi>
    </NGrid>

    <div class="section-card table-card">
      <h3 class="section-title">文件列表</h3>
      <ProTable
        :columns="fileColumns"
        :request="
          (p) =>
            getOssAdminFilesApi(
              { page: p.page, page_size: p.pageSize },
              { silent: true, skipAuthLogout: true }
            ).then((r) => ({ list: r.files, total: r.total, page: p.page, page_size: p.pageSize }))
        "
        row-key="id"
      />
    </div>

    <div class="section-card table-card">
      <h3 class="section-title">存储排行 TOP 10</h3>
      <ProTable :columns="topUserColumns" :data="topUsers" row-key="user_id" />
    </div>
  </div>
</template>

<style scoped>
.oss-admin-page {
  max-width: 100%;
}
.page-heading {
  margin-bottom: 16px;
}
.page-heading h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}
.stats-grid {
  margin-bottom: 16px;
}
.section-card {
  background: rgba(255, 248, 236, 0.72);
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-md);
  backdrop-filter: blur(4px);
}
.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  gap: 6px;
}
.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}
.table-card {
  padding: 16px;
  margin-bottom: 16px;
}
.section-title {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
</style>
