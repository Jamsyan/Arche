<template>
  <header
    class="base-header"
    :class="[`base-header--${layoutMode}`, { 'is-mobile': appStore.isMobile }]"
  >
    <!-- Header Left -->
    <div class="header-left">
      <button
        v-if="layoutMode !== 'guest'"
        class="menu-toggle"
        @click="$emit('toggle-sidebar')"
        aria-label="切换侧边栏"
      >
        <NIcon size="20"><MenuOutline /></NIcon>
      </button>
      <SiteLogo size="md" />
    </div>

    <!-- Header Center — guest 模式下的导航 + 搜索 -->
    <div v-if="layoutMode === 'guest'" class="header-center">
      <nav class="nav-menu">
        <RouterLink to="/" class="nav-item" :class="{ active: $route.path === '/' }"
          >首页</RouterLink
        >
        <RouterLink to="/explore" class="nav-item">探索</RouterLink>
        <RouterLink v-if="isLoggedIn" to="/create" class="nav-item">创作</RouterLink>
        <RouterLink v-if="isLoggedIn" to="/assets" class="nav-item">素材库</RouterLink>
        <RouterLink v-if="isLoggedIn" to="/tasks" class="nav-item">托管任务</RouterLink>
        <RouterLink to="/github" class="nav-item">GitHub</RouterLink>
      </nav>
      <div class="search-section">
        <div class="search-wrap">
          <NIcon class="search-leading-icon" size="17" aria-hidden="true">
            <SearchOutline />
          </NIcon>
          <input
            v-model.trim="searchKeyword"
            class="search-input"
            type="search"
            placeholder="搜索"
            aria-label="搜索文章"
            @keydown.enter="goSearch"
          />
        </div>
      </div>
    </div>

    <!-- Header Center — user/admin 模式下的面包屑 -->
    <div v-else class="header-center">
      <div class="breadcrumb">
        <span v-for="(item, index) in breadcrumb" :key="index">
          {{ item }}
          <span v-if="index < breadcrumb.length - 1" class="breadcrumb-sep">/</span>
        </span>
      </div>
    </div>

    <!-- Header Right — 整体组切换（mode="out-in" 避免双元素并发导致的 reflow 跳变） -->
    <div class="header-right">
      <Transition name="group-swap" mode="out-in">
        <div v-if="layoutMode === 'guest' && !isLoggedIn" key="logged-out" class="logged-out-group">
          <a :href="repoUrl" target="_blank" rel="noopener noreferrer" class="nav-item">加入我们</a>
          <RouterLink to="/login" class="nav-item login-btn">登录</RouterLink>
        </div>
        <div
          v-else-if="isLoggedIn && layoutMode === 'guest'"
          key="logged-in"
          class="logged-in-group"
        >
          <div class="user-menu-wrap">
            <button class="avatar-btn" @click="showUserMenu = !showUserMenu" aria-label="用户菜单">
              <NIcon size="20"><PersonCircleOutline /></NIcon>
            </button>
            <div v-if="showUserMenu" class="user-dropdown" @click="showUserMenu = false">
              <!-- 用户信息头 -->
              <div class="dropdown-header">
                <NIcon size="28" class="dropdown-avatar"><PersonCircleOutline /></NIcon>
                <div class="dropdown-user-info">
                  <span class="dropdown-username">{{
                    userStore.userInfo?.username || '用户'
                  }}</span>
                  <span class="dropdown-email">{{ userStore.userInfo?.email || '' }}</span>
                </div>
              </div>
              <div class="dropdown-stats">
                <div class="stat-cell">
                  <span class="stat-num">--</span>
                  <span class="stat-label">帖子</span>
                </div>
                <div class="stat-cell">
                  <span class="stat-num">--</span>
                  <span class="stat-label">收藏</span>
                </div>
                <div class="stat-cell">
                  <span class="stat-num">--</span>
                  <span class="stat-label">积分</span>
                </div>
              </div>
              <div class="dropdown-divider"></div>
              <RouterLink to="/profile" class="dropdown-item">
                <NIcon size="16"><PersonOutline /></NIcon>
                <span>个人中心</span>
              </RouterLink>
              <RouterLink v-if="isAdmin" to="/console" class="dropdown-item">
                <NIcon size="16"><SettingsOutline /></NIcon>
                <span>控制台</span>
              </RouterLink>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item logout-item" @click="handleLogout">
                <NIcon size="16"><LogOutOutline /></NIcon>
                <span>退出登录</span>
              </button>
            </div>
          </div>
          <RouterLink v-if="isAdmin" to="/console" class="nav-item console-btn">控制台</RouterLink>
        </div>
      </Transition>

      <!-- 其他布局模式下的用户菜单 -->
      <div v-if="layoutMode !== 'guest'" class="user-menu-wrap">
        <button class="user-info-btn" @click="showUserMenu = !showUserMenu" aria-label="用户菜单">
          <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
          <NIcon size="24" class="avatar-icon"><PersonCircleOutline /></NIcon>
        </button>
        <div v-if="showUserMenu" class="user-dropdown">
          <button v-if="layoutMode === 'user'" class="dropdown-item" @click="goToProfile">
            个人中心
          </button>
          <button v-if="layoutMode === 'admin'" class="dropdown-item" @click="goToHome">
            回到首页
          </button>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item logout-item" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import {
  SearchOutline,
  MenuOutline,
  PersonCircleOutline,
  PersonOutline,
  SettingsOutline,
  LogOutOutline
} from '@vicons/ionicons5'
import SiteLogo from '@/components/SiteLogo.vue'
import { useUserStore } from '@/store/modules/user'
import { useAppStore } from '@/store/modules/app'

const props = defineProps<{
  layoutMode: 'guest' | 'user' | 'admin'
}>()

defineEmits<{
  'toggle-sidebar': []
}>()

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const appStore = useAppStore()

const searchKeyword = ref('')
const showUserMenu = ref(false)
const repoUrl = 'https://github.com/jamnodesmith/Arche'

const isLoggedIn = computed(() => userStore.isLoggedIn)
const isAdmin = computed(() => (userStore.userInfo?.level ?? 5) === 0)

const breadcrumb = computed(() => {
  const path = route.path
  const layoutLabel = props.layoutMode === 'admin' ? '管理后台' : '首页'
  if (path === '/') return [layoutLabel]

  const routeName = route.name
  if (routeName && typeof routeName === 'string') {
    return [layoutLabel, routeName]
  }
  return [layoutLabel, '页面']
})

const goSearch = () => {
  router.push({
    path: '/explore',
    query: { q: searchKeyword.value || undefined }
  })
}

const handleLogout = async () => {
  showUserMenu.value = false
  await userStore.logout()
  router.push('/')
}

const goToProfile = () => {
  router.push('/profile')
  showUserMenu.value = false
}

const goToHome = () => {
  router.push('/')
  showUserMenu.value = false
}

const handleClickOutside = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  if (!target.closest('.header-right') && !target.closest('.user-menu-wrap')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.base-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: var(--surface-color);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  padding: 0 var(--content-padding);
  gap: var(--layout-gap);
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

.header-center {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
  position: relative;
}

/* ── Guest Mode: Nav Menu ── */
.nav-menu {
  display: flex;
  gap: var(--spacing-xs);
  align-items: center;
  flex-shrink: 0;
}

/* ── Menu Toggle ── */
.menu-toggle {
  width: 36px;
  height: 36px;
  border: none;
  background: var(--surface-color);
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: background-color var(--transition-fast);
}

.menu-toggle:hover {
  background: var(--surface-strong-color);
}

/* ── Search Section (centered flex) ── */
.search-section {
  flex: 1;
  display: flex;
  justify-content: center;
  min-width: 0;
}

/* ── Nav Item ── */
.nav-item {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  padding: 8px 14px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  font-size: 14px;
  white-space: nowrap;
}

.nav-item:hover,
.nav-item.active {
  background: var(--primary-light-color);
  color: var(--primary-color);
}

.login-btn {
  background: var(--primary-color);
  color: #fff;
  border-radius: var(--radius-full);
  padding: 8px 18px;
}

.login-btn:hover {
  background: var(--primary-hover-color);
  color: #fff;
}

/* ── 登录后组（头像 + 控制台） ── */
.logged-in-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

/* ── 未登录组（加入我们 + 登录） ── */
.logged-out-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

/* ── Guest Mode: Search ── */
.search-wrap {
  position: relative;
  width: 100%;
  max-width: 480px;
}

.search-input {
  width: 100%;
  height: 36px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-color);
  background: var(--bg-color);
  padding: 0 14px 0 36px;
  color: var(--text-primary);
  outline: none;
  font-size: 13px;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
}

.search-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-light-color);
  background: var(--surface-color);
}

.search-leading-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
  z-index: 1;
}

.search-wrap:focus-within .search-leading-icon {
  color: var(--primary-color);
}

/* ── Breadcrumb ── */
.breadcrumb {
  font-size: 14px;
  color: var(--text-secondary);
}

.breadcrumb-sep {
  margin: 0 var(--spacing-sm);
  color: var(--text-tertiary);
}

/* ── User Menu (guest) ── */
.avatar-btn {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  font-size: 13px;
  background: var(--surface-color);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.avatar-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

/* ── User Info Button (user/admin) ── */
.user-info-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
  border: none;
  background: transparent;
  color: inherit;
  font: inherit;
}

.user-info-btn:hover {
  background: var(--surface-strong-color);
}

.username {
  font-weight: var(--font-weight-medium);
  font-size: 14px;
  color: var(--text-secondary);
}

.avatar-icon {
  color: var(--primary-color);
}

/* ── User Dropdown ── */
.user-menu-wrap {
  position: relative;
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  min-width: 150px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  z-index: 300;
  overflow: hidden;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 9px 14px;
  font-size: 13px;
  color: var(--text-primary);
  text-decoration: none;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background var(--transition-fast);
  font-family: inherit;
}

.dropdown-item:hover {
  background: var(--primary-light-color);
  color: var(--primary-color);
}

.logout-item:hover {
  color: var(--error-color);
}

.dropdown-divider {
  height: 1px;
  background: var(--divider-color);
  margin: 4px 0;
}

/* ── Dropdown Header ── */
.dropdown-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--divider-color);
}

.dropdown-avatar {
  color: var(--primary-color);
  flex-shrink: 0;
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.dropdown-username {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.dropdown-email {
  font-size: 11px;
  color: var(--text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ── Dropdown Stats ── */
.dropdown-stats {
  display: flex;
  padding: 10px 14px;
  border-bottom: 1px solid var(--divider-color);
}

.stat-cell {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}

.stat-num {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 10px;
  color: var(--text-tertiary);
}

/* ── Dropdown items with icons ── */
.dropdown-item {
  display: flex !important;
  align-items: center;
  gap: 8px;
}

/* ── Responsive ── */
@media (max-width: 992px) {
  .base-header--guest .header-center {
    gap: var(--spacing-sm);
  }

  .base-header--guest .nav-menu {
    gap: 2px;
  }

  .base-header--guest .nav-item {
    padding: 6px 10px;
    font-size: 13px;
  }

  .search-wrap {
    max-width: 300px;
  }
}

/* ── 控制台按钮基础样式 ── */
.console-btn {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  padding: 8px 14px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  font-size: 14px;
  white-space: nowrap;
}

.console-btn:hover {
  background: var(--primary-light-color);
  color: var(--primary-color);
}

/* ════════════════════════════════════════
   登录转场动画
   单 <Transition mode="out-in"> 先离场后入场
   ════════════════════════════════════════ */

/* ── 旧组（加入我们 + 登录）离场：向左淡出 ── */
.group-swap-leave-active {
  transition: all 0.3s ease;
}
.group-swap-leave-to {
  opacity: 0;
  transform: translateX(-15px);
}

/* ── 新组（头像 + 控制台）入场：从右侧滑入 ── */
.group-swap-enter-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.group-swap-enter-from {
  opacity: 0;
  transform: translateX(25px);
}
</style>
