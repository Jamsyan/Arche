<template>
  <!-- 操作按钮插槽，会显示在工作台的顶部标题栏右侧 -->
  <template #actions>
    <a-button type="text" size="small" @click="fetchJobs" :loading="refreshing">
      <template #icon><icon-refresh /></template>
      刷新
    </a-button>
    <a-button type="primary" size="small" @click="showCreateModal = true">
      <template #icon><icon-plus /></template>
      新建训练
    </a-button>
  </template>

  <!-- 页面内容 -->
  <div class="cloud-tasks">
    <!-- 统计概览 -->
    <div class="status-row">
      <div class="status-card">
        <div class="status-num">{{ stats.total ?? 0 }}</div>
        <div class="status-label">总任务</div>
      </div>
      <div class="status-card s-success">
        <div class="status-num">{{ stats.byStatus?.completed ?? 0 }}</div>
        <div class="status-label">完成</div>
      </div>
      <div class="status-card s-running">
        <div class="status-num">{{ stats.byStatus?.running ?? 0 }}</div>
        <div class="status-label">训练中</div>
      </div>
      <div class="status-card s-fail">
        <div class="status-num">{{ stats.byStatus?.failed ?? 0 }}</div>
        <div class="status-label">失败</div>
      </div>
    </div>

    <!-- 运行中训练 -->
    <div class="section-header">
      <icon-sync class="section-icon spin" />
      <span>正在训练</span>
      <a-tag v-if="runningJobs.length > 0" size="small" color="blue">{{ runningJobs.length }}</a-tag>
    </div>

    <div v-if="runningJobs.length === 0" class="empty-hint">暂无进行中的训练任务</div>
    <div v-else class="training-grid">
      <div v-for="job in runningJobs" :key="job.id" class="training-card">
        <div class="training-header">
          <span class="training-name">{{ job.name }}</span>
          <a-tag color="blue" size="small">训练中</a-tag>
        </div>

        <!-- 进度信息 -->
        <div v-if="job.progress_info && (job.progress_info.epoch || job.progress_info.loss)" class="progress-section">
          <div class="progress-info">
            <span v-if="job.progress_info.epoch !== undefined">Epoch {{ job.progress_info.epoch }}</span>
            <span v-if="job.progress_info.loss !== undefined">Loss: {{ job.progress_info.loss.toFixed(4) }}</span>
            <span v-if="job.progress_info.step !== undefined">Step {{ job.progress_info.step }}</span>
          </div>
        </div>

        <!-- 当前步骤 -->
        <div v-if="job.orchestrator_step && job.orchestrator_step !== 'idle'" class="step-badge">
          <a-tag color="cyan" size="small">{{ stepLabel(job.orchestrator_step) }}</a-tag>
        </div>

        <div class="training-footer">
          <a-button type="text" size="mini" @click="viewSteps(job)">步骤</a-button>
          <a-button type="text" size="mini" @click="viewLogs(job)">日志</a-button>
          <a-button type="text" size="mini" status="danger" @click="stopJob(job)">停止</a-button>
        </div>
      </div>
    </div>

    <!-- 任务列表 -->
    <div class="section-header">
      <icon-list class="section-icon" />
      <span>全部任务</span>
    </div>

    <a-table
      :data="allJobs"
      :columns="jobColumns"
      row-key="id"
      :bordered="false"
      :pagination="pagination"
      class="task-table"
      @page-change="onPageChange"
    >
      <template #name="{ record }">
        <span class="job-name">{{ record.name }}</span>
      </template>
      <template #status="{ record }">
        <a-tag :color="jobStatusColor(record.status)">{{ jobStatusLabel(record.status) }}</a-tag>
      </template>
      <template #step="{ record }">
        <a-tag v-if="record.orchestrator_step && record.orchestrator_step !== 'idle'" color="cyan" size="small">
          {{ stepLabel(record.orchestrator_step) }}
        </a-tag>
        <span v-else class="text-muted">-</span>
      </template>
      <template #progress="{ record }">
        <span v-if="record.progress_info && record.progress_info.epoch" class="progress-text">
          Epoch {{ record.progress_info.epoch }}
        </span>
        <span v-else class="text-muted">-</span>
      </template>
      <template #created_at="{ record }">
        <span class="time-text">{{ formatTime(record.created_at) }}</span>
      </template>
      <template #actions="{ record }">
        <a-space size="small">
          <a-button v-if="record.status === 'pending' && !record.orchestrator_step" type="text" size="mini" @click="launchJob(record)">启动</a-button>
          <a-button v-if="record.status === 'pending' && record.orchestrator_step" type="text" size="mini" @click="startJob(record)">手动启动</a-button>
          <a-button v-if="record.status === 'running'" type="text" size="mini" status="danger" @click="stopJob(record)">停止</a-button>
          <a-button type="text" size="mini" @click="viewSteps(record)">步骤</a-button>
          <a-button type="text" size="mini" @click="viewLogs(record)">日志</a-button>
          <a-button type="text" size="mini" status="danger" @click="deleteJob(record)">删除</a-button>
        </a-space>
      </template>
    </a-table>

    <!-- 日志面板 -->
    <a-drawer v-model:visible="logDrawerVisible" title="训练日志" width="720">
      <div v-if="logContent" class="log-panel">
        <div class="log-content">
          <pre v-for="(line, i) in logLines" :key="i" class="log-line">{{ line }}</pre>
        </div>
      </div>
    </a-drawer>

    <!-- 步骤时间线 -->
    <a-drawer v-model:visible="stepsDrawerVisible" title="编排步骤" width="640">
      <a-timeline v-if="steps.length > 0" class="steps-timeline">
        <a-timeline-item
          v-for="step in steps"
          :key="step.step_name"
          :color="stepStatusColor(step.status)"
        >
          <div class="step-item">
            <span class="step-name">{{ stepLabel(step.step_name) }}</span>
            <a-tag :color="stepStatusColor(step.status)" size="small">{{ step.status }}</a-tag>
            <div v-if="step.error_message" class="step-error">{{ step.error_message }}</div>
            <div v-if="step.started_at" class="step-time">
              {{ new Date(step.started_at).toLocaleString('zh-CN') }}
              <span v-if="step.retry_count > 0"> · 重试 {{ step.retry_count }} 次</span>
            </div>
          </div>
        </a-timeline-item>
      </a-timeline>
      <div v-else class="empty-steps">暂无步骤记录</div>
    </a-drawer>

    <!-- 新建训练弹窗 -->
    <a-modal v-model:visible="showCreateModal" title="新建训练任务" @ok="createJob" :mask-closable="false" width="680">
      <a-form :model="newJob" layout="vertical">
        <a-form-item label="任务名称" field="name" :rules="[{ required: true, message: '请输入任务名称' }]">
          <a-input v-model="newJob.name" placeholder="例如：文章分类微调" />
        </a-form-item>

        <a-divider style="margin: 12px 0">仓库配置</a-divider>

        <a-form-item label="Git 仓库 URL" field="repoUrl" :rules="[{ required: true, message: '请输入仓库 URL' }]">
          <a-input v-model="newJob.repoUrl" placeholder="https://github.com/user/repo.git" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="分支">
              <a-input v-model="newJob.repoBranch" placeholder="main" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="训练脚本">
              <a-input v-model="newJob.trainingScript" placeholder="train.py" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="Git Token（私有仓库必填）">
          <a-input v-model="newJob.repoToken" placeholder="ghp_xxxx（可选）" />
        </a-form-item>

        <a-divider style="margin: 12px 0">资源选择</a-divider>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="Provider">
              <a-select v-model="newJob.provider">
                <a-option value="mock">Mock（开发）</a-option>
                <a-option value="zhixingyun">智星云</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="GPU 类型">
              <a-select v-model="newJob.gpuType">
                <a-option value="RTX4090">RTX 4090</a-option>
                <a-option value="A100">A100</a-option>
                <a-option value="H100">H100</a-option>
                <a-option value="V100">V100</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="数据集配置">
          <a-select v-model="newJob.datasetId" placeholder="选择数据集（可选）">
            <a-option v-for="dataset in datasets" :key="dataset.id" :value="dataset.id">
              {{ dataset.name }} ({{ formatBytes(dataset.size_bytes) }})
            </a-option>
          </a-select>
        </a-form-item>

        <a-form-item label="模型配置" field="config">
          <a-textarea
            v-model="newJob.configText"
            placeholder='{"epochs": 10, "learning_rate": 2e-5}'
            :auto-size="{ minRows: 3, maxRows: 6 }"
          />
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
  IconPlus, IconSync, IconRefresh, IconList,
} from '@arco-design/web-vue/es/icon'

const { authHeaders } = useAuth()
const refreshing = ref(false)
const showCreateModal = ref(false)
const logDrawerVisible = ref(false)
const stepsDrawerVisible = ref(false)
const logContent = ref('')
const steps = ref([])
const allJobs = ref([])
const datasets = ref([])
const stats = ref({ total: 0, byStatus: {} })
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const pagination = { showTotal: true, pageSize: 20 }

const runningJobs = computed(() => allJobs.value.filter(j => j.status === 'running'))

const JOB_STATUS = {
  running: { label: '训练中', color: 'blue' },
  pending: { label: '等待中', color: 'orange' },
  completed: { label: '完成', color: 'green' },
  failed: { label: '失败', color: 'red' },
  stopped: { label: '已停止', color: 'gray' },
  cancelled: { label: '已取消', color: 'gray' },
}

const STEP_LABELS = {
  idle: '未开始',
  creating_instance: '创建实例',
  waiting_instance: '等待实例',
  connecting_ssh: 'SSH 连接',
  setting_up_env: '环境配置',
  cloning_repo: '拉取代码',
  installing_deps: '安装依赖',
  fetching_dataset: '拉取数据集',
  starting_training: '启动训练',
  monitoring_training: '训练中',
  collecting_artifacts: '回收产物',
  shutting_down: '关停实例',
  completed: '完成',
  failed: '失败',
}

function jobStatusColor(status) { return JOB_STATUS[status]?.color ?? 'gray' }
function jobStatusLabel(status) { return JOB_STATUS[status]?.label ?? status }
function stepLabel(step) { return STEP_LABELS[step] ?? step }

function stepStatusColor(status) {
  const map = { completed: 'green', running: 'blue', failed: 'red', pending: 'gray', skipped: 'gray' }
  return map[status] ?? 'gray'
}

const logLines = computed(() => logContent.value ? logContent.value.split('\n') : [])

const jobColumns = [
  { title: '名称', slotName: 'name', width: 200 },
  { title: '状态', slotName: 'status', width: 90 },
  { title: '当前步骤', slotName: 'step', width: 140 },
  { title: '进度', slotName: 'progress', width: 100 },
  { title: '创建时间', slotName: 'created_at', width: 180 },
  { title: '操作', slotName: 'actions', width: 320, fixed: 'right' },
]

const newJob = ref({
  name: '',
  repoUrl: '',
  repoBranch: 'main',
  repoToken: '',
  trainingScript: 'train.py',
  provider: 'mock',
  gpuType: 'RTX4090',
  datasetId: undefined,
  configText: '{"epochs": 10}',
})

// 工具函数：格式化时间
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

// 工具函数：格式化字节大小
function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`
}

// 获取数据集列表（用于新建任务时选择）
async function fetchDatasets() {
  try {
    const res = await fetch('/api/cloud/datasets?page_size=100', { headers: authHeaders() })
    const data = await res.json()
    if (data.code === 'ok') {
      datasets.value = data.data.items || []
    }
  } catch (e) {
    console.error('获取数据集失败', e)
  }
}

async function fetchJobs() {
  refreshing.value = true
  try {
    const [jobsRes] = await Promise.all([
      fetch(`/api/cloud/jobs?page=${page.value}&page_size=${pageSize.value}`, { headers: authHeaders() }),
    ])
    const jobsData = await jobsRes.json()
    if (jobsData.code === 'ok') {
      allJobs.value = jobsData.data.items || []
      total.value = jobsData.data.total || 0
      pagination.total = total.value

      // 统计状态
      const byStatus = {}
      allJobs.value.forEach(job => {
        byStatus[job.status] = (byStatus[job.status] || 0) + 1
      })
      stats.value = {
        total: total.value,
        byStatus,
      }
    }
  } catch {
    Message.error('加载任务失败')
  } finally {
    refreshing.value = false
  }
}

function onPageChange(p) {
  page.value = p
  fetchJobs()
}

async function createJob() {
  if (!newJob.value.name?.trim()) { Message.warning('请填写任务名称'); return }
  if (!newJob.value.repoUrl?.trim()) { Message.warning('请填写 Git 仓库 URL'); return }
  let config = {}
  try {
    config = JSON.parse(newJob.value.configText || '{}')
  } catch {
    Message.warning('模型配置 JSON 格式错误')
    return
  }

  // 如果选择了数据集，添加到配置中
  if (newJob.value.datasetId) {
    config.dataset_id = newJob.value.datasetId
  }

  try {
    const res = await fetch('/api/cloud/jobs', {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        name: newJob.value.name,
        config,
        repo_url: newJob.value.repoUrl,
        repo_branch: newJob.value.repoBranch,
        repo_token: newJob.value.repoToken || undefined,
        training_script: newJob.value.trainingScript,
        provider: newJob.value.provider,
        gpu_type: newJob.value.gpuType,
      }),
    })
    const result = await res.json()
    if (result.code === 'ok') {
      Message.success('训练任务创建成功')
      showCreateModal.value = false
      newJob.value = { name: '', repoUrl: '', repoBranch: 'main', repoToken: '', trainingScript: 'train.py', provider: 'mock', gpuType: 'RTX4090', datasetId: undefined, configText: '{"epochs": 10}' }
      await fetchJobs()
    } else {
      Message.error(result.message || '创建失败')
    }
  } catch {
    Message.error('网络错误')
  }
}

async function launchJob(job) {
  try {
    const res = await fetch(`/api/cloud/jobs/${job.id}/launch`, { method: 'POST', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') { Message.success('已提交编排任务，自动执行中...'); await fetchJobs() }
    else Message.error(result.message)
  } catch { Message.error('网络错误') }
}

async function startJob(job) {
  try {
    const res = await fetch(`/api/cloud/jobs/${job.id}/start`, { method: 'POST', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') { Message.success('启动成功'); await fetchJobs() }
    else Message.error(result.message)
  } catch { Message.error('网络错误') }
}

async function stopJob(job) {
  try {
    const res = await fetch(`/api/cloud/jobs/${job.id}/stop`, { method: 'POST', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') { Message.success('已停止'); await fetchJobs() }
    else Message.error(result.message)
  } catch { Message.error('网络错误') }
}

async function deleteJob(job) {
  try {
    const res = await fetch(`/api/cloud/jobs/${job.id}`, { method: 'DELETE', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') { Message.success('已删除'); await fetchJobs() }
    else Message.error(result.message)
  } catch { Message.error('网络错误') }
}

async function viewLogs(job) {
  try {
    const res = await fetch(`/api/cloud/jobs/${job.id}/logs?lines=500`, { headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') {
      logContent.value = result.data?.content || result.data?.logs || '暂无日志'
      logDrawerVisible.value = true
    } else {
      Message.error(result.message || '获取日志失败')
    }
  } catch {
    Message.error('网络错误')
  }
}

async function viewSteps(job) {
  try {
    const res = await fetch(`/api/cloud/jobs/${job.id}/steps`, { headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') {
      steps.value = result.data || []
      stepsDrawerVisible.value = true
    } else {
      Message.error(result.message || '获取步骤失败')
    }
  } catch {
    Message.error('网络错误')
  }
}

onMounted(() => {
  fetchJobs()
  fetchDatasets()
})
</script>

<style scoped>
.cloud-tasks {
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

.status-card.s-success .status-num { color: #00b42a; }
.status-card.s-running .status-num { color: #165dff; }
.status-card.s-fail .status-num { color: #f53f3f; }

.status-label {
  font-size: 13px;
  color: #86909c;
}

/* 区块标题 */
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 16px;
}

.section-icon {
  width: 18px;
  height: 18px;
  color: #86909c;
}

.spin {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-hint {
  text-align: center;
  padding: 48px;
  color: #86909c;
  background: rgba(255, 255, 255, 0.4);
  border: 1px dashed #e5e6eb;
  border-radius: 12px;
}

/* 训练中卡片网格 */
.training-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 16px;
}

.training-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
  transition: all 0.2s ease;
}

.training-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.training-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.training-name {
  font-size: 16px;
  font-weight: 600;
  flex: 1;
  color: #1d2129;
}

.progress-section {
  margin-bottom: 12px;
}

.progress-info {
  font-size: 13px;
  color: #4e5969;
  display: flex;
  gap: 16px;
}

.step-badge {
  margin-bottom: 12px;
}

.training-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  border-top: 1px solid #e5e6eb;
  padding-top: 12px;
  margin-top: 8px;
}

/* 任务表格 */
.task-table {
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.7);
}

.job-name {
  font-weight: 500;
  color: #1d2129;
}

.text-muted {
  color: #86909c;
}

.progress-text {
  font-size: 13px;
  color: #4e5969;
}

.time-text {
  font-size: 13px;
  color: #4e5969;
}

/* 日志面板 */
.log-panel {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
}

.log-content {
  flex: 1;
  overflow-y: auto;
  background: #1f2328;
  border-radius: 8px;
  padding: 16px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.6;
}

.log-line {
  margin: 0;
  color: #c9d1d9;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-line:nth-child(odd) {
  color: #8b949e;
}

/* 步骤时间线 */
.steps-timeline {
  padding: 0 8px;
}

.step-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.step-name {
  font-weight: 500;
  font-size: 14px;
  color: #1d2129;
}

.step-error {
  color: #f53f3f;
  font-size: 12px;
}

.step-time {
  color: #86909c;
  font-size: 12px;
}

.empty-steps {
  text-align: center;
  padding: 48px;
  color: #86909c;
}
</style>
