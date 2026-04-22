<template>
  <div class="blog-shell">
    <header class="mac-menubar">
      <!-- 左：Logo + 应用名 -->
      <div class="menubar-left">
        <router-link to="/" class="menubar-brand">
          <img src="/logo.png" alt="锦年志" class="menubar-logo" />
        </router-link>
        <span class="menubar-appname">锦年志</span>
        <span class="menubar-divider"></span>
        <span class="menubar-pagename">{{ currentPageTitle }}</span>
      </div>

      <!-- 中：导航 -->
      <nav class="menubar-center">
        <router-link to="/" class="nav-item" :class="{ active: route.path === '/' }" title="博客首页">
          <icon-home class="nav-icon" />
          <span class="nav-label">首页</span>
        </router-link>
        <template v-if="isAuthenticated">
          <router-link to="/platform" class="nav-item" :class="{ active: route.path === '/platform' }" title="任务中心">
            <icon-apps class="nav-icon" />
            <span class="nav-label">任务</span>
          </router-link>
        </template>
      </nav>

      <!-- 右：时间 + 头像 -->
      <div class="menubar-right">
        <span class="menubar-time">{{ currentTime }}</span>
        <template v-if="!isAuthenticated">
          <a-button shape="circle" class="login-btn" @click="$router.push('/login')">
            <icon-user />
          </a-button>
        </template>
        <template v-else>
          <LevelBadge :level="userLevel" />
          <a-dropdown trigger="click" position="br">
            <div class="avatar-wrap" :class="{ 'has-avatar': avatarUrl }">
              <img v-if="avatarUrl" :src="avatarUrl" alt="avatar" class="avatar-img" />
              <div v-else class="avatar-circle">
                <span class="avatar-letter">{{ userInitial }}</span>
              </div>
            </div>
            <template #content>
              <a-doption @click="$router.push('/platform')">
                <template #icon><icon-apps /></template>
                任务中心
              </a-doption>
              <a-doption @click="handleAvatarChange">
                <template #icon><icon-camera /></template>
                更换头像
              </a-doption>
              <a-doption @click="handleLogout">
                <template #icon><icon-export /></template>
                退出登录
              </a-doption>
            </template>
          </a-dropdown>
          <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileSelected" />
        </template>
      </div>
    </header>
    <main class="blog-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LevelBadge from '../LevelBadge.vue'
import { useAuth } from '../../router/auth.js'
import { Message } from '@arco-design/web-vue'
import {
  IconUser, IconHome, IconApps, IconExport, IconCamera,
} from '@arco-design/web-vue/es/icon'

const route = useRoute()
const router = useRouter()
const { level, user, isAuthenticated, logout, loadUser } = useAuth()

const userLevel = computed(() => level.value ?? 5)
const userInitial = computed(() => user.value?.username ? user.value.username[0].toUpperCase() : 'U')

const avatarUrl = ref(localStorage.getItem('veil_avatar') || '')
const fileInput = ref(null)
const currentTime = ref('')

const PAGE_TITLES = {
  '/': '博客',
  '/login': '登录',
  '/register': '注册',
}

const currentPageTitle = computed(() => {
  const path = route.path
  if (PAGE_TITLES[path]) return PAGE_TITLES[path]
  if (route.path.startsWith('/post/')) return '文章'
  return '锦年志'
})

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
updateClock()
const clockTimer = setInterval(updateClock, 10000)

onUnmounted(() => {
  clearInterval(clockTimer)
})

function handleLogout() { logout(); router.push('/') }
function handleAvatarChange() { fileInput.value?.click() }
function onFileSelected(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) { Message.warning('头像图片不能超过 2MB'); return }
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarUrl.value = e.target.result
    localStorage.setItem('veil_avatar', e.target.result)
  }
  reader.readAsDataURL(file)
  event.target.value = ''
}

onMounted(() => {
  const saved = localStorage.getItem('veil_avatar')
  if (saved) avatarUrl.value = saved
})
</script>

<style scoped>
.blog-shell { min-height: 100vh; display: flex; flex-direction: column; }

/* ===== macOS Menu Bar 风格 ===== */
.mac-menubar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  padding: 0 16px;
  height: 38px;
  background: rgba(255,255,255,0.72);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(0,0,0,0.08);
  position: sticky;
  top: 0;
  z-index: 200;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.menubar-left {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 180px;
}

.menubar-brand {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.menubar-logo {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.08);
  box-shadow: 0 1px 3px rgba(0,0,0,0.12);
}

.menubar-appname {
  font-family: 'Ma Shan Zheng', cursive;
  font-size: 16px;
  font-weight: 400;
  color: var(--color-text-1);
}

.menubar-divider {
  width: 1px;
  height: 16px;
  background: var(--color-border-2);
  margin: 0 4px;
}

.menubar-pagename {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-2);
}

.menubar-center {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 6px;
  text-decoration: none;
  color: var(--color-text-3);
  transition: background 0.12s, color 0.12s;
  font-size: 12px;
  line-height: 1;
}

.nav-item:hover {
  background: rgba(0,0,0,0.06);
  color: var(--color-text-1);
  text-decoration: none;
}

.nav-item.active {
  background: rgba(0,0,0,0.08);
  color: var(--color-text-1);
  font-weight: 500;
}

.nav-icon { width: 14px; height: 14px; }
.nav-label { white-space: nowrap; }

.menubar-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  min-width: 180px;
}

.menubar-time {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-3);
  font-variant-numeric: tabular-nums;
}

.login-btn :deep(.arco-btn) {
  width: 26px; height: 26px; padding: 0; border-radius: 50%;
  background: var(--color-fill-2);
  border: 1.5px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  display: flex; align-items: center; justify-content: center;
}

.login-btn :deep(.arco-btn:hover) { background: var(--color-fill-3); }

.avatar-wrap { cursor: pointer; }

.avatar-circle {
  width: 26px; height: 26px; border-radius: 50%;
  background: var(--color-primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600;
  border: 1.5px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
  transition: box-shadow 0.15s;
}

.avatar-wrap:hover .avatar-circle { box-shadow: 0 2px 8px rgba(0,0,0,0.2); }

.avatar-img {
  width: 26px; height: 26px; border-radius: 50%; object-fit: cover;
  border: 1.5px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
  transition: box-shadow 0.15s;
}

.avatar-wrap:hover .avatar-img { box-shadow: 0 2px 8px rgba(0,0,0,0.2); }

.blog-main { flex: 1; max-width: 1280px; width: 100%; margin: 0 auto; padding: 20px 24px; }

@media (max-width: 768px) {
  .menubar-left { min-width: auto; }
  .menubar-pagename { display: none; }
  .menubar-right { min-width: auto; gap: 6px; }
  .menubar-time { display: none; }
  .nav-label { display: none; }
}
</style>
