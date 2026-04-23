<template>
  <div class="cloud-workspace">
    <!-- 左侧侧边栏 -->
    <aside class="workspace-sidebar">
      <div class="sidebar-header">
        <icon-cloud class="sidebar-logo" />
        <h2>云训练</h2>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.name === item.name }"
        >
          <component :is="item.icon" class="nav-icon" />
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
          <!-- 运行状态指示器 -->
          <div v-if="item.status" class="status-indicator" :class="item.status">
            <div class="status-dot"></div>
          </div>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="resource-stats">
          <div class="stat-item">
            <span class="stat-label">运行中任务</span>
            <span class="stat-value">{{ runningJobsCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">GPU 实例</span>
            <span class="stat-value">{{ runningInstancesCount }}</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- 右侧主内容区 -->
    <main class="workspace-main">
      <div class="main-header">
        <h1>{{ currentPageTitle }}</h1>
        <div class="header-actions">
          <!-- 刷新按钮（所有页面通用） -->
          <a-button type="text" size="small" @click="refreshCurrentPage" :loading="refreshing">
            <template #icon><icon-refresh /></template>
            刷新
          </a-button>
          <!-- 创建按钮（仅任务页显示） -->
          <a-button v-if="isTasksPage" type="primary" size="small" @click="$emit('createJob')">
            <template #icon><icon-plus /></template>
            新建训练
          </a-button>
        </div>
      </div>
      <div class="main-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  IconCloud,
  IconServer,
  IconDatabase,
  IconGitBranch,
  IconFileArchive,
  IconRefresh,
  IconPlus,
} from '@arco-design/web-vue/es/icon'

const route = useRoute()
const router = useRouter()

const refreshing = ref(false)

// 导航项配置
const navItems = [
  {
    path: '/ops/cloud/tasks',
    name: 'cloud-tasks',
    label: '训练任务',
    icon: IconServer,
    status: ref('running'), // 暂时模拟有运行中的任务
  },
  {
    path: '/ops/cloud/datasets',
    name: 'cloud-datasets',
    label: '数据集',
    icon: IconDatabase,
  },
  {
    path: '/ops/cloud/repos',
    name: 'cloud-repos',
    label: '代码仓库',
    icon: IconGitBranch,
  },
  {
    path: '/ops/cloud/artifacts',
    name: 'cloud-artifacts',
    label: '制品中心',
    icon: IconFileArchive,
  },
]

// 统计数据（模拟）
const runningJobsCount = ref(2)
const runningInstancesCount = ref(3)

// 当前页面标题
const currentPageTitle = computed(() => {
  const currentItem = navItems.find(item => item.name === route.name)
  return currentItem?.label || '云训练'
})

const isTasksPage = computed(() => route.name === 'cloud-tasks')

// 刷新当前页面数据
function refreshCurrentPage() {
  refreshing.value = true
  // 触发子组件刷新事件（后续通过事件总线或 provide/inject 实现）
  setTimeout(() => {
    refreshing.value = false
  }, 500)
}

// 页面加载时获取真实统计
onMounted(() => {
  // 后续实现：调用API获取真实的运行中任务和实例数量
})
</script>

<style scoped>
.cloud-workspace {
  display: flex;
  min-height: calc(100vh - 64px);
  gap: 24px;
  padding: 24px;
  background: #f7f8fa;
}

/* 侧边栏样式 */
.workspace-sidebar {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.sidebar-logo {
  font-size: 32px;
  color: #165dff;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  color: #4e5969;
  text-decoration: none;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(22, 93, 255, 0.06);
  color: #165dff;
}

.nav-item.active {
  background: rgba(22, 93, 255, 0.1);
  color: #165dff;
  font-weight: 500;
}

.nav-icon {
  font-size: 20px;
}

.nav-label {
  flex: 1;
  font-size: 14px;
}

.nav-badge {
  padding: 2px 8px;
  background: #f53f3f;
  color: white;
  border-radius: 10px;
  font-size: 12px;
}

/* 状态指示器 */
.status-indicator {
  width: 8px;
  height: 8px;
  position: relative;
}

.status-indicator.running .status-dot {
  width: 100%;
  height: 100%;
  background: #00b42a;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 0 0 rgba(0, 180, 42, 0.4);
  }
  50% {
    opacity: 0.7;
    box-shadow: 0 0 0 6px rgba(0, 180, 42, 0);
  }
}

.status-indicator.success .status-dot {
  background: #00b42a;
  border-radius: 50%;
}

.status-indicator.error .status-dot {
  background: #f53f3f;
  border-radius: 50%;
}

.sidebar-footer {
  margin-top: auto;
  padding: 20px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.resource-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 13px;
  color: #86909c;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

/* 主内容区 */
.workspace-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.main-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #1d2129;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.main-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 24px;
  min-height: 0;
}
</style>
