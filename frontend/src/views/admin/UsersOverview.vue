<template>
  <div class="users-dashboard">
    <div class="page-header">
      <div class="page-header-row">
        <div class="page-header-left">
          <h1 class="page-title">用户管理</h1>
          <p class="page-desc">用户数据总览与全量管理</p>
        </div>
        <div class="page-header-tools">
          <button class="refresh-btn" title="刷新数据" @click="loadUsers()">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polyline points="23 4 23 10 17 10" />
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
            </svg>
          </button>
          <ArButton size="sm" @click="showCreateModal = true">+ 创建用户</ArButton>
        </div>
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
      <ArTable
        :columns="columns"
        :data="users"
        :loading="loading"
        :pagination="{ page, pageSize, itemCount: total }"
        @update:page="handlePageChange"
        @update:page-size="
          (v: number) => {
            pageSize = v
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

    <!-- 等级编辑弹窗 -->
    <NModal v-model:show="showLevelModal" title="编辑用户等级" preset="card" style="width: 360px">
      <div class="modal-hint">当前编辑：{{ editingUser?.username }}</div>
      <NSelect v-model:value="levelEditValue" :options="levelOptions" />
      <template #footer>
        <div style="display: flex; gap: 8px; justify-content: flex-end">
          <ArButton @click="showLevelModal = false">取消</ArButton>
          <ArButton type="primary" @click="handleLevelChange">确认</ArButton>
        </div>
      </template>
    </NModal>

    <!-- 封禁弹窗 -->
    <NModal v-model:show="showBanModal" title="封禁用户" preset="card" style="width: 400px">
      <div class="modal-hint">选择对「{{ editingUser?.username }}」的封禁方式</div>
      <div class="ban-options">
        <button
          class="ban-option"
          :class="{ 'ban-option--active': banDuration === 'permanent' }"
          @click="banDuration = 'permanent'"
        >
          永久封禁
        </button>
        <button
          class="ban-option"
          :class="{ 'ban-option--active': banDuration === 10 }"
          @click="banDuration = 10"
        >
          封禁 10 小时
        </button>
        <button
          class="ban-option"
          :class="{ 'ban-option--active': banDuration === 24 }"
          @click="banDuration = 24"
        >
          封禁 24 小时
        </button>
        <button
          class="ban-option"
          :class="{ 'ban-option--active': banDuration === 72 }"
          @click="banDuration = 72"
        >
          封禁 72 小时
        </button>
        <div class="ban-custom-row">
          <button
            class="ban-option"
            :class="{ 'ban-option--active': banDuration === 'custom' }"
            @click="banDuration = 'custom'"
          >
            自定义
          </button>
          <NInputNumber v-model:value="customBanHours" :min="1" :max="720" style="width: 100px" />
          <span class="ban-custom-unit">小时</span>
        </div>
      </div>
      <template #footer>
        <div style="display: flex; gap: 8px; justify-content: flex-end">
          <ArButton @click="showBanModal = false">取消</ArButton>
          <ArButton type="primary" @click="handleBanConfirm">确认封禁</ArButton>
        </div>
      </template>
    </NModal>
  </div>
</template>

<script setup lang="ts">
import { ref, h, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { NModal, NForm, NFormItem, NSelect, NPopconfirm, NInputNumber } from 'naive-ui'
import { ArTag, ArTable, ArButton } from '@/components/ui'
import type { ArTableColumn } from '@/components/ui/ArTable.vue'
import { getUserStatsApi, type UserStats } from '@/services/api/auth'
import {
  getUsersApi,
  disableUserApi,
  enableUserApi,
  updateUserApi,
  createAdminUserApi,
  deleteUserApi,
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
const users = ref<AdminUser[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)

// ── 等级编辑弹窗 ──
const showLevelModal = ref(false)
const editingUser = ref<AdminUser | null>(null)
const levelEditValue = ref(5)

// ── 封禁弹窗 ──
const showBanModal = ref(false)
const banDuration = ref<string | number>('permanent')
const customBanHours = ref(24)

const columns: ArTableColumn[] = [
  {
    title: '用户 ID',
    key: 'id',
    width: 110,
    render: (row) =>
      h(
        'span',
        {
          class: 'id-cell',
          title: '点击复制',
          onClick: () => {
            navigator.clipboard.writeText(row.id).catch(() => {})
            message.success('已复制用户 ID')
          }
        },
        row.id.slice(0, 8) + '...'
      )
  },
  {
    title: '用户',
    key: 'username',
    width: 140,
    render: (row) => h('span', { class: 'user-name' }, row.nickname || row.username)
  },
  {
    title: '邮箱',
    key: 'email',
    width: 200,
    ellipsis: true,
    render: (row) => row.email || '-'
  },
  {
    title: '等级',
    key: 'level',
    width: 80,
    render: (row) => {
      const lv = row.level ?? 5
      return h(
        ArTag,
        {
          color: lv === 0 ? 'red' : 'default',
          size: 'sm',
          style: { cursor: 'pointer' },
          onClick: () => openLevelEdit(row)
        },
        { default: () => `P${lv}` }
      )
    }
  },
  {
    title: '状态',
    key: 'is_active',
    width: 100,
    render: (row) => {
      const active = row.is_active !== false
      return h(
        ArTag,
        {
          color: active ? 'green' : 'red',
          size: 'sm',
          style: { cursor: active ? 'pointer' : 'default' },
          onClick: () => handleStatusClick(row)
        },
        { default: () => (active ? '活跃' : '禁用') }
      )
    }
  },
  {
    title: '注册 / 活跃',
    key: 'created_at',
    width: 150,
    render: (row) => {
      const created = row.created_at ? row.created_at.slice(0, 10) : '-'
      const updated = row.updated_at ? row.updated_at.slice(0, 10) : null
      const same = updated === (row.created_at ? row.created_at.slice(0, 10) : null)
      if (!updated || same) {
        return h('span', { class: 'time-cell' }, `注册: ${created}`)
      }
      return h('div', { class: 'time-cell' }, [
        h('div', null, `注册: ${created}`),
        h('div', { style: { color: 'var(--text-tertiary)', fontSize: '11px' } }, `活跃: ${updated}`)
      ])
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 340,
    render: (row) => {
      const isActive = row.is_active !== false
      const btns = [
        { label: '下线', onClick: () => handleForceLogout(row), disabled: !isActive },
        { label: '删号', onClick: () => handleDeleteUser(row), confirm: true },
        { label: '查看资产', onClick: () => handleViewAssets(row) },
        { label: '行为分析', onClick: () => message.info('行为分析页面开发中') },
        { label: '审计日志', onClick: () => message.info('审计日志页面开发中') }
      ]
      return h(
        'div',
        { class: 'action-cell' },
        btns.map((b) => {
          if (b.confirm) {
            return h(
              NPopconfirm,
              {
                title: '确认删除',
                content: `确定永久删除用户「${row.username}」吗？`,
                positiveText: '确认删除',
                negativeText: '取消',
                onPositiveClick: b.onClick
              },
              {
                trigger: () =>
                  h(
                    ArButton,
                    { size: 'sm', type: 'ghost', disabled: b.disabled },
                    { default: () => b.label }
                  )
              }
            )
          }
          return h(
            ArButton,
            { size: 'sm', type: 'ghost', disabled: b.disabled, onClick: b.onClick },
            { default: () => b.label }
          )
        })
      )
    }
  }
]

async function loadUsers(resetPage?: number) {
  if (resetPage !== undefined) page.value = resetPage
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, page_size: pageSize.value }
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

// ── 等级编辑 ──
function openLevelEdit(row: AdminUser) {
  editingUser.value = row
  levelEditValue.value = row.level ?? 5
  showLevelModal.value = true
}

async function handleLevelChange() {
  if (!editingUser.value) return
  try {
    await updateUserApi(editingUser.value.id, { level: levelEditValue.value })
    message.success(`用户「${editingUser.value.username}」等级已更新为 P${levelEditValue.value}`)
    showLevelModal.value = false
    editingUser.value = null
    loadUsers(page.value)
  } catch {
    message.error('等级更新失败')
  }
}

// ── 状态操作（封禁 / 解封）──
function handleStatusClick(row: AdminUser) {
  const active = row.is_active !== false
  if (active) {
    editingUser.value = row
    banDuration.value = 'permanent'
    showBanModal.value = true
  } else {
    handleEnableUser(row)
  }
}

async function handleEnableUser(row: AdminUser) {
  try {
    await enableUserApi(row.id)
    row.is_active = true
    message.success(`用户「${row.username}」已解封`)
    loadUsers(page.value)
  } catch {
    message.error('解封失败')
  }
}

async function handleBanConfirm() {
  if (!editingUser.value) return
  try {
    await disableUserApi(editingUser.value.id)
    editingUser.value.is_active = false
    const duration = banDuration.value
    if (duration === 'permanent') {
      message.success(`用户「${editingUser.value.username}」已永久封禁`)
    } else {
      const hours = duration === 'custom' ? customBanHours.value : (duration as number)
      message.success(
        `用户「${editingUser.value.username}」已封禁 ${hours} 小时（定时解封功能待接入）`
      )
    }
    showBanModal.value = false
    editingUser.value = null
    loadUsers(page.value)
  } catch {
    message.error('封禁失败')
  }
}

// ── 操作栏 ──
function handleForceLogout(row: AdminUser) {
  message.info(`强制下线功能待实现（将使「${row.username}」的 token 立即失效）`)
}

function handleViewAssets(row: AdminUser) {
  message.info(`即将跳转至「${row.username}」的资产详情页面`)
}

async function handleDeleteUser(row: AdminUser) {
  try {
    await deleteUserApi(row.id)
    message.success(`用户「${row.username}」已删除`)
    loadUsers(page.value)
  } catch {
    message.error('删除失败')
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
const padding = { top: 8, bottom: 25, left: 45, right: 10 }
const chartW = 600
const chartH = 200
const chartAreaH = chartH - padding.top - padding.bottom

const chartData = computed(() => {
  const trend = stats.value.daily_trend ?? []
  return trend.length === 0 ? [0] : trend.map((t) => t.count)
})

// Y 轴最大值（以 5 为步长向上取整）
const yMax = computed(() => {
  const max = Math.max(...chartData.value, 1)
  return Math.ceil(max / 5) * 5
})

// Y 轴标签（0 → yMax 等分 5 段，共 6 个标签，从上到下递减）
const yLabels = computed(() => {
  const step = yMax.value / 5
  return [0, 1, 2, 3, 4, 5].map((i) => String(Math.round(step * (5 - i))))
})

const gridY = (i: number) => padding.top + (chartAreaH / 5) * i
const chartPoints = computed(() =>
  chartData.value.map((value, i) => ({
    x:
      padding.left +
      (i / Math.max(chartData.value.length - 1, 1)) * (chartW - padding.left - padding.right),
    y: padding.top + chartAreaH * (1 - value / yMax.value)
  }))
)
const xPositions = computed(() => chartPoints.value.map((p) => p.x))
const xLabels = computed(() => {
  const trend = stats.value.daily_trend ?? []
  return trend.length === 0
    ? []
    : trend.map((t, i) => {
        if (i % 5 === 0 || i === trend.length - 1) {
          return t.date ? t.date.slice(5) : `${i + 1}日`
        }
        return ''
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
  margin-bottom: 20px;
}
.page-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.page-header-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
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
}
.page-header-tools {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  padding-top: 4px;
}
.refresh-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all 0.15s ease;
}
.refresh-btn:hover {
  background: var(--primary-light-color);
  color: var(--primary-color);
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

/* ── 用户 ID 列 ── */
.id-cell {
  font-family: var(--font-mono, 'SF Mono', 'Fira Code', monospace);
  font-size: 11px;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: color 0.15s ease;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  background: var(--surface-inset-color);
}
.id-cell:hover {
  color: var(--primary-color);
  background: var(--primary-light-color);
}

/* ── 用户名列 ── */
.user-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

/* ── 时间列 ── */
.time-cell {
  line-height: 1.5;
  font-size: 12px;
}

/* ── 操作栏 ── */
.action-cell {
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
  flex-wrap: nowrap;
}

/* ── 弹窗辅助 ── */
.modal-hint {
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}

/* ── 封禁选项 ── */
.ban-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.ban-option {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  padding: 0 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: var(--surface-color);
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
}
.ban-option:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}
.ban-option--active {
  border-color: var(--primary-color);
  background: var(--primary-light-color);
  color: var(--primary-color);
  font-weight: 600;
}
.ban-custom-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.ban-custom-unit {
  font-size: 13px;
  color: var(--text-secondary);
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
