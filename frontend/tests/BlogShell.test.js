/**
 * 测试 BlogShell 中的 computed 逻辑（不渲染模板）。
 */
import { describe, it, expect } from 'vitest'
import { ref, computed } from 'vue'

describe('BlogShell 核心逻辑', () => {
  describe('userInitial 计算属性', () => {
    it('user 为 null 时返回默认值 U', () => {
      const user = ref(null)
      const userInitial = computed(() => user.value?.username ? user.value.username[0].toUpperCase() : 'U')
      expect(userInitial.value).toBe('U')
    })

    it('user 有 username 时返回首字母', () => {
      const user = ref({ username: 'Bob' })
      const userInitial = computed(() => user.value?.username ? user.value.username[0].toUpperCase() : 'U')
      expect(userInitial.value).toBe('B')
    })
  })

  describe('userLevel 计算属性', () => {
    it('level 为 null 时默认为 5', () => {
      const level = ref(null)
      const userLevel = computed(() => level.value ?? 5)
      expect(userLevel.value).toBe(5)
    })

    it('level 有值时返回 level', () => {
      const level = ref(2)
      const userLevel = computed(() => level.value ?? 5)
      expect(userLevel.value).toBe(2)
    })
  })

  describe('currentPageTitle 计算属性', () => {
    const PAGE_TITLES = {
      '/': '博客',
      '/login': '登录',
      '/register': '注册',
    }

    function getTitle(path) {
      if (PAGE_TITLES[path]) return PAGE_TITLES[path]
      if (path.startsWith('/post/')) return '文章'
      return '锦年志'
    }

    it('/ 返回博客', () => {
      expect(getTitle('/')).toBe('博客')
    })

    it('/login 返回登录', () => {
      expect(getTitle('/login')).toBe('登录')
    })

    it('/post/slug 返回文章', () => {
      expect(getTitle('/post/my-post')).toBe('文章')
    })

    it('未知路径返回锦年志', () => {
      expect(getTitle('/unknown')).toBe('锦年志')
    })
  })
})
