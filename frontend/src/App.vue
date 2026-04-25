<template>
  <NConfigProvider :theme="theme">
    <NMessageProvider>
      <NDialogProvider>
        <NNotificationProvider>
          <NLoadingBarProvider>
            <!-- 动态选择布局 -->
            <GuestLayout v-if="currentLayout === 'guest'">
              <RouterView />
            </GuestLayout>
            <UserLayout v-else-if="currentLayout === 'user'">
              <RouterView />
            </UserLayout>
            <AdminLayout v-else-if="currentLayout === 'admin'">
              <RouterView />
            </AdminLayout>
            <!-- 默认用访客布局 -->
            <GuestLayout v-else>
              <RouterView />
            </GuestLayout>
          </NLoadingBarProvider>
        </NNotificationProvider>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NConfigProvider, NMessageProvider, NDialogProvider, NNotificationProvider, NLoadingBarProvider, darkTheme } from 'naive-ui'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/store/modules/app'
import GuestLayout from '@/layouts/GuestLayout.vue'
import UserLayout from '@/layouts/UserLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'

const route = useRoute()
const appStore = useAppStore()

// 计算当前应该使用的布局
const currentLayout = computed(() => {
  return route.meta.layout as 'guest' | 'user' | 'admin' || 'guest'
})

// 主题切换
const theme = computed(() => {
  return appStore.theme === 'dark' ? darkTheme : null
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
