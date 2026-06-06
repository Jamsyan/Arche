<template>
  <div class="users-dashboard">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <p class="page-desc">用户数据总览与全量管理</p>
      <div class="page-actions">
        <NInput
          v-model:value="searchQ"
          placeholder="搜索用户名/邮箱..."
          clearable
          size="small"
          style="width: 200px"
          @keyup.enter="loadUsers(1)"
        />
        <ArButton size="sm" @click="showCreateModal = true">+ 创建用户</ArButton>
        <ArButton size="sm" @click="loadUsers()">刷新</ArButton>
      </div>
    </div>

    <!-- 指标卡片 -->
    <div class="metric-grid">
      <div class="metric-card">
        <span class="metric-value">{{ stats.total_users ?? '--' }}</span>
        <span class="metric-label">注册用户</span>
      </div>
      <div class="metric-card">
        <span class="metric-value">{{ stats.active_users ?? '--' }}</span>
        <span class="metric-label">活跃用户</span>
      </div>
      <div class="metric-card">
        <span class="metric-value">{{ stats.today_new ?? '--' }}</span>
        <span class="metric-label">今日新增</span>
      </div>
      <div class="metric-card">
        <span class="metric-value">{{ stats.disabled_users ?? '--' }}</span>
        <span class="metric-label">已禁用</span>
      </div>
    </div>

    <!-- 图表行 -->
    <div class="charts-row">
      <div class="chart-card">
        <h2 class="card-title">用户增长趋势</h2>
        <div class="chart-body">
          <svg viewBox="0 0 600 200" class="trend-chart">
            <line
              v-for="i in 5"
              :key="'g' + i"
              x1="45"
              :y1="gridY(i)"
              x2="580"
              :y2="gridY(i)"
              stroke="var(--border-color)"
              stroke-width="0.5"
            />
            <text
              v-for="(label, i) in yLabels"
              :key="'yl' + i"
              x="40"
              :y="gridY(i) + 4"
              text-anchor="end"
              class="chart-label"
            >
              {{ label }}
            </text>
            <path
              v-if="bezierPath"
              :d="bezierPath"
              fill="none"
              stroke="var(--primary-color)"
              stroke-width="2.5"
              stroke-linejoin="round"
              stroke-linecap="round"
            />
            <path v-if="fillPath" :d="fillPath" fill="url(#userGrad)" opacity="0.15" />
            <defs>
              <linearGradient id="userGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="var(--primary-color)" />
                <stop offset="100%" stop-color="var(--primary-color)" stop-opacity="0" />
              </linearGradient>
            </defs>
            <text
              v-for="(label, i) in xLabels"
              :key="'xl' + i"
              :x="xPositions[i]"
              y="194"
              text-anchor="middle"
              class="chart-label"
            >
              {{ label }}
            </text>
          </svg>
        </div>
      </div>
      <div class="chart-card">
        <h2 class="card-title">用户等级分布</h2>
        <div v-if="levelBars.length > 0" class="level-list">
          <div v-for="l in levelBars" :key="l.level" class="level-row">
            <span class="level-label">P{{ l.level }}</span>
            <div class="level-bar-track">
              <div class="level-bar-fill" :style="{ width: l.pct + '%', background: l.color }" />
            </div>
            <span class="level-count">{{ l.count }}</span>
          </div>
        </div>
        <div v-else class="empty-hint">暂无数据</div>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="table-section">
      <div class="table-header">
        <span class="table-title">全部用户（{{ total }}）</span>
      </div>
      <ArTable
        :columns="columns"
        :data="users"
        :loading="loading"
        :pagination="{ page, pageSize: pageSize as unknown as number, itemCount: total }"
        @update:page="handlePageChange"
        @update:page-size="
          (v: number) => {
            pageSize = v as unknown as number
            loadUsers(1)
          }
        "
      />
    </div>

    <!-- 创建用户弹窗 -->
    <NModal v-model:show="showCreateModal" title="创建用户" preset="card" style="width: 420px">
      <NForm ref="createFormRef" :model="createForm" label-placement="top">
        <NFormItem
          label="用户名"
          path="username"
          :rule="[{ required: true, message: '请输入用户名' }]"
        >
          <NInput v-model:value="createForm.username" placeholder="用户名" />
        </NFormItem>
        <NFormItem label="邮箱" path="email" :rule="[{ required: true, message: '请输入邮箱' }]">
          <NInput v-model:value="createForm.email" placeholder="邮箱" />
        </NFormItem>
        <NFormItem label="密码" path="password" :rule="[{ required: true, message: '请输入密码' }]">
          <NInput v-model:value="createForm.password" type="password" placeholder="密码" />
        </NFormItem>
        <NFormItem label="等级">
          <NSelect v-model:value="createForm.level" :options="levelOptions" />
        </NFormItem>
      </NForm>
      <template #footer>
        <div style="display: flex; gap: 8px; justify-content: flex-end">
          <ArButton @click="showCreateModal = false">取消</ArButton>
          <ArButton type="primary" @click="handleCreateUser">创建</ArButton>
        </div>
      </template>
    </NModal>
  </div>
</template>

<script setup lang="ts">
import { ref, h, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { NInput, NModal, NForm, NFormItem, NSelect, NPopconfirm } from 'naive-ui'
import { ArButton, ArTag, ArTable } from '@/components/ui'
import { getUserStatsApi, type UserStats } from '@/services/api/auth'
import {
  getUsersApi,
  disableUserApi,
  enableUserApi,
  createAdminUserApi,
  type AdminUser,
  type Paginated
} from '@/services/api'

const message = useMessage()

// ── 统计 ──
const stats = ref<UserStats>({
  total_users: 0,
  active_users: 0,
  disabled_users: 0,
  today_new: 0,
  by_level: {},
  daily_trend: []
})

async function fetchStats() {
  try {
    stats.value = await getUserStatsApi()
  } catch {
    /* silent */
  }
}

// ── 用户列表 ──
const searchQ = ref('')
const users = ref<AdminUser[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
let pageSize = ref(10)

const columns: DataTableColumns<AdminUser> = [
  {
    title: '用户',
    key: 'username',
    ellipsis: true,
    render: (row) =>
      h('div', { class: 'user-cell' }, [
        h(
          'div',
          { class: 'user-cell-avatar' },
          (row.nickname || row.username).charAt(0).toUpperCase()
        ),
        h('div', { class: 'user-cell-info' }, [
          h('div', { class: 'user-cell-name' }, row.nickname || row.username),
          h('div', { class: 'user-cell-email' }, row.email || '-')
        ])
      ])
  },
  {
    title: '等级',
    key: 'level',
    width: 100,
    render: (row) => {
      const lv = row.level ?? 5
      const color = lv === 0 ? 'red' : lv <= 2 ? 'primary' : 'default'
      return h(ArTag, { color, size: 'sm' }, { default: () => `P${lv}` })
    }
  },
  {
    title: '状态',
    key: 'is_active',
    width: 80,
    render: (row) => {
      const active = row.is_active !== false
      return h(
        ArTag,
        { color: active ? 'green' : 'red', size: 'sm' },
        { default: () => (active ? '活跃' : '禁用') }
      )
    }
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 100,
    render: (row) => (row.created_at ? row.created_at.slice(0, 10) : '-')
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    render: (row) => {
      const isActive = row.is_active !== false
      return h('div', { class: 'action-cell' }, [
        h(
          ArButton,
          { size: 'sm', onClick: () => message.info('等级编辑功能待实现') },
          { default: () => '等级' }
        ),
        h(
          NPopconfirm,
          {
            title: '确认操作',
            content: `确定${isActive ? '禁用' : '启用'}用户「${row.username}」吗？`,
            positiveText: '确认',
            negativeText: '取消',
            onPositiveClick: () => toggleUserStatus(row)
          },
          {
            trigger: () =>
              h(
                ArButton,
                { size: 'sm', type: isActive ? 'ghost' : 'primary' },
                { default: () => (isActive ? '禁用' : '启用') }
              )
          }
        )
      ])
    }
  }
]

async function loadUsers(resetPage?: number) {
  if (resetPage !== undefined) page.value = resetPage
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, page_size: pageSize.value }
    if (searchQ.value) params.q = searchQ.value
    const res = await getUsersApi(params as any)
    const paginated = res as unknown as Paginated<AdminUser>
    users.value = (paginated.list || paginated.items || []).map((u) => ({ ...u, key: u.id }))
    total.value = paginated.total || 0
  } catch {
    message.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

async function toggleUserStatus(row: AdminUser) {
  try {
    if (row.is_active !== false) {
      await disableUserApi(row.id)
      row.is_active = false
      message.success('用户已禁用')
    } else {
      await enableUserApi(row.id)
      row.is_active = true
      message.success('用户已启用')
    }
  } catch {
    message.error('操作失败')
  }
}

function handlePageChange(p: number) {
  page.value = p
  loadUsers()
}

// ── 创建用户 ──
const showCreateModal = ref(false)
const createForm = ref({ username: '', email: '', password: '', level: 5 })
const levelOptions = [
  { label: 'P0 - 管理员', value: 0 },
  { label: 'P1 - 高级', value: 1 },
  { label: 'P2', value: 2 },
  { label: 'P3', value: 3 },
  { label: 'P4', value: 4 },
  { label: 'P5 - 普通用户', value: 5 }
]

async function handleCreateUser() {
  if (!createForm.value.username || !createForm.value.email || !createForm.value.password) {
    message.warning('请填写完整信息')
    return
  }
  try {
    await createAdminUserApi({
      username: createForm.value.username,
      email: createForm.value.email,
      password: createForm.value.password,
      level: createForm.value.level
    })
    message.success('创建成功')
    showCreateModal.value = false
    createForm.value = { username: '', email: '', password: '', level: 5 }
    loadUsers(1)
    fetchStats()
  } catch {
    message.error('创建失败')
  }
}

// ── 增长趋势图表 ──
const yLabels = ['100%', '80%', '60%', '40%', '20%', '0%']
const padding = { top: 8, bottom: 25, left: 45, right: 10 }
const chartW = 600
const chartH = 200
const chartAreaH = chartH - padding.top - padding.bottom

const chartData = computed(() => {
  const trend = stats.value.daily_trend ?? []
  return trend.length === 0 ? [0] : trend.map((t) => t.count)
})
const normalizedData = computed(() => {
  const max = Math.max(...chartData.value, 1)
  return chartData.value.map((v) => v / max)
})
const gridY = (i: number) => padding.top + (chartAreaH / 5) * i
const chartPoints = computed(() =>
  normalizedData.value.map((ratio, i) => ({
    x:
      padding.left +
      (i / Math.max(normalizedData.value.length - 1, 1)) * (chartW - padding.left - padding.right),
    y: padding.top + chartAreaH * (1 - ratio)
  }))
)
const xPositions = computed(() => chartPoints.value.map((p) => p.x))
const xLabels = computed(() => {
  const trend = stats.value.daily_trend ?? []
  return trend.length === 0
    ? []
    : trend.map((_, i) => {
        const day = i + 1
        return day % 5 === 1 || day === 1 || day === trend.length ? `${day}日` : ''
      })
})

function bezierSmooth(points: { x: number; y: number }[]): string {
  if (points.length === 0) return ''
  if (points.length === 1) return `M ${points[0].x} ${points[0].y}`
  const tension = points.length > 10 ? 2 : 3
  let d = `M ${points[0].x} ${points[0].y}`
  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[i]
    const p1 = points[i + 1]
    const segLen = (p1.x - p0.x) / tension
    d += ` C ${p0.x + segLen} ${p0.y}, ${p1.x - segLen} ${p1.y}, ${p1.x} ${p1.y}`
  }
  return d
}

const bezierPath = computed(() => bezierSmooth(chartPoints.value))
const fillPath = computed(() => {
  if (!bezierPath.value || chartPoints.value.length === 0) return ''
  const last = chartPoints.value[chartPoints.value.length - 1]
  const first = chartPoints.value[0]
  return `${bezierPath.value} L ${last.x} ${chartH - padding.bottom} L ${first.x} ${chartH - padding.bottom} Z`
})

// ── 等级分布 ──
const levelColors = ['#9a5a2f', '#4f7a57', '#1890ff', '#722ed1', '#b98529', '#d97706']
const levelBars = computed(() => {
  const byLevel = stats.value.by_level ?? {}
  const entries = Object.entries(byLevel).map(([level, count]) => ({ level: Number(level), count }))
  entries.sort((a, b) => a.level - b.level)
  const maxCount = Math.max(...entries.map((e) => e.count), 1)
  return entries.map((e, i) => ({
    ...e,
    pct: (e.count / maxCount) * 100,
    color: levelColors[i % levelColors.length]
  }))
})

onMounted(() => {
  fetchStats()
  loadUsers()
})
</script>

<style scoped>
.users-dashboard {
  max-width: 100%;
}

.page-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}
.page-desc {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0;
  width: 100%;
}
.page-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}
.metric-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 20px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}
.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}
.metric-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}
.chart-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px;
}
.chart-body {
  width: 100%;
}
.trend-chart {
  width: 100%;
  height: auto;
  display: block;
}
.chart-label {
  font-size: 10px;
  fill: var(--text-tertiary);
  font-family: inherit;
}

.level-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.level-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.level-label {
  width: 28px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  flex-shrink: 0;
}
.level-bar-track {
  flex: 1;
  height: 8px;
  background: var(--bg-color);
  border-radius: 4px;
  overflow: hidden;
}
.level-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}
.level-count {
  width: 28px;
  font-size: 12px;
  color: var(--text-secondary);
  text-align: right;
  flex-shrink: 0;
}
.empty-hint {
  text-align: center;
  color: var(--text-tertiary);
  font-size: 13px;
  padding: 40px 0;
}

/* ── 用户列表 ── */
.table-section {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}
.table-header {
  padding: 14px 16px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}
.table-footer {
  display: flex;
  justify-content: center;
  padding: 12px 16px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-cell-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--primary-light-color);
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}
.user-cell-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.user-cell-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}
.user-cell-email {
  font-size: 11px;
  color: var(--text-tertiary);
}

.action-cell {
  display: flex;
  gap: 6px;
  align-items: center;
}

@media (max-width: 768px) {
  .metric-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
