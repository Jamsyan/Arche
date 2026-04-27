import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/services/api/auth'
import { loginApi, logoutApi, getUserInfoApi, type LoginParams } from '@/services/api/auth'
import { usePermissionStore } from '@/store/modules/permission'

export type UserRole = 'user' | 'admin' | 'guest'

export const useUserStore = defineStore(
  'user',
  () => {
    // token
    const token = ref<string | null>(localStorage.getItem('token'))
    // 用户信息
    const userInfo = ref<UserInfo | null>(null)
    // 登录状态
    const isLoggedIn = computed(() => !!token.value && !!userInfo.value)

    const applyUserSession = (nextToken: string, nextUserInfo: UserInfo) => {
      const permissionStore = usePermissionStore()

      token.value = nextToken
      userInfo.value = nextUserInfo
      permissionStore.setUserPermission(nextUserInfo.role, nextUserInfo.permissions)

      localStorage.setItem('token', nextToken)
      localStorage.setItem('userInfo', JSON.stringify(nextUserInfo))
    }

    const mockUsers: Record<UserRole, UserInfo> = {
      user: {
        id: '1',
        username: 'user',
        nickname: '普通用户',
        role: 'user',
        permissions: ['posts:read', 'posts:edit']
      },
      admin: {
        id: '2',
        username: 'admin',
        nickname: '管理员',
        role: 'admin',
        permissions: ['*']
      },
      guest: {
        id: '3',
        username: 'guest',
        nickname: '访客',
        role: 'guest',
        permissions: []
      }
    }

    // 真实登录入口，后续页面接账号密码时仍走同一条身份链路
    const login = async (params: LoginParams) => {
      const res = await loginApi(params)
      applyUserSession(res.token, res.userInfo)
      return res
    }

    // 演示模式登录，只保留在 userStore 内，避免再扩散第二套认证状态
    const loginAsRole = async (role: UserRole) => {
      const res = {
        token: `mock-token-${role}-${Date.now()}`,
        userInfo: mockUsers[role]
      }

      applyUserSession(res.token, res.userInfo)
      return res
    }

    // 登出
    const logout = async () => {
      try {
        await logoutApi()
      } finally {
        // 无论接口是否调用成功，都清除本地状态
        clearUserState()
      }
    }

    // 获取用户信息
    const getUserInfo = async () => {
      const res = await getUserInfoApi()
      userInfo.value = res
      localStorage.setItem('userInfo', JSON.stringify(res))
      usePermissionStore().setUserPermission(res.role, res.permissions)
      return res
    }

    // 清除用户状态
    const clearUserState = () => {
      token.value = null
      userInfo.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      usePermissionStore().resetPermission()
    }

    // 初始化用户状态，从localStorage恢复
    const initUserState = () => {
      const savedToken = localStorage.getItem('token')
      const savedUserInfo = localStorage.getItem('userInfo')
      if (savedToken) {
        token.value = savedToken
      }
      if (savedUserInfo) {
        try {
          const parsedUserInfo = JSON.parse(savedUserInfo) as UserInfo
          userInfo.value = parsedUserInfo
          usePermissionStore().setUserPermission(parsedUserInfo.role, parsedUserInfo.permissions)
        } catch (e) {
          console.error('解析用户信息失败:', e)
          localStorage.removeItem('userInfo')
        }
      }
    }

    return {
      token,
      userInfo,
      isLoggedIn,
      login,
      loginAsRole,
      logout,
      getUserInfo,
      clearUserState,
      initUserState
    }
  },
  {
    persist: false // 这里我们自己处理持久化，不需要插件
  }
)
