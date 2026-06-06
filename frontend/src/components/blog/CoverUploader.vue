<script setup lang="ts">
import { ref } from 'vue'
import { uploadOssFileApi } from '@/services/api'
import { $message } from '@/utils/message'

defineProps<{
  coverUrl: string
}>()

const emit = defineEmits<{
  'update:coverUrl': [url: string]
}>()

// ── 状态 ──
const uploading = ref(false)
const isDragOver = ref(false)

// ── 上传封面 ──
async function uploadCover(file: File) {
  if (!file.type.startsWith('image/')) {
    $message.error('请选择图片文件')
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    $message.error('文件大小不能超过 10MB')
    return
  }

  uploading.value = true
  try {
    const result = await uploadOssFileApi(file, false)
    // uploadOssFileApi 返回 OSSUploadResponse，需要解出 data
    const response = result as unknown as { data: { id: string } }
    const fileId = response.data?.id
    if (fileId) {
      emit('update:coverUrl', `/api/oss/files/${fileId}`)
    }
  } catch (e) {
    console.error('封面上传失败:', e)
    $message.error('封面上传失败')
  } finally {
    uploading.value = false
  }
}

// ── 点击选择文件 ──
function handleClick() {
  if (uploading.value) return
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = () => {
    const file = input.files?.[0]
    if (file) uploadCover(file)
  }
  input.click()
}

// ── 拖拽事件 ──
function handleDragOver(e: DragEvent) {
  e.preventDefault()
  e.stopPropagation()
  isDragOver.value = true
}

function handleDragLeave(e: DragEvent) {
  e.preventDefault()
  e.stopPropagation()
  isDragOver.value = false
}

function handleDrop(e: DragEvent) {
  e.preventDefault()
  e.stopPropagation()
  isDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) uploadCover(file)
}

// ── 删除封面 ──
function handleDelete(e: MouseEvent) {
  e.stopPropagation()
  emit('update:coverUrl', '')
}
</script>

<template>
  <div class="cover-uploader">
    <!-- 有封面 → 预览模式 -->
    <div v-if="coverUrl" class="cover-preview" @click="handleClick">
      <img :src="coverUrl" alt="封面预览" class="cover-image" />
      <div class="cover-overlay">
        <span class="overlay-text">{{ uploading ? '上传中...' : '更换封面' }}</span>
      </div>
      <button
        class="cover-delete-btn"
        :disabled="uploading"
        aria-label="删除封面"
        @click.stop="handleDelete"
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="delete-icon"
        >
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
      <div v-if="uploading" class="cover-uploading-overlay">
        <div class="uploading-spinner" />
      </div>
    </div>

    <!-- 无封面 → 上传区域 -->
    <div
      v-else
      :class="['cover-upload-area', { 'is-dragover': isDragOver, 'is-uploading': uploading }]"
      @click="handleClick"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      <svg
        v-if="!uploading"
        class="upload-area-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
      >
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
      </svg>
      <div v-if="!uploading" class="upload-area-text">
        <span class="upload-area-title">点击上传封面</span>
        <span class="upload-area-hint">支持拖拽 · 最大 10MB</span>
      </div>
      <div v-else class="uploading-area-status">
        <div class="uploading-spinner" />
        <span>上传中...</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cover-uploader {
  width: 100%;
  max-width: 100%;
  border-radius: var(--radius-md);
  overflow: hidden;
  font-family: var(--font-sans);
}

/* ── 上传区域 ── */
.cover-upload-area {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-md);
  background: var(--surface-color);
  cursor: pointer;
  transition:
    border-color var(--transition-normal),
    background-color var(--transition-normal);
}

.cover-upload-area:hover {
  border-color: var(--primary-color);
  background: var(--primary-light-color);
}

.cover-upload-area.is-dragover {
  border-color: var(--primary-color);
  background: var(--primary-light-color);
  box-shadow: 0 0 0 3px var(--primary-light-color);
}

.cover-upload-area.is-uploading {
  cursor: not-allowed;
  opacity: 0.7;
}

.upload-area-icon {
  width: 36px;
  height: 36px;
  color: var(--text-tertiary);
  transition: color var(--transition-fast);
}

.cover-upload-area:hover .upload-area-icon {
  color: var(--primary-color);
}

.upload-area-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.upload-area-title {
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  transition: color var(--transition-fast);
}

.cover-upload-area:hover .upload-area-title {
  color: var(--primary-color);
}

.upload-area-hint {
  font-size: 11px;
  color: var(--text-tertiary);
}

.uploading-area-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 13px;
  color: var(--text-tertiary);
}

/* ── 预览模式 ── */
.cover-preview {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  background: var(--surface-inset-color);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0);
  transition: background-color var(--transition-normal);
}

.cover-preview:hover .cover-overlay {
  background: rgba(0, 0, 0, 0.45);
}

.overlay-text {
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  color: #fff;
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.cover-preview:hover .overlay-text {
  opacity: 1;
}

/* ── 删除按钮 ── */
.cover-delete-btn {
  position: absolute;
  top: var(--spacing-sm);
  right: var(--spacing-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  cursor: pointer;
  opacity: 0;
  transition:
    opacity var(--transition-fast),
    background-color var(--transition-fast);
  z-index: 2;
}

.cover-preview:hover .cover-delete-btn {
  opacity: 1;
}

.cover-delete-btn:hover:not(:disabled) {
  background: var(--error-color);
}

.cover-delete-btn:disabled {
  cursor: not-allowed;
}

.delete-icon {
  width: 14px;
  height: 14px;
}

/* ── 上传中遮罩 ── */
.cover-uploading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.35);
  z-index: 1;
}

/* ── 加载动画 ── */
.uploading-spinner {
  width: 28px;
  height: 28px;
  border: 2.5px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
