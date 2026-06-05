<template>
  <aside
    v-if="mode === 'thin' ? menuItems.length > 0 : true"
    class="base-sidebar"
    :class="[
      `base-sidebar--${mode}`,
      {
        'sidebar-collapsed': collapsed,
        'sidebar-open': !collapsed && isMobile,
        'sidebar-empty': menuItems.length === 0
      }
    ]"
  >
    <nav class="sidebar-nav">
      <!-- Thin mode (guest) -->
      <template v-if="mode === 'thin'">
        <RouterLink
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ 'nav-item-active': isActive(item.path) }"
        >
          <span class="nav-text">{{ item.title }}</span>
        </RouterLink>
      </template>

      <!-- User mode: normal sidebar -->
      <template v-else-if="mode === 'normal'">
        <RouterLink
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ 'nav-item-active': isActive(item.path) }"
        >
          <component :is="item.icon" v-if="item.icon" class="nav-icon" />
          <span v-if="!collapsed" class="nav-text">{{ item.title }}</span>
        </RouterLink>
      </template>

      <!-- Admin mode: grouped sidebar -->
      <template v-else-if="mode === 'grouped'">
        <div v-for="group in groupedItems" :key="group.title" class="nav-group">
          <span v-if="!collapsed && group.title" class="nav-group-title">{{ group.title }}</span>
          <RouterLink
            v-for="item in group.items"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ 'nav-item-active': isActive(item.path) }"
          >
            <component :is="item.icon" v-if="item.icon" class="nav-icon" />
            <span v-if="!collapsed" class="nav-text">{{ item.title }}</span>
          </RouterLink>
        </div>
      </template>
    </nav>

    <!-- Mobile overlay -->
    <div v-if="isMobile && !collapsed" class="sidebar-overlay" @click="$emit('close')" />
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type { Component } from 'vue'
import { useAppStore } from '@/store/modules/app'

interface SidebarItem {
  title: string
  path: string
  icon?: Component
}

interface NavGroup {
  title: string
  items: SidebarItem[]
}

const props = withDefaults(
  defineProps<{
    menuItems: SidebarItem[]
    collapsed: boolean
    mode: 'thin' | 'normal' | 'grouped'
    currentPath?: string
  }>(),
  {
    currentPath: ''
  }
)

defineEmits<{
  close: []
}>()

const route = useRoute()
const appStore = useAppStore()

const isMobile = computed(() => appStore.isMobile)

const isActive = (path: string) => {
  const current = props.currentPath || route.path
  return current === path || current.startsWith(path + '/')
}

// Group items for admin mode — currently each item is its own group
// Future: support proper grouping via route meta
const groupedItems = computed<NavGroup[]>(() => {
  if (props.mode !== 'grouped') return []
  return [{ title: '系统管理', items: props.menuItems }]
})
</script>

<style scoped>
.base-sidebar {
  position: fixed;
  top: 56px;
  bottom: 0;
  left: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  background: var(--surface-color);
  border-right: 1px solid var(--border-color);
  z-index: 90;
  transition:
    width var(--transition-slow) var(--ease-out-spring),
    transform var(--transition-slow) var(--ease-out-spring);
}

/* ── Thin mode (guest) ── */
.base-sidebar--thin {
  width: 180px;
}

.base-sidebar--thin .sidebar-nav {
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.base-sidebar--thin .nav-item {
  display: block;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
}

.base-sidebar--thin .nav-item:hover {
  background: var(--primary-light-color);
  color: var(--primary-color);
}

.base-sidebar--thin .nav-item-active {
  background: var(--primary-light-color);
  color: var(--primary-color);
  font-weight: var(--font-weight-semibold);
}

/* ── Normal mode (user) ── */
.base-sidebar--normal {
  width: 240px;
}

.base-sidebar--normal.sidebar-collapsed {
  width: 64px;
}

.base-sidebar--normal .sidebar-nav {
  padding: var(--spacing-sm) 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.base-sidebar--normal .nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin: 0 var(--spacing-sm);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  font-size: 14px;
  font-weight: var(--font-weight-medium);
}

.base-sidebar--normal .nav-item:hover {
  background: var(--primary-light-color);
  color: var(--primary-color);
}

.base-sidebar--normal .nav-item-active {
  background: var(--primary-color);
  color: var(--text-on-primary, #fff);
}

.base-sidebar--normal .nav-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.base-sidebar--normal .nav-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ── Grouped mode (admin) ── */
.base-sidebar--grouped {
  width: 240px;
}

.base-sidebar--grouped.sidebar-collapsed {
  width: 64px;
}

.base-sidebar--grouped .sidebar-nav {
  padding: var(--spacing-sm) 0;
}

.base-sidebar--grouped .nav-group {
  margin-bottom: var(--spacing-md);
}

.base-sidebar--grouped .nav-group-title {
  display: block;
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: 11px;
  color: var(--text-tertiary);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.base-sidebar--grouped .nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin: 0 var(--spacing-sm);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  font-size: 14px;
  font-weight: var(--font-weight-medium);
}

.base-sidebar--grouped .nav-item:hover {
  background: var(--primary-light-color);
  color: var(--primary-color);
}

.base-sidebar--grouped .nav-item-active {
  background: var(--primary-color);
  color: var(--text-on-primary, #fff);
}

.base-sidebar--grouped .nav-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.base-sidebar--grouped .nav-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ── Mobile overlay ── */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: -1;
}

.base-sidebar.sidebar-empty {
  display: none;
}

/* ── Mobile responsive ── */
@media (max-width: 992px) {
  .base-sidebar--thin,
  .base-sidebar--normal,
  .base-sidebar--grouped {
    width: 220px;
    transform: translateX(-100%);
    z-index: 95;
  }

  .base-sidebar--thin.sidebar-open,
  .base-sidebar--normal.sidebar-open,
  .base-sidebar--grouped.sidebar-open {
    transform: translateX(0);
  }

  .base-sidebar--normal.sidebar-collapsed,
  .base-sidebar--grouped.sidebar-collapsed {
    transform: translateX(-100%);
    width: 220px;
  }

  .base-sidebar--normal.sidebar-collapsed.sidebar-open,
  .base-sidebar--grouped.sidebar-collapsed.sidebar-open {
    transform: translateX(0);
    width: 220px;
  }
}

/* ── Scrollbar ── */
.base-sidebar::-webkit-scrollbar {
  width: 4px;
}

.base-sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.base-sidebar::-webkit-scrollbar-thumb {
  background: var(--primary-light-color);
  border-radius: 2px;
}

.base-sidebar::-webkit-scrollbar-thumb:hover {
  background: color-mix(in srgb, var(--primary-color) 34%, transparent);
}
</style>
