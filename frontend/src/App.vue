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
    primaryColor: '#9a5a2f',
    primaryColorHover: '#b8743d',
    primaryColorPressed: '#6f3f22',
    successColor: '#4f7a57',
    warningColor: '#b98529',
    errorColor: '#b34c3f',
    borderRadius: '12px'
  },
  Card: {
    color: 'rgba(255, 248, 236, 0.72)',
    colorModal: 'rgba(255, 248, 236, 0.72)',
    colorPopover: 'rgba(255, 248, 236, 0.72)',
    borderColor: 'rgba(130, 95, 65, 0.14)',
    titleTextColor: 'var(--text-primary)',
    actionColor: 'rgba(255, 248, 236, 0.42)'
  },
  Input: {
    color: 'rgba(255, 248, 236, 0.52)',
    colorFocus: 'rgba(255, 248, 236, 0.52)',
    border: '1px solid rgba(130, 95, 65, 0.14)',
    borderHover: '1px solid #b8743d',
    borderFocus: '1px solid #b8743d',
    boxShadowFocus: '0 0 0 2px rgba(154, 90, 47, 0.2)',
    placeholderColor: 'rgba(130, 95, 65, 0.35)'
  },
  InternalSelection: {
    color: 'rgba(255, 248, 236, 0.52)',
    colorActive: 'rgba(255, 248, 236, 0.52)',
    colorDisabled: 'rgba(255, 248, 236, 0.32)',
    border: '1px solid rgba(130, 95, 65, 0.14)',
    borderHover: '1px solid #b8743d',
    borderFocus: '1px solid #b8743d',
    boxShadowFocus: '0 0 0 2px rgba(154, 90, 47, 0.2)',
    placeholderColor: 'rgba(130, 95, 65, 0.35)'
  },
  InternalSelectMenu: {
    color: 'rgba(255, 248, 236, 0.97)',
    optionColorPending: 'rgba(154, 90, 47, 0.08)',
    optionColorActive: 'rgba(154, 90, 47, 0.06)',
    optionColorActivePending: 'rgba(154, 90, 47, 0.12)',
    optionTextColor: '#333639'
  },
  DataTable: {
    thColor: 'rgba(255, 248, 236, 0.52)',
    thColorHover: 'rgba(255, 248, 236, 0.72)',
    tdColor: 'rgba(255, 248, 236, 0.52)',
    tdColorHover: 'rgba(154, 90, 47, 0.04)',
    borderColor: 'rgba(130, 95, 65, 0.1)',
    thTextColor: '#5f5b54',
    tdTextColor: '#333639',
    thFontWeight: '600',
    thIconColor: 'rgba(130, 95, 65, 0.35)',
    thIconColorActive: '#9a5a2f',
    tdColorStriped: 'rgba(255, 248, 236, 0.62)'
  },
  Pagination: {
    itemColorDisabled: 'transparent',
    itemColor: 'transparent',
    itemColorHover: 'transparent',
    itemColorActive: 'transparent',
    buttonBorder: '1px solid rgba(130, 95, 65, 0.14)',
    buttonBorderHover: '1px solid rgba(130, 95, 65, 0.14)',
    buttonBorderPressed: '1px solid rgba(130, 95, 65, 0.14)',
    buttonColor: 'transparent',
    buttonColorHover: 'transparent',
    buttonColorPressed: 'transparent'
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
  },
  Dialog: {
    color: 'rgba(255, 248, 236, 0.97)'
  },
  Modal: {
    color: 'rgba(255, 248, 236, 0.97)'
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
