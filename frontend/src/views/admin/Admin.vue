<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute, RouterView } from 'vue-router'
import { NLayout, NLayoutSider, NLayoutContent, NMenu, type MenuOption } from 'naive-ui'
import { PeopleOutline, ExtensionPuzzleOutline } from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()

const menuOptions: MenuOption[] = [
  {
    label: '用户管理',
    key: 'AdminUsers',
    icon: () => h(PeopleOutline)
  },
  {
    label: '插件管理',
    key: 'AdminPlugins',
    icon: () => h(ExtensionPuzzleOutline)
  }
]

const activeKey = computed(() => {
  return route.name?.toString() || 'AdminUsers'
})

const handleMenuSelect = (key: string) => {
  const routeName = key as 'AdminUsers' | 'AdminPlugins'
  router.push({ name: routeName })
}
</script>

<template>
  <NLayout hasSider class="admin-layout">
    <NLayoutSider bordered class="admin-sider">
      <div class="admin-logo">
        <h3>Arche 管理后台</h3>
      </div>
      <NMenu
        mode="vertical"
        :value="activeKey"
        :options="menuOptions"
        @update:value="handleMenuSelect"
      />
    </NLayoutSider>
    <NLayoutContent class="admin-content">
      <RouterView />
    </NLayoutContent>
  </NLayout>
</template>

<style scoped>
.admin-layout {
  min-height: calc(100vh - 64px);
}

.admin-sider {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border-right: var(--glass-border);
}

.admin-logo {
  padding: 24px 16px;
  border-bottom: 1px solid rgba(24, 160, 88, 0.2);
}

.admin-logo h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--success-color);
}

.admin-content {
  background: transparent;
}

/* 管理员菜单特殊样式 */
.admin-sider :deep(.n-menu-item-content--selected) {
  background-color: rgba(24, 160, 88, 0.1);
  color: var(--success-color);
}

.admin-sider :deep(.n-menu-item-content:hover) {
  background-color: rgba(24, 160, 88, 0.05);
}
</style>
