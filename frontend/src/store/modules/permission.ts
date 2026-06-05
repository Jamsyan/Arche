import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RouteRecordRaw } from 'vue-router'
import router, { adminRoutes } from '@/router'

export const usePermissionStore = defineStore(
  'permission',
  () => {
    const routes = ref<RouteRecordRaw[]>([])
    const permissions = ref<string[]>([])
    const level = ref<number>(5) // P0=最高, P5=最低
    const routesLoaded = ref(false)

    const whiteList = ['/login', '/404', '/403']

    // 是否为管理员（level 0）
    const isAdmin = () => level.value === 0

    // P等级检查：等级数字越小权限越高
    const hasLevel = (requiredLevel: number): boolean => level.value <= requiredLevel

    const hasPermission = (permission: string): boolean => {
      return (
        level.value === 0 ||
        permissions.value.includes('*') ||
        permissions.value.includes(permission)
      )
    }

    const generateRoutes = async (userLevel: number): Promise<RouteRecordRaw[]> => {
      // 清除之前动态注册的 admin 路由
      if (router.hasRoute('Admin')) {
        router.removeRoute('Admin')
      }

      const accessibleRoutes = userLevel === 0 ? adminRoutes : []
      routes.value = accessibleRoutes

      // 管理员动态注册 admin 路由
      if (userLevel === 0 && adminRoutes.length > 0) {
        router.addRoute(adminRoutes[0]!)
      }

      routesLoaded.value = true
      return accessibleRoutes
    }

    const setPermissions = (perms: string[]) => {
      permissions.value = perms
    }

    const setUserPermission = (perms: string[] = [], userLevel = 5) => {
      permissions.value = perms
      level.value = userLevel
    }

    const resetPermission = () => {
      // 清除动态注册的 admin 路由
      if (router.hasRoute('Admin')) {
        router.removeRoute('Admin')
      }

      routes.value = []
      permissions.value = []
      level.value = 5
      routesLoaded.value = false
    }

    const resetState = () => {
      resetPermission()
    }

    return {
      routes,
      permissions,
      level,
      routesLoaded,
      whiteList,
      isAdmin,
      hasLevel,
      hasPermission,
      generateRoutes,
      setPermissions,
      setUserPermission,
      resetPermission,
      resetState
    }
  },
  {
    persist: false
  }
)
