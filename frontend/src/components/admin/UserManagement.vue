<template>
  <div class="user-management">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.push('/admin')" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <a-button type="text" size="mini" @click="$router.push('/platform')" class="back-btn">
          <template #icon><icon-home /></template>
        </a-button>
        <icon-user class="header-icon" />
        <h1 class="page-title">用户管理</h1>
      </div>
      <a-space>
        <a-button type="text" size="small" @click="fetchUsers" :loading="refreshing">
          <template #icon><icon-refresh /></template>
        </a-button>
        <a-input-search v-model="searchQuery" placeholder="搜索用户..." size="small" style="width: 180px" @search="doSearch" />
      </a-space>
    </div>

    <!-- 用户统计 -->
    <div class="status-row">
      <div class="status-card">
        <div class="status-num">{{ userStats.total }}</div>
        <div class="status-label">总用户</div>
      </div>
      <div class="status-card s-active">
        <div class="status-num">{{ userStats.active }}</div>
        <div class="status-label">正常</div>
      </div>
      <div class="status-card s-banned">
        <div class="status-num">{{ userStats.disabled }}</div>
        <div class="status-label">已禁用</div>
      </div>
      <div class="status-card">
        <div class="status-num">{{ users.length }}</div>
        <div class="status-label">当前页</div>
      </div>
    </div>

    <!-- 用户列表 -->
    <a-table
      :data="users"
      :columns="userColumns"
      row-key="id"
      :bordered="false"
      :pagination="pagination"
      :loading="loading"
      class="user-table"
      @page-change="onPageChange"
    >
      <template #user="{ record }">
        <div class="user-cell">
          <a-avatar :size="32" :style="{ backgroundColor: levelColor(record.level) }">
            {{ (record.username || 'U')[0].toUpperCase() }}
          </a-avatar>
          <div class="user-info">
            <span class="user-name">{{ record.username }}</span>
            <span class="user-email">{{ record.email || '—' }}</span>
          </div>
        </div>
      </template>
      <template #level="{ record }">
        <LevelBadge :level="record.level ?? 5" />
      </template>
      <template #status="{ record }">
        <a-tag :color="record.is_active === false ? 'red' : 'green'">
          {{ record.is_active === false ? '已禁用' : '正常' }}
        </a-tag>
      </template>
      <template #joined="{ record }">
        <span style="font-size: 12px; color: var(--color-text-3)">
          {{ record.created_at ? new Date(record.created_at).toLocaleDateString('zh-CN') : '-' }}
        </span>
      </template>
      <template #actions="{ record }">
        <a-dropdown trigger="click" position="bl">
          <a-button type="text" size="mini">
            操作
            <icon-down />
          </a-button>
          <template #content>
            <a-doption @click="changeLevel(record)">
              <template #icon><icon-swap /></template>
              修改等级
            </a-doption>
            <a-doption v-if="record.is_active !== false" @click="disableUser(record)" class="danger-option">
              <template #icon><icon-stop /></template>
              禁用用户
            </a-doption>
            <a-doption v-else @click="enableUser(record)">
              <template #icon><icon-check /></template>
              启用用户
            </a-doption>
            <a-doption @click="viewUserDetail(record)">
              <template #icon><icon-eye /></template>
              查看详情
            </a-doption>
          </template>
        </a-dropdown>
      </template>
    </a-table>

    <!-- 修改等级弹窗 -->
    <a-modal v-model:visible="showLevelModal" title="修改用户等级" @ok="confirmLevelChange" :mask-closable="false">
      <p style="margin-bottom: 16px; color: var(--color-text-2)">
        用户 <b>{{ targetUser?.username }}</b> 当前等级：P{{ targetUser?.level ?? '—' }}
      </p>
      <a-select v-model="newLevel" size="large" style="width: 100%">
        <a-option :value="0">P0 - 管理员</a-option>
        <a-option :value="1">P1 - 高级用户</a-option>
        <a-option :value="2">P2 - 中级用户</a-option>
        <a-option :value="3">P3 - 初级用户</a-option>
        <a-option :value="4">P4 - 注册用户</a-option>
        <a-option :value="5">P5 - 访客</a-option>
      </a-select>
    </a-modal>

    <!-- 用户详情抽屉 -->
    <a-drawer v-model:visible="showDetailDrawer" title="用户详情" width="480">
      <div v-if="detailUser" class="detail-content">
        <div class="detail-section">
          <h4 class="detail-title">基本信息</h4>
          <div class="detail-row"><span class="detail-label">ID</span><span class="detail-mono">{{ detailUser.id }}</span></div>
          <div class="detail-row"><span class="detail-label">用户名</span><span>{{ detailUser.username }}</span></div>
          <div class="detail-row"><span class="detail-label">邮箱</span><span>{{ detailUser.email || '未设置' }}</span></div>
          <div class="detail-row"><span class="detail-label">等级</span><LevelBadge :level="detailUser.level ?? 5" /></div>
          <div class="detail-row"><span class="detail-label">状态</span>
            <a-tag :color="detailUser.is_active === false ? 'red' : 'green'">{{ detailUser.is_active === false ? '已禁用' : '正常' }}</a-tag>
          </div>
          <div class="detail-row"><span class="detail-label">注册时间</span><span>{{ detailUser.created_at ? new Date(detailUser.created_at).toLocaleString('zh-CN') : '-' }}</span></div>
        </div>
      </div>
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import LevelBadge from '../LevelBadge.vue'
import { useAuth } from '../../router/auth.js'
import {
  IconUser, IconArrowLeft, IconHome, IconRefresh, IconDown,
  IconSwap, IconStop, IconCheck, IconEye,
} from '@arco-design/web-vue/es/icon'

const { authHeaders } = useAuth()
const searchQuery = ref('')
const refreshing = ref(false)
const loading = ref(true)
const showLevelModal = ref(false)
const showDetailDrawer = ref(false)
const targetUser = ref(null)
const detailUser = ref(null)
const newLevel = ref(5)

const userStats = ref({ total: 0, active: 0, disabled: 0 })
const users = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const pagination = { showTotal: true, pageSize: 20 }

const LEVEL_COLORS = {
  0: '#cf222e', 1: '#d4a72c', 2: '#0969da',
  3: '#1a7f37', 4: '#6e7781', 5: '#aab8c2',
}

function levelColor(level) { return LEVEL_COLORS[level] ?? '#aab8c2' }

const userColumns = [
  { title: '用户', slotName: 'user', width: 240 },
  { title: '等级', slotName: 'level', width: 100 },
  { title: '状态', slotName: 'status', width: 80 },
  { title: '注册时间', slotName: 'joined', width: 140 },
  { title: '操作', slotName: 'actions', width: 100, fixed: 'right' },
]

async function fetchUsers(status = null) {
  loading.value = true
  try {
    const url = `/api/auth/users?page=${page.value}&page_size=${pageSize.value}${status ? `&status=${status}` : ''}`
    const res = await fetch(url, { headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') {
      const data = result.data || {}
      users.value = data.items || []
      total.value = data.total || 0
      pagination.total = total.value
      userStats.value.total = data.total ?? 0
      // 分别统计 active/disabled
      const [activeRes, disabledRes] = await Promise.all([
        fetch(`/api/auth/users?page=1&page_size=1&status=active`, { headers: authHeaders() }),
        fetch(`/api/auth/users?page=1&page_size=1&status=disabled`, { headers: authHeaders() }),
      ])
      const activeData = await activeRes.json()
      const disabledData = await disabledRes.json()
      userStats.value.active = activeData.data?.total ?? 0
      userStats.value.disabled = disabledData.data?.total ?? 0
    } else {
      Message.error(result.message || '加载用户失败')
    }
  } catch {
    Message.error('网络错误')
  } finally {
    loading.value = false
  }
}

function onPageChange(p) {
  page.value = p
  fetchUsers()
}

function doSearch() {
  if (!searchQuery.value.trim()) { fetchUsers(); return }
  // 前端过滤
  const q = searchQuery.value.toLowerCase()
  users.value = users.value.filter(u =>
    (u.username || '').toLowerCase().includes(q) ||
    (u.email && u.email.toLowerCase().includes(q))
  )
}

function changeLevel(user) {
  targetUser.value = user
  newLevel.value = user.level ?? 5
  showLevelModal.value = true
}

async function confirmLevelChange() {
  if (!targetUser.value) return
  try {
    const res = await fetch(`/api/auth/users/${targetUser.value.id}`, {
      method: 'PUT',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ level: newLevel.value }),
    })
    const result = await res.json()
    if (result.code === 'ok') {
      const oldLevel = targetUser.value.level
      targetUser.value.level = newLevel.value
      Message.success(`已将 ${targetUser.value.username} 从 P${oldLevel} 调整为 P${newLevel.value}`)
      showLevelModal.value = false
    } else {
      Message.error(result.message || '修改失败')
    }
  } catch {
    Message.error('网络错误')
  }
}

async function disableUser(user) {
  Modal.confirm({
    title: '确认禁用',
    content: `确定禁用用户 "${user.username}" 吗？禁用后该用户将无法登录。`,
    buttonProps: { status: 'danger' },
    onOk: async () => {
      try {
        const res = await fetch(`/api/auth/users/${user.id}/disable`, { method: 'POST', headers: authHeaders() })
        const result = await res.json()
        if (result.code === 'ok') {
          user.is_active = false
          Message.warning(`已禁用用户: ${user.username}`)
          await fetchUsers()
        } else {
          Message.error(result.message || '操作失败')
        }
      } catch { Message.error('网络错误') }
    },
  })
}

async function enableUser(user) {
  try {
    const res = await fetch(`/api/auth/users/${user.id}/enable`, { method: 'POST', headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') {
      user.is_active = true
      Message.success(`已启用用户: ${user.username}`)
      await fetchUsers()
    } else {
      Message.error(result.message)
    }
  } catch { Message.error('网络错误') }
}

function viewUserDetail(user) {
  detailUser.value = user
  showDetailDrawer.value = true
}

onMounted(() => { fetchUsers() })
</script>

<style scoped>
.user-management { max-width: 1100px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 4px; }
.header-icon { width: 24px; height: 24px; color: var(--color-primary); margin-left: 6px; }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }

.status-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
.status-card {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  padding: 16px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.status-card .status-num { font-size: 28px; font-weight: 700; color: var(--color-text-1); line-height: 1; }
.status-card.s-active .status-num { color: #1a7f37; }
.status-card.s-banned .status-num { color: #cf222e; }
.status-label { font-size: 12px; color: var(--color-text-4); margin-top: 4px; }

.user-table { border-radius: var(--border-radius-large); overflow: hidden; }
.user-cell { display: flex; align-items: center; gap: 12px; }
.user-info { display: flex; flex-direction: column; }
.user-name { font-weight: 500; font-size: 14px; }
.user-email { font-size: 12px; color: var(--color-text-4); }
.danger-option :deep(.arco-dropdown-option-content) { color: #cf222e; }

.detail-content { display: flex; flex-direction: column; gap: 24px; }
.detail-title { font-size: 14px; font-weight: 600; color: var(--color-text-2); margin: 0 0 12px; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--color-border-1); }
.detail-label { font-size: 13px; color: var(--color-text-4); }
.detail-row span:not(.detail-label):not(.arco-tag) { font-size: 13px; color: var(--color-text-1); font-weight: 500; }
.detail-mono { font-family: monospace; font-size: 11px; color: var(--color-text-3); }
</style>
