<template>
  <div
    class="base-layout"
    :class="[`base-layout--${layoutMode}`, { 'is-mobile': appStore.isMobile }]"
  >
    <BaseHeader :layout-mode="layoutMode" @toggle-sidebar="toggleSidebar" />

    <div class="layout-body">
      <!-- Sidebar: only render when there are items or for user/admin modes -->
      <BaseSidebar
        v-if="hasSidebar"
        :menu-items="sidebarItems"
        :collapsed="isSidebarCollapsed"
        :mode="sidebarMode"
        :current-path="$route.path"
        @close="closeSidebar"
      />

      <!-- Main content -->
      <main class="layout-content" :class="{ 'sidebar-empty': !hasSidebar }">
        <slot />
      </main>
    </div>

    <FooterBar v-if="showFooter" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/store/modules/app'
import type { Component } from 'vue'
import BaseHeader from './BaseHeader.vue'
import BaseSidebar from './BaseSidebar.vue'
import FooterBar from './FooterBar.vue'

interface SidebarItem {
  title: string
  path: string
  icon?: Component
}

const props = withDefaults(
  defineProps<{
    layoutMode: 'guest' | 'user' | 'admin'
    sidebarItems?: SidebarItem[]
    showFooter?: boolean
    consoleMode?: boolean
  }>(),
  {
    sidebarItems: () => [],
    showFooter: true,
    consoleMode: false
  }
)

const appStore = useAppStore()

const sidebarMode = computed<'thin' | 'normal' | 'grouped'>(() => {
  const modeMap: Record<string, 'thin' | 'normal' | 'grouped'> = {
    guest: 'thin',
    user: 'normal',
    admin: 'grouped'
  }
  return modeMap[props.layoutMode] || 'thin'
})

const isSidebarCollapsed = computed(() => {
  if (props.layoutMode === 'guest') return false
  return appStore.sidebarCollapsed
})

// Show sidebar when there are items, or always for user/admin modes even with no items
const hasSidebar = computed(() => {
  if (props.layoutMode === 'guest') return props.sidebarItems.length > 0
  return true
})

const toggleSidebar = () => {
  appStore.toggleSidebar()
}

const closeSidebar = () => {
  if (appStore.isMobile) {
    appStore.setSidebarCollapsed(true)
  }
}
</script>

<style scoped>
.base-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-gradient-light);
  color: var(--text-primary);
}

.layout-body {
  display: flex;
  flex: 1;
  padding-top: 56px;
  min-height: calc(100vh - 56px);
}

.layout-content {
  flex: 1;
  padding: var(--content-padding);
  min-width: 0;
  margin-left: 0;
  transition: margin-left var(--transition-slow) var(--ease-out-spring);
}

/* Guest mode: sidebar takes space only when present */
.base-layout--guest .layout-content:not(.sidebar-empty) {
  margin-left: 180px;
}

/* User/Admin mode: normal sidebar width */
.base-layout--user .layout-content,
.base-layout--admin .layout-content {
  margin-left: 240px;
}

/* User/Admin mode: collapsed sidebar */
.base-layout--user.is-mobile .layout-content,
.base-layout--admin.is-mobile .layout-content {
  margin-left: 0;
}

/* Mobile: no sidebar margin */
@media (max-width: 992px) {
  .base-layout--guest .layout-content:not(.sidebar-empty) {
    margin-left: 0;
  }
}
</style>
