<template>
  <div class="platform-shell">
    <header class="mac-menubar">
      <!-- 左：Logo + 应用名 -->
      <div class="menubar-left">
        <router-link to="/" class="menubar-brand">
          <img src="/logo.png" alt="锦年志" class="menubar-logo" />
        </router-link>
        <span class="menubar-appname">锦年志</span>
        <span class="menubar-divider"></span>
        <!-- 当前页面标题 -->
        <span class="menubar-pagename">{{ currentPageTitle }}</span>
      </div>

      <!-- 中：Dock 快捷入口 -->
      <nav class="menubar-center">
        <router-link
          v-for="item in alwaysItems"
          :key="item.id"
          :to="item.route"
          class="dock-item"
          :class="{ active: route.path === item.route }"
          :title="item.title"
        >
          <component :is="`icon-${item.icon}`" class="dock-icon" />
        </router-link>

        <div v-if="pinned.length > 0" class="dock-divider"></div>

        <router-link
          v-for="item in pinned"
          :key="item.id"
          :to="item.route"
          class="dock-item pinned"
          :class="{ active: route.path.startsWith(item.route) }"
          :title="item.title"
        >
          <component :is="`icon-${item.icon}`" class="dock-icon" />
          <span class="dock-label">{{ item.title }}</span>
        </router-link>

        <div class="dock-item dock-add" @click="showDockPanel = true" title="添加快捷入口">
          <icon-plus class="dock-icon" />
        </div>
      </nav>

      <!-- 右：等级 + 头像 + 系统状态 -->
      <div class="menubar-right">
        <span class="menubar-time">{{ currentTime }}</span>
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
      </div>
    </header>

    <main class="platform-main">
      <router-view />
    </main>

    <!-- Dock 管理面板 -->
    <a-modal v-model:visible="showDockPanel" title="管理快捷入口" width="480" :footer="false">
      <div class="dock-panel">
        <div class="dock-section">
          <span class="dock-section-label">已添加</span>
          <div v-if="pinned.length === 0" class="dock-empty">暂无快捷入口</div>
          <div v-else class="dock-list" id="dock-pinned-list">
            <div
              v-for="item in pinned"
              :key="item.id"
              class="dock-list-item"
              :draggable="true"
              @dragstart="onDockDragStart($event, item)"
              @dragend="onDockDragEnd"
            >
              <icon-drag-dot-vertical class="dock-drag-handle" />
              <component :is="`icon-${item.icon}`" class="dock-list-icon" />
              <span class="dock-list-title">{{ item.title }}</span>
              <a-button type="text" size="mini" @click="unpin(item.id)">移除</a-button>
            </div>
          </div>
        </div>
        <div class="dock-section">
          <span class="dock-section-label">可添加</span>
          <div v-if="available.length === 0" class="dock-empty">没有更多可添加的入口</div>
          <div v-else class="dock-list">
            <div v-for="item in available" :key="item.id" class="dock-list-item available">
              <component :is="`icon-${item.icon}`" class="dock-list-icon" />
              <span class="dock-list-title">{{ item.title }}</span>
              <a-button type="text" size="mini" @click="pin(item.id)">添加</a-button>
            </div>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LevelBadge from '../LevelBadge.vue'
import { useAuth } from '../../router/auth.js'
import { Message } from '@arco-design/web-vue'
import { useDock } from '../../router/dock.js'
import {
  IconExport, IconCamera, IconApps, IconPlus, IconDragDotVertical,
} from '@arco-design/web-vue/es/icon'

const route = useRoute()
const router = useRouter()
const { user, logout, level } = useAuth()

const props = defineProps({ userLevel: { type: Number, default: 5 } })

const {
  alwaysItems,
  pinned,
  available,
  pin,
  unpin,
  isPinned,
  reorder,
  updateLevel,
  showDockPanel
} = useDock(level)

const fileInput = ref(null)
const avatarUrl = ref(localStorage.getItem('veil_avatar') || '')
const currentTime = ref('')

const userInitial = computed(() => user.value?.username ? user.value.username[0].toUpperCase() : 'U')

// 当前页面标题
const PAGE_TITLES = {
  '/platform': '任务中心',
  '/editor': '文章编辑',
  '/upload': '文件上传',
  '/storage': '存储管理',
  '/moderation': '审核面板',
  '/github': 'GitHub 代理',
  '/ops/crawler': '爬虫仪表盘',
  '/ops/cloud': '云训练',
  '/ops/assets': '资产管理',
  '/admin': '管理员面板',
  '/admin/users': '用户管理',
}

const currentPageTitle = computed(() => {
  const path = route.path
  // 精确匹配
  if (PAGE_TITLES[path]) return PAGE_TITLES[path]
  // 前缀匹配
  for (const [p, title] of Object.entries(PAGE_TITLES)) {
    if (path.startsWith(p) && p !== '/') return title
  }
  return '锦年志'
})

// 时钟
function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
updateClock()
const clockTimer = setInterval(updateClock, 10000)

function handleLogout() { logout(); router.push('/') }

function handleAvatarChange() {
  fileInput.value?.click()
}

function onFileSelected(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    Message.warning('头像图片不能超过 2MB')
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

// Dock 拖拽排序
let dockDragItem = null

function onDockDragStart(event, item) {
  dockDragItem = item
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', item.id)
}

function onDockDragEnd() {
  dockDragItem = null
}

onMounted(() => {
  const saved = localStorage.getItem('veil_avatar')
  if (saved) avatarUrl.value = saved

  // Dock 列表拖拽排序
  const dockList = document.getElementById('dock-pinned-list')
  if (!dockList) return

  dockList.addEventListener('dragover', (e) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    const afterElement = getDragAfterElement(dockList, e.clientY)
    const draggable = document.querySelector('.dock-list-item.dragging')
    if (draggable) {
      if (afterElement == null) {
        dockList.appendChild(draggable)
      } else {
        dockList.insertBefore(draggable, afterElement)
      }
    }
  })

  dockList.addEventListener('drop', (e) => {
    e.preventDefault()
    const items = dockList.querySelectorAll('.dock-list-item')
    const newOrder = []
    items.forEach(el => {
      const title = el.querySelector('.dock-list-title')?.textContent
      const found = pinned.value.find(p => p.title === title)
      if (found) newOrder.push(found.id)
    })
    if (newOrder.length > 0) {
      reorder(newOrder)
    }
  })
})

function getDragAfterElement(container, y) {
  const draggableElements = [...container.querySelectorAll('.dock-list-item:not(.dragging)')]
  return draggableElements.reduce((closest, child) => {
    const box = child.getBoundingClientRect()
    const offset = y - box.top - box.height / 2
    if (offset < 0 && offset > closest.offset) {
      return { offset, element: child }
    }
    return closest
  }, { offset: Number.NEGATIVE_INFINITY }).element
}

onUnmounted(() => {
  clearInterval(clockTimer)
})
</script>

<style scoped>
.platform-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-fill-1);
}

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

/* 左侧：Logo + 应用名 + 页面名 */
.menubar-left {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 200px;
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

/* 中间：Dock */
.menubar-center {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1px;
}

.dock-item {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 4px 7px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--color-text-3);
  transition: background 0.12s, color 0.12s;
  text-decoration: none;
  font-size: 12px;
  line-height: 1;
}

.dock-item:hover {
  background: rgba(0,0,0,0.06);
  color: var(--color-text-1);
}

.dock-item.active {
  background: rgba(0,0,0,0.08);
  color: var(--color-text-1);
  font-weight: 500;
}

.dock-icon {
  width: 14px;
  height: 14px;
}

.dock-label {
  white-space: nowrap;
}

.dock-divider {
  width: 1px;
  height: 18px;
  background: var(--color-border-1);
  margin: 0 4px;
}

.dock-add {
  color: var(--color-text-4);
}

.dock-add:hover {
  color: var(--color-text-1);
}

/* 右侧：时间 + 等级 + 头像 */
.menubar-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  min-width: 200px;
}

.menubar-time {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-3);
  font-variant-numeric: tabular-nums;
}

.avatar-wrap {
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-circle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  border: 1.5px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
  transition: box-shadow 0.15s;
}

.avatar-wrap:hover .avatar-circle {
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.avatar-img {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  object-fit: cover;
  border: 1.5px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
  transition: box-shadow 0.15s;
}

.avatar-wrap:hover .avatar-img {
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

/* ===== 主内容区 ===== */
.platform-main {
  flex: 1;
  padding: 20px 24px;
}

/* ===== Dock 管理面板 ===== */
.dock-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dock-section { }

.dock-section-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: block;
  margin-bottom: 8px;
}

.dock-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dock-list-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--color-fill-1);
  border-radius: var(--border-radius-small);
  cursor: default;
}

.dock-list-item.available {
  opacity: 0.7;
}

.dock-list-item.available:hover {
  opacity: 1;
}

.dock-list-item[draggable="true"] {
  cursor: grab;
}

.dock-list-item[draggable="true"]:active {
  cursor: grabbing;
}

.dock-drag-handle {
  width: 14px;
  height: 14px;
  color: var(--color-text-4);
  flex-shrink: 0;
}

.dock-list-icon {
  width: 16px;
  height: 16px;
  color: var(--color-text-3);
}

.dock-list-title {
  flex: 1;
  font-size: 13px;
}

.dock-empty {
  font-size: 12px;
  color: var(--color-text-4);
  padding: 12px 0;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .menubar-left { min-width: auto; }
  .menubar-pagename { display: none; }
  .menubar-right { min-width: auto; gap: 6px; }
  .menubar-time { display: none; }
  .dock-label { display: none; }
}
</style>
