import { ref } from 'vue'

const isAuthenticated = ref(false)
const role = ref(null)

export function useAuth() {
  async function loadUser() {
    try {
      const res = await fetch('/api/auth/me')
      if (res.ok) {
        const data = await res.json()
        isAuthenticated.value = true
        role.value = data.role
      }
    } catch {
      isAuthenticated.value = false
      role.value = null
    }
  }

  async function login(username, password) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
    if (res.ok) {
      await loadUser()
      return { ok: true }
    }
    return { ok: false, error: 'Login failed' }
  }

  async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' })
    isAuthenticated.value = false
    role.value = null
  }

  return { isAuthenticated, role, loadUser, login, logout }
}
