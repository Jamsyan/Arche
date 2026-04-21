<template>
  <div class="blog-shell">
    <header class="blog-header">
      <!-- 左：Logo（点击回首页） -->
      <router-link to="/" class="header-brand">
        <img src="/logo.png" alt="Veil" class="logo-img" />
      </router-link>

      <!-- 中：纯线条图标导航 -->
      <nav class="header-center">
        <!-- 博客首页 -->
        <router-link to="/" class="nav-icon-link" :class="{ active: route.path === '/' }" title="博客首页">
          <icon-home class="nav-icon" />
        </router-link>
        <!-- 已登录时显示平台图标 -->
        <template v-if="isAuthenticated">
          <router-link to="/platform" class="nav-icon-link" :class="{ active: route.path === '/platform' }" title="控制台">
            <icon-apps class="nav-icon" />
          </router-link>
          <router-link to="/editor" class="nav-icon-link" :class="{ active: route.path === '/editor' }" title="编辑器">
            <icon-edit class="nav-icon" />
          </router-link>
          <router-link to="/upload" class="nav-icon-link" :class="{ active: route.path === '/upload' }" title="上传">
            <icon-upload class="nav-icon" />
          </router-link>
        </template>
      </nav>

      <!-- 右：头像 -->
      <div class="header-right">
        <!-- 未登录：登录按钮 -->
        <a-button v-if="!isAuthenticated" class="avatar-btn" @click="$router.push('/login')">
          <icon-user />
        </a-button>
        <!-- 已登录：用户头像 + 下拉菜单 -->
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
                <template #icon><icon-user /></template>
                个人中心
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
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            style="display: none"
            @change="onFileSelected"
          />
        </template>
      </div>
    </header>
    <main class="blog-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import LevelBadge from '../LevelBadge.vue'
import { useAuth } from '../../router/auth.js'
import {
  IconUser,
  IconHome,
  IconApps,
  IconEdit,
  IconUpload,
  IconExport,
  IconCamera,
} from '@arco-design/web-vue/es/icon'

const route = useRoute()
const { level, user, isAuthenticated, logout } = useAuth()

const userLevel = computed(() => level.value ?? 5)
const userInitial = computed(() => {
  if (user.value?.username) {
    return user.value.username[0].toUpperCase()
  }
  return 'U'
})

// 头像管理
const avatarUrl = ref(localStorage.getItem('veil_avatar') || '')
const fileInput = ref(null)

function handleLogout() {
  logout()
}

function handleAvatarChange() {
  fileInput.value?.click()
}

function onFileSelected(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    alert('头像图片不能超过 2MB')
    return
  }
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
  if (saved) {
    avatarUrl.value = saved
  }
})
</script>

<style scoped>
.blog-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.blog-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid var(--color-border-1);
  position: sticky;
  top: 0;
  z-index: 100;
  height: 56px;
}

.header-brand { display: flex; align-items: center; text-decoration: none; }
.logo-img {
  width: 36px; height: 36px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08);
  animation: slideFromLeft 0.4s ease-out;
}

.header-center {
  display: flex; justify-content: center; align-items: center; gap: 2px;
}
.nav-icon-link {
  display: flex; align-items: center; justify-content: center;
  width: 38px; height: 38px;
  border-radius: var(--border-radius-medium);
  text-decoration: none;
  transition: background 0.15s;
  flex-shrink: 0;
}
.nav-icon-link:hover { background: var(--color-fill-2); }
.nav-icon-link.active { background: var(--color-fill-3); }
.nav-icon {
  width: 20px; height: 20px;
  color: var(--color-text-3);
}
.nav-icon-link.active .nav-icon { color: var(--color-text-1); }
.nav-icon-link:hover .nav-icon { color: var(--color-text-1); }

.header-right { display: flex; align-items: center; justify-content: flex-end; gap: 10px; }
.avatar-btn :deep(.arco-btn) {
  width: 34px; height: 34px; padding: 0; border-radius: 50%;
  background: var(--color-fill-2);
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15), 0 1px 2px rgba(0,0,0,0.08);
  display: flex; align-items: center; justify-content: center;
  animation: slideFromRight 0.4s ease-out;
}
.avatar-btn :deep(.arco-btn:hover) { background: var(--color-fill-3); }

.avatar-wrap { cursor: pointer; position: relative; }
.avatar-circle {
  width: 34px; height: 34px; border-radius: 50%;
  background: var(--color-primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 600;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15), 0 1px 2px rgba(0,0,0,0.08);
  animation: slideFromRight 0.4s ease-out;
  transition: box-shadow 0.15s;
}
.avatar-wrap:hover .avatar-circle { box-shadow: 0 4px 12px rgba(0,0,0,0.25); }
.avatar-img {
  width: 34px; height: 34px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15), 0 1px 2px rgba(0,0,0,0.08);
  animation: slideFromRight 0.4s ease-out;
  transition: box-shadow 0.15s;
}
.avatar-wrap:hover .avatar-img { box-shadow: 0 4px 12px rgba(0,0,0,0.25); }

.blog-main {
  flex: 1; max-width: 860px; width: 100%; margin: 0 auto; padding: 32px 24px;
}

/* 动画 */
@keyframes slideFromRight {
  from { opacity: 0; transform: translateX(20px) scale(0.9); }
  to { opacity: 1; transform: translateX(0) scale(1); }
}
@keyframes slideFromLeft {
  from { opacity: 0; transform: translateX(-20px) scale(0.9); }
  to { opacity: 1; transform: translateX(0) scale(1); }
}
</style>
