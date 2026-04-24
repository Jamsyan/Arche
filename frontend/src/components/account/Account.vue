<template>
  <div class="account-page">
    <div class="account-card">
      <div class="account-header">
        <div class="avatar-section">
          <div class="avatar-wrap" @click="triggerAvatarChange">
            <img v-if="avatarUrl" :src="avatarUrl" alt="avatar" class="avatar-img" />
            <div v-else class="avatar-circle">
              <span class="avatar-letter">{{ userInitial }}</span>
            </div>
            <div class="avatar-overlay">
              <icon-camera />
            </div>
          </div>
          <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileSelected" />
        </div>
        <div class="account-info">
          <h2 class="account-name">{{ userInfo?.username || '加载中...' }}</h2>
          <div class="account-meta">
            <LevelBadge :level="level ?? 5" />
            <span class="account-email">{{ userInfo?.email || '' }}</span>
          </div>
          <p class="account-joined">注册于 {{ formatDate(userInfo?.created_at) }}</p>
        </div>
      </div>

      <a-divider />

      <div class="account-stats">
        <div class="stat-item">
          <div class="stat-num">{{ stats.posts }}</div>
          <div class="stat-label">文章</div>
        </div>
        <div class="stat-item">
          <div class="stat-num">{{ stats.views }}</div>
          <div class="stat-label">阅读</div>
        </div>
        <div class="stat-item">
          <div class="stat-num">{{ stats.likes }}</div>
          <div class="stat-label">获赞</div>
        </div>
        <div class="stat-item">
          <div class="stat-num">{{ stats.favorites }}</div>
          <div class="stat-label">收藏</div>
        </div>
      </div>

      <a-divider />

      <div class="account-actions">
        <a-button type="primary" @click="$router.push('/editor')">
          <template #icon><icon-edit /></template>
          写文章
        </a-button>
        <a-button @click="$router.push('/platform')">
          <template #icon><icon-apps /></template>
          返回任务中心
        </a-button>
        <a-button status="danger" @click="handleLogout">
          <template #icon><icon-export /></template>
          退出登录
        </a-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../router/auth.js'
import LevelBadge from '../LevelBadge.vue'
import { blog } from '../../api'
import { Message } from '@arco-design/web-vue'
import {
  IconCamera, IconEdit, IconApps, IconExport,
} from '@arco-design/web-vue/es/icon'

const router = useRouter()
const { user, level, logout } = useAuth()

const userInfo = ref(null)
const avatarUrl = ref(localStorage.getItem('veil_avatar') || '')
const fileInput = ref(null)

const stats = ref({ posts: 0, views: 0, likes: 0, favorites: 0 })

const userInitial = computed(() =>
  userInfo.value?.username?.[0]?.toUpperCase() || 'U'
)

function formatDate(dateStr) {
  if (!dateStr) return '未知'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function triggerAvatarChange() {
  fileInput.value?.click()
}

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

async function fetchStats() {
  try {
    const [postsData, favData] = await Promise.all([
      blog.myPosts({ page: 1, page_size: 1 }),
      blog.favorites({ page: 1, page_size: 1 }),
    ])
    stats.value.posts = postsData?.total || 0
    stats.value.favorites = favData?.total || 0
  } catch {}
}

function handleLogout() {
  logout()
  router.push('/')
}

onMounted(() => {
  userInfo.value = user.value
  const saved = localStorage.getItem('veil_avatar')
  if (saved) avatarUrl.value = saved
  fetchStats()
})
</script>

<style scoped>
.account-page {
  max-width: 600px;
  margin: 40px auto;
  padding: 0 16px;
}

.account-card {
  background: white;
  border-radius: var(--border-radius-large);
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.account-header {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-wrap {
  position: relative;
  cursor: pointer;
  flex-shrink: 0;
}

.avatar-img,
.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-circle {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark-1));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-wrap:hover .avatar-overlay { opacity: 1; }

.avatar-info { flex: 1; }
.account-name { margin: 0 0 8px; font-size: 22px; font-weight: 700; }
.account-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.account-email { font-size: 13px; color: var(--color-text-3); }
.account-joined { margin: 0; font-size: 12px; color: var(--color-text-4); }

.account-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  text-align: center;
}

.stat-item { padding: 12px; }
.stat-num { font-size: 24px; font-weight: 700; color: var(--color-text-1); }
.stat-label { font-size: 12px; color: var(--color-text-4); margin-top: 4px; }

.account-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
