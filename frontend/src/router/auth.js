import { ref } from 'vue'

const TOKEN_KEY = 'veil_token'
const LEVEL_KEY = 'veil_level'

// 模块级响应式状态，所有组件共享
const isAuthenticated = ref(false)
const level = ref(null)
const user = ref(null)

// 初始化：从 localStorage 恢复登录状态
function initAuth() {
  const token = localStorage.getItem(TOKEN_KEY)
  const storedLevel = localStorage.getItem(LEVEL_KEY)
  if (token) {
    isAuthenticated.value = true
    level.value = storedLevel !== null ? parseInt(storedLevel, 10) : null
  }
}

export function useAuth() {
  /**
   * 获取当前用户的 token
   */
  function getToken() {
    return localStorage.getItem(TOKEN_KEY)
  }

  /**
   * 构建带 Bearer token 的请求头
   */
  function authHeaders(extra = {}) {
    const token = getToken()
    return token
      ? { ...extra, Authorization: `Bearer ${token}` }
      : extra
  }

  /**
   * 登录
   * @param {string} username
   * @param {string} password
   * @returns {{ ok: boolean, error?: string }}
   */
  async function login(username, password) {
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        return { ok: false, error: err.message || '登录失败' }
      }
      const resData = await res.json()
      // 后端: { "code": "ok", "data": { "access_token": "...", "user": {...} } }
      const { access_token, user: userInfo } = resData.data
      localStorage.setItem(TOKEN_KEY, access_token)
      const userLevel = parseInt(userInfo.level, 10)
      localStorage.setItem(LEVEL_KEY, String(userLevel))
      isAuthenticated.value = true
      level.value = userLevel
      user.value = userInfo
      return { ok: true }
    } catch {
      return { ok: false, error: '网络错误，请稍后重试' }
    }
  }

  /**
   * 注册（新用户默认 P5）
   * @param {string} username
   * @param {string} password
   * @returns {{ ok: boolean, error?: string }}
   */
  async function register(username, password) {
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        return { ok: false, error: err.message || '注册失败' }
      }
      const resData = await res.json()
      // 后端: { "code": "ok", "data": { "user": {...} } } 注册也返回 access_token
      const { access_token, user: userInfo } = resData.data
      localStorage.setItem(TOKEN_KEY, access_token)
      const userLevel = parseInt(userInfo.level, 10)
      localStorage.setItem(LEVEL_KEY, String(userLevel))
      isAuthenticated.value = true
      level.value = userLevel
      user.value = userInfo
      return { ok: true }
    } catch {
      return { ok: false, error: '网络错误，请稍后重试' }
    }
  }

  /**
   * 登出
   */
  async function logout() {
    const token = getToken()
    if (token) {
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: authHeaders()
        })
      } catch {
        // 服务端不可达也清除本地状态
      }
    }
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(LEVEL_KEY)
    isAuthenticated.value = false
    level.value = null
    user.value = null
  }

  /**
   * 从服务端加载用户信息（刷新 token 后调用）
   */
  async function loadUser() {
    const token = getToken()
    if (!token) {
      isAuthenticated.value = false
      level.value = null
      user.value = null
      return
    }
    try {
      const res = await fetch('/api/auth/me', {
        headers: authHeaders()
      })
      if (res.ok) {
        const resData = await res.json()
        const userData = resData.data
        isAuthenticated.value = true
        level.value = parseInt(userData.level, 10)
        user.value = userData
        localStorage.setItem(LEVEL_KEY, String(userData.level))
      } else if (res.status === 401) {
        // 仅 401 确认 token 失效，才清除本地状态
        logout()
      }
      // 其他错误码（如 500/404）说明接口尚未就绪，保留本地状态
    } catch {
      // 网络不可达，保留本地状态
    }
  }

  return {
    isAuthenticated,
    level,
    user,
    initAuth,
    getToken,
    authHeaders,
    login,
    register,
    logout,
    loadUser
  }
}
