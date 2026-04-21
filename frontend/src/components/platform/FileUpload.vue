<template>
  <div class="upload-page">
    <a-card :bordered="false" style="margin-bottom: 24px">
      <a-typography-title :heading="5" style="margin: 0 0 16px">文件上传</a-typography-title>

      <a-upload
        action="/api/oss/upload"
        :headers="uploadHeaders"
        :show-file-list="false"
        @success="handleUploadSuccess"
        @error="handleUploadError"
        @progress="handleProgress"
      >
        <template #upload-button>
          <a-drag :custom="true">
            <div class="upload-drag-area">
              <icon-upload class="upload-icon" />
              <a-text>拖拽文件到此处，或点击上传</a-text>
              <a-typography-text type="secondary" style="font-size: 12px; margin-top: 4px">
                支持任意文件格式
              </a-typography-text>
            </div>
          </a-drag>
        </template>
      </a-upload>

      <!-- 上传进度 -->
      <div v-if="uploading" style="margin-top: 16px">
        <a-progress :percent="uploadPercent" status="active" />
        <a-typography-text type="secondary" style="margin-left: 8px">
          上传中 {{ uploadPercent }}%
        </a-typography-text>
      </div>
    </a-card>

    <!-- 我的文件列表 -->
    <a-card :bordered="false">
      <template #title>
        <a-space>
          <a-typography-title :heading="5" style="margin: 0">我的文件</a-typography-title>
          <a-button size="mini" @click="loadFiles">
            <template #icon><icon-refresh /></template>
          </a-button>
        </a-space>
      </template>

      <a-table
        :data="fileList"
        :loading="loadingFiles"
        :pagination="{ pageSize: 10 }"
        row-key="id"
        :columns="columns"
      >
        <template #size="{ record }">
          {{ formatSize(record.size) }}
        </template>
        <template #storage_type="{ record }">
          <a-tag :color="storageTypeColor(record.storage_type)">
            {{ record.storage_type }}
          </a-tag>
        </template>
        <template #created_at="{ record }">
          {{ formatDate(record.created_at) }}
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  IconUpload,
  IconRefresh,
} from '@arco-design/web-vue/es/icon'
import { useAuth } from '../../router/auth.js'

const { getToken, authHeaders } = useAuth()

const uploading = ref(false)
const uploadPercent = ref(0)
const fileList = ref([])
const loadingFiles = ref(false)

const uploadHeaders = computed(() => {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
})

const columns = [
  { title: '文件名', dataIndex: 'name', width: 300 },
  { title: '大小', slotName: 'size', width: 120 },
  { title: '存储类型', slotName: 'storage_type', width: 120 },
  { title: '上传时间', slotName: 'created_at', width: 180 },
]

const STORAGE_TYPE_COLORS = {
  hot: 'blue',
  warm: 'orange',
  cold: 'gray',
}

function storageTypeColor(type) {
  return STORAGE_TYPE_COLORS[type] ?? 'gray'
}

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function handleProgress(event) {
  if (event.percent !== undefined) {
    uploadPercent.value = Math.round(event.percent)
  }
}

function handleUploadSuccess(fileItem) {
  uploading.value = false
  uploadPercent.value = 0
  Message.success('上传成功')
  loadFiles()
}

function handleUploadError() {
  uploading.value = false
  uploadPercent.value = 0
  Message.error('上传失败，请重试')
}

async function loadFiles() {
  loadingFiles.value = true
  try {
    const res = await fetch('/api/oss/files', {
      headers: authHeaders(),
    })
    if (!res.ok) {
      Message.error('获取文件列表失败')
      return
    }
    const resData = await res.json()
    fileList.value = resData.data ?? []
  } catch {
    Message.error('网络错误')
  } finally {
    loadingFiles.value = false
  }
}

onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.upload-page {
  max-width: 1000px;
  margin: 0 auto;
}

.upload-page :deep(.arco-card) {
  border-radius: var(--border-radius-large);
  margin-bottom: 16px;
}

.upload-drag-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  border: 2px dashed var(--color-border-2);
  border-radius: var(--border-radius-large);
  cursor: pointer;
  transition: border-color 0.3s, background 0.3s;
}

.upload-drag-area:hover {
  border-color: var(--color-primary);
  background: var(--color-fill-2);
}

.upload-icon {
  font-size: 48px;
  color: var(--color-text-3);
  margin-bottom: 12px;
}
</style>
