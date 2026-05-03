<template>
  <NConfigProvider :theme="theme" :theme-overrides="themeOverrides">
    <NMessageProvider>
      <NDialogProvider>
        <NNotificationProvider>
          <NLoadingBarProvider>
            <!-- 动态选择布局 -->
            <GuestLayout v-if="currentLayout === 'guest'">
              <RouterView v-slot="{ Component }">
                <Transition :name="appStore.transitionName" mode="out-in">
                  <component :is="Component" />
                </Transition>
              </RouterView>
            </GuestLayout>
            <UserLayout v-else-if="currentLayout === 'user'">
              <RouterView v-slot="{ Component }">
                <Transition :name="appStore.transitionName" mode="out-in">
                  <component :is="Component" />
                </Transition>
              </RouterView>
            </UserLayout>
            <AdminLayout v-else-if="currentLayout === 'admin'">
              <RouterView v-slot="{ Component }">
                <Transition :name="appStore.transitionName" mode="out-in">
                  <component :is="Component" />
                </Transition>
              </RouterView>
            </AdminLayout>
            <!-- 默认用访客布局 -->
            <GuestLayout v-else>
              <RouterView v-slot="{ Component }">
                <Transition :name="appStore.transitionName" mode="out-in">
                  <component :is="Component" />
                </Transition>
              </RouterView>
            </GuestLayout>
          </NLoadingBarProvider>
        </NNotificationProvider>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  NConfigProvider,
  NMessageProvider,
  NDialogProvider,
  NNotificationProvider,
  NLoadingBarProvider,
  darkTheme,
  type GlobalThemeOverrides
} from 'naive-ui'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/store/modules/app'
import GuestLayout from '@/layouts/GuestLayout.vue'
import UserLayout from '@/layouts/UserLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'

const route = useRoute()
const appStore = useAppStore()
const themeOverrides: GlobalThemeOverrides = {
  common: {
    // naive-ui 内部会对颜色做 rgba 计算，必须使用可直接解析的颜色值
    primaryColor: '#9a5a2f',
    primaryColorHover: '#b8743d',
    primaryColorPressed: '#6f3f22',
    successColor: '#4f7a57',
    warningColor: '#b98529',
    errorColor: '#b34c3f',
    borderRadius: '12px'
  }
}

// 计算当前应该使用的布局
const currentLayout = computed(() => {
  return (route.meta.layout as 'guest' | 'user' | 'admin') || 'guest'
})

// 主题切换
const theme = computed(() => {
  return appStore.theme === 'dark' ? darkTheme : null
})
</script>
