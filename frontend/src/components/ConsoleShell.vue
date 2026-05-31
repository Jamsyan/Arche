<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import {
  AppsOutline,
  DocumentTextOutline,
  CreateOutline,
  PersonOutline,
  InformationCircleOutline,
  ArrowBackOutline
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()

const navGroups = [
  {
    label: '',
    items: [{ label: '控制台首页', icon: AppsOutline, to: '/console' }]
  },
  {
    label: '创作',
    items: [
      { label: '我的文章', icon: DocumentTextOutline, to: '/posts' },
      { label: '写文章', icon: CreateOutline, to: '/posts/new' },
      { label: '创作者看板', icon: InformationCircleOutline, to: '/creator' }
    ]
  },
  {
    label: '系统',
    items: [{ label: '个人中心', icon: PersonOutline, to: '/profile' }]
  }
]

const isActive = (path: string) => {
  if (path === '/console') return route.path === '/console'
  return route.path.startsWith(path)
}

const goBack = () => {
  router.push('/console')
}
</script>

<template>
  <div class="console-shell">
    <aside class="console-sidebar">
      <div class="sidebar-header">
        <span class="sidebar-title">导航</span>
      </div>
      <nav class="sidebar-nav">
        <template v-for="group in navGroups" :key="group.label">
          <div v-if="group.label" class="group-label">{{ group.label }}</div>
          <button
            v-for="item in group.items"
            :key="item.to"
            class="nav-btn"
            :class="{ active: isActive(item.to) }"
            @click="router.push(item.to)"
          >
            <NIcon size="18"><component :is="item.icon" /></NIcon>
            <span>{{ item.label }}</span>
          </button>
        </template>
      </nav>
    </aside>
    <main class="console-content">
      <button class="back-btn" @click="goBack">
        <NIcon size="16"><ArrowBackOutline /></NIcon>
        <span>返回控制台</span>
      </button>
      <slot />
    </main>
  </div>
</template>

<style scoped>
.console-shell {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 16px;
  align-items: stretch;
}

.console-sidebar {
  background: rgba(255, 248, 236, 0.72);
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-md);
  padding: 12px 12px 0;
}

.sidebar-header {
  padding: 4px 8px 10px;
  border-bottom: 1px solid rgba(130, 95, 65, 0.1);
  margin-bottom: 6px;
}

.sidebar-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  letter-spacing: 0.08em;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.group-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  padding: 10px 10px 4px;
  letter-spacing: 0.06em;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  width: 100%;
}

.nav-btn:hover {
  background: rgba(154, 90, 47, 0.08);
  color: var(--primary-color);
}

.nav-btn.active {
  background: rgba(154, 90, 47, 0.12);
  color: var(--primary-color);
  font-weight: 600;
}

.console-content {
  min-width: 0;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  margin-bottom: 12px;
  border: none;
  border-radius: var(--radius-sm);
  background: rgba(154, 90, 47, 0.06);
  color: var(--text-tertiary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: rgba(154, 90, 47, 0.12);
  color: var(--primary-color);
}

@media (max-width: 860px) {
  .console-shell {
    grid-template-columns: 1fr;
  }
  .console-sidebar {
    display: none;
  }
}
</style>
