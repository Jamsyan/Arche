<template>
  <div class="user-layout" :class="{ 'is-mobile': appStore.isMobile }">
    <!-- 顶部导航栏 -->
    <header class="layout-header">
      <div class="header-left">
        <button class="menu-toggle" @click="toggleSidebar">
          <MenuOutline />
        </button>
        <div class="logo">
          <h3>Arche</h3>
        </div>
      </div>
      <div class="header-right">
        <div class="user-info" @click="showUserMenu = !showUserMenu">
          <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
          <PersonCircleOutline class="avatar" />
        </div>
        <!-- 用户下拉菜单 -->
        <div v-if="showUserMenu" class="user-menu">
          <div class="menu-item" @click="goToProfile"><PersonOutline /> 个人中心</div>
          <div class="menu-item" @click="handleLogout"><LogOutOutline /> 退出登录</div>
        </div>
      </div>
    </header>

    <div class="layout-body">
      <!-- 侧边栏 -->
      <aside
        class="layout-sidebar"
        :class="{
          'sidebar-collapsed': sidebarCollapsed,
          'sidebar-open': appStore.isMobile && !sidebarCollapsed
        }"
      >
        <nav class="sidebar-nav">
          <RouterLink
            v-for="item in userMenu"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ 'nav-item-active': $route.path === item.path }"
          >
            <component :is="item.icon" class="nav-icon" />
            <span v-if="!sidebarCollapsed" class="nav-text">{{ item.title }}</span>
          </RouterLink>
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
  PersonOutline,
  LogOutOutline,
  HomeOutline
} from '@/icons'
import { useUserStore } from '@/store/modules/user'
import { useAppStore } from '@/store/modules/app'
import { usePermissionStore } from '@/store/modules/permission'
import { $message } from '@/utils/message'
import { buildLayoutMenus } from '@/router/menu'

const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()
const permissionStore = usePermissionStore()

const sidebarCollapsed = computed(() => appStore.sidebarCollapsed)
const showUserMenu = ref(false)

const userMenu = computed(() => {
  const menus = buildLayoutMenus(permissionStore.routes, 'user')
  const homeMenu = {
    title: '首页',
    path: '/',
    icon: HomeOutline
  }
  return [homeMenu, ...menus]
})

// 面包屑计算
const breadcrumb = computed(() => {
  const path = router.currentRoute.value.path
  if (path === '/') return ['首页']
  const currentMenu = userMenu.value.find((item) => item.path === path)
  if (currentMenu) {
    return ['首页', currentMenu.title]
  }
  return ['首页', '页面']
})

// 切换侧边栏
const toggleSidebar = () => {
  appStore.toggleSidebar()
}

// 跳转到个人中心
const goToProfile = () => {
  router.push('/profile')
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
.user-layout {
  min-height: 100vh;
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
  border-bottom: var(--glass-border);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.menu-toggle {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255, 250, 241, 0.76);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.menu-toggle:hover {
  background: rgba(239, 227, 207, 0.92);
  transform: scale(1.05);
}

.logo h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  background: var(--bg-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-right {
  display: flex;
  align-items: center;
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(239, 227, 207, 0.82);
}

.username {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-secondary);
}

.avatar {
  font-size: 24px;
  color: var(--primary-color);
}

.user-menu {
  position: absolute;
  top: 52px;
  right: 0;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  border-radius: var(--radius-lg);
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
  transition: all 0.3s ease;
  font-size: 14px;
  color: var(--text-secondary);
}

.menu-item:hover {
  background: var(--primary-light-color);
  color: var(--primary-color);
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
  border-right: var(--glass-border);
  transition: width 0.3s ease;
  position: fixed;
  top: 64px;
  bottom: 0;
  overflow-y: auto;
}

.layout-sidebar.sidebar-collapsed {
  width: 64px;
}

.sidebar-nav {
  padding: var(--spacing-md) 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin: 0 8px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.nav-item:hover {
  background: var(--primary-light-color);
  color: var(--primary-color);
  transform: translateX(4px);
}

.nav-item.nav-item-active {
  background: var(--primary-color);
  color: white;
  box-shadow: var(--shadow-md);
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
  padding: var(--spacing-lg);
}

.layout-sidebar.sidebar-collapsed + .layout-content {
  margin-left: 64px;
}

.user-layout.is-mobile .layout-sidebar {
  width: 220px;
  transform: translateX(-100%);
  z-index: 250;
}

.user-layout.is-mobile .layout-sidebar.sidebar-open {
  transform: translateX(0);
}

.user-layout.is-mobile .layout-content,
.user-layout.is-mobile .layout-sidebar.sidebar-collapsed + .layout-content {
  margin-left: 0;
}

.content-header {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--spacing-lg);
}

.breadcrumb {
  font-size: 14px;
  color: var(--text-secondary);
}

.breadcrumb .separator {
  margin: 0 var(--spacing-sm);
  color: var(--text-tertiary);
}

.content-body {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  border-radius: var(--radius-lg);
  min-height: calc(100vh - 210px);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

/* 滚动条样式 */
.layout-sidebar::-webkit-scrollbar {
  width: 4px;
}

.layout-sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.layout-sidebar::-webkit-scrollbar-thumb {
  background: rgba(154, 90, 47, 0.22);
  border-radius: 2px;
}

.layout-sidebar::-webkit-scrollbar-thumb:hover {
  background: rgba(154, 90, 47, 0.34);
}
</style>
