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
        <a-button type="text" size="small" @click="refresh" :loading="refreshing">
          <template #icon><icon-refresh /></template>
        </a-button>
        <a-button
          :type="status.running ? 'primary' : 'outline'"
          :status="status.running ? 'danger' : 'success'"
          size="small"
          @click="toggleCrawler"
        >
          {{ status.running ? '停止' : '启动' }}
        </a-button>
      </a-space>
    </div>

    <!-- 统计概览 -->
    <div class="status-row">
      <div class="status-card">
        <div class="status-num">{{ stats.totalCrawled }}</div>
        <div class="status-label">总抓取</div>
      </div>
      <div class="status-card s-running">
        <div class="status-num">{{ status.activeTasks }}</div>
        <div class="status-label">运行中</div>
      </div>
      <div class="status-card s-info">
        <div class="status-num">{{ status.queueSize }}</div>
        <div class="status-label">队列长度</div>
      </div>
      <div class="status-card s-info">
        <div class="status-num">{{ status.seedsCount }}</div>
        <div class="status-label">种子数</div>
      </div>
      <div class="status-card s-fail">
        <div class="status-num">{{ status.pagesRejected }}</div>
        <div class="status-label">拒绝数</div>
      </div>
    </div>

    <!-- 运行状态 -->
    <div class="section-header">
      <icon-sync class="section-icon" :class="{ spin: status.running }" />
      <span>运行状态</span>
      <a-tag :color="status.running ? 'green' : 'gray'" size="small">
        {{ status.running ? '运行中' : '已停止' }}
      </a-tag>
      <span v-if="status.running" class="uptime">已运行: {{ formatUptime(status.uptimeSeconds) }}</span>
    </div>

    <!-- 最近抓取记录 -->
    <div class="section-header">
      <icon-list class="section-icon" />
      <span>最近抓取</span>
    </div>

    <a-table
      :data="records"
      :columns="recordColumns"
      row-key="id"
      :bordered="false"
      :pagination="pagination"
      class="task-table"
      @page-change="onPageChange"
    >
      <template #url="{ record }">
        <span class="url-cell" :title="record.url">{{ truncate(record.url, 60) }}</span>
      </template>
      <template #title="{ record }">
        <span class="title-cell">{{ record.title || '-' }}</span>
      </template>
      <template #content_type="{ record }">
        <a-tag v-if="record.content_type" :color="contentTypeColor(record.content_type)" size="small">
          {{ record.content_type }}
        </a-tag>
        <span v-else>-</span>
      </template>
      <template #crawled_at="{ record }">
        {{ record.crawled_at ? new Date(record.crawled_at).toLocaleString('zh-CN') : '-' }}
      </template>
    </a-table>

    <!-- 手动添加种子 -->
    <div class="section-header">
      <icon-plus class="section-icon" />
      <span>手动添加种子</span>
    </div>

    <div class="add-seed-form">
      <a-input
        v-model="newSeedUrl"
        placeholder="输入 URL 后按回车添加"
        @press-enter="addSeed"
        size="small"
        style="flex: 1; max-width: 500px;"
      />
      <a-button type="primary" size="small" @click="addSeed" :disabled="!newSeedUrl">
        添加
      </a-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useAuth } from '../../router/auth.js'
import {
  IconBug, IconRefresh, IconArrowLeft, IconSync, IconList, IconPlus,
} from '@arco-design/web-vue/es/icon'

const { authHeaders } = useAuth()
const refreshing = ref(false)
const records = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const pagination = { showTotal: true, pageSize: 20 }

const status = ref({
  running: false,
  uptimeSeconds: 0,
  activeTasks: 0,
  queueSize: 0,
  seedsCount: 0,
  pagesCrawled: 0,
  pagesRejected: 0,
  domainsActive: {},
})

const stats = ref({ totalCrawled: 0, byType: {}, byDomain: {} })
const newSeedUrl = ref('')

const CONTENT_TYPE_COLORS = {
  article: 'blue',
  post: 'green',
  product: 'orange',
  nav: 'gray',
  ad: 'red',
  functional: 'red',
  other: 'gray',
}

function contentTypeColor(type) {
  return CONTENT_TYPE_COLORS[type] || 'gray'
}

function truncate(str, len) {
  if (!str) return ''
  return str.length > len ? str.slice(0, len) + '...' : str
}

function formatUptime(seconds) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return `${h}h ${m}m`
}

const recordColumns = [
  { title: 'URL', slotName: 'url', ellipsis: true, tooltip: true, width: 300 },
  { title: '标题', slotName: 'title', ellipsis: true, tooltip: true, width: 200 },
  { title: '类型', slotName: 'content_type', width: 80 },
  { title: '状态码', dataIndex: 'status_code', width: 70 },
  { title: '抓取时间', slotName: 'crawled_at', width: 160 },
]

async function refresh() {
  refreshing.value = true
  try {
    const [statusRes, statsRes, recordsRes] = await Promise.all([
      fetch('/api/crawler/status', { headers: authHeaders() }),
      fetch('/api/crawler/stats', { headers: authHeaders() }),
      fetch(`/api/crawler/records?page=${page.value}&page_size=${pageSize.value}`, { headers: authHeaders() }),
    ])
    const sData = await statusRes.json()
    if (sData.code === 'ok') status.value = { ...status.value, ...sData.data }

    const stData = await statsRes.json()
    if (stData.code === 'ok') stats.value = stData.data

    const rData = await recordsRes.json()
    if (rData.code === 'ok') {
      records.value = rData.data.items || []
      total.value = rData.data.total || 0
      pagination.total = total.value
    }
  } catch {
    Message.error('加载数据失败')
  } finally {
    refreshing.value = false
  }
}

function onPageChange(p) {
  page.value = p
  refresh()
}

async function toggleCrawler() {
  const endpoint = status.value.running ? '/api/crawler/stop' : '/api/crawler/start'
  try {
    const res = await fetch(endpoint, { method: 'POST', headers: authHeaders() })
    const data = await res.json()
    if (data.code === 'ok') {
      Message.success(data.message)
      await refresh()
    } else {
      Message.error(data.message || '操作失败')
    }
  } catch {
    Message.error('网络错误')
  }
}

async function addSeed() {
  if (!newSeedUrl.value?.trim()) return
  try {
    const res = await fetch('/api/crawler/seeds', {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ url: newSeedUrl.value.trim() }),
    })
    const data = await res.json()
    if (data.code === 'ok') {
      Message.success('种子已添加')
      newSeedUrl.value = ''
      await refresh()
    } else {
      Message.warning(data.message || '添加失败')
    }
  } catch {
    Message.error('网络错误')
  }
}

onMounted(() => { refresh() })
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
.uptime { font-size: 12px; color: var(--color-text-4); margin-left: auto; }

.task-table { border-radius: var(--border-radius-large); overflow: hidden; }
.url-cell { font-size: 12px; color: var(--color-text-3); font-family: monospace; }
.title-cell { font-size: 13px; color: var(--color-text-2); }

.add-seed-form { display: flex; gap: 8px; align-items: center; }
</style>
