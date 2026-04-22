<template>
  <div class="dashboard-layout">
    <!-- 左侧锚定区：固定不动 -->
    <aside class="sidebar">
      <!-- 用户身份面板 -->
      <div class="identity-panel">
        <div class="avatar-section">
          <img v-if="avatarUrl" :src="avatarUrl" alt="avatar" class="identity-avatar" />
          <div v-else class="identity-avatar-placeholder">{{ userInitial }}</div>
        </div>
        <div class="identity-info">
          <h2 class="identity-name">{{ userInfo?.username ?? '加载中...' }}</h2>
          <div class="identity-meta">
            <LevelBadge :level="level ?? 5" />
            <span class="identity-role">{{ roleLabel }}</span>
          </div>
          <div class="identity-detail">
            <span class="detail-item">
              <icon-calendar class="detail-icon" />
              {{ formatDate(userInfo?.created_at) }} 加入
            </span>
            <span class="detail-item" v-if="userInfo?.email">
              <icon-email class="detail-icon" />
              {{ userInfo.email }}
            </span>
          </div>
        </div>
        <div class="identity-stats">
          <div class="stat-block">
            <div class="stat-num">{{ postCount }}</div>
            <div class="stat-label">文章</div>
          </div>
          <div class="stat-block">
            <div class="stat-num">{{ totalViews }}</div>
            <div class="stat-label">阅读</div>
          </div>
          <div class="stat-block">
            <div class="stat-num">{{ totalLikes }}</div>
            <div class="stat-label">获赞</div>
          </div>
          <div class="stat-block">
            <div class="stat-num">{{ storageUsed }}</div>
            <div class="stat-label">MB</div>
          </div>
        </div>
      </div>

      <!-- 管理员监控面板（仅 P0） -->
      <div v-if="level !== null && level <= 0" class="admin-panel-card">
        <div class="admin-panel-header">
          <icon-dashboard class="admin-panel-icon" />
          <span>系统监控</span>
          <a-tag color="red" size="mini">P0</a-tag>
        </div>
        <div class="admin-monitor-grid">
          <div class="admin-monitor-item">
            <span class="admin-monitor-label">CPU</span>
            <span class="admin-monitor-value">{{ sysInfo.cpu }}%</span>
            <a-progress :percent="sysInfo.cpu" size="mini" :stroke-width="4" />
          </div>
          <div class="admin-monitor-item">
            <span class="admin-monitor-label">内存</span>
            <span class="admin-monitor-value">{{ sysInfo.memoryPercent }}%</span>
            <a-progress :percent="sysInfo.memoryPercent" size="mini" :stroke-width="4" />
          </div>
          <div class="admin-monitor-item">
            <span class="admin-monitor-label">磁盘</span>
            <span class="admin-monitor-value">{{ sysInfo.diskPercent }}%</span>
            <a-progress :percent="sysInfo.diskPercent" size="mini" :stroke-width="4" />
          </div>
          <div class="admin-monitor-item">
            <span class="admin-monitor-label">在线</span>
            <span class="admin-monitor-value">{{ sysInfo.onlineUsers }}</span>
          </div>
          <div class="admin-monitor-item">
            <span class="admin-monitor-label">QPS</span>
            <span class="admin-monitor-value">{{ sysInfo.qps }}</span>
          </div>
          <div class="admin-monitor-item">
            <span class="admin-monitor-label">请求</span>
            <span class="admin-monitor-value">{{ sysInfo.requests }}</span>
          </div>
        </div>
        <div class="admin-quick-links">
          <a-button type="text" size="mini" @click="$router.push('/admin/users')">
            <template #icon><icon-user /></template>用户
          </a-button>
          <a-button type="text" size="mini" @click="$router.push('/admin')">
            <template #icon><icon-settings /></template>设置
          </a-button>
        </div>
      </div>
    </aside>

    <!-- 右侧滚动区 -->
    <main class="main-content">
      <!-- 关注焦点 / 待办任务 -->
      <div class="focus-section" ref="focusSectionRef">
        <div class="section-header">
          <icon-pushpin class="section-icon" />
          <span>关注焦点</span>
          <span class="section-hint">拖拽卡片到此处置顶</span>
        </div>
        <div class="focus-grid" id="focus-zone">
          <div
            v-for="card in focusCards"
            :key="card.id"
            class="focus-card"
            :draggable="true"
            @dragstart="onDragStart($event, card, 'focus')"
            @dragend="onDragEnd"
            @click="card.onClick"
          >
            <div class="focus-card-remove" @click.stop="removeFromFocus(card.id)" title="移除">
              <icon-close />
            </div>
            <div class="focus-card-header">
              <component :is="card.icon" class="focus-card-icon" />
              <span class="focus-card-title">{{ card.title }}</span>
            </div>
            <div class="focus-card-body">
              <component :is="card.body" />
            </div>
          </div>
          <div v-if="focusCards.length === 0" class="focus-empty">
            <icon-pushpin class="focus-empty-icon" />
            <span>拖拽下方卡片到此处</span>
          </div>
        </div>
      </div>

      <!-- 创作者数据卡片 -->
      <div class="section-header">
        <icon-bar-chart class="section-icon" />
        <span>创作数据</span>
      </div>
      <div class="creator-grid" id="creator-zone">
        <div
          v-for="card in creatorCards"
          :key="card.id"
          class="creator-card"
          :draggable="true"
          @dragstart="onDragStart($event, card, 'creator')"
          @dragend="onDragEnd"
          @click="card.onClick"
        >
          <div class="card-drag-handle" title="拖拽">
            <icon-drag-dot-vertical />
          </div>
          <div class="creator-header">
            <component :is="card.icon" class="creator-icon" />
            <span class="creator-title">{{ card.title }}</span>
          </div>
          <div class="creator-body">
            <component :is="card.body" />
          </div>
          <div class="creator-footer">
            <component :is="card.footer" />
          </div>
        </div>
      </div>

      <!-- 系统任务卡片 -->
      <div class="section-header">
        <icon-settings class="section-icon" />
        <span>系统任务</span>
      </div>
      <div class="task-grid" id="task-zone">
        <div
          v-for="card in taskCards"
          :key="card.id"
          class="task-card"
          :class="{ 'admin-task': card.adminOnly }"
          :draggable="true"
          @dragstart="onDragStart($event, card, 'task')"
          @dragend="onDragEnd"
          @click="card.onClick"
        >
          <div class="card-drag-handle" title="拖拽">
            <icon-drag-dot-vertical />
          </div>
          <div class="card-header">
            <component :is="card.icon" class="card-icon" :class="{ 'admin-icon': card.adminOnly }" />
            <span class="card-title">{{ card.title }}</span>
          </div>
          <div class="card-body">
            <component :is="card.body" />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import LevelBadge from '../LevelBadge.vue'
import { useAuth } from '../../router/auth.js'
import {
  IconCalendar, IconEmail, IconBarChart, IconEdit, IconUpload,
  IconCheck, IconCheckCircle, IconBug, IconCloud, IconStorage,
  IconApps, IconSync, IconClose, IconLock, IconDesktop,
  IconGithub, IconPushpin, IconDashboard, IconUser, IconSettings,
  IconDragDotVertical,
} from '@arco-design/web-vue/es/icon'

const router = useRouter()
const { loadUser, user, level } = useAuth()

const userInfo = ref(null)
const avatarUrl = ref(localStorage.getItem('veil_avatar') || '')
const moderationPending = ref(0)
const storageUsed = ref(0)
const storageTotal = ref(500)
const postCount = ref(0)
const totalViews = ref(0)
const totalLikes = ref(0)
const postHistory = ref([30, 45, 25, 60, 40, 55, 35, 70, 50, 65, 45, 80])

const ROLE_LABELS = {
  0: '管理员', 1: '高级用户', 2: '中级用户',
  3: '初级用户', 4: '注册用户', 5: '访客',
}
const roleLabel = computed(() => ROLE_LABELS[level.value ?? 5] ?? '未知')
const userInitial = computed(() => userInfo.value?.username ? userInfo.value.username[0].toUpperCase() : 'U')

const storagePercent = computed(() => storageTotal.value ? Math.round((storageUsed.value / storageTotal.value) * 100) : 0)

// 管理员系统信息
const sysInfo = ref({
  cpu: 23, memoryPercent: 26, diskPercent: 24,
  onlineUsers: 7, qps: 12.3, requests: 18453,
})

// ====== 关注焦点卡片 ======
const focusCards = ref([])

// ====== 创作者卡片 ======
const creatorCards = computed(() => [
  {
    id: 'articles',
    icon: IconEdit,
    title: '文章总览',
    onClick: () => router.push('/editor'),
    body: () => h('div', { class: 'creator-stat' }, [
      h('span', { class: 'creator-num' }, postCount.value),
      h('span', { class: 'creator-unit' }, '篇'),
    ]),
    footer: () => h('div', { class: 'creator-footer-inner' }, [
      h('span', { class: 'footer-label' }, '阅读'),
      h('span', { class: 'footer-value' }, totalViews.value),
      h('span', { class: 'footer-divider' }, '|'),
      h('span', { class: 'footer-label' }, '获赞'),
      h('span', { class: 'footer-value' }, totalLikes.value),
    ]),
  },
  {
    id: 'files',
    icon: IconUpload,
    title: '文件管理',
    onClick: () => router.push('/upload'),
    body: () => h('div', null, [
      h('div', { class: 'creator-stat' }, [
        h('span', { class: 'creator-num' }, '0'),
        h('span', { class: 'creator-unit' }, '个'),
      ]),
    ]),
    footer: () => h('div', { class: 'creator-footer-inner' }, [
      h('span', { class: 'footer-label' }, '已用'),
      h('span', { class: 'footer-value' }, storageUsed.value + ' MB'),
      h('span', { class: 'footer-divider' }, '/'),
      h('span', { class: 'footer-value' }, storageTotal.value + ' MB'),
    ]),
  },
  {
    id: 'moderation',
    icon: IconCheck,
    title: '审核队列',
    onClick: () => router.push('/moderation'),
    body: () => moderationPending.value > 0
      ? h('div', { class: 'moderation-list' }, [
          h('span', { class: 'mod-item' }, [
            h('span', { class: 'mod-dot pending' }),
            `待审核 ${moderationPending.value}`,
          ]),
        ])
      : h('div', { class: 'mod-empty' }, [
          h('span', null, '暂无待审内容'),
        ]),
    footer: () => moderationPending.value > 0
      ? h('span', { class: 'footer-status pending' }, '需要处理')
      : h('span', { class: 'footer-status done' }, '全部完成'),
  },
])

// ====== 系统任务卡片 ======
const taskCards = computed(() => {
  const cards = [
    {
      id: 'crawler',
      icon: IconBug,
      title: '爬虫任务',
      onClick: () => router.push('/ops/crawler'),
      body: () => h('div', { class: 'task-empty' }, [
        h('span', null, '暂无爬虫任务'),
      ]),
    },
    {
      id: 'cloud',
      icon: IconCloud,
      title: '云训练',
      onClick: () => router.push('/ops/cloud'),
      body: () => h('div', { class: 'task-empty' }, [
        h('span', null, '暂无训练任务'),
      ]),
    },
    {
      id: 'storage',
      icon: IconStorage,
      title: '存储管理',
      onClick: () => router.push('/storage'),
      body: () => h('div', { class: 'storage-detail' }, [
        h('div', { class: 'storage-item' }, [
          h('span', { class: 'storage-label' }, '本地'),
          h('span', { class: 'storage-value' }, `${storageUsed.value}/${storageTotal.value}M`),
        ]),
      ]),
    },
    {
      id: 'github',
      icon: IconGithub,
      title: 'GitHub 代理',
      onClick: () => router.push('/github'),
      body: () => h('div', { class: 'task-empty' }, [
        h('span', null, '管理追踪仓库'),
      ]),
    },
    {
      id: 'assets',
      icon: IconApps,
      title: '资产管理',
      onClick: () => router.push('/ops/assets'),
      body: () => h('div', { class: 'task-empty' }, [
        h('span', null, '暂无资产'),
      ]),
    },
  ]

  // P0 管理员卡片
  if (level.value !== null && level.value <= 0) {
    cards.push({
      id: 'admin',
      icon: IconLock,
      title: '管理员面板',
      adminOnly: true,
      onClick: () => router.push('/admin'),
      body: () => h('div', { class: 'admin-task-body' }, [
        h('span', { class: 'admin-stat' }, [
          h('span', null, `${sysInfo.value.onlineUsers} 在线`),
        ]),
      ]),
    })
  }

  return cards
})

function formatDate(dateStr) {
  if (!dateStr) return '未知'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// ====== 拖拽逻辑 ======
let dragData = null

function onDragStart(event, card, source) {
  dragData = { card, source }
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', card.id)
  // 设置拖拽图像
  const el = event.target.closest('.task-card, .creator-card')
  if (el) {
    const rect = el.getBoundingClientRect()
    event.dataTransfer.setDragImage(el, rect.width / 2, 20)
  }
}

function onDragEnd() {
  dragData = null
}

// 关注焦点区 drop 处理
const focusSectionRef = ref(null)

onMounted(() => {
  const focusZone = document.getElementById('focus-zone')
  if (!focusZone) return

  focusZone.addEventListener('dragover', (e) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    focusZone.classList.add('drag-over')
  })

  focusZone.addEventListener('dragleave', () => {
    focusZone.classList.remove('drag-over')
  })

  focusZone.addEventListener('drop', (e) => {
    e.preventDefault()
    focusZone.classList.remove('drag-over')
    if (dragData && !focusCards.value.find(c => c.id === dragData.card.id)) {
      focusCards.value.push({ ...dragData.card })
    }
  })
})

function removeFromFocus(id) {
  focusCards.value = focusCards.value.filter(c => c.id !== id)
}

async function fetchStatus() {
  try {
    const token = localStorage.getItem('veil_token')
    if (!token) return
    const modRes = await fetch('/api/blog/moderation/pending?page=1&page_size=1', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (modRes.ok) {
      const data = await modRes.json()
      moderationPending.value = data.data?.total || 0
    }
    // 存储用量
    const storageRes = await fetch('/api/oss/storage/stats?user_scope=true', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (storageRes.ok) {
      const sData = await storageRes.json()
      if (sData.code === 'ok') {
        storageUsed.value = Math.round((sData.data.total_size || 0) / 1024 / 1024)
      }
    }
  } catch {}
}

onMounted(async () => {
  await loadUser()
  if (user.value) {
    userInfo.value = user.value
    const saved = localStorage.getItem('veil_avatar')
    if (saved) avatarUrl.value = saved
  }
  fetchStatus()
})
</script>

<style scoped>
/* ===== 整体布局：左侧锚定 + 右侧滚动 ===== */
.dashboard-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  max-width: 1280px;
  margin: 0 auto;
  align-items: start;
}

/* ===== 左侧锚定区 ===== */
.sidebar {
  position: sticky;
  top: 72px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ===== 右侧滚动区 ===== */
.main-content {
  min-width: 0;
  padding-bottom: 48px;
}

/* ===== 身份面板 ===== */
.identity-panel {
  background: rgba(255,255,255,0.75);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: var(--border-radius-large);
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.avatar-section { margin-bottom: 12px; }

.identity-avatar {
  width: 64px; height: 64px;
  border-radius: 50%;
  border: 3px solid #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  object-fit: cover;
}

.identity-avatar-placeholder {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark-1));
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 700;
  border: 3px solid #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}

.identity-info { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.identity-name { margin: 0; font-size: 18px; font-weight: 700; color: var(--color-text-1); }
.identity-meta { display: flex; align-items: center; gap: 8px; }
.identity-role { font-size: 12px; color: var(--color-text-3); }
.identity-detail { display: flex; flex-direction: column; gap: 4px; }
.detail-item { display: flex; align-items: center; gap: 4px; font-size: 11px; color: var(--color-text-4); }
.detail-icon { width: 12px; height: 12px; }

.identity-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-1);
}

.stat-block { text-align: center; }
.stat-num { font-size: 18px; font-weight: 700; color: var(--color-text-1); line-height: 1; }
.stat-label { font-size: 10px; color: var(--color-text-4); margin-top: 2px; text-transform: uppercase; letter-spacing: 0.5px; }

/* ===== 管理员监控面板 ===== */
.admin-panel-card {
  background: rgba(255,255,255,0.75);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(207,34,46,0.15);
  border-radius: var(--border-radius-large);
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.admin-panel-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 600; color: var(--color-text-2);
  margin-bottom: 12px;
}

.admin-panel-icon { width: 14px; height: 14px; color: #cf222e; }

.admin-monitor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.admin-monitor-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px;
  background: var(--color-fill-1);
  border-radius: var(--border-radius-small);
}

.admin-monitor-label { font-size: 10px; color: var(--color-text-4); text-transform: uppercase; }
.admin-monitor-value { font-size: 16px; font-weight: 700; color: var(--color-text-1); }

.admin-quick-links {
  display: flex;
  gap: 4px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-1);
}

/* ===== 分区标题 ===== */
.section-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600; color: var(--color-text-2);
  margin-bottom: 12px;
}

.section-icon { width: 16px; height: 16px; color: var(--color-text-4); }
.section-hint { font-size: 11px; color: var(--color-text-4); font-weight: 400; margin-left: auto; }

/* ===== 关注焦点区 ===== */
.focus-section {
  margin-bottom: 24px;
}

.focus-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  min-height: 60px;
  padding: 12px;
  border: 2px dashed transparent;
  border-radius: var(--border-radius-large);
  transition: border-color 0.2s, background 0.2s;
}

.focus-grid.drag-over {
  border-color: var(--color-primary);
  background: rgba(91,127,164,0.05);
}

.focus-empty {
  grid-column: 1 / -1;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 24px;
  color: var(--color-text-4);
  font-size: 13px;
}

.focus-empty-icon { width: 32px; height: 32px; color: var(--color-border-2); }

.focus-card {
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: var(--border-radius-large);
  padding: 14px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  position: relative;
}

.focus-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
  transform: translateY(-1px);
}

.focus-card-remove {
  position: absolute; top: 6px; right: 6px;
  display: flex; align-items: center; justify-content: center;
  width: 20px; height: 20px;
  border-radius: 50%;
  cursor: pointer;
  color: var(--color-text-4);
  opacity: 0;
  transition: opacity 0.15s, background 0.15s;
  z-index: 2;
}

.focus-card:hover .focus-card-remove { opacity: 1; }
.focus-card-remove:hover { background: var(--color-fill-2); color: var(--color-text-1); }
.focus-card-remove .arco-icon { width: 12px; height: 12px; }

.focus-card-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
}

.focus-card-icon { width: 16px; height: 16px; color: var(--color-primary); }
.focus-card-title { font-size: 13px; font-weight: 600; color: var(--color-text-1); }
.focus-card-body { font-size: 12px; color: var(--color-text-3); }

/* ===== 创作者网格 ===== */
.creator-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.creator-card {
  background: rgba(255,255,255,0.75);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: var(--border-radius-large);
  padding: 16px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  position: relative;
}

.creator-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}

.creator-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 12px;
}

.creator-icon { width: 18px; height: 18px; color: var(--color-primary); }
.creator-title { font-size: 13px; font-weight: 600; color: var(--color-text-1); flex: 1; }

.creator-body { min-height: 48px; margin-bottom: 12px; }

.creator-stat { display: flex; align-items: baseline; gap: 4px; }
.creator-num { font-size: 28px; font-weight: 700; color: var(--color-text-1); line-height: 1; }
.creator-unit { font-size: 13px; color: var(--color-text-4); }

.creator-footer-inner {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px;
}

.footer-label { color: var(--color-text-4); }
.footer-value { color: var(--color-text-2); font-weight: 600; }
.footer-divider { color: var(--color-border-2); }
.footer-status { font-weight: 600; padding: 2px 8px; border-radius: 6px; font-size: 11px; }
.footer-status.pending { background: rgba(212,167,44,0.15); color: #9a6700; }
.footer-status.done { background: rgba(26,127,55,0.1); color: #1a7f37; }

.moderation-list { display: flex; gap: 8px; }
.mod-item { display: flex; align-items: center; gap: 4px; font-size: 13px; color: var(--color-text-2); }
.mod-dot { width: 8px; height: 8px; border-radius: 50%; }
.mod-dot.pending { background: #d4a72c; box-shadow: 0 0 6px #d4a72c60; }
.mod-empty { display: flex; align-items: center; gap: 8px; color: var(--color-text-4); font-size: 13px; }

/* ===== 系统任务网格 ===== */
.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.task-card {
  background: rgba(255,255,255,0.75);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: var(--border-radius-large);
  padding: 16px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  position: relative;
}

.task-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}

.task-card.admin-task {
  border-color: rgba(207,34,46,0.15);
}

.task-card.admin-task:hover {
  border-color: #cf222e;
}

.admin-task .admin-icon { color: #cf222e !important; }
.admin-task-body { text-align: center; padding: 4px 0; }
.admin-stat { font-size: 12px; color: var(--color-text-3); }

.card-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 12px;
}

.card-icon { width: 18px; height: 18px; color: var(--color-primary); }
.card-title { font-size: 13px; font-weight: 600; color: var(--color-text-1); }

.card-body { min-height: 40px; }

.task-empty {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 16px 0;
  color: var(--color-text-4);
  font-size: 13px;
}

.storage-detail { display: flex; flex-direction: column; gap: 6px; }
.storage-item { display: flex; align-items: center; gap: 8px; }
.storage-label { font-size: 11px; color: var(--color-text-3); width: 40px; flex-shrink: 0; }
.storage-value { font-size: 11px; color: var(--color-text-2); }

/* ===== 拖拽手柄 ===== */
.card-drag-handle {
  position: absolute; top: 6px; right: 8px;
  display: flex; align-items: center; justify-content: center;
  width: 20px; height: 20px;
  border-radius: 4px;
  cursor: grab;
  color: var(--color-text-4);
  opacity: 0;
  transition: opacity 0.15s, background 0.15s;
  z-index: 2;
}

.creator-card:hover .card-drag-handle,
.task-card:hover .card-drag-handle { opacity: 0.6; }
.card-drag-handle:hover { opacity: 1 !important; background: var(--color-fill-2); }
.card-drag-handle .arco-icon { width: 14px; height: 14px; }

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .dashboard-layout {
    grid-template-columns: 1fr;
  }
  .sidebar {
    position: static;
  }
  .creator-grid {
    grid-template-columns: 1fr;
  }
  .task-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
