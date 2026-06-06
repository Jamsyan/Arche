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
      <span v-if="layoutMode === 'admin'" class="admin-badge">管理员</span>
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
        <RouterLink v-if="isLoggedIn" to="/scheduler" class="nav-item">调度器</RouterLink>
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

    <!-- Header Right — 头像 / 控制台 / 登录 -->
    <div class="header-right">
      <!-- 用户头像（guest 已登录时在控制台旁边） -->
      <div v-if="isLoggedIn && layoutMode === 'guest'" class="user-menu-wrap">
        <button class="avatar-btn" @click="showUserMenu = !showUserMenu" aria-label="用户菜单">
          <NIcon size="20"><PersonCircleOutline /></NIcon>
        </button>
        <div v-if="showUserMenu" class="user-dropdown" @click="showUserMenu = false">
          <RouterLink to="/profile" class="dropdown-item">个人中心</RouterLink>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item logout-item" @click="handleLogout">退出登录</button>
        </div>
      </div>
      <div v-if="layoutMode === 'guest'" class="header-actions">
        <RouterLink v-if="isLoggedIn" to="/console" class="nav-item">控制台</RouterLink>
        <template v-else>
          <a :href="repoUrl" target="_blank" rel="noopener noreferrer" class="nav-item">加入我们</a>
          <RouterLink to="/login" class="nav-item login-btn">登录</RouterLink>
        </template>
      </div>
      <div v-else class="user-menu-wrap">
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
import { SearchOutline, MenuOutline, PersonCircleOutline } from '@vicons/ionicons5'
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

/* ── Header Actions (right side) ── */
.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  flex-shrink: 0;
}

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

/* ── Admin Badge ── */
.admin-badge {
  background: color-mix(in srgb, var(--success-color) 14%, transparent);
  border: 1px solid color-mix(in srgb, var(--success-color) 45%, transparent);
  color: var(--success-color);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
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
  right: 0;
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
</style>
