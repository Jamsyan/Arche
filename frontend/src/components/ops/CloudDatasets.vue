<template>
  <!-- 操作按钮插槽 -->
  <template #actions>
    <a-button type="text" size="small" @click="fetchDatasets" :loading="refreshing">
      <template #icon><icon-refresh /></template>
      刷新
    </a-button>
    <a-button type="primary" size="small" @click="showImportModal = true">
      <template #icon><icon-plus /></template>
      导入数据集
    </a-button>
  </template>

  <div class="cloud-datasets">
    <!-- 统计卡片 -->
    <div class="status-row">
      <div class="status-card">
        <div class="status-num">{{ stats.total ?? 0 }}</div>
        <div class="status-label">总数据集</div>
      </div>
      <div class="status-card s-local">
        <div class="status-num">{{ stats.bySource?.local ?? 0 }}</div>
        <div class="status-label">本地存储</div>
      </div>
      <div class="status-card s-modelscope">
        <div class="status-num">{{ stats.bySource?.modelscope ?? 0 }}</div>
        <div class="status-label">魔搭社区</div>
      </div>
      <div class="status-card s-aliyun">
        <div class="status-num">{{ stats.bySource?.aliyun ?? 0 }}</div>
        <div class="status-label">阿里云 OSS</div>
      </div>
    </div>

    <!-- 数据集列表 -->
    <a-table
      :data="datasets"
      :columns="datasetColumns"
      row-key="id"
      :bordered="false"
      :pagination="pagination"
      class="dataset-table"
      @page-change="onPageChange"
    >
      <template #name="{ record }">
        <div class="dataset-item">
          <icon-folder class="dataset-icon" />
          <div class="dataset-info">
            <span class="dataset-name">{{ record.name }}</span>
            <span v-if="record.description" class="dataset-desc">{{ record.description }}</span>
          </div>
          <a-tag v-for="tag in record.tags" :key="tag" size="mini" color="blue">{{ tag }}</a-tag>
        </div>
      </template>
      <template #size="{ record }">
        <span class="size-text">{{ formatBytes(record.size_bytes) }}</span>
      </template>
      <template #source="{ record }">
        <a-tag :color="sourceColor(record.source)" size="small">{{ sourceLabel(record.source) }}</a-tag>
      </template>
      <template #files="{ record }">
        <span class="file-count">{{ record.file_count }} 个文件</span>
      </template>
      <template #created_at="{ record }">
        <span class="time-text">{{ formatTime(record.created_at) }}</span>
      </template>
      <template #actions="{ record }">
        <a-space size="small">
          <a-button size="mini" @click="syncDataset(record)">
            <template #icon><icon-sync /></template>
            同步
          </a-button>
          <a-button size="mini" @click="viewDataset(record)">
            <template #icon><icon-eye /></template>
            浏览
          </a-button>
          <a-popconfirm
            content="确定要删除这个数据集吗？删除后不可恢复。"
            @ok="deleteDataset(record)"
          >
            <a-button size="mini" status="danger">
              <template #icon><icon-delete /></template>
              删除
            </a-button>
          </a-popconfirm>
        </a-space>
      </template>
    </a-table>

    <!-- 导入数据集弹窗 -->
    <a-modal v-model:visible="showImportModal" title="导入数据集" @ok="importDataset" width="600">
      <a-form :model="newDataset" layout="vertical">
        <a-form-item label="数据集名称" field="name" :rules="[{ required: true, message: '请输入数据集名称' }]">
          <a-input v-model="newDataset.name" placeholder="例如：维基百科中文语料" />
        </a-form-item>

        <a-form-item label="描述">
          <a-textarea v-model="newDataset.description" placeholder="简要描述数据集内容" :auto-size="{ minRows: 2, maxRows: 4 }" />
        </a-form-item>

        <a-form-item label="来源" field="source">
          <a-radio-group v-model="newDataset.source">
            <a-radio value="local">本地 MinIO</a-radio>
            <a-radio value="modelscope">魔搭 ModelScope</a-radio>
            <a-radio value="aliyun">阿里云 OSS</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item v-if="newDataset.source === 'modelscope'" label="ModelScope 数据集 ID" :rules="[{ required: true, message: '请输入数据集 ID' }]">
          <a-input v-model="newDataset.config.modelscope_id" placeholder="例如：damo/nlp_bert_base_zh" />
        </a-form-item>

        <a-form-item v-if="newDataset.source === 'local' || newDataset.source === 'aliyun'" label="路径" :rules="[{ required: true, message: '请输入存储路径' }]">
          <a-input v-model="newDataset.path" placeholder="例如：datasets/wikipedia/zh/202401" />
        </a-form-item>

        <a-form-item label="标签">
          <a-select v-model="newDataset.tags" mode="tags" placeholder="输入标签后按回车">
            <a-option v-for="tag in commonTags" :key="tag" :value="tag">{{ tag }}</a-option>
          </a-select>
        </a-form-item>

        <a-form-item label="配置（JSON）" v-if="newDataset.source !== 'local'">
          <a-textarea
            v-model="newDataset.configText"
            placeholder='{"access_key": "xxx", "version": "1.0"}'
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 浏览文件弹窗 -->
    <a-drawer v-model:visible="fileDrawerVisible" title="浏览数据集文件" width="640">
      <div v-if="currentDataset" class="file-browser">
        <div class="file-path">
          <icon-folder />
          <span>{{ currentDataset.path }}</span>
        </div>
        <div class="file-list">
          <div v-for="file in fileList" :key="file.name" class="file-item">
            <icon-file class="file-icon" />
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatBytes(file.size) }}</span>
          </div>
        </div>
        <div v-if="fileList.length === 0" class="empty-files">暂无文件</div>
      </div>
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useAuth } from '../../router/auth.js'
import {
  IconPlus, IconRefresh, IconFolder, IconSync,
  IconEye, IconDelete, IconFile,
} from '@arco-design/web-vue/es/icon'

const { authHeaders } = useAuth()
const refreshing = ref(false)
const showImportModal = ref(false)
const fileDrawerVisible = ref(false)
const datasets = ref([])
const currentDataset = ref(null)
const fileList = ref([])
const stats = ref({ total: 0, bySource: {} })
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const pagination = { showTotal: true, pageSize: 20 }

const commonTags = ['nlp', 'cv', '语音', '多模态', '中文', '英文', '分类', '生成', '预训练']

const SOURCE_INFO = {
  local: { label: '本地存储', color: 'blue' },
  modelscope: { label: '魔搭社区', color: 'purple' },
  aliyun: { label: '阿里云 OSS', color: 'orange' },
}

function sourceColor(source) { return SOURCE_INFO[source]?.color ?? 'gray' }
function sourceLabel(source) { return SOURCE_INFO[source]?.label ?? source }

const datasetColumns = [
  { title: '名称', slotName: 'name', width: 300 },
  { title: '大小', slotName: 'size', width: 100 },
  { title: '来源', slotName: 'source', width: 120 },
  { title: '文件数', slotName: 'files', width: 100 },
  { title: '创建时间', slotName: 'created_at', width: 180 },
  { title: '操作', slotName: 'actions', width: 240, fixed: 'right' },
]

const newDataset = ref({
  name: '',
  description: '',
  source: 'local',
  path: '',
  tags: [],
  configText: '{}',
  config: {},
})

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

async function fetchDatasets() {
  refreshing.value = true
  try {
    const res = await fetch(`/api/cloud/datasets?page=${page.value}&page_size=${pageSize.value}`, { headers: authHeaders() })
    const data = await res.json()
    if (data.code === 'ok') {
      datasets.value = data.data.items || []
      total.value = data.data.total || 0
      pagination.total = total.value

      // 统计来源
      const bySource = {}
      datasets.value.forEach(ds => {
        bySource[ds.source] = (bySource[ds.source] || 0) + 1
      })
      stats.value = {
        total: total.value,
        bySource,
      }
    }
  } catch {
    Message.error('加载数据集失败')
  } finally {
    refreshing.value = false
  }
}

function onPageChange(p) {
  page.value = p
  fetchDatasets()
}

async function importDataset() {
  if (!newDataset.value.name?.trim()) { Message.warning('请输入数据集名称'); return }
  if (!newDataset.value.path?.trim() && newDataset.value.source !== 'modelscope') { Message.warning('请输入存储路径'); return }
  if (newDataset.value.source === 'modelscope' && !newDataset.value.config.modelscope_id?.trim()) { Message.warning('请输入 ModelScope 数据集 ID'); return }

  // 解析配置 JSON
  let config = {}
  try {
    config = JSON.parse(newDataset.value.configText || '{}')
  } catch {
    Message.warning('配置 JSON 格式错误')
    return
  }

  // 合并 modelscope_id 到配置
  if (newDataset.value.source === 'modelscope' && newDataset.value.config.modelscope_id) {
    config.modelscope_id = newDataset.value.config.modelscope_id
  }

  try {
    const res = await fetch('/api/cloud/datasets', {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        name: newDataset.value.name,
        description: newDataset.value.description,
        path: newDataset.value.path,
        source: newDataset.value.source,
        tags: newDataset.value.tags,
        config,
      }),
    })
    const result = await res.json()
    if (result.code === 'ok') {
      Message.success('数据集导入成功')
      showImportModal.value = false
      newDataset.value = { name: '', description: '', source: 'local', path: '', tags: [], configText: '{}', config: {} }
      await fetchDatasets()
    } else {
      Message.error(result.message || '导入失败')
    }
  } catch {
    Message.error('网络错误')
  }
}

async function syncDataset(dataset) {
  try {
    const res = await fetch(`/api/cloud/datasets/${dataset.id}/sync`, { method: 'POST', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') {
      Message.success('同步任务已提交，将在后台进行')
    } else {
      Message.error(result.message)
    }
  } catch {
    Message.error('网络错误')
  }
}

async function viewDataset(dataset) {
  currentDataset.value = dataset
  fileDrawerVisible.value = true
  // 这里可以实现获取文件列表的逻辑
  // const res = await fetch(`/api/cloud/datasets/${dataset.id}/files`, { headers: authHeaders() })
  // fileList.value = ...
}

async function deleteDataset(dataset) {
  try {
    const res = await fetch(`/api/cloud/datasets/${dataset.id}`, { method: 'DELETE', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') {
      Message.success('数据集已删除')
      await fetchDatasets()
    } else {
      Message.error(result.message)
    }
  } catch {
    Message.error('网络错误')
  }
}

onMounted(() => {
  fetchDatasets()
})
</script>

<style scoped>
.cloud-datasets {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
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

.status-card.s-local .status-num { color: #165dff; }
.status-card.s-modelscope .status-num { color: #722ed1; }
.status-card.s-aliyun .status-num { color: #ff7d00; }

.status-label {
  font-size: 13px;
  color: #86909c;
}

/* 数据集表格 */
.dataset-table {
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.7);
}

.dataset-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dataset-icon {
  font-size: 24px;
  color: #165dff;
  flex-shrink: 0;
}

.dataset-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.dataset-name {
  font-weight: 500;
  color: #1d2129;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dataset-desc {
  font-size: 12px;
  color: #86909c;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.size-text {
  font-size: 13px;
  color: #4e5969;
}

.file-count {
  font-size: 13px;
  color: #4e5969;
}

.time-text {
  font-size: 13px;
  color: #4e5969;
}

/* 文件浏览器 */
.file-browser {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-path {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(22, 93, 255, 0.05);
  border-radius: 8px;
  color: #165dff;
  font-weight: 500;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.file-item:hover {
  background: rgba(22, 93, 255, 0.05);
}

.file-icon {
  font-size: 20px;
  color: #86909c;
  flex-shrink: 0;
}

.file-name {
  flex: 1;
  color: #1d2129;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: #86909c;
  font-size: 13px;
  flex-shrink: 0;
}

.empty-files {
  text-align: center;
  padding: 48px;
  color: #86909c;
}
</style>
