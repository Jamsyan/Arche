<template>
  <BaseLayout layout-mode="admin" :sidebar-items="adminMenu" :show-footer="false">
    <slot />
  </BaseLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePermissionStore } from '@/store/modules/permission'
import { buildLayoutMenus } from '@/router/menu'
import BaseLayout from './BaseLayout.vue'

const permissionStore = usePermissionStore()

const adminMenu = computed(() => buildLayoutMenus(permissionStore.routes, 'admin'))
</script>
