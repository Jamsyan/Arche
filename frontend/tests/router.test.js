/**
 * 测试路由守卫逻辑（beforeEach 回调）。
 * 不依赖 router 实例，直接测试守卫函数。
 */
import { describe, it, expect, beforeEach } from 'vitest'

// 守卫逻辑提取为纯函数（与 router/index.js 中的 beforeEach 一致）
function guardBefore(to) {
  const token = localStorage.getItem('veil_token')
  const storedLevel = localStorage.getItem('veil_level')
  const userLevel = storedLevel !== null ? parseInt(storedLevel, 10) : null

  if (to.name === 'login' || to.name === 'register') {
    if (userLevel !== null) return '/'
    return
  }

  if (to.meta.requiredLevel !== undefined) {
    if (userLevel === null) return '/login'
    if (userLevel > to.meta.requiredLevel) return '/'
  }
}

describe('路由守卫', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('未登录用户', () => {
    it('访问 /platform 重定向到 /login', () => {
      const result = guardBefore({ name: 'platform', meta: { requiredLevel: 4 }, path: '/platform' })
      expect(result).toBe('/login')
    })

    it('访问 / 正常通过', () => {
      const result = guardBefore({ name: 'blog-home', meta: {}, path: '/' })
      expect(result).toBeUndefined()
    })

    it('访问 /login 正常通过', () => {
      const result = guardBefore({ name: 'login', meta: {}, path: '/login' })
      expect(result).toBeUndefined()
    })

    it('访问 /register 正常通过', () => {
      const result = guardBefore({ name: 'register', meta: {}, path: '/register' })
      expect(result).toBeUndefined()
    })

    it('访问 /post/slug 正常通过', () => {
      const result = guardBefore({ name: 'blog-post', meta: {}, path: '/post/test' })
      expect(result).toBeUndefined()
    })
  })

  describe('已登录用户', () => {
    it('已登录访问 /login 重定向到首页', () => {
      localStorage.setItem('veil_token', 'tok')
      localStorage.setItem('veil_level', '3')
      const result = guardBefore({ name: 'login', meta: {}, path: '/login' })
      expect(result).toBe('/')
    })

    it('已登录访问 /register 重定向到首页', () => {
      localStorage.setItem('veil_token', 'tok')
      localStorage.setItem('veil_level', '3')
      const result = guardBefore({ name: 'register', meta: {}, path: '/register' })
      expect(result).toBe('/')
    })

    it('P3 用户访问 P4 路由（/platform）正常通过', () => {
      localStorage.setItem('veil_token', 'tok')
      localStorage.setItem('veil_level', '3')
      const result = guardBefore({ name: 'platform', meta: { requiredLevel: 4 }, path: '/platform' })
      expect(result).toBeUndefined()
    })

    it('P5 用户访问 P4 路由重定向到首页', () => {
      localStorage.setItem('veil_token', 'tok')
      localStorage.setItem('veil_level', '5')
      const result = guardBefore({ name: 'platform', meta: { requiredLevel: 4 }, path: '/platform' })
      expect(result).toBe('/')
    })

    it('P3 用户访问 P3 路由（/editor）正常通过', () => {
      localStorage.setItem('veil_token', 'tok')
      localStorage.setItem('veil_level', '3')
      const result = guardBefore({ name: 'blog-editor', meta: { requiredLevel: 3 }, path: '/editor' })
      expect(result).toBeUndefined()
    })

    it('P3 用户访问 P0 路由重定向到首页', () => {
      localStorage.setItem('veil_token', 'tok')
      localStorage.setItem('veil_level', '3')
      const result = guardBefore({ name: 'admin-panel', meta: { requiredLevel: 0 }, path: '/admin' })
      expect(result).toBe('/')
    })

    it('P0 用户访问 P0 路由正常通过', () => {
      localStorage.setItem('veil_token', 'tok')
      localStorage.setItem('veil_level', '0')
      const result = guardBefore({ name: 'admin-panel', meta: { requiredLevel: 0 }, path: '/admin' })
      expect(result).toBeUndefined()
    })

    it('P4 用户访问 P1 路由重定向到首页', () => {
      localStorage.setItem('veil_token', 'tok')
      localStorage.setItem('veil_level', '4')
      const result = guardBefore({ name: 'file-upload', meta: { requiredLevel: 1 }, path: '/upload' })
      expect(result).toBe('/')
    })
  })
})
