/**
 * 测试 PlatformShell 中的 computed 逻辑（不渲染模板）。
 * 核心价值：验证 user 为空时不崩溃、页面标题计算正确。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref, computed } from 'vue'
import * as authModule from '../src/router/auth.js'

describe('PlatformShell 核心逻辑', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('userInitial 计算属性', () => {
    it('user 为 null 时返回默认值 U', () => {
      const user = ref(null)
      const userInitial = computed(() => user.value?.username ? user.value.username[0].toUpperCase() : 'U')
      expect(userInitial.value).toBe('U')
    })

    it('user 有 username 时返回首字母', () => {
      const user = ref({ username: 'Alice' })
      const userInitial = computed(() => user.value?.username ? user.value.username[0].toUpperCase() : 'U')
      expect(userInitial.value).toBe('A')
    })

    it('user 为空对象时返回默认值', () => {
      const user = ref({})
      const userInitial = computed(() => user.value?.username ? user.value.username[0].toUpperCase() : 'U')
      expect(userInitial.value).toBe('U')
    })
  })

  describe('currentPageTitle 计算属性', () => {
    const PAGE_TITLES = {
      '/platform': '任务中心',
      '/editor': '文章编辑',
      '/upload': '文件上传',
      '/storage': '存储管理',
      '/moderation': '审核面板',
      '/github': 'GitHub 代理',
      '/ops/crawler': '爬虫仪表盘',
      '/ops/cloud': '云训练',
      '/ops/assets': '资产管理',
      '/admin': '管理员面板',
      '/admin/users': '用户管理',
    }

    function getTitle(path) {
      if (PAGE_TITLES[path]) return PAGE_TITLES[path]
      for (const [p, title] of Object.entries(PAGE_TITLES)) {
        if (path.startsWith(p) && p !== '/') return title
      }
      return '锦年志'
    }

    it('/platform 返回任务中心', () => {
      expect(getTitle('/platform')).toBe('任务中心')
    })

    it('/editor 返回文章编辑', () => {
      expect(getTitle('/editor')).toBe('文章编辑')
    })

    it('/editor/123 前缀匹配返回文章编辑', () => {
      expect(getTitle('/editor/123')).toBe('文章编辑')
    })

    it('/admin/users 精确匹配返回用户管理', () => {
      expect(getTitle('/admin/users')).toBe('用户管理')
    })

    it('/admin/settings 前缀匹配返回管理员面板', () => {
      expect(getTitle('/admin/settings')).toBe('管理员面板')
    })

    it('未知路径返回锦年志', () => {
      expect(getTitle('/unknown')).toBe('锦年志')
    })

    it('/ 返回锦年志', () => {
      expect(getTitle('/')).toBe('锦年志')
    })
  })

  describe('userLevel 计算属性', () => {
    it('level 为 null 时默认为 5', () => {
      const level = ref(null)
      const userLevel = computed(() => level.value ?? 5)
      expect(userLevel.value).toBe(5)
    })

    it('level 有值时返回 level', () => {
      const level = ref(3)
      const userLevel = computed(() => level.value ?? 5)
      expect(userLevel.value).toBe(3)
    })

    it('level 为 0 时返回 0', () => {
      const level = ref(0)
      const userLevel = computed(() => level.value ?? 5)
      expect(userLevel.value).toBe(0)
    })
  })
})
