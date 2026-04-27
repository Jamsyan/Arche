<template>
  <div class="admin-layout">
    <!-- 顶部导航栏 -->
    <header class="layout-header">
      <div class="header-left">
        <button class="menu-toggle" @click="toggleSidebar">
          <MenuOutline />
        </button>
        <div class="logo">
          <h3>Arche 管理后台</h3>
        </div>
      </div>
      <div class="header-right">
        <div class="header-actions">
          <span class="admin-badge">管理员</span>
        </div>
        <div class="user-info" @click="showUserMenu = !showUserMenu">
          <span class="username">{{ userStore.userInfo?.username || '管理员' }}</span>
          <PersonCircleOutline class="avatar" />
        </div>
        <!-- 用户下拉菜单 -->
        <div v-if="showUserMenu" class="user-menu">
          <div class="menu-item" @click="goToHome"><HomeOutline /> 回到首页</div>
          <div class="menu-item" @click="handleLogout"><LogOutOutline /> 退出登录</div>
        </div>
      </div>
    </header>

    <div class="layout-body">
      <!-- 侧边栏 -->
      <aside class="layout-sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
        <nav class="sidebar-nav">
          <div class="nav-group">
            <span v-if="!sidebarCollapsed" class="nav-group-title">系统管理</span>
            <RouterLink
              v-for="item in adminMenu"
              :key="item.path"
              :to="item.path"
              class="nav-item"
              :class="{ 'nav-item-active': $route.path.startsWith(item.path) }"
            >
              <component :is="item.icon" class="nav-icon" />
              <span v-if="!sidebarCollapsed" class="nav-text">{{ item.title }}</span>
            </RouterLink>
          </div>
        </nav>
      </aside>

      <!-- 主内容区 -->
      <main class="layout-content">
        <div class="content-header">
          <!-- 面包屑 -->
          <div class="breadcrumb">
            <span v-for="(item, index) in breadcrumb" :key="index">
              {{ item }}
              <span v-if="index < breadcrumb.length - 1" class="separator">/</span>
            </span>
          </div>
          <!-- 操作栏 -->
          <div class="content-actions">
            <slot name="actions" />
          </div>
        </div>
        <div class="content-body">
          <slot />
          <!-- 页面内容在这里 -->
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  MenuOutline,
  PersonCircleOutline,
  HomeOutline,
  LogOutOutline,
  PeopleOutline,
  AppsOutline
} from '@/icons'
import { useUserStore } from '@/store/modules/user'
import { useAppStore } from '@/store/modules/app'
import { $message } from '@/utils/message'

const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

const sidebarCollapsed = computed(() => appStore.sidebarCollapsed)
const showUserMenu = ref(false)

// 管理员侧边栏菜单
const adminMenu = [
  {
    title: '用户管理',
    path: '/admin/users',
    icon: PeopleOutline
  },
  {
    title: '插件管理',
    path: '/admin/plugins',
    icon: AppsOutline
  }
]

// 面包屑计算
const breadcrumb = computed(() => {
  const path = router.currentRoute.value.path
  if (path.startsWith('/admin/users')) return ['管理后台', '用户管理']
  if (path.startsWith('/admin/plugins')) return ['管理后台', '插件管理']
  return ['管理后台']
})

// 切换侧边栏
const toggleSidebar = () => {
  appStore.toggleSidebar()
}

// 回到首页
const goToHome = () => {
  router.push('/')
  showUserMenu.value = false
}

// 退出登录
const handleLogout = async () => {
  await userStore.logout()
  $message.success('退出登录成功')
  router.push('/login')
  showUserMenu.value = false
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: var(--bg-gradient-light);
  color: var(--text-primary);
}

.layout-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-toggle {
  width: 36px;
  height: 36px;
  border: none;
  background: var(--glass-bg);
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.menu-toggle:hover {
  background: var(--glass-bg-hover);
}

.logo h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-color);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
}

.header-actions {
  display: flex;
  align-items: center;
}

.admin-badge {
  background: color-mix(in srgb, var(--success-color) 14%, transparent);
  border: 1px solid color-mix(in srgb, var(--success-color) 45%, transparent);
  color: var(--success-color);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.3s ease;
}

.user-info:hover {
  background: var(--glass-bg-hover);
}

.username {
  font-weight: 500;
  font-size: 14px;
}

.avatar {
  font-size: 24px;
  color: var(--text-secondary);
}

.user-menu {
  position: absolute;
  top: 52px;
  right: 0;
  background: var(--glass-bg);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-lg);
  min-width: 160px;
  padding: 8px 0;
  z-index: 200;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.3s ease;
  font-size: 14px;
}

.menu-item:hover {
  background: var(--glass-bg-hover);
}

.layout-body {
  display: flex;
  padding-top: 64px;
  min-height: calc(100vh - 64px);
}

.layout-sidebar {
  width: 240px;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border-right: 1px solid var(--border-color);
  transition: width 0.3s ease;
  position: fixed;
  top: 64px;
  bottom: 0;
  left: 0;
  overflow-y: auto;
}

.layout-sidebar.sidebar-collapsed {
  width: 64px;
}

.sidebar-nav {
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-group {
  margin-bottom: 16px;
}

.nav-group-title {
  display: block;
  padding: 8px 24px;
  font-size: 12px;
  color: var(--text-tertiary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin: 0 8px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.nav-item:hover {
  background: var(--glass-bg-hover);
  color: var(--primary-color);
}

.nav-item.nav-item-active {
  background: var(--primary-color);
  color: #fff;
}

.nav-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.nav-text {
  flex: 1;
}

.layout-content {
  flex: 1;
  margin-left: 240px;
  transition: margin-left 0.3s ease;
  padding: 24px;
}

.layout-sidebar.sidebar-collapsed + .layout-content {
  margin-left: 64px;
}

.content-header {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  padding: 16px 24px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-md);
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.breadcrumb {
  font-size: 14px;
  color: var(--text-secondary);
}

.breadcrumb .separator {
  margin: 0 8px;
  color: var(--text-tertiary);
}

.content-actions {
  display: flex;
  gap: 12px;
}

.content-body {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-sm);
  min-height: calc(100vh - 210px);
  padding: 24px;
  box-shadow: var(--shadow-md);
}
</style>
