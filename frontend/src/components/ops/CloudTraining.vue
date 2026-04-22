<template>
  <div class="ops-page">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.push('/platform')" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <icon-cloud class="header-icon" />
        <h1 class="page-title">云训练</h1>
      </div>
      <a-space>
        <a-button type="text" size="small" @click="refreshData" :loading="refreshing">
          <template #icon><icon-refresh /></template>
        </a-button>
        <a-button type="primary" size="small" @click="showCreateModal = true">
          <template #icon><icon-plus /></template>
          新建训练
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
        <div class="status-label">完成</div>
      </div>
      <div class="status-card s-running">
        <div class="status-num">{{ stats.running }}</div>
        <div class="status-label">训练中</div>
      </div>
      <div class="status-card s-fail">
        <div class="status-num">{{ stats.failed }}</div>
        <div class="status-label">失败</div>
      </div>
      <div class="status-card s-gpu">
        <div class="status-num">{{ gpuUsage }}</div>
        <div class="status-label">GPU 占用</div>
      </div>
    </div>

    <!-- 运行中训练 -->
    <div class="section-header">
      <icon-sync class="section-icon spin" />
      <span>正在训练</span>
      <a-tag v-if="runningTasks.length > 0" size="small" color="blue">{{ runningTasks.length }}</a-tag>
    </div>

    <div v-if="runningTasks.length === 0" class="empty-hint">暂无进行中的训练任务</div>
    <div v-else class="training-grid">
      <div v-for="task in runningTasks" :key="task.id" class="training-card">
        <div class="training-header">
          <span class="training-name">{{ task.name }}</span>
          <a-tag color="blue" size="small">{{ task.model }}</a-tag>
        </div>
        <div class="training-body">
          <!-- 损失曲线 -->
          <div class="loss-chart">
            <div class="chart-title">Loss</div>
            <div class="chart-bars">
              <div v-for="(v, i) in task.lossHistory" :key="i" class="chart-bar"
                :style="{ height: v + '%', background: lossBarColor(v) }"></div>
            </div>
            <div class="chart-values">
              <span class="loss-current">{{ task.lossCurrent }}</span>
            </div>
          </div>
          <!-- 指标 -->
          <div class="training-metrics">
            <div class="metric">
              <span class="metric-label">Epoch</span>
              <span class="metric-value">{{ task.epoch }}/{{ task.totalEpochs }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">进度</span>
              <a-progress :percent="task.progress" size="small" />
            </div>
            <div class="metric">
              <span class="metric-label">GPU</span>
              <span class="metric-value">{{ task.gpuMem }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">耗时</span>
              <span class="metric-value">{{ task.duration }}</span>
            </div>
          </div>
        </div>
        <div class="training-footer">
          <a-button type="text" size="mini" @click="viewLogs(task)">日志</a-button>
          <a-button type="text" size="mini" @click="viewMetrics(task)">指标</a-button>
          <a-button type="text" size="mini" status="danger" @click="stopTraining(task)">停止</a-button>
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
          <a-tag color="blue" size="mini">{{ record.model }}</a-tag>
        </div>
      </template>
      <template #status="{ record }">
        <a-tag :color="taskStatusColor(record.status)">{{ taskStatusLabel(record.status) }}</a-tag>
      </template>
      <template #progress="{ record }">
        <a-progress v-if="record.status === 'running'" :percent="record.progress" size="small" />
        <span v-else class="progress-done">—</span>
      </template>
      <template #loss="{ record }">
        <span class="loss-value" :class="{ 'loss-bad': record.loss > 1.0 }">{{ record.loss }}</span>
      </template>
      <template #actions="{ record }">
        <a-space size="small">
          <a-button type="text" size="mini" @click="viewLogs(record)">日志</a-button>
          <a-button v-if="record.status === 'failed'" type="text" size="mini" @click="restartTraining(record)">重试</a-button>
          <a-button v-if="record.status === 'success'" type="text" size="mini">导出</a-button>
        </a-space>
      </template>
    </a-table>

    <!-- 日志面板 -->
    <a-drawer v-model:visible="logDrawerVisible" title="训练日志" width="640">
      <div v-if="currentLogTask" class="log-panel">
        <div class="log-header">
          <span class="log-task-name">{{ currentLogTask.name }}</span>
          <a-tag color="blue" size="small">{{ currentLogTask.model }}</a-tag>
        </div>
        <div class="log-content">
          <pre v-for="(line, i) in currentLogTask.logs" :key="i" class="log-line">{{ line }}</pre>
        </div>
      </div>
    </a-drawer>

    <!-- 新建训练弹窗 -->
    <a-modal v-model:visible="showCreateModal" title="新建训练任务" @ok="createTraining">
      <a-form :model="newTask" layout="vertical">
        <a-form-item label="任务名称" field="name">
          <a-input v-model="newTask.name" placeholder="例如：文章分类微调" />
        </a-form-item>
        <a-form-item label="基础模型" field="model">
          <a-select v-model="newTask.model">
            <a-option value="qwen-7b">Qwen-7B</a-option>
            <a-option value="qwen-14b">Qwen-14B</a-option>
            <a-option value="llama-3-8b">Llama-3-8B</a-option>
            <a-option value="custom">自定义</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="数据集" field="dataset">
          <a-input v-model="newTask.dataset" placeholder="数据集路径或 ID" />
        </a-form-item>
        <a-form-item label="Epoch 数" field="epochs">
          <a-input-number v-model="newTask.epochs" :min="1" :max="100" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  IconCloud, IconPlus, IconSync, IconArrowLeft,
  IconRefresh, IconList,
} from '@arco-design/web-vue/es/icon'

const refreshing = ref(false)
const showCreateModal = ref(false)
const logDrawerVisible = ref(false)
const currentLogTask = ref(null)
const gpuUsage = ref(72)

const newTask = ref({ name: '', model: 'qwen-7b', dataset: '', epochs: 10 })

const stats = ref({ total: 0, success: 0, running: 0, failed: 0 })
const allTasks = ref([])

const runningTasks = computed(() => allTasks.value.filter(t => t.status === 'running'))

const TASK_STATUS = {
  running: { label: '训练中', color: 'blue' },
  queued: { label: '排队中', color: 'orange' },
  success: { label: '完成', color: 'green' },
  failed: { label: '失败', color: 'red' },
  cancelled: { label: '已取消', color: 'gray' },
}

function taskStatusColor(status) { return TASK_STATUS[status]?.color ?? 'gray' }
function taskStatusLabel(status) { return TASK_STATUS[status]?.label ?? status }

function lossBarColor(v) {
  if (v > 60) return '#cf222e'
  if (v > 30) return '#d4a72c'
  return '#1a7f37'
}

const taskColumns = [
  { title: '名称', dataIndex: 'name', slotName: 'name', width: 240 },
  { title: '状态', slotName: 'status', width: 90 },
  { title: '进度', slotName: 'progress', width: 140 },
  { title: 'Loss', slotName: 'loss', width: 80 },
  { title: 'Epoch', dataIndex: 'epoch_info', width: 100 },
  { title: '更新时间', dataIndex: 'updated_at', width: 160 },
  { title: '操作', slotName: 'actions', width: 160, fixed: 'right' },
]

function refreshData() {
  refreshing.value = true
  setTimeout(() => { refreshing.value = false }, 500)
}

function viewLogs(task) {
  currentLogTask.value = {
    ...task,
    logs: [
      `[${task.updated_at}] 开始训练任务: ${task.name}`,
      '[INFO] 加载模型权重...',
      '[INFO] 模型: ' + task.model,
      '[INFO] 数据集加载完成',
      '[INFO] 优化器初始化完成 (AdamW, lr=2e-5)',
      '[INFO] Epoch 1/10 - loss: 2.341 - acc: 0.412',
      '[INFO] Epoch 2/10 - loss: 1.876 - acc: 0.534',
      '[INFO] Epoch 3/10 - loss: 1.203 - acc: 0.678',
      '[INFO] Checkpoint saved at epoch 3',
      '[INFO] 继续训练...',
    ],
  }
  logDrawerVisible.value = true
}

function viewMetrics(task) {
  Message.info('指标详情功能开发中')
}

function stopTraining(task) {
  Message.info(`已停止训练: ${task.name}`)
}

function restartTraining(task) {
  Message.info(`重新执行训练: ${task.name}`)
}

function createTraining() {
  if (!newTask.value.name || !newTask.value.dataset) {
    Message.warning('请填写任务名称和数据集')
    return
  }
  Message.success(`训练任务创建成功: ${newTask.value.name}`)
  showCreateModal.value = false
  newTask.value = { name: '', model: 'qwen-7b', dataset: '', epochs: 10 }
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
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  padding: 16px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.status-card .status-num { font-size: 28px; font-weight: 700; color: var(--color-text-1); line-height: 1; }
.status-card.s-success .status-num { color: #1a7f37; }
.status-card.s-running .status-num { color: #0969da; }
.status-card.s-fail .status-num { color: #cf222e; }
.status-card.s-gpu .status-num { color: #6e7781; }
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

.training-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 12px; }
.training-card {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.training-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.training-name { font-size: 15px; font-weight: 600; flex: 1; }
.training-body { margin-bottom: 12px; }

.loss-chart { margin-bottom: 12px; }
.chart-title { font-size: 12px; color: var(--color-text-4); margin-bottom: 6px; }
.chart-bars { display: flex; align-items: flex-end; gap: 2px; height: 48px; margin-bottom: 4px; }
.chart-bar { flex: 1; border-radius: 2px 2px 0 0; min-height: 4px; transition: height 0.3s; }
.chart-values { text-align: right; }
.loss-current { font-size: 13px; font-weight: 600; color: var(--color-text-1); }

.training-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.metric { display: flex; justify-content: space-between; align-items: center; font-size: 12px; }
.metric-label { color: var(--color-text-4); }
.metric-value { color: var(--color-text-2); font-weight: 500; }

.training-footer { display: flex; justify-content: flex-end; gap: 4px; border-top: 1px solid var(--color-border-1); padding-top: 8px; }

.task-table { border-radius: var(--border-radius-large); overflow: hidden; }
.task-table :deep(.arco-table) { border-radius: var(--border-radius-large); }
.task-name-cell { display: flex; align-items: center; gap: 8px; }
.task-name { font-weight: 500; }
.progress-done { color: var(--color-text-4); }
.loss-value { font-family: 'SF Mono', monospace; font-size: 12px; }
.loss-bad { color: #cf222e; }

.log-panel { display: flex; flex-direction: column; height: 100%; }
.log-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid var(--color-border-1); }
.log-task-name { font-weight: 600; font-size: 14px; }
.log-content { flex: 1; overflow-y: auto; background: #1f2328; border-radius: var(--border-radius-medium); padding: 12px; font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; line-height: 1.6; }
.log-line { margin: 0; color: #c9d1d9; }
.log-line:nth-child(odd) { color: #8b949e; }
</style>
