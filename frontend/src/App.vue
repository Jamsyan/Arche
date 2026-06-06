<template>
  <NConfigProvider :theme="theme" :theme-overrides="themeOverrides">
    <NMessageProvider>
      <NDialogProvider>
        <NNotificationProvider>
          <NLoadingBarProvider>
            <RouterView v-slot="{ Component, route: r }">
              <Transition :name="appStore.transitionName" mode="out-in">
                <component
                  :is="layoutMap[(r.meta.layout as string) || 'guest'] || GuestLayout"
                  :key="r.fullPath"
                >
                  <component :is="Component" :key="r.fullPath" />
                </component>
              </Transition>
            </RouterView>
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
import { useAppStore } from '@/store/modules/app'
import GuestLayout from '@/layouts/GuestLayout.vue'
import UserLayout from '@/layouts/UserLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'

const appStore = useAppStore()

const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#9a5a2f',
    primaryColorHover: '#b8743d',
    primaryColorPressed: '#6f3f22',
    successColor: '#4f7a57',
    warningColor: '#b98529',
    errorColor: '#b34c3f',
    borderRadius: '12px'
  },
  Progress: {
    railColor: 'rgba(130, 95, 65, 0.1)'
  },
  Tag: {
    color: 'rgba(154, 90, 47, 0.08)',
    border: 'none',
    textColor: '#5f5b54',
    closeColor: 'rgba(130, 95, 65, 0.35)'
  },
  Button: {
    textColorGhost: '#5f5b54',
    border: '1px solid rgba(130, 95, 65, 0.14)',
    borderHover: '1px solid #b8743d',
    borderPressed: '1px solid #6f3f22',
    borderFocus: '1px solid #b8743d'
  }
}

const layoutMap: Record<string, typeof GuestLayout> = {
  guest: GuestLayout,
  user: UserLayout,
  admin: AdminLayout
}

// 主题切换
const theme = computed(() => {
  return appStore.theme === 'dark' ? darkTheme : null
})
</script>
