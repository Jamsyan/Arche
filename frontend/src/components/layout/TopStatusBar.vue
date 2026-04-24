<template>
  <header class="top-status-bar">
    <!-- 左侧：页面标题 -->
    <div class="status-left">
      <span class="page-title">{{ currentPageTitle }}</span>
    </div>

    <!-- 中间：状态指示器 -->
    <div class="status-center">
      <div
        v-for="status in visibleStatuses"
        :key="status.key"
        class="status-item"
        :title="status.description"
      >
        <component :is="status.icon" class="status-icon" />
        <span class="status-value">{{ status.value }}</span>
        <span class="status-label">{{ status.label }}</span>
      </div>
    </div>

    <!-- 右侧：时间 + 用户信息 -->
    <div class="status-right">
      <span class="current-time">{{ currentTime }}</span>
      <LevelBadge :level="userLevel" />
      <a-dropdown trigger="click" position="br">
        <div class="avatar-wrap">
          <img v-if="avatarUrl" :src="avatarUrl" alt="avatar" class="avatar-img" />
          <div v-else class="avatar-circle">
            <span>{{ userInitial }}</span>
          </div>
        </div>
        <template #content>
          <a-doption @click="$router.push('/account')">
            <template #icon><icon-user /></template>
            账号管理
          </a-doption>
          <a-doption @click="handleLogout">
            <template #icon><icon-export /></template>
            退出登录
          </a-doption>
        </template>
      </a-dropdown>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../../router/auth.js'
import LevelBadge from '../LevelBadge.vue'
import { monitor, crawler, blog } from '../../api'
import {
  IconUser,
  IconExport,
  IconRefresh,
  IconClockCircle,
  IconFire,
  IconStorage,
  IconHome
} from '@arco-design/web-vue/es/icon'

const route = useRoute()
const router = useRouter()
const { user, logout, level } = useAuth()

const userLevel = computed(() => level.value || 0)
const userInitial = computed(() => user.value?.username?.[0]?.toUpperCase() || 'U')

const avatarUrl = ref(localStorage.getItem('veil_avatar') || '')

// 页面标题映射
const PAGE_TITLES = {
  '/monitor': '监控大屏',
  '/platform': '任务中心',
  '/': '首页',
  '/editor': '文章编辑',
  '/upload': '文件上传',
  '/storage': '存储管理',
  '/github': 'GitHub 代理',
  '/ops': '运维管理',
  '/ops/crawler': '爬虫管理',
  '/ops/cloud': '云训练',
  '/admin': '管理后台',
  '/account': '账号管理'
}

const currentPageTitle = computed(() => {
  const path = route.path
  if (PAGE_TITLES[path]) return PAGE_TITLES[path]
  // 匹配最长前缀（如 /ops/cloud/tasks 匹配 /ops/cloud）
  const matched = Object.keys(PAGE_TITLES)
    .filter(k => path.startsWith(k))
    .sort((a, b) => b.length - a.length)[0]
  return matched ? PAGE_TITLES[matched] : '锦年志'
})

// 时间
const currentTime = ref('')
let timeTimer = null

function updateTime() {
  currentTime.value = new Date().toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  updateTime()
  timeTimer = setInterval(updateTime, 10000)
  startStatusPolling()
  const saved = localStorage.getItem('veil_avatar')
  if (saved) avatarUrl.value = saved
})

onUnmounted(() => {
  if (timeTimer) clearInterval(timeTimer)
  stopStatusPolling()
})

// 状态指示器
const statuses = ref([
  {
    key: 'qps',
    icon: IconFire,
    label: 'QPS',
    value: ref('--'),
    description: '每秒请求数',
    pages: ['/monitor', '/ops'],
    fetchInterval: 30000,
    load: async () => {
      try {
        const d = await monitor.systemQps()
        return d?.value ?? '--'
      } catch { return '--' }
    }
  },
  {
    key: 'memory',
    icon: IconStorage,
    label: '内存',
    value: ref('--'),
    description: '系统内存使用率',
    pages: ['/monitor', '/ops'],
    fetchInterval: 30000,
    load: async () => {
      try {
        const d = await monitor.systemMemory()
        return d?.percent ?? '--'
      } catch { return '--' }
    }
  },
  {
    key: 'crawler',
    icon: IconRefresh,
    label: '队列',
    value: ref('--'),
    description: '爬虫队列长度',
    pages: ['/ops/crawler'],
    fetchInterval: 10000,
    load: async () => {
      try {
        const d = await crawler.status()
        return d?.length ?? '--'
      } catch { return '--' }
    }
  },
  {
    key: 'posts',
    icon: IconHome,
    label: '帖子',
    value: ref('--'),
    description: '当前帖子数',
    pages: ['/'],
    fetchInterval: 60000,
    load: async () => {
      try {
        const d = await blog.listPosts({ page: 1, page_size: 1 })
        return d?.total ?? '--'
      } catch { return '--' }
    }
  }
])

// 状态轮询
let pollingTimers = []

function startStatusPolling() {
  stopStatusPolling()
  const path = route.path
  for (const s of statuses.value) {
    if (s.pages.some(p => path === p || path.startsWith(p))) {
      // 立即执行一次
      s.load().then(v => { s.value.value = v })
      // 定时轮询
      const timer = setInterval(async () => {
        s.value.value = await s.load()
      }, s.fetchInterval)
      pollingTimers.push(timer)
    }
  }
}

function stopStatusPolling() {
  for (const t of pollingTimers) clearInterval(t)
  pollingTimers = []
}

// 路由变化时重新轮询
watch(() => route.path, () => { startStatusPolling() })

const visibleStatuses = computed(() => {
  const path = route.path
  return statuses.value.filter(s =>
    s.pages.some(p => path === p || path.startsWith(p))
  )
})

function handleLogout() {
  logout()
  router.push('/')
}

</script>

<style scoped>
.top-status-bar {
  height: 40px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  font-size: 12px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.status-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.page-title {
  font-weight: 500;
  color: var(--color-text-1);
}

.status-center {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--color-text-3);
  cursor: default;
}

.status-icon {
  width: 14px;
  height: 14px;
}

.status-value {
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  color: var(--color-text-2);
}

.status-label {
  font-size: 11px;
}

.status-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.current-time {
  color: var(--color-text-3);
  font-variant-numeric: tabular-nums;
}

.avatar-wrap {
  cursor: pointer;
}

.avatar-circle,
.avatar-img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.avatar-circle {
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .status-center {
    display: none;
  }
}
</style>
