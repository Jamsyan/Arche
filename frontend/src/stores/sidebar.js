/**
 * 侧边栏状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSidebarStore = defineStore('sidebar', () => {
  // 展开/收起状态
  const expanded = ref(true)

  // 插件区排序（存储顺序）
  const pluginOrder = ref([])

  // 加载保存的状态
  function loadState() {
    const saved = localStorage.getItem('sidebar_state')
    if (saved) {
      try {
        const state = JSON.parse(saved)
        expanded.value = state.expanded ?? true
        pluginOrder.value = state.pluginOrder ?? []
      } catch (e) {
        console.warn('Failed to load sidebar state:', e)
      }
    }
  }

  // 保存状态
  function saveState() {
    localStorage.setItem('sidebar_state', JSON.stringify({
      expanded: expanded.value,
      pluginOrder: pluginOrder.value
    }))
  }

  // 切换展开/收起
  function toggle() {
    expanded.value = !expanded.value
    saveState()
  }

  // 更新插件顺序
  function updatePluginOrder(newOrder) {
    pluginOrder.value = newOrder
    saveState()
  }

  // 初始化
  loadState()

  return {
    expanded,
    pluginOrder,
    toggle,
    updatePluginOrder,
    loadState
  }
})
