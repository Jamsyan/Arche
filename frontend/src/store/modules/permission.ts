import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { RouteRecordRaw } from 'vue-router'
import { roleRoutes } from '@/router'

// 路由权限类型
export interface PermissionState {
  // 可访问的路由
  routes: RouteRecordRaw[]
  // 权限码列表
  permissions: string[]
  // 角色
  role: string
  // 路由是否已经加载
  routesLoaded: boolean
}

export const usePermissionStore = defineStore(
  'permission',
  () => {
    const routes = ref<RouteRecordRaw[]>([])
    const permissions = ref<string[]>([])
    const role = ref<string>('guest')
    const routesLoaded = ref(false)

    // 路由白名单，不需要权限就可以访问
    const whiteList = ['/login', '/404', '/403']

    // 检查是否有权限
    const hasPermission = (permission: string): boolean => {
      return permissions.value.includes(permission) || role.value === 'admin'
    }

    // 根据角色生成可访问的路由
    const generateRoutes = async (userRole: string): Promise<RouteRecordRaw[]> => {
      role.value = userRole
      // 从路由配置中获取对应用户角色的路由
      const accessibleRoutes = roleRoutes[userRole as keyof typeof roleRoutes] || []
      routes.value = accessibleRoutes
      routesLoaded.value = true
      return accessibleRoutes
    }

    // 设置权限列表
    const setPermissions = (perms: string[]) => {
      permissions.value = perms
    }

    // 重置权限状态
    const resetPermission = () => {
      routes.value = []
      permissions.value = []
      role.value = 'guest'
      routesLoaded.value = false
    }

    return {
      routes,
      permissions,
      role,
      routesLoaded,
      whiteList,
      hasPermission,
      generateRoutes,
      setPermissions,
      resetPermission
    }
  },
  {
    persist: false // 权限不需要持久化，每次登录重新获取
  }
)
