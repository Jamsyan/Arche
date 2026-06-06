<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getMyOssFilesApi, getOssFileUrl } from '@/services/api'
import { $message } from '@/utils/message'
import type { OSSFile } from '@/services/api'

const props = withDefaults(
  defineProps<{
    files?: Array<{ id: string; index: number; url: string; name: string }>
    quotaUsed?: number
    quotaTotal?: number
  }>(),
  {
    files: () => [],
    quotaUsed: 0,
    quotaTotal: 0
  }
)

const emit = defineEmits<{
  insert: [refStr: string]
  upload: [file: File]
}>()

// ── 状态 ──
const ossFiles = ref<OSSFile[]>([])
const loading = ref(false)
const error = ref('')
const uploading = ref(false)

// ── 构建 id → index 映射 ──
const fileIndexMap = computed(() => {
  const map = new Map<string, number>()
  for (const f of props.files) {
    map.set(f.id, f.index)
  }
  return map
})

// ── 缩略图 URL ──
function getThumbUrl(file: OSSFile): string {
  return getOssFileUrl(file.id)
}

// ── 获取文件列表 ──
async function fetchFiles() {
  loading.value = true
  error.value = ''
  try {
    const result = await getMyOssFilesApi({ limit: 50, offset: 0 })
    ossFiles.value = result.list
  } catch (e) {
    error.value = '加载素材失败'
    console.error('获取 OSS 文件列表失败:', e)
  } finally {
    loading.value = false
  }
}

// ── 点击资源 ──
function handleFileClick(file: OSSFile) {
  const idx = fileIndexMap.value.get(file.id)
  if (idx !== undefined) {
    emit('insert', `#${idx}`)
  } else {
    // 如果不在已引用列表中，计算下一个可用索引
    const maxIdx = props.files.reduce((max, f) => Math.max(max, f.index), 0)
    emit('insert', `#${maxIdx + 1}`)
  }
}

// ── 上传 ──
function handleUploadClick() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = () => {
    const file = input.files?.[0]
    if (!file) return
    if (file.size > 10 * 1024 * 1024) {
      $message.error('文件大小不能超过 10MB')
      return
    }
    emit('upload', file)
    // 上传后刷新列表
    fetchFiles()
  }
  input.click()
}

// ── 格式化字节 ──
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  const idx = Math.min(i, units.length - 1)
  return `${(bytes / Math.pow(k, idx)).toFixed(1)} ${units[idx]}`
}

// ── 配额进度 ──
const quotaPercent = computed(() => {
  if (props.quotaTotal <= 0) return 0
  return Math.min((props.quotaUsed / props.quotaTotal) * 100, 100)
})

onMounted(fetchFiles)
</script>

<template>
  <aside class="asset-sidebar">
    <!-- 标题 -->
    <div class="sidebar-header">
      <h3 class="sidebar-title">帖子素材</h3>
    </div>

    <!-- 上传按钮 -->
    <button
      class="upload-btn"
      :disabled="uploading"
      @click="handleUploadClick"
    >
      <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="17 8 12 3 7 8" />
        <line x1="12" y1="3" x2="12" y2="15" />
      </svg>
      <span>{{ uploading ? '上传中...' : '上传' }}</span>
    </button>

    <!-- 加载中 -->
    <div v-if="loading" class="sidebar-loading">
      <div class="loading-spinner" />
      <span>加载中...</span>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="sidebar-error">
      <span>{{ error }}</span>
      <button class="retry-btn" @click="fetchFiles">重试</button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="ossFiles.length === 0" class="sidebar-empty">
      <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
      </svg>
      <span>暂无素材</span>
    </div>

    <!-- 文件网格 -->
    <div v-else class="file-grid">
      <button
        v-for="(file, idx) in ossFiles"
        :key="file.id"
        class="file-item"
        :title="`#${fileIndexMap.get(file.id) ?? idx + 1} - ${file.path || file.id}`"
        @click="handleFileClick(file)"
      >
        <img
          :src="getThumbUrl(file)"
          :alt="file.path || '素材'"
          class="file-thumb"
          loading="lazy"
        />
        <span class="file-badge">#{{ fileIndexMap.get(file.id) ?? idx + 1 }}</span>
      </button>
    </div>

    <!-- 配额 -->
    <div class="quota-bar">
      <div class="quota-info">
        <span class="quota-label">配额使用</span>
        <span class="quota-value">
          {{ formatBytes(quotaUsed) }}
          <template v-if="quotaTotal > 0"> / {{ formatBytes(quotaTotal) }}</template>
        </span>
      </div>
      <div v-if="quotaTotal > 0" class="quota-track">
        <div class="quota-fill" :style="{ width: quotaPercent + '%' }" />
      </div>
    </div>
  </aside>
</template>

<style scoped>
.asset-sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-left: 1px solid var(--border-color);
  background: var(--surface-color);
  border-radius: var(--radius-md);
  font-family: var(--font-sans);
  height: 100%;
  overflow-y: auto;
}

/* ── 标题 ── */
.sidebar-header {
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-color);
}

.sidebar-title {
  margin: 0;
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

/* ── 上传按钮 ── */
.upload-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 8px 16px;
  background: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition:
    background-color var(--transition-fast),
    transform var(--transition-fast);
}

.upload-btn:hover:not(:disabled) {
  background: var(--primary-hover-color);
}

.upload-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.upload-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upload-icon {
  width: 16px;
  height: 16px;
}

/* ── 加载中 ── */
.sidebar-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xl) 0;
  color: var(--text-tertiary);
  font-size: 13px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ── 错误提示 ── */
.sidebar-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg) 0;
  color: var(--error-color);
  font-size: 13px;
}

.retry-btn {
  padding: 4px 12px;
  background: transparent;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
  font-size: 12px;
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.retry-btn:hover {
  background: var(--primary-light-color);
}

/* ── 空状态 ── */
.sidebar-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xl) 0;
  color: var(--text-tertiary);
  font-size: 13px;
}

.empty-icon {
  width: 32px;
  height: 32px;
  opacity: 0.5;
}

/* ── 文件网格 ── */
.file-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  flex: 1;
}

.file-item {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--surface-inset-color);
  cursor: pointer;
  padding: 0;
  transition:
    border-color var(--transition-fast),
    transform var(--transition-fast),
    box-shadow var(--transition-fast);
}

.file-item:hover {
  border-color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.file-item:active {
  transform: translateY(0);
}

.file-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.file-badge {
  position: absolute;
  right: 2px;
  bottom: 2px;
  padding: 1px 4px;
  font-size: 10px;
  font-weight: var(--font-weight-semibold);
  color: #fff;
  background: rgba(0, 0, 0, 0.55);
  border-radius: 3px;
  line-height: 1.3;
  pointer-events: none;
}

/* ── 配额 ── */
.quota-bar {
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--border-color);
}

.quota-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.quota-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.quota-value {
  font-size: 11px;
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
}

.quota-track {
  width: 100%;
  height: 4px;
  background: var(--surface-inset-color);
  border-radius: 2px;
  overflow: hidden;
}

.quota-fill {
  height: 100%;
  background: var(--primary-color);
  border-radius: 2px;
  transition: width var(--transition-normal);
}
</style>
