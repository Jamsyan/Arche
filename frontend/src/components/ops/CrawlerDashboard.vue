<template>
  <div class="ops-page">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.push('/platform')" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <icon-bug class="header-icon" />
        <h1 class="page-title">爬虫仪表盘</h1>
      </div>
      <a-space>
        <a-button type="text" size="small" @click="refreshData" :loading="refreshing">
          <template #icon><icon-refresh /></template>
        </a-button>
        <a-button type="primary" size="small" @click="showCreateModal = true">
          <template #icon><icon-plus /></template>
          新建任务
        </a-button>
      </a-space>
    </div>

    <!-- 统计概览 -->
    <div class="status-row">
      <div class="status-card">
        <div class="status-num">{{ stats.total }}</div>
        <div class="status-label">总任务</div>
      </div>
      <div class="status-card s-success">
        <div class="status-num">{{ stats.success }}</div>
        <div class="status-label">成功</div>
      </div>
      <div class="status-card s-running">
        <div class="status-num">{{ stats.running }}</div>
        <div class="status-label">运行中</div>
      </div>
      <div class="status-card s-fail">
        <div class="status-num">{{ stats.failed }}</div>
        <div class="status-label">失败</div>
      </div>
      <div class="status-card s-info">
        <div class="status-num">{{ stats.records }}</div>
        <div class="status-label">总数据条</div>
      </div>
    </div>

    <!-- 运行中任务 -->
    <div class="section-header">
      <icon-sync class="section-icon spin" />
      <span>正在运行</span>
      <a-tag v-if="runningTasks.length > 0" size="small" color="blue">{{ runningTasks.length }}</a-tag>
    </div>

    <div v-if="runningTasks.length === 0" class="empty-hint">暂无运行中的任务</div>
    <div v-else class="running-grid">
      <div v-for="task in runningTasks" :key="task.id" class="running-card">
        <div class="running-header">
          <a-tag :color="taskTypeColor(task.type)" size="small">{{ task.typeLabel }}</a-tag>
          <span class="running-url" :title="task.url">{{ task.url }}</span>
          <span class="running-schedule">{{ task.schedule }}</span>
        </div>
        <div class="running-body">
          <div class="running-progress">
            <a-progress :percent="task.progress" size="small" :show-text="false" />
            <span class="progress-text">{{ task.progress }}%</span>
          </div>
          <div class="running-stats">
            <span class="stat"><icon-file /> {{ task.records }} 条</span>
            <span class="stat"><icon-clock-circle /> {{ task.duration }}</span>
            <span class="stat"><icon-download /> {{ task.size }}</span>
          </div>
        </div>
        <div class="running-footer">
          <a-button type="text" size="mini" @click="viewLogs(task)">日志</a-button>
          <a-button type="text" size="mini" status="danger" @click="stopTask(task)">停止</a-button>
        </div>
      </div>
    </div>

    <!-- 任务列表 -->
    <div class="section-header">
      <icon-list class="section-icon" />
      <span>全部任务</span>
    </div>

    <a-table
      :data="allTasks"
      :columns="taskColumns"
      row-key="id"
      :bordered="false"
      :pagination="{ pageSize: 10 }"
      class="task-table"
    >
      <template #name="{ record }">
        <div class="task-name-cell">
          <span class="task-name">{{ record.name }}</span>
          <a-tag :color="taskTypeColor(record.type)" size="mini">{{ record.typeLabel }}</a-tag>
        </div>
      </template>
      <template #status="{ record }">
        <a-tag :color="taskStatusColor(record.status)">
          {{ taskStatusLabel(record.status) }}
        </a-tag>
      </template>
      <template #progress="{ record }">
        <a-progress v-if="record.status === 'running'" :percent="record.progress" size="small" />
        <span v-else class="progress-done">—</span>
      </template>
      <template #actions="{ record }">
        <a-space size="small">
          <a-button type="text" size="mini" @click="viewLogs(record)">日志</a-button>
          <a-button v-if="record.status === 'paused'" type="text" size="mini" @click="resumeTask(record)">恢复</a-button>
          <a-button v-if="record.status === 'running'" type="text" size="mini" status="danger" @click="stopTask(record)">停止</a-button>
          <a-button v-if="record.status === 'success' || record.status === 'failed'" type="text" size="mini" @click="restartTask(record)">重试</a-button>
        </a-space>
      </template>
    </a-table>

    <!-- 日志面板 -->
    <a-drawer v-model:visible="logDrawerVisible" title="任务日志" width="640">
      <div v-if="currentLogTask" class="log-panel">
        <div class="log-header">
          <span class="log-task-name">{{ currentLogTask.name }}</span>
          <a-tag :color="taskStatusColor(currentLogTask.status)">{{ taskStatusLabel(currentLogTask.status) }}</a-tag>
        </div>
        <div class="log-content">
          <pre v-for="(line, i) in currentLogTask.logs" :key="i" class="log-line">{{ line }}</pre>
        </div>
      </div>
    </a-drawer>

    <!-- 新建任务弹窗 -->
    <a-modal v-model:visible="showCreateModal" title="新建爬虫任务" @ok="createTask">
      <a-form :model="newTask" layout="vertical">
        <a-form-item label="任务名称" field="name">
          <a-input v-model="newTask.name" placeholder="例如：知乎热榜抓取" />
        </a-form-item>
        <a-form-item label="目标 URL" field="url">
          <a-input v-model="newTask.url" placeholder="https://..." />
        </a-form-item>
        <a-form-item label="任务类型" field="type">
          <a-select v-model="newTask.type">
            <a-option value="full">全站抓取</a-option>
            <a-option value="page">单页抓取</a-option>
            <a-option value="api">API 数据</a-option>
            <a-option value="rss">RSS 订阅</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="调度规则" field="schedule">
          <a-select v-model="newTask.schedule">
            <a-option value="once">仅执行一次</a-option>
            <a-option value="hourly">每小时</a-option>
            <a-option value="daily">每天</a-option>
            <a-option value="weekly">每周</a-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  IconBug, IconPlus, IconSync, IconArrowLeft,
  IconRefresh, IconList, IconFile, IconClockCircle, IconDownload,
} from '@arco-design/web-vue/es/icon'

const refreshing = ref(false)
const showCreateModal = ref(false)
const logDrawerVisible = ref(false)
const currentLogTask = ref(null)

const newTask = ref({ name: '', url: '', type: 'full', schedule: 'daily' })

const stats = ref({ total: 0, success: 0, running: 0, failed: 0, records: 0 })

const allTasks = ref([])

const runningTasks = computed(() => allTasks.value.filter(t => t.status === 'running'))

const TASK_TYPES = {
  full: { label: '全站', color: 'blue' },
  page: { label: '单页', color: 'orange' },
  api: { label: 'API', color: 'green' },
  rss: { label: 'RSS', color: 'purple' },
}

function taskTypeColor(type) { return TASK_TYPES[type]?.color ?? 'gray' }

const TASK_STATUS = {
  running: { label: '运行中', color: 'blue' },
  paused: { label: '已暂停', color: 'orange' },
  success: { label: '完成', color: 'green' },
  failed: { label: '失败', color: 'red' },
  pending: { label: '等待中', color: 'gray' },
}

function taskStatusColor(status) { return TASK_STATUS[status]?.color ?? 'gray' }
function taskStatusLabel(status) { return TASK_STATUS[status]?.label ?? status }

const taskColumns = [
  { title: '名称', dataIndex: 'name', slotName: 'name', width: 260 },
  { title: '目标 URL', dataIndex: 'url', ellipsis: true, tooltip: true },
  { title: '状态', slotName: 'status', width: 90 },
  { title: '进度', slotName: 'progress', width: 140 },
  { title: '数据量', dataIndex: 'records', width: 80 },
  { title: '更新时间', dataIndex: 'updated_at', width: 160 },
  { title: '操作', slotName: 'actions', width: 180, fixed: 'right' },
]

function refreshData() {
  refreshing.value = true
  setTimeout(() => { refreshing.value = false }, 500)
}

function viewLogs(task) {
  currentLogTask.value = {
    ...task,
    logs: [
      `[${task.updated_at}] 开始抓取 ${task.url}`,
      '[INFO] 初始化爬虫引擎...',
      '[INFO] 加载请求头伪装...',
      '[INFO] 代理池连接成功',
      '[INFO] 目标站点响应 200 OK',
      '[INFO] 解析 HTML 结构...',
      `[INFO] 已提取 ${task.records} 条数据`,
      '[INFO] 数据清洗完成',
      '[INFO] 写入本地存储...',
    ],
  }
  logDrawerVisible.value = true
}

function stopTask(task) {
  Message.info(`已停止任务: ${task.name}`)
}

function resumeTask(task) {
  Message.info(`已恢复任务: ${task.name}`)
}

function restartTask(task) {
  Message.info(`重新执行任务: ${task.name}`)
}

function createTask() {
  if (!newTask.value.name || !newTask.value.url) {
    Message.warning('请填写任务名称和目标 URL')
    return
  }
  Message.success(`任务创建成功: ${newTask.value.name}`)
  showCreateModal.value = false
  newTask.value = { name: '', url: '', type: 'full', schedule: 'daily' }
}
</script>

<style scoped>
.ops-page { max-width: 1100px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.header-icon { width: 24px; height: 24px; color: var(--color-primary); }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }

.status-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 24px; }
.status-card {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  padding: 16px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.status-card .status-num { font-size: 28px; font-weight: 700; color: var(--color-text-1); line-height: 1; }
.status-card.s-success .status-num { color: #1a7f37; }
.status-card.s-running .status-num { color: #0969da; }
.status-card.s-fail .status-num { color: #cf222e; }
.status-card.s-info .status-num { color: #6e7781; }
.status-label { font-size: 12px; color: var(--color-text-4); margin-top: 4px; }

.section-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600; color: var(--color-text-2);
  margin-bottom: 12px; margin-top: 24px;
}
.section-icon { width: 16px; height: 16px; color: var(--color-text-4); }
.spin { animation: spin 1.5s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.empty-hint {
  text-align: center; padding: 32px; color: var(--color-text-4);
  background: rgba(255,255,255,0.5); border: 1px dashed var(--color-border-2);
  border-radius: var(--border-radius-large); margin-bottom: 16px;
}

.running-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 12px; }
.running-card {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.running-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.running-url { font-size: 13px; color: var(--color-text-2); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.running-schedule { font-size: 11px; color: var(--color-text-4); background: var(--color-fill-2); padding: 2px 8px; border-radius: 8px; }
.running-body { margin-bottom: 8px; }
.running-progress { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.progress-text { font-size: 12px; color: var(--color-text-3); white-space: nowrap; }
.running-stats { display: flex; gap: 16px; }
.stat { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: var(--color-text-3); }
.stat .arco-icon { width: 12px; height: 12px; }
.running-footer { display: flex; justify-content: flex-end; gap: 4px; border-top: 1px solid var(--color-border-1); padding-top: 8px; }

.task-table { border-radius: var(--border-radius-large); overflow: hidden; }
.task-table :deep(.arco-table) { border-radius: var(--border-radius-large); }
.task-name-cell { display: flex; align-items: center; gap: 8px; }
.task-name { font-weight: 500; }
.progress-done { color: var(--color-text-4); }

.log-panel { display: flex; flex-direction: column; height: 100%; }
.log-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid var(--color-border-1); }
.log-task-name { font-weight: 600; font-size: 14px; }
.log-content { flex: 1; overflow-y: auto; background: #1f2328; border-radius: var(--border-radius-medium); padding: 12px; font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; line-height: 1.6; }
.log-line { margin: 0; color: #c9d1d9; }
.log-line:nth-child(odd) { color: #8b949e; }
</style>
