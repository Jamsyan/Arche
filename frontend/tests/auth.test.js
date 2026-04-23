/**
 * 测试 useAuth 核心逻辑：登录、登出、加载用户、状态管理。
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { useAuth } from '../src/router/auth.js'

// 每个测试隔离 localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = String(value) },
    removeItem: (key) => { delete store[key] },
    clear: () => { store = {} },
  }
})()

Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock })

describe('useAuth', () => {
  beforeEach(() => {
    localStorage.clear()
    // 重置模块级状态
    const { initAuth } = useAuth()
    // 手动重置 — 因为 useAuth 是单例
    const auth = useAuth()
    auth.isAuthenticated.value = false
    auth.level.value = null
    auth.user.value = null
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('初始化', () => {
    it('无 token 时 isAuth 为 false', () => {
      const { isAuthenticated } = useAuth()
      expect(isAuthenticated.value).toBe(false)
    })

    it('有 token 和 level 时恢复状态', () => {
      localStorage.setItem('veil_token', 'test-token')
      localStorage.setItem('veil_level', '3')
      const { initAuth, isAuthenticated, level } = useAuth()
      initAuth()
      expect(isAuthenticated.value).toBe(true)
      expect(level.value).toBe(3)
    })

    it('token 存在但 level 缺失时 level 为 null', () => {
      localStorage.setItem('veil_token', 'test-token')
      const { initAuth, isAuthenticated, level } = useAuth()
      initAuth()
      expect(isAuthenticated.value).toBe(true)
      expect(level.value).toBe(null)
    })
  })

  describe('getToken / authHeaders', () => {
    it('无 token 时 getToken 返回 null', () => {
      const { getToken } = useAuth()
      expect(getToken()).toBeNull()
    })

    it('有 token 时返回 token', () => {
      localStorage.setItem('veil_token', 'abc123')
      const { getToken } = useAuth()
      expect(getToken()).toBe('abc123')
    })

    it('authHeaders 无 token 时返回空对象', () => {
      const { authHeaders } = useAuth()
      expect(authHeaders()).toEqual({})
    })

    it('authHeaders 有 token 时带 Authorization 头', () => {
      localStorage.setItem('veil_token', 'abc123')
      const { authHeaders } = useAuth()
      expect(authHeaders()).toEqual({ Authorization: 'Bearer abc123' })
    })

    it('authHeaders 合并额外头', () => {
      localStorage.setItem('veil_token', 'abc123')
      const { authHeaders } = useAuth()
      expect(authHeaders({ 'Content-Type': 'application/json' })).toEqual({
        'Content-Type': 'application/json',
        Authorization: 'Bearer abc123',
      })
    })
  })

  describe('login', () => {
    it('登录成功设置状态和 localStorage', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            code: 'ok',
            data: {
              access_token: 'new-token',
              user: { id: 1, username: 'testuser', level: 3 },
            },
          }),
        })
      )
      const { login, isAuthenticated, level, user, getToken } = useAuth()
      const result = await login('test', 'pass')
      expect(result.ok).toBe(true)
      expect(isAuthenticated.value).toBe(true)
      expect(level.value).toBe(3)
      expect(user.value.username).toBe('testuser')
      expect(getToken()).toBe('new-token')
      expect(localStorage.getItem('veil_token')).toBe('new-token')
      expect(localStorage.getItem('veil_level')).toBe('3')
    })

    it('登录失败返回错误', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: false,
          json: () => Promise.resolve({ message: '密码错误' }),
        })
      )
      const { login } = useAuth()
      const result = await login('test', 'wrong')
      expect(result.ok).toBe(false)
      expect(result.error).toBe('密码错误')
    })

    it('网络错误返回错误', async () => {
      globalThis.fetch = vi.fn(() => Promise.reject(new Error('network')))
      const { login } = useAuth()
      const result = await login('test', 'pass')
      expect(result.ok).toBe(false)
    })
  })

  describe('register', () => {
    it('注册成功设置状态', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            code: 'ok',
            data: {
              access_token: 'reg-token',
              user: { id: 2, username: 'newuser', level: 4 },
            },
          }),
        })
      )
      const { register, isAuthenticated, level, user } = useAuth()
      const result = await register('a@b.com', 'newuser', '123456')
      expect(result.ok).toBe(true)
      expect(isAuthenticated.value).toBe(true)
      expect(level.value).toBe(4)
      expect(user.value.username).toBe('newuser')
    })
  })

  describe('logout', () => {
    it('清除本地状态和 storage', async () => {
      localStorage.setItem('veil_token', 'tok')
      localStorage.setItem('veil_level', '2')
      globalThis.fetch = vi.fn(() => Promise.resolve({ ok: true }))
      const { logout, isAuthenticated, level, user, getToken } = useAuth()
      // 先设状态
      const auth = useAuth()
      auth.isAuthenticated.value = true
      auth.level.value = 2
      auth.user.value = { id: 1 }
      await logout()
      expect(isAuthenticated.value).toBe(false)
      expect(level.value).toBe(null)
      expect(user.value).toBe(null)
      expect(getToken()).toBeNull()
      expect(localStorage.getItem('veil_token')).toBeNull()
      expect(localStorage.getItem('veil_level')).toBeNull()
    })

    it('服务端不可达仍清除本地状态', async () => {
      localStorage.setItem('veil_token', 'tok')
      globalThis.fetch = vi.fn(() => Promise.reject(new Error('down')))
      const { logout, isAuthenticated, getToken } = useAuth()
      const auth = useAuth()
      auth.isAuthenticated.value = true
      await logout()
      expect(isAuthenticated.value).toBe(false)
      expect(getToken()).toBeNull()
    })
  })

  describe('loadUser', () => {
    it('无 token 时清空状态', async () => {
      const { loadUser, isAuthenticated, level, user } = useAuth()
      const auth = useAuth()
      auth.isAuthenticated.value = true
      auth.level.value = 3
      auth.user.value = { id: 1 }
      await loadUser()
      expect(isAuthenticated.value).toBe(false)
      expect(level.value).toBe(null)
      expect(user.value).toBe(null)
    })

    it('有 token 且接口正常时刷新用户信息', async () => {
      localStorage.setItem('veil_token', 'tok')
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            code: 'ok',
            data: { id: 1, username: 'refreshed', level: 2 },
          }),
        })
      )
      const { loadUser, user, level } = useAuth()
      await loadUser()
      expect(user.value.username).toBe('refreshed')
      expect(level.value).toBe(2)
    })

    it('401 时自动 logout', async () => {
      localStorage.setItem('veil_token', 'expired')
      const { loadUser, logout, isAuthenticated } = useAuth()
      // mock logout 以便验证
      const origLogout = useAuth().logout
      globalThis.fetch = vi.fn(() => Promise.resolve({ ok: false, status: 401 }))
      await loadUser()
      expect(isAuthenticated.value).toBe(false)
    })

    it('500 时保留本地状态', async () => {
      localStorage.setItem('veil_token', 'tok')
      localStorage.setItem('veil_level', '3')
      globalThis.fetch = vi.fn(() => Promise.resolve({ ok: false, status: 500 }))
      const { loadUser, isAuthenticated, level } = useAuth()
      const auth = useAuth()
      auth.isAuthenticated.value = true
      auth.level.value = 3
      await loadUser()
      expect(isAuthenticated.value).toBe(true)
      expect(level.value).toBe(3)
    })
  })
})
