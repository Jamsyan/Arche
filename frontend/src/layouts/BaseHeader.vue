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
        <RouterLink v-if="isLoggedIn" to="/scheduler" class="nav-item">调度器</RouterLink>
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

    <!-- Header Right — 头像 / 控制台 / 登录 -->
    <div class="header-right">
      <!-- 登录后头像（仅 guest 模式，rAF 驱动从右边缘滑入） -->
      <div v-if="isLoggedIn && layoutMode === 'guest'" ref="avatarRef" class="user-menu-wrap">
        <button class="avatar-btn" @click="showUserMenu = !showUserMenu" aria-label="用户菜单">
          <NIcon size="20"><PersonCircleOutline /></NIcon>
        </button>
        <div v-if="showUserMenu" class="user-dropdown" @click="showUserMenu = false">
          <RouterLink v-if="!isAdmin" to="/profile" class="dropdown-item">个人中心</RouterLink>
          <RouterLink v-if="isAdmin" to="/console" class="dropdown-item">控制台</RouterLink>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item logout-item" @click="handleLogout">退出登录</button>
        </div>
      </div>

      <!-- 加入我们 / 登录（未登录时显示，带动画淡出） -->
      <div
        v-if="layoutMode === 'guest' && (!isLoggedIn || justLoggedIn)"
        ref="loginActionsRef"
        class="header-actions"
        :class="{ 'fade-out': justLoggedIn }"
      >
        <a :href="repoUrl" target="_blank" rel="noopener noreferrer" class="nav-item">加入我们</a>
        <RouterLink to="/login" class="nav-item login-btn">登录</RouterLink>
      </div>

      <!-- 控制台按钮（管理员登录后出现，rAF 驱动淡入） -->
      <RouterLink
        v-if="isLoggedIn && layoutMode === 'guest' && isAdmin"
        ref="consoleBtnRef"
        to="/console"
        class="nav-item console-btn"
      >
        控制台
      </RouterLink>

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
import { computed, ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
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
const isAdmin = computed(() => (userStore.userInfo?.level ?? 5) === 0)

// 模板引用
const avatarRef = ref<HTMLElement | null>(null)
const loginActionsRef = ref<HTMLElement | null>(null)
const consoleBtnRef = ref<HTMLElement | null>(null)

// 控制"加入我们/登录"的淡出
const justLoggedIn = ref(false)

// ── 动画工具：requestAnimationFrame 驱动的线性插值 ──
const easeInOutQuad = (t: number) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t)

const animateRb = (
  el: HTMLElement,
  from: { translateX: number; opacity: number },
  to: { translateX: number; opacity: number },
  duration: number,
  delay: number = 0
): Promise<void> => {
  const startTime = performance.now() + delay

  return new Promise<void>((resolve) => {
    const tick = (now: number) => {
      if (now < startTime) {
        requestAnimationFrame(tick)
        return
      }
      const elapsed = now - startTime
      const raw = Math.min(Math.max(elapsed / duration, 0), 1)
      const progress = easeInOutQuad(raw)

      const x = from.translateX + (to.translateX - from.translateX) * progress
      const opacity = from.opacity + (to.opacity - from.opacity) * progress

      el.style.transform = `translateX(${x}px)`
      el.style.opacity = String(opacity)
      el.style.willChange = 'transform, opacity'

      if (raw < 1) {
        requestAnimationFrame(tick)
      } else {
        el.style.transform = ''
        el.style.opacity = ''
        el.style.willChange = ''
        resolve()
      }
    }
    requestAnimationFrame(tick)
  })
}

// ── 执行整套登录动画 ──
const playLoginAnimation = async () => {
  const avatarEl = avatarRef.value
  const loginEl = loginActionsRef.value
  const consoleEl = consoleBtnRef.value

  if (!avatarEl) return

  // 等 DOM 布局完成
  await nextTick()

  // 计算头像的自然位置到视口右边沿的距离
  const rect = avatarEl.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  // header-right 的内边距 / gap / 到右边沿的距离
  const rightPadding = viewportWidth - rect.right
  // 起始偏移：头像当前位置 + 到右边缘的距离（让头像从右边缘外进来）
  const travelDistance = rightPadding + rect.width + 8

  // 并行动画
  const promises: Promise<void>[] = []

  // ① 头像从右边缘滑入
  avatarEl.style.opacity = '0'
  avatarEl.style.transform = `translateX(${travelDistance}px)`
  avatarEl.style.willChange = 'transform, opacity'
  // 强制重排让初始状态生效
  avatarEl.offsetHeight
  promises.push(
    animateRb(
      avatarEl,
      { translateX: travelDistance, opacity: 0 },
      { translateX: 0, opacity: 1 },
      500
    )
  )

  // ② 加入我们/登录 淡出
  if (loginEl) {
    loginEl.style.willChange = 'transform, opacity'
    promises.push(
      animateRb(loginEl, { translateX: 0, opacity: 1 }, { translateX: -15, opacity: 0 }, 350)
    )
  }

  // ③ 控制台按钮淡入
  if (consoleEl) {
    consoleEl.style.opacity = '0'
    consoleEl.style.transform = 'translateX(8px)'
    consoleEl.style.willChange = 'transform, opacity'
    consoleEl.offsetHeight
    promises.push(
      animateRb(consoleEl, { translateX: 8, opacity: 0 }, { translateX: 0, opacity: 1 }, 400, 120)
    )
  }

  await Promise.all(promises)

  // 动画完成，清理 will-change
  if (avatarEl) {
    avatarEl.style.willChange = ''
  }
  if (loginEl) {
    loginEl.style.transform = ''
    loginEl.style.opacity = ''
    loginEl.style.willChange = ''
  }
  if (consoleEl) {
    consoleEl.style.transform = ''
    consoleEl.style.opacity = ''
    consoleEl.style.willChange = ''
  }

  // 移除登录按钮
  justLoggedIn.value = false
}

// ── 监听登录状态变化 ──
watch(
  () => userStore.isLoggedIn,
  (newVal, oldVal) => {
    if (newVal && !oldVal) {
      justLoggedIn.value = true
      // 等 Vue 渲染出新 DOM（avatar、console-btn 出现在 DOM 中）
      nextTick(() => {
        playLoginAnimation()
      })
    }
  }
)

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

/* ── 加入我们 / 登录 淡出（rAF 尚未接管前防止闪烁） ── */
.header-actions.fade-out {
  animation: fadeOutLeft 0.35s ease forwards;
  pointer-events: none;
}

@keyframes fadeOutLeft {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(-15px);
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
</style>
