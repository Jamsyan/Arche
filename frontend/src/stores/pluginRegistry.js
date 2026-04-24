/**
 * 插件注册中心
 * 管理所有插件注册的侧边栏项和原子组件
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePluginRegistry = defineStore('pluginRegistry', () => {
  // 侧边栏注册
  const sidebarItems = ref([])

  // 原子组件注册
  const atomicComponents = ref([])

  // 注册侧边栏项
  function registerSidebar(item) {
    const existing = sidebarItems.value.findIndex(i => i.id === item.id)
    if (existing >= 0) {
      sidebarItems.value[existing] = item
    } else {
      sidebarItems.value.push(item)
    }
  }

  // 注册原子组件
  function registerComponent(component) {
    const existing = atomicComponents.value.findIndex(c => c.id === component.id)
    if (existing >= 0) {
      atomicComponents.value[existing] = component
    } else {
      atomicComponents.value.push(component)
    }
  }

  // 批量注册
  function register(items) {
    if (items.sidebar) {
      items.sidebar.forEach(registerSidebar)
    }
    if (items.components) {
      items.components.forEach(registerComponent)
    }
  }

  // 根据页面获取可捡起的组件
  function getComponentsByPage(pageId) {
    return atomicComponents.value.filter(c => c.pageId === pageId)
  }

  // 根据权限获取侧边栏项
  function getSidebarByRole(role) {
    if (!role) return []  // 未登录返回空
    const roleLevels = { P0: 0, P1: 1, P2: 2, P3: 3, P4: 4 }
    const userLevel = roleLevels[role] ?? 99

    const items = sidebarItems.value.filter(item => {
      const requiredLevel = roleLevels[item.requiredRole] ?? 99
      return userLevel <= requiredLevel
    })

    // 防御：如果有 token 但 role 解析失败，返回所有条目（确保侧栏不空）
    if (items.length === 0 && localStorage.getItem('veil_token')) {
      return sidebarItems.value
    }
    return items
  }

  // 分类侧边栏项
  const categorizedSidebar = computed(() => {
    const items = {
      // 系统固定项
      system: [],
      // 监控大屏
      monitor: [],
      // 用户区
      user: [],
      // 插件区（可排序）
      plugins: [],
      // 运维区
      ops: []
    }

    sidebarItems.value.forEach(item => {
      switch (item.category) {
        case 'system':
          items.system.push(item)
          break
        case 'monitor':
          items.monitor.push(item)
          break
        case 'user':
          items.user.push(item)
          break
        case 'ops':
          items.ops.push(item)
          break
        case 'plugin':
        default:
          items.plugins.push(item)
      }
    })

    return items
  })

  // 重置（用于测试或切换用户）
  function reset() {
    sidebarItems.value = []
    atomicComponents.value = []
  }

  return {
    sidebarItems,
    atomicComponents,
    categorizedSidebar,
    register,
    registerSidebar,
    registerComponent,
    getComponentsByPage,
    getSidebarByRole,
    reset
  }
})
