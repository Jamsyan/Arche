import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RouteRecordRaw } from 'vue-router'
import { roleRoutes } from '@/router'

export const usePermissionStore = defineStore(
  'permission',
  () => {
    const routes = ref<RouteRecordRaw[]>([])
    const permissions = ref<string[]>([])
    const role = ref<string>('guest')
    const level = ref<number>(5) // P0=最高, P5=最低
    const routesLoaded = ref(false)

    const whiteList = ['/login', '/404', '/403']

    // P等级检查：等级数字越小权限越高
    const hasLevel = (requiredLevel: number): boolean => level.value <= requiredLevel

    const hasPermission = (permission: string): boolean => {
      return (
        level.value === 0 ||
        permissions.value.includes('*') ||
        permissions.value.includes(permission)
      )
    }

    const generateRoutes = async (userRole: string): Promise<RouteRecordRaw[]> => {
      role.value = userRole
      const accessibleRoutes = roleRoutes[userRole as keyof typeof roleRoutes] || []
      routes.value = accessibleRoutes
      routesLoaded.value = true
      return accessibleRoutes
    }

    const setPermissions = (perms: string[]) => {
      permissions.value = perms
    }

    const setUserPermission = (userRole: string, perms: string[] = [], userLevel = 5) => {
      role.value = userRole
      permissions.value = perms
      level.value = userLevel
    }

    const resetPermission = () => {
      routes.value = []
      permissions.value = []
      role.value = 'guest'
      level.value = 5
      routesLoaded.value = false
    }

    const resetState = () => {
      resetPermission()
    }

    return {
      routes,
      permissions,
      role,
      level,
      routesLoaded,
      whiteList,
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
