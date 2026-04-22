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
        <a-button type="text" size="small" @click="fetchTasks" :loading="refreshing">
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
        <div class="status-num">{{ stats.totalTasks }}</div>
        <div class="status-label">总任务</div>
      </div>
      <div class="status-card s-success">
        <div class="status-num">{{ stats.byStatus?.completed ?? 0 }}</div>
        <div class="status-label">完成</div>
      </div>
      <div class="status-card s-running">
        <div class="status-num">{{ stats.byStatus?.running ?? 0 }}</div>
        <div class="status-label">运行中</div>
      </div>
      <div class="status-card s-fail">
        <div class="status-num">{{ stats.byStatus?.failed ?? 0 }}</div>
        <div class="status-label">失败</div>
      </div>
      <div class="status-card s-info">
        <div class="status-num">{{ stats.totalResults }}</div>
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
          <span class="running-name">{{ task.name }}</span>
          <a-tag color="blue" size="small">运行中</a-tag>
        </div>
        <div class="running-body">
          <div class="running-stats">
            <span class="stat">种子 {{ task.seed_urls?.length ?? 0 }} 个</span>
            <span class="stat">间隔 {{ task.schedule_interval }}h</span>
          </div>
        </div>
        <div class="running-footer">
          <a-button type="text" size="mini" @click="runTask(task)">执行</a-button>
          <a-button type="text" size="mini" status="danger" @click="deleteTask(task)">删除</a-button>
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
      :pagination="pagination"
      class="task-table"
      @page-change="onPageChange"
    >
      <template #name="{ record }">
        <div class="task-name-cell">
          <span class="task-name">{{ record.name }}</span>
        </div>
      </template>
      <template #status="{ record }">
        <a-tag :color="taskStatusColor(record.status)">
          {{ taskStatusLabel(record.status) }}
        </a-tag>
      </template>
      <template #seed_urls="{ record }">
        <span class="seed-urls">{{ (record.seed_urls || []).slice(0, 2).join(', ') }}{{ (record.seed_urls || []).length > 2 ? '...' : '' }}</span>
      </template>
      <template #actions="{ record }">
        <a-space size="small">
          <a-button v-if="record.status !== 'running'" type="text" size="mini" @click="runTask(record)">执行</a-button>
          <a-button v-if="record.status === 'running'" type="text" size="mini" status="warning" @click="pauseTask(record)">暂停</a-button>
          <a-button v-if="record.status === 'paused'" type="text" size="mini" @click="resumeTask(record)">恢复</a-button>
          <a-button type="text" size="mini" status="danger" @click="deleteTask(record)">删除</a-button>
        </a-space>
      </template>
    </a-table>

    <!-- 新建任务弹窗 -->
    <a-modal v-model:visible="showCreateModal" title="新建爬虫任务" @ok="createTask" :mask-closable="false">
      <a-form :model="newTask" layout="vertical">
        <a-form-item label="任务名称" field="name" :rules="[{ required: true, message: '请输入任务名称' }]">
          <a-input v-model="newTask.name" placeholder="例如：知乎热榜抓取" />
        </a-form-item>
        <a-form-item label="种子 URL" field="seedUrls" :rules="[{ required: true, message: '请输入至少一个 URL' }]">
          <a-textarea
            v-model="newTask.seedUrlsText"
            placeholder="每行一个 URL"
            :auto-size="{ minRows: 3, maxRows: 6 }"
          />
        </a-form-item>
        <a-form-item label="调度间隔（小时）" field="scheduleInterval">
          <a-input-number v-model="newTask.schedule_interval" :min="0" :max="168">
            <template #suffix>小时（0 = 仅一次）</template>
          </a-input-number>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useAuth } from '../../router/auth.js'
import {
  IconBug, IconPlus, IconSync, IconArrowLeft,
  IconRefresh, IconList,
} from '@arco-design/web-vue/es/icon'

const { authHeaders } = useAuth()
const refreshing = ref(false)
const showCreateModal = ref(false)
const allTasks = ref([])
const stats = ref({ totalTasks: 0, byStatus: {}, totalResults: 0 })
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const pagination = { showTotal: true, pageSize: 20 }
const runningTasks = computed(() => allTasks.value.filter(t => t.status === 'running'))

const TASK_STATUS = {
  running: { label: '运行中', color: 'blue' },
  paused: { label: '已暂停', color: 'orange' },
  completed: { label: '完成', color: 'green' },
  failed: { label: '失败', color: 'red' },
  pending: { label: '等待中', color: 'gray' },
}

function taskStatusColor(status) { return TASK_STATUS[status]?.color ?? 'gray' }
function taskStatusLabel(status) { return TASK_STATUS[status]?.label ?? status }

const taskColumns = [
  { title: '名称', slotName: 'name', width: 200 },
  { title: '状态', slotName: 'status', width: 90 },
  { title: '种子 URL', slotName: 'seed_urls', ellipsis: true, tooltip: true },
  { title: '调度间隔', dataIndex: 'schedule_interval', width: 100,
    formatter: ({ cellValue }) => cellValue ? `${cellValue}h` : '一次' },
  { title: '创建时间', dataIndex: 'created_at', width: 160,
    formatter: ({ cellValue }) => cellValue ? new Date(cellValue).toLocaleString('zh-CN') : '-' },
  { title: '操作', slotName: 'actions', width: 200, fixed: 'right' },
]

const newTask = ref({ name: '', seedUrlsText: '', schedule_interval: 0 })

async function fetchTasks() {
  refreshing.value = true
  try {
    const [tasksRes, statsRes] = await Promise.all([
      fetch(`/api/crawler/tasks?page=${page.value}&page_size=${pageSize.value}`, { headers: authHeaders() }),
      fetch('/api/crawler/stats', { headers: authHeaders() }),
    ])
    const tasksData = await tasksRes.json()
    const statsData = await statsRes.json()
    if (tasksData.code === 'ok') {
      allTasks.value = tasksData.data.items || []
      total.value = tasksData.data.total || 0
      pagination.total = total.value
    }
    if (statsData.code === 'ok') {
      stats.value = statsData.data
    }
  } catch {
    Message.error('加载数据失败')
  } finally {
    refreshing.value = false
  }
}

function onPageChange(p) {
  page.value = p
  fetchTasks()
}

async function createTask() {
  if (!newTask.value.name?.trim()) { Message.warning('请填写任务名称'); return }
  const urls = newTask.value.seedUrlsText.split('\n').map(u => u.trim()).filter(Boolean)
  if (urls.length === 0) { Message.warning('请输入至少一个 URL'); return }

  try {
    const res = await fetch('/api/crawler/tasks', {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        name: newTask.value.name,
        seed_urls: urls,
        schedule_interval: newTask.value.schedule_interval,
      }),
    })
    const result = await res.json()
    if (result.code === 'ok') {
      Message.success('任务创建成功')
      showCreateModal.value = false
      newTask.value = { name: '', seedUrlsText: '', schedule_interval: 0 }
      await fetchTasks()
    } else {
      Message.error(result.message || '创建失败')
    }
  } catch {
    Message.error('网络错误')
  }
}

async function runTask(task) {
  try {
    const res = await fetch(`/api/crawler/tasks/${task.id}/run`, { method: 'POST', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') { Message.success('执行完成'); await fetchTasks() }
    else Message.error(result.message || '执行失败')
  } catch { Message.error('网络错误') }
}

async function pauseTask(task) {
  try {
    const res = await fetch(`/api/crawler/tasks/${task.id}/pause`, { method: 'POST', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') { Message.success('已暂停'); await fetchTasks() }
    else Message.error(result.message)
  } catch { Message.error('网络错误') }
}

async function resumeTask(task) {
  try {
    const res = await fetch(`/api/crawler/tasks/${task.id}/resume`, { method: 'POST', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') { Message.success('已恢复'); await fetchTasks() }
    else Message.error(result.message)
  } catch { Message.error('网络错误') }
}

async function deleteTask(task) {
  try {
    const res = await fetch(`/api/crawler/tasks/${task.id}`, { method: 'DELETE', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') { Message.success('已删除'); await fetchTasks() }
    else Message.error(result.message)
  } catch { Message.error('网络错误') }
}

onMounted(() => { fetchTasks() })
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
.running-name { font-size: 15px; font-weight: 600; flex: 1; }
.running-body { margin-bottom: 8px; }
.running-stats { display: flex; gap: 16px; }
.stat { font-size: 12px; color: var(--color-text-3); }
.running-footer { display: flex; justify-content: flex-end; gap: 4px; border-top: 1px solid var(--color-border-1); padding-top: 8px; }

.task-table { border-radius: var(--border-radius-large); overflow: hidden; }
.task-name-cell { display: flex; align-items: center; gap: 8px; }
.task-name { font-weight: 500; }
.seed-urls { font-size: 12px; color: var(--color-text-3); font-family: monospace; }
</style>
