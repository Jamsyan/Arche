<template>
  <div class="platform-shell">
    <header class="platform-header">
      <!-- 左：Logo（点击回博客首页） -->
      <router-link to="/" class="header-brand">
        <img src="/logo.png" alt="Veil" class="logo-img" />
      </router-link>

      <!-- 中：纯线条图标导航 -->
      <nav class="header-center">
        <!-- 首页图标：跳回博客主页 -->
        <router-link to="/" class="nav-icon-link" :class="{ active: route.path === '/' }" title="博客首页">
          <icon-home class="nav-icon" />
        </router-link>
        <!-- 其他功能图标 -->
        <router-link
          v-for="item in navItems"
          :key="item.key"
          :to="item.key"
          class="nav-icon-link"
          :class="{ active: currentPath === item.key || currentPath.startsWith(item.key + '/') }"
          :title="item.label"
        >
          <component :is="item.icon" class="nav-icon" />
        </router-link>
      </nav>

      <!-- 右：用户头像 + 下拉菜单 -->
      <div class="header-right">
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
        <!-- 隐藏的文件选择器 -->
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          style="display: none"
          @change="onFileSelected"
        />
      </div>
    </header>

    <main class="platform-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import LevelBadge from '../LevelBadge.vue'
import { useAuth } from '../../router/auth.js'
import {
  IconUser,
  IconExport,
  IconCamera,
  IconHome,
  IconApps,
  IconEdit,
  IconUpload,
  IconGithub,
  IconStorage,
  IconCheck,
  IconBug,
  IconCloud,
} from '@arco-design/web-vue/es/icon'

const route = useRoute()
const currentPath = computed(() => route.path)
const { user } = useAuth()

const props = defineProps({ userLevel: { type: Number, default: 5 } })
const emit = defineEmits(['logout'])

const fileInput = ref(null)

// 头像管理（localStorage 存储 base64）
const avatarUrl = ref(localStorage.getItem('veil_avatar') || '')

const ICON_MAP = {
  '/platform': IconApps,
  '/editor': IconEdit,
  '/upload': IconUpload,
  '/github': IconGithub,
  '/storage': IconStorage,
  '/moderation': IconCheck,
  '/ops/crawler': IconBug,
  '/ops/cloud': IconCloud,
  '/ops/assets': IconApps,
}

const navItems = computed(() => {
  const items = [{ key: '/platform', label: '仪表盘' }]
  if (props.userLevel <= 3) items.push({ key: '/editor', label: '编辑器' })
  if (props.userLevel <= 2) items.push({ key: '/upload', label: '上传' })
  if (props.userLevel <= 1) {
    items.push({ key: '/github', label: 'GitHub' })
    items.push({ key: '/storage', label: '存储' })
    items.push({ key: '/moderation', label: '审核' })
  }
  if (props.userLevel <= 0) {
    items.push({ key: '/ops/crawler', label: '爬虫' })
    items.push({ key: '/ops/cloud', label: '云训练' })
    items.push({ key: '/ops/assets', label: '资产' })
  }
  // 添加图标映射
  return items.map(item => ({
    ...item,
    icon: ICON_MAP[item.key] || IconHome,
  }))
})

const userInitial = computed(() => {
  if (user.value?.username) {
    return user.value.username[0].toUpperCase()
  }
  return 'U'
})

function handleLogout() {
  emit('logout')
}

function handleAvatarChange() {
  fileInput.value?.click()
}

function onFileSelected(event) {
  const file = event.target.files?.[0]
  if (!file) return

  // 限制大小 2MB
  if (file.size > 2 * 1024 * 1024) {
    alert('头像图片不能超过 2MB')
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target.result
    avatarUrl.value = dataUrl
    localStorage.setItem('veil_avatar', dataUrl)
  }
  reader.readAsDataURL(file)
  event.target.value = '' // 重置
}

onMounted(() => {
  // 从 localStorage 恢复头像
  const saved = localStorage.getItem('veil_avatar')
  if (saved) {
    avatarUrl.value = saved
  }
})
</script>

<style scoped>
.platform-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.platform-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  padding: 0 24px;
  background: var(--color-bg-1);
  border-bottom: 1px solid var(--color-border-1);
  height: 56px;
  position: sticky;
  top: 0;
  z-index: 100;
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
  display: flex; justify-content: center; align-items: center; gap: 2px; overflow-x: auto;
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

.platform-main {
  flex: 1; padding: 24px; background: var(--color-fill-1);
}

/* 动画 */
@keyframes slideFromRight {
  from {
    opacity: 0;
    transform: translateX(20px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}
@keyframes slideFromLeft {
  from {
    opacity: 0;
    transform: translateX(-20px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}
</style>
