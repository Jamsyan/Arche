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
        <a-button type="text" size="small" @click="refreshStorage">
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
          <a-progress :percent="localPercent" size="medium" />
          <div class="overview-stats">
            <span>已用 <b>{{ storageUsed }} MB</b></span>
            <span>总量 <b>{{ storageTotal }} MB</b></span>
            <span>剩余 <b>{{ storageTotal - storageUsed }} MB</b></span>
          </div>
        </div>
      </div>
      <div class="overview-card oss" :class="{ 'oss-disconnected': !ossConnected }">
        <div class="overview-header">
          <icon-cloud class="overview-icon" />
          <span class="overview-title">OSS 远程存储</span>
          <a-tag v-if="ossConnected" color="blue" size="small">已连接</a-tag>
          <a-tag v-else color="gray" size="small">未接入</a-tag>
        </div>
        <div class="overview-body">
          <div v-if="!ossConnected" class="oss-disconnect-hint">
            <p>OSS 远程存储尚未配置</p>
            <a-button type="outline" size="small" @click="showOssConfigModal = true">配置 OSS</a-button>
          </div>
          <div v-else>
            <a-progress :percent="ossPercent" size="medium" />
            <div class="overview-stats">
              <span>已用 <b>{{ ossUsed }} MB</b></span>
              <span>总量 <b>{{ ossTotal }} MB</b></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 存储浏览 -->
    <a-tabs v-model:active-key="activeTab" class="storage-tabs">
      <a-tab-pane key="local" title="本地存储">
        <div class="storage-browser">
          <!-- 路径导航 -->
          <div class="breadcrumb-bar">
            <a-breadcrumb>
              <a-breadcrumb-item @click="navigateTo([])">
                <icon-home class="bc-icon" /> 根目录
              </a-breadcrumb-item>
              <a-breadcrumb-item v-for="(seg, i) in localPath" :key="i" @click="navigateTo(localPath.slice(0, i + 1))">
                {{ seg }}
              </a-breadcrumb-item>
            </a-breadcrumb>
          </div>

          <!-- 工具栏 -->
          <div class="toolbar">
            <a-input-search v-model="localSearch" placeholder="搜索文件..." size="small" style="width: 200px" />
            <a-space>
              <a-button type="text" size="mini" @click="createFolder('local')">
                <template #icon><icon-folder-add /></template>
                新建文件夹
              </a-button>
            </a-space>
          </div>

          <!-- 文件列表 -->
          <a-table
            :data="localFiles"
            :columns="fileColumns"
            row-key="id"
            :bordered="false"
            :pagination="{ pageSize: 15 }"
            class="file-table"
          >
            <template #name="{ record }">
              <div class="file-name-cell" :class="{ clickable: record.type === 'folder' }"
                @click="record.type === 'folder' ? openFolder(record.name) : null">
                <icon-folder v-if="record.type === 'folder'" class="file-icon folder" />
                <icon-file v-else class="file-icon" />
                <span class="file-name">{{ record.name }}</span>
              </div>
            </template>
            <template #size="{ record }">
              <span v-if="record.type === 'folder'">—</span>
              <span v-else>{{ formatSize(record.size) }}</span>
            </template>
            <template #actions="{ record }">
              <a-space size="small">
                <a-button v-if="record.type === 'file'" type="text" size="mini">下载</a-button>
                <a-button type="text" size="mini" status="danger">删除</a-button>
              </a-space>
            </template>
          </a-table>
        </div>
      </a-tab-pane>

      <a-tab-pane key="oss" title="OSS 远程存储" :disabled="!ossConnected">
        <div v-if="!ossConnected" class="oss-empty">
          <icon-cloud class="oss-empty-icon" />
          <p>OSS 远程存储尚未配置</p>
          <a-button type="outline" size="small" @click="showOssConfigModal = true">配置 OSS</a-button>
        </div>
        <div v-else class="storage-browser">
          <div class="breadcrumb-bar">
            <a-breadcrumb>
              <a-breadcrumb-item @click="ossPath = []">
                <icon-cloud class="bc-icon" /> OSS 根目录
              </a-breadcrumb-item>
              <a-breadcrumb-item v-for="(seg, i) in ossPath" :key="i" @click="ossPath = ossPath.slice(0, i + 1)">
                {{ seg }}
              </a-breadcrumb-item>
            </a-breadcrumb>
          </div>
          <div class="toolbar">
            <a-input-search v-model="ossSearch" placeholder="搜索文件..." size="small" style="width: 200px" />
          </div>
          <a-table
            :data="ossFiles"
            :columns="fileColumns"
            row-key="id"
            :bordered="false"
            :pagination="{ pageSize: 15 }"
            class="file-table"
          >
            <template #name="{ record }">
              <div class="file-name-cell" :class="{ clickable: record.type === 'folder' }"
                @click="record.type === 'folder' ? ossPath = [...ossPath, record.name] : null">
                <icon-folder v-if="record.type === 'folder'" class="file-icon folder" />
                <icon-file v-else class="file-icon" />
                <span class="file-name">{{ record.name }}</span>
              </div>
            </template>
            <template #size="{ record }">
              <span v-if="record.type === 'folder'">—</span>
              <span v-else>{{ formatSize(record.size) }}</span>
            </template>
            <template #actions="{ record }">
              <a-space size="small">
                <a-button v-if="record.type === 'file'" type="text" size="mini">下载</a-button>
                <a-button type="text" size="mini" status="danger">删除</a-button>
              </a-space>
            </template>
          </a-table>
        </div>
      </a-tab-pane>
    </a-tabs>

    <!-- OSS 配置弹窗 -->
    <a-modal v-model:visible="showOssConfigModal" title="配置 OSS 远程存储" @ok="saveOssConfig">
      <a-form :model="ossConfig" layout="vertical">
        <a-form-item label="Endpoint" field="endpoint">
          <a-input v-model="ossConfig.endpoint" placeholder="oss-cn-hangzhou.aliyuncs.com" />
        </a-form-item>
        <a-form-item label="Access Key ID" field="accessKeyId">
          <a-input v-model="ossConfig.accessKeyId" placeholder="LTAI..." />
        </a-form-item>
        <a-form-item label="Access Key Secret" field="accessKeySecret">
          <a-input-password v-model="ossConfig.accessKeySecret" placeholder="••••••••" />
        </a-form-item>
        <a-form-item label="Bucket" field="bucket">
          <a-input v-model="ossConfig.bucket" placeholder="my-bucket" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  IconStorage, IconCloud, IconUpload, IconArrowLeft,
  IconRefresh, IconFolder, IconFile, IconHome, IconFolderAdd,
} from '@arco-design/web-vue/es/icon'

const activeTab = ref('local')
const localSearch = ref('')
const ossSearch = ref('')
const localPath = ref([])
const ossPath = ref([])
const showOssConfigModal = ref(false)
const ossConnected = ref(false)

const ossConfig = ref({ endpoint: '', accessKeyId: '', accessKeySecret: '', bucket: '' })

const storageUsed = ref(127)
const storageTotal = ref(500)
const ossUsed = ref(0)
const ossTotal = ref(2000)

const localPercent = computed(() => storageTotal.value ? Math.round((storageUsed.value / storageTotal.value) * 100) : 0)
const ossPercent = computed(() => ossTotal.value ? Math.round((ossUsed.value / ossTotal.value) * 100) : 0)

const localFiles = ref([
  { id: 1, name: 'uploads', type: 'folder', size: 0, updated_at: '2026-04-20' },
  { id: 2, name: 'backups', type: 'folder', size: 0, updated_at: '2026-04-19' },
  { id: 3, name: 'models', type: 'folder', size: 0, updated_at: '2026-04-18' },
  { id: 4, name: 'config.yaml', type: 'file', size: 2048, updated_at: '2026-04-21' },
  { id: 5, name: 'data.db', type: 'file', size: 52428800, updated_at: '2026-04-22' },
])

const ossFiles = ref([
  { id: 10, name: 'datasets', type: 'folder', size: 0, updated_at: '2026-04-20' },
  { id: 11, name: 'checkpoints', type: 'folder', size: 0, updated_at: '2026-04-19' },
])

const fileColumns = [
  { title: '名称', dataIndex: 'name', slotName: 'name', width: 300 },
  { title: '大小', slotName: 'size', width: 100 },
  { title: '修改时间', dataIndex: 'updated_at', width: 160 },
  { title: '操作', slotName: 'actions', width: 140, fixed: 'right' },
]

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

function refreshStorage() {
  Message.info('刷新存储信息')
}

function openFolder(name) {
  localPath.value = [...localPath.value, name]
  Message.info(`进入目录: ${name}`)
}

function navigateTo(path) {
  localPath.value = path
}

function createFolder(type) {
  Message.info(`新建文件夹 (${type})`)
}

function saveOssConfig() {
  if (!ossConfig.value.endpoint || !ossConfig.value.accessKeyId) {
    Message.warning('请填写 Endpoint 和 Access Key')
    return
  }
  ossConnected.value = true
  showOssConfigModal.value = false
  Message.success('OSS 配置成功')
}
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

.oss-disconnected { opacity: 0.7; }
.oss-disconnect-hint { text-align: center; padding: 24px 0; color: var(--color-text-4); }
.oss-disconnect-hint p { margin-bottom: 12px; }

.storage-tabs { margin-top: 8px; }
.storage-browser { min-height: 400px; }
.breadcrumb-bar {
  padding: 8px 0; margin-bottom: 12px;
  border-bottom: 1px solid var(--color-border-1);
}
.bc-icon { width: 14px; height: 14px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }

.file-table { border-radius: var(--border-radius-large); overflow: hidden; }
.file-name-cell { display: flex; align-items: center; gap: 8px; }
.file-name-cell.clickable { cursor: pointer; }
.file-name-cell.clickable:hover .file-name { color: var(--color-primary); }
.file-icon { width: 16px; height: 16px; color: var(--color-text-3); flex-shrink: 0; }
.file-icon.folder { color: #d4a72c; }
.file-name { font-weight: 500; }

.oss-empty {
  text-align: center; padding: 64px 24px; color: var(--color-text-4);
  background: rgba(255,255,255,0.5); border: 1px dashed var(--color-border-2);
  border-radius: var(--border-radius-large);
}
.oss-empty-icon { width: 48px; height: 48px; color: var(--color-border-2); margin-bottom: 12px; }
.oss-empty p { margin: 8px 0 16px; font-size: 14px; }
</style>
