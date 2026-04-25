import { defineStore } from 'pinia'
import { ref } from 'vue'

export type Theme = 'light' | 'dark'

export type LayoutType = 'default' | 'simple'

export const useAppStore = defineStore(
  'app',
  () => {
    // 主题
    const theme = ref<Theme>('light')
    // 布局方式
    const layout = ref<LayoutType>('default')
    // 侧边栏是否折叠
    const sidebarCollapsed = ref(false)
    // 是否显示面包屑
    const breadcrumbVisible = ref(true)
    // 是否显示标签栏
    const tabsVisible = ref(true)
    // 是否显示页脚
    const footerVisible = ref(true)
    // 语言
    const language = ref('zh-CN')
    // 页面切换动画
    const transitionName = ref('fade-transform')

    // 切换主题
    const toggleTheme = () => {
      theme.value = theme.value === 'light' ? 'dark' : 'light'
      // 切换主题时更新html的class
      if (theme.value === 'dark') {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }

    // 切换侧边栏折叠状态
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }

    // 设置折叠状态
    const setSidebarCollapsed = (collapsed: boolean) => {
      sidebarCollapsed.value = collapsed
    }

    // 切换布局
    const setLayout = (newLayout: LayoutType) => {
      layout.value = newLayout
    }

    return {
      theme,
      layout,
      sidebarCollapsed,
      breadcrumbVisible,
      tabsVisible,
      footerVisible,
      language,
      transitionName,
      toggleTheme,
      toggleSidebar,
      setSidebarCollapsed,
      setLayout
    }
  },
  {
    persist: true // 开启持久化，默认存储到localStorage，存储所有状态
  }
)
