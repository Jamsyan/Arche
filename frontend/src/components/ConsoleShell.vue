<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import {
  AppsOutline,
  DocumentTextOutline,
  CreateOutline,
  PersonOutline,
  InformationCircleOutline,
  SettingsOutline,
  ArrowBackOutline,
  ChevronDownOutline
} from '@vicons/ionicons5'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isAdmin = computed(() => (userStore.userInfo?.level ?? 5) === 0)
const collapsedGroups = ref<Set<string>>(new Set())

const navGroups = computed(() => {
  const groups = [
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
    }
  ]

  if (isAdmin.value) {
    groups.push({
      label: '管理',
      items: [
        { label: '用户管理', icon: PersonOutline, to: '/admin/users' },
        { label: '系统监控', icon: SettingsOutline, to: '/admin/system' },
        { label: 'OSS 存储', icon: DocumentTextOutline, to: '/admin/oss' },
        { label: '配置管理', icon: SettingsOutline, to: '/admin/config' },
        { label: '爬虫管理', icon: InformationCircleOutline, to: '/admin/crawler' },
        { label: '资产目录', icon: AppsOutline, to: '/admin/assets' },
        { label: '帖子管理', icon: DocumentTextOutline, to: '/admin/moderation/posts' },
        { label: '插件管理', icon: AppsOutline, to: '/admin/plugins' }
      ]
    })
  }

  return groups
})

const isActive = (path: string) => route.path === path

const goBack = () => {
  router.push('/console')
}

const toggleGroup = (label: string) => {
  const next = new Set(collapsedGroups.value)
  if (next.has(label)) {
    next.delete(label)
  } else {
    next.add(label)
  }
  collapsedGroups.value = next
}

const isGroupCollapsed = (label: string) => collapsedGroups.value.has(label)
</script>

<template>
  <div class="console-shell">
    <aside class="console-sidebar">
      <div class="sidebar-header">
        <span class="sidebar-title">导航</span>
      </div>
      <nav class="sidebar-nav">
        <template v-for="group in navGroups" :key="group.label">
          <div
            v-if="group.label"
            class="group-label"
            :class="{ collapsed: isGroupCollapsed(group.label) }"
            @click="toggleGroup(group.label)"
          >
            <span>{{ group.label }}</span>
            <NIcon size="14" class="group-chevron"><ChevronDownOutline /></NIcon>
          </div>
          <button
            v-for="item in group.items"
            :key="item.to"
            v-show="group.label ? !isGroupCollapsed(group.label) : true"
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
  padding: 12px;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  padding: 10px 10px 4px;
  letter-spacing: 0.06em;
  cursor: pointer;
  user-select: none;
  transition: color 0.2s;
}

.group-label:hover {
  color: var(--text-secondary);
}

.group-chevron {
  transition: transform 0.2s ease;
  color: var(--text-quaternary);
}

.group-label.collapsed .group-chevron {
  transform: rotate(-90deg);
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
