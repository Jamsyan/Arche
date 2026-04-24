<template>
  <div class="file-management">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <a-space>
        <a-select
          v-model="filterUserId"
          placeholder="按用户过滤"
          style="width: 280px"
          allow-clear
          @change="loadFiles"
        >
          <a-option v-for="user in userOptions" :key="user.user_id" :value="user.user_id">
            {{ shortId(user.user_id) }}
          </a-option>
        </a-select>
        <a-button @click="loadFiles" :loading="loading">
          <template #icon><icon-refresh /></template>
          刷新
        </a-button>
      </a-space>
    </div>

    <!-- 文件表格 -->
    <a-table
      :data="files"
      :columns="fileColumns"
      row-key="id"
      :pagination="{ showTotal: true, pageSize: 20 }"
      :loading="loading"
    >
      <template #name="{ record }">
        <div class="file-name-cell">
          <icon-file class="file-icon" />
          <span class="file-name">{{ fileName(record) }}</span>
        </div>
      </template>
      <template #owner="{ record }">
        <span v-if="record.owner_id" class="owner-cell">{{ shortId(record.owner_id) }}</span>
        <span v-else class="tenant-cell">租户: {{ record.tenant_id }}</span>
      </template>
      <template #size="{ record }">
        {{ formatBytes(record.size) }}
      </template>
      <template #storage_type="{ record }">
        <a-tag :color="record.storage_type === 'local' ? 'green' : 'blue'" size="small">
          {{ record.storage_type }}
        </a-tag>
      </template>
      <template #is_private="{ record }">
        <a-tag :color="record.is_private ? 'orange' : 'gray'" size="small">
          {{ record.is_private ? '私有' : '公开' }}
        </a-tag>
      </template>
      <template #created_at="{ record }">
        {{ record.created_at ? new Date(record.created_at).toLocaleString('zh-CN') : '-' }}
      </template>
      <template #actions="{ record }">
        <a-button type="text" size="mini" status="danger" @click="confirmDelete(record)">
          删除
        </a-button>
      </template>
    </a-table>

    <a-empty v-if="!loading && files.length === 0" description="暂无文件" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { IconRefresh, IconFile } from '@arco-design/web-vue/es/icon'
import { oss } from '../../api'

const files = ref([])
const userOptions = ref([])
const filterUserId = ref(null)
const loading = ref(false)

const fileColumns = [
  { title: '名称', slotName: 'name', width: 250, ellipsis: true },
  { title: '所有者', slotName: 'owner', width: 180 },
  { title: '大小', slotName: 'size', width: 100 },
  { title: '类型', slotName: 'storage_type', width: 80 },
  { title: 'MIME', dataIndex: 'mime_type', width: 120, ellipsis: true },
  { title: '可见性', slotName: 'is_private', width: 80 },
  { title: '上传时间', slotName: 'created_at', width: 160 },
  { title: '操作', slotName: 'actions', width: 80, fixed: 'right' },
]

function shortId(id) {
  return id ? `${id.slice(0, 8)}...${id.slice(-4)}` : '-'
}

function fileName(record) {
  return record.path ? record.path.split('/').pop() || record.path : 'unnamed'
}

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let v = bytes
  while (v >= 1024 && i < units.length - 1) { v /= 1024; i++ }
  return `${v.toFixed(1)} ${units[i]}`
}

async function loadFiles() {
  loading.value = true
  try {
    const params = { limit: 200, offset: 0 }
    if (filterUserId.value) params.user_id = filterUserId.value

    const data = await oss.adminFiles(params)
    if (data) files.value = data.files || []
  } catch (err) {
    Message.error(err.message || '加载文件失败')
  } finally {
    loading.value = false
  }
}

async function loadUserOptions() {
  try {
    const data = await oss.adminQuotas({ limit: 200 })
    if (data) userOptions.value = data.items || []
  } catch { /* 忽略 */ }
}

function confirmDelete(record) {
  Modal.confirm({
    title: '确认删除',
    content: `确定删除文件 "${fileName(record)}" 吗？此操作不可恢复。`,
    onOk: async () => {
      try {
        await oss.adminDeleteFile(record.id)
        Message.success('删除成功')
        await loadFiles()
      } catch (err) {
        Message.error(err.message || '删除失败')
      }
    },
  })
}

onMounted(() => {
  loadFiles()
  loadUserOptions()
})
</script>

<style scoped>
.filter-bar { margin-bottom: 16px; }
.file-name-cell { display: flex; align-items: center; gap: 8px; }
.file-icon { width: 16px; height: 16px; color: var(--color-text-3); flex-shrink: 0; }
.file-name { font-weight: 500; }
.owner-cell, .tenant-cell { font-family: monospace; font-size: 12px; }
</style>
