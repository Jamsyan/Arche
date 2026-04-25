import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/services/api/auth'
import { loginApi, logoutApi, getUserInfoApi, type LoginParams } from '@/services/api/auth'

export const useUserStore = defineStore(
  'user',
  () => {
    // token
    const token = ref<string | null>(localStorage.getItem('token'))
    // 用户信息
    const userInfo = ref<UserInfo | null>(null)
    // 登录状态
    const isLoggedIn = computed(() => !!token.value && !!userInfo.value)

    // 登录（演示模式，直接传角色）
    const login = async (role: 'user' | 'admin' | 'guest') => {
      // 模拟调用登录接口
      // const res = await loginApi(params)

      // 模拟返回数据
      const mockUsers = {
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

      const res = {
        token: `mock-token-${role}-${Date.now()}`,
        userInfo: mockUsers[role]
      }

      token.value = res.token
      userInfo.value = res.userInfo
      // 保存token到localStorage
      localStorage.setItem('token', res.token)
      localStorage.setItem('userInfo', JSON.stringify(res.userInfo))
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
      return res
    }

    // 清除用户状态
    const clearUserState = () => {
      token.value = null
      userInfo.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
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
          userInfo.value = JSON.parse(savedUserInfo)
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
