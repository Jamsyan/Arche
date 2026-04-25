// 认证相关的组合式函数
// 后续会完善实现
import { ref, computed } from 'vue'

export type UserRole = 'guest' | 'user' | 'admin'

interface User {
  id: string
  name: string
  role: UserRole
  avatar?: string
}

// 模拟用户状态
const currentUser = ref<User | null>(null)
const isAuthenticated = computed(() => currentUser.value !== null)
const userRole = computed(() => currentUser.value?.role ?? 'guest')

// 模拟登录
export async function login(role: UserRole = 'user') {
  const mockUsers: Record<UserRole, User> = {
    guest: { id: 'guest', name: '访客', role: 'guest' },
    user: { id: 'user-1', name: '普通用户', role: 'user', avatar: '/user-avatar.png' },
    admin: { id: 'admin-1', name: '管理员', role: 'admin', avatar: '/admin-avatar.png' }
  }
  currentUser.value = mockUsers[role]
  return Promise.resolve()
}

// 模拟登出
export async function logout() {
  currentUser.value = null
  return Promise.resolve()
}

export function useAuth() {
  return {
    currentUser,
    isAuthenticated,
    userRole,
    login,
    logout
  }
}
