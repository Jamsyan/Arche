<template>
  <NConfigProvider
    :theme="theme"
    :theme-overrides="themeOverrides"
    :locale="zhCN"
    :date-locale="dateZhCN"
  >
    <NMessageProvider>
      <NDialogProvider>
        <NNotificationProvider>
          <NLoadingBarProvider>
            <RouterView v-slot="{ Component, route: r }">
              <component :is="layoutMap[(r.meta.layout as string) || 'guest'] || GuestLayout">
                <component
                  :is="Component"
                  :key="r.matched[0]?.path === '/console' ? '/console' : r.fullPath"
                />
              </component>
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
  zhCN,
  dateZhCN,
  type GlobalThemeOverrides
} from 'naive-ui'
import { useAppStore } from '@/lib/store/modules/app'
import GuestLayout from '@/layouts/GuestLayout.vue'
import UserLayout from '@/layouts/UserLayout.vue'

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
  },
  Popover: {
    color: 'var(--surface-color)',
    border: '1px solid var(--border-color)',
    borderRadius: 'var(--radius-md)',
    fontSize: '12px'
  },
  Select: {
    menuColor: 'var(--surface-color)',
    menuBorder: '1px solid var(--border-color)',
    menuBorderRadius: 'var(--radius-md)',
    menuBoxShadow: 'var(--shadow-lg)',
    optGroupTextColor: 'var(--text-secondary)',
    optGroupFontSize: '11px'
  },
  InternalSelectMenu: {
    color: 'var(--surface-color)',
    border: '1px solid var(--border-color)',
    borderRadius: 'var(--radius-md)',
    boxShadow: 'var(--shadow-lg)',
    optionColor: 'transparent',
    optionColorHover: 'var(--primary-light-color)',
    optionColorActive: 'var(--primary-light-color)',
    optionTextColor: 'var(--text-primary)',
    optionTextColorHover: 'var(--primary-color)',
    optionTextColorActive: 'var(--primary-color)',
    optionFontSize: '12px',
    optionHeight: '28px'
  },
  Pagination: {
    itemFontSizeSmall: '12px',
    itemFontSizeActive: '12px',
    itemTextColor: 'var(--text-secondary)',
    itemTextColorHover: 'var(--primary-color)',
    itemTextColorActive: 'var(--primary-color)',
    itemColor: 'transparent',
    itemColorHover: 'var(--primary-light-color)',
    itemColorActive: 'var(--primary-light-color)',
    itemBorder: '1px solid var(--border-color)',
    itemBorderHover: '1px solid var(--primary-color)',
    itemBorderActive: '1px solid var(--primary-color)',
    itemBorderRadius: 'var(--radius-sm)',
    buttonColor: 'transparent',
    buttonColorHover: 'var(--primary-light-color)',
    buttonBorder: '1px solid var(--border-color)',
    buttonBorderHover: '1px solid var(--primary-color)',
    buttonIconColor: 'var(--text-tertiary)',
    buttonIconColorHover: 'var(--primary-color)',
    inputBorderColor: 'var(--border-color)',
    inputBorderColorHover: 'var(--primary-color)',
    inputBorderColorFocus: 'var(--primary-color)',
    selectBorderColor: 'var(--border-color)',
    selectBorderColorHover: 'var(--primary-color)',
    selectBorderColorFocus: 'var(--primary-color)',
    prefixFontSize: '12px',
    suffixFontSize: '12px'
  }
}

const layoutMap: Record<string, typeof GuestLayout> = {
  guest: GuestLayout,
  user: UserLayout
}

// 主题切换
const theme = computed(() => {
  return appStore.theme === 'dark' ? darkTheme : null
})
</script>
