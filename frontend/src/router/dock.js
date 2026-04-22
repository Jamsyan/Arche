/**
 * Dock 管理 — 顶部导航栏快捷入口。
 * 用户可将仪表盘卡片「钉」到顶部栏（类似 macOS Dock）。
 * 状态持久化到 localStorage。
 */
import { ref, computed, watch } from 'vue'

const DOCK_KEY = 'veil_dock'

// 所有可用 dock 项目定义
const AVAILABLE_ITEMS = [
  { id: 'home',       title: '首页',       icon: 'home',       route: '/',             level: 5, always: true },
  { id: 'editor',     title: '文章编辑',   icon: 'edit',       route: '/editor',       level: 3 },
  { id: 'upload',     title: '文件上传',   icon: 'upload',     route: '/upload',       level: 1 },
  { id: 'storage',    title: '存储管理',   icon: 'storage',    route: '/storage',      level: 1 },
  { id: 'moderation', title: '审核',       icon: 'check',      route: '/moderation',   level: 1 },
  { id: 'github',     title: 'GitHub',     icon: 'github',     route: '/github',       level: 1 },
  { id: 'crawler',    title: '爬虫',       icon: 'bug',        route: '/ops/crawler',  level: 0 },
  { id: 'cloud',      title: '云训练',     icon: 'cloud',      route: '/ops/cloud',    level: 0 },
  { id: 'assets',     title: '资产',       icon: 'apps',       route: '/ops/assets',   level: 0 },
  { id: 'admin',      title: '管理员',     icon: 'lock',       route: '/admin',        level: 0 },
]

// 模块级响应式状态
const pinnedIds = ref([])
const showDockPanel = ref(false)

// 从 localStorage 恢复
function loadPinned() {
  try {
    const stored = localStorage.getItem(DOCK_KEY)
    if (stored) pinnedIds.value = JSON.parse(stored)
  } catch { /* ignore */ }
}

// 保存到 localStorage
function savePinned() {
  localStorage.setItem(DOCK_KEY, JSON.stringify(pinnedIds.value))
}

// 持久化
watch(pinnedIds, savePinned, { deep: true })

// 模块初始化时加载
loadPinned()

/**
 * 获取当前用户可见的 dock 项目。
 * @param {number} userLevel
 * @returns {{ pinned: Array, available: Array, showDockPanel: Ref }}
 */
export function useDock(userLevel) {
  const level = ref(userLevel ?? 5)

  // 始终显示的项目（如首页）
  const alwaysItems = AVAILABLE_ITEMS.filter(i => i.always)

  // 用户权限可见的项目（computed 使其随 level 变化而更新）
  const visibleItems = computed(() =>
    AVAILABLE_ITEMS.filter(i => !i.always && i.level >= level.value)
  )

  // 已钉住的项目（computed 使其随 pinnedIds 和 visibleItems 变化而更新）
  const pinned = computed(() =>
    pinnedIds.value
      .map(id => visibleItems.value.find(i => i.id === id))
      .filter(Boolean)
  )

  // 未钉住但可钉的项目
  const available = computed(() =>
    visibleItems.value.filter(i => !pinnedIds.value.includes(i.id))
  )

  function pin(id) {
    if (!pinnedIds.value.includes(id)) {
      pinnedIds.value.push(id)
    }
  }

  function unpin(id) {
    pinnedIds.value = pinnedIds.value.filter(x => x !== id)
  }

  function isPinned(id) {
    return pinnedIds.value.includes(id)
  }

  // 根据新顺序重新排列 pinnedIds（保持原有的 pinned + 未拖拽的）
  function reorder(ids) {
    const current = new Set(pinnedIds.value)
    const reordered = ids.filter(id => current.has(id))
    const remaining = [...current].filter(id => !ids.includes(id))
    pinnedIds.value = [...reordered, ...remaining]
  }

  // 更新 level（用于登录后刷新 dock）
  function updateLevel(newLevel) {
    level.value = newLevel
  }

  return {
    alwaysItems,
    pinned,
    available,
    pin,
    unpin,
    isPinned,
    reorder,
    updateLevel,
    showDockPanel,
  }
}
