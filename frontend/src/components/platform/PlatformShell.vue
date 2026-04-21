<template>
  <a-layout class="platform-shell">
    <a-layout-header class="platform-header">
      <a-typography-title :heading="5" style="margin: 0; color: #fff">Veil</a-typography-title>

      <a-menu mode="horizontal" :selected-keys="[currentPath]" class="platform-nav" @menu-item-click="$router.push">
        <a-menu-item key="/platform">仪表盘</a-menu-item>
        <a-menu-item v-if="userLevel <= 3" key="/editor">编辑器</a-menu-item>
        <a-menu-item v-if="userLevel <= 2" key="/upload">上传</a-menu-item>
        <a-menu-item v-if="userLevel <= 1" key="/github">GitHub</a-menu-item>
        <a-menu-item v-if="userLevel <= 1" key="/storage">存储</a-menu-item>
        <a-menu-item v-if="userLevel <= 1" key="/moderation">审核</a-menu-item>
        <a-menu-item v-if="userLevel <= 0" key="/ops/crawler">爬虫</a-menu-item>
        <a-menu-item v-if="userLevel <= 0" key="/ops/cloud">云训练</a-menu-item>
        <a-menu-item v-if="userLevel <= 0" key="/ops/assets">资产</a-menu-item>
      </a-menu>

      <LevelBadge :level="userLevel" />

      <a-button type="outline" size="small" @click="$emit('logout')">
        退出
      </a-button>
    </a-layout-header>

    <a-layout-content class="platform-main">
      <router-view />
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import LevelBadge from '../LevelBadge.vue'

const route = useRoute()
const currentPath = computed(() => route.path)

defineProps({ userLevel: { type: Number, default: 5 } })
defineEmits(['logout'])
</script>

<style scoped>
.platform-shell { min-height: 100vh; }
.platform-header {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #1d2129;
  padding: 0 24px;
}
.platform-nav {
  flex: 1;
  background: transparent;
  border-bottom: none;
}
.platform-nav :deep(.arco-menu-item) {
  color: rgb(var(--gray-6));
  font-size: 14px;
}
.platform-nav :deep(.arco-menu-item:hover) {
  color: rgb(var(--gray-8));
}
.platform-nav :deep(.arco-menu-item.arco-menu-selected) {
  color: rgb(var(--primary-6));
}
.platform-main {
  padding: 24px;
  background: var(--color-fill-2);
}
</style>
