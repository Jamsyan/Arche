<template>
  <aside class="sidebar" :class="{ collapsed: !expanded }">
    <!-- 折叠按钮 -->
    <div class="sidebar-toggle" @click="toggleSidebar">
      <icon-menu-unfold v-if="!expanded" />
      <icon-menu-fold v-else />
    </div>

    <div class="sidebar-content">
      <!-- 监控大屏入口（固定） -->
      <div class="sidebar-section monitor-section">
        <router-link to="/monitor" class="sidebar-item monitor-item">
          <icon-dashboard class="sidebar-icon" />
          <span v-if="expanded" class="sidebar-label">监控大屏</span>
        </router-link>
      </div>

      <!-- 用户区 -->
      <div v-if="hasUserSection" class="sidebar-section user-section">
        <div
          v-for="item in userItems"
          :key="item.id"
          class="sidebar-item"
          :class="{ active: isActive(item) }"
          @click="navigate(item)"
        >
          <component :is="getIcon(item.icon)" class="sidebar-icon" />
          <span v-if="expanded" class="sidebar-label">{{ item.name }}</span>
        </div>
      </div>

      <!-- 插件区（可排序） -->
      <div v-if="pluginItems.length > 0" class="sidebar-section plugins-section">
        <div v-if="expanded" class="section-title">插件</div>
        <div
          v-for="item in sortedPluginItems"
          :key="item.id"
          class="sidebar-item"
          :class="{ active: isActive(item) }"
          @click="navigate(item)"
          :draggable="expanded"
          @dragstart="onDragStart($event, item)"
          @dragover.prevent
          @drop="onDrop($event, item)"
        >
          <component :is="getIcon(item.icon)" class="sidebar-icon" />
          <span v-if="expanded" class="sidebar-label">{{ item.name }}</span>
        </div>
      </div>

      <!-- 运维区（P0 专用） -->
      <div v-if="hasOpsSection" class="sidebar-section ops-section">
        <div v-if="expanded" class="section-title">运维</div>
        <div
          v-for="item in opsItems"
          :key="item.id"
          class="sidebar-item"
          :class="{ active: isActive(item) }"
          @click="navigate(item)"
        >
          <component :is="getIcon(item.icon)" class="sidebar-icon" />
          <span v-if="expanded" class="sidebar-label">{{ item.name }}</span>
        </div>
      </div>

      <!-- 底部：账号管理（固定） -->
      <div class="sidebar-footer">
        <div class="sidebar-divider"></div>
        <div
          class="sidebar-item"
          :class="{ active: route.path === '/account' }"
          @click="$router.push('/account')"
        >
          <icon-user class="sidebar-icon" />
          <span v-if="expanded" class="sidebar-label">账号</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSidebarStore } from '../../stores/sidebar.js'
import { usePluginRegistry } from '../../stores/pluginRegistry.js'
import { useAuth } from '../../router/auth.js'
import {
  IconMenuUnfold,
  IconMenuFold,
  IconDashboard,
  IconUser,
  IconHome,
  IconEdit,
  IconFolder,
  IconCommon,
  IconSettings,
  IconTool,
  IconApps,
  IconBug,
  IconCloud,
  IconGithub,
  IconSafe,
  IconUpload,
  IconStorage,
} from '@arco-design/web-vue/es/icon'

const route = useRoute()
const router = useRouter()
const sidebarStore = useSidebarStore()
const pluginRegistry = usePluginRegistry()
const { level, isAuthenticated } = useAuth()

// 用户角色
const userRole = computed(() => {
  if (!isAuthenticated.value) return null
  const lvl = level.value
  if (lvl === 0) return 'P0'
  if (lvl === 1) return 'P1'
  if (lvl === 2) return 'P2'
  if (lvl === 3) return 'P3'
  if (lvl === 4) return 'P4'
  return 'P4'
})

// 展开/收起
const expanded = computed(() => sidebarStore.expanded)
function toggleSidebar() {
  sidebarStore.toggle()
}

// 获取分类后的侧边栏项
const categorized = computed(() => pluginRegistry.categorizedSidebar)

// 获取用户可访问的所有侧边栏项
const allSidebarItems = computed(() => {
  return pluginRegistry.getSidebarByRole(userRole.value)
})

// 插件项（可排序）
const pluginItems = computed(() => {
  return allSidebarItems.value.filter(item => item.category === 'plugin')
})

// 运维项
const opsItems = computed(() => {
  return allSidebarItems.value.filter(item => item.category === 'ops')
})

// 用户项
const userItems = computed(() => [
  { id: 'blog', name: '博客首页', route: '/', icon: 'home' },
  { id: 'platform', name: '任务中心', route: '/platform', icon: 'apps' },
])

// 是否有用户区
const hasUserSection = computed(() => true)  // 始终显示
// 是否有运维区（根据用户权限显示）
const hasOpsSection = computed(() => opsItems.value.length > 0)

// 根据排序后的顺序展示插件
const sortedPluginItems = computed(() => {
  const order = sidebarStore.pluginOrder
  if (!order || order.length === 0) return pluginItems.value

  return [...pluginItems.value].sort((a, b) => {
    const aIdx = order.indexOf(a.id)
    const bIdx = order.indexOf(b.id)
    if (aIdx === -1 && bIdx === -1) return 0
    if (aIdx === -1) return 1
    if (bIdx === -1) return -1
    return aIdx - bIdx
  })
})

// 判断是否激活
function isActive(item) {
  if (item.route === '/') return route.path === '/'
  return route.path.startsWith(item.route)
}

// 导航
function navigate(item) {
  router.push(item.route)
}

// 获取图标组件
const iconMap = {
  home: IconHome,
  edit: IconEdit,
  folder: IconFolder,
  common: IconCommon,
  settings: IconSettings,
  tool: IconTool,
  apps: IconApps,
  dashboard: IconDashboard,
  user: IconUser,
  bug: IconBug,
  cloud: IconCloud,
  github: IconGithub,
  safe: IconSafe,
  upload: IconUpload,
  storage: IconStorage,
}

function getIcon(iconName) {
  return iconMap[iconName] || IconApps
}

// 拖拽排序
const draggingItem = ref(null)

function onDragStart(event, item) {
  draggingItem.value = item
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', item.id)
}

function onDrop(event, targetItem) {
  if (!draggingItem.value || draggingItem.value.id === targetItem.id) return

  const order = [...sidebarStore.pluginOrder]
  const fromIdx = order.indexOf(draggingItem.value.id)
  const toIdx = order.indexOf(targetItem.id)

  if (fromIdx >= 0) {
    order.splice(fromIdx, 1)
  }
  order.splice(toIdx, 0, draggingItem.value.id)

  sidebarStore.updatePluginOrder(order)
  draggingItem.value = null
}
</script>

<style scoped>
.sidebar {
  width: 200px;
  height: 100vh;
  background: var(--color-bg-2);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: width 0.2s ease;
  position: sticky;
  top: 0;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 56px;
}

.sidebar-toggle {
  padding: 12px;
  display: flex;
  justify-content: flex-end;
  cursor: pointer;
  color: var(--color-text-3);
  font-size: 16px;
  margin: auto;
}

.sidebar-toggle:hover {
  color: var(--color-text-1);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

.sidebar-section {
  margin-bottom: 16px;
}

.section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 4px 8px;
  margin-bottom: 4px;
}

.sidebar-divider {
  height: 1px;
  background: var(--color-border);
  margin: 8px 0;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--color-text-2);
  transition: all 0.15s ease;
  text-decoration: none;
  font-size: 14px;
}

.sidebar-item:hover {
  background: var(--color-fill-2);
  color: var(--color-text-1);
}

.sidebar-item.active {
  background: var(--color-primary-light-1);
  color: var(--color-primary);
  font-weight: 500;
}

.sidebar-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.sidebar-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.monitor-item {
  background: var(--color-primary-light-2);
  color: var(--color-primary);
  font-weight: 500;
}

.monitor-item:hover {
  background: var(--color-primary-light-1);
}

.sidebar.collapsed .sidebar-item {
  justify-content: center;
  padding: 10px;
}

.sidebar.collapsed .section-title {
  display: none;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 8px;
}

.sidebar-divider {
  height: 1px;
  background: var(--color-border-1);
  margin: 8px 0;
}
</style>
