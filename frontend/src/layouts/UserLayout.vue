<template>
  <BaseLayout layout-mode="user" :sidebar-items="userMenu" :show-footer="false">
    <slot />
  </BaseLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { HomeOutline } from '@/icons'
import { usePermissionStore } from '@/lib/store/modules/permission'
import { buildLayoutMenus } from '@/lib/router/menu'
import BaseLayout from './BaseLayout.vue'

const permissionStore = usePermissionStore()

const userMenu = computed(() => {
  const menus = buildLayoutMenus(permissionStore.routes, 'user')
  const homeMenu = {
    title: '首页',
    path: '/',
    icon: HomeOutline
  }
  return [homeMenu, ...menus]
})
</script>
