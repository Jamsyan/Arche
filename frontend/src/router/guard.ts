import router from './index'
import { resetAllStores } from '@/store'
import { useUserStore } from '@/store/modules/user'
import { usePermissionStore } from '@/store/modules/permission'
import { $message } from '@/utils/message'
import { AUTH_UNAUTHORIZED_EVENT } from '@/constants/auth'
import { cancelAllPendingRequests } from '@/services/request'
let routerInitiated = false

const onUnauthorized = () => {
  resetAllStores()

  if (router.currentRoute.value.path !== '/login') {
    router.push('/login')
  }
}

window.addEventListener(AUTH_UNAUTHORIZED_EVENT, onUnauthorized)

const canAccessRoutePermission = (
  permissionStore: ReturnType<typeof usePermissionStore>,
  routePermission: unknown
) => {
  if (!routePermission) {
    return true
  }

  if (typeof routePermission === 'string') {
    return permissionStore.hasPermission(routePermission)
  }

  if (Array.isArray(routePermission)) {
    return routePermission.some((permission) => permissionStore.hasPermission(String(permission)))
  }

  return true
}

router.beforeEach(async (to, from, next) => {
  if (from.path && from.path !== to.path) {
    cancelAllPendingRequests()
  }

  const userStore = useUserStore()
  const permissionStore = usePermissionStore()

  // 初始化用户状态（页面刷新时从localStorage恢复）
  if (!routerInitiated) {
    userStore.initUserState()
    routerInitiated = true
  }

  const token = userStore.token
  // 公开页面（requiresAuth=false）允许匿名访问
  if (to.meta?.requiresAuth === false || permissionStore.whiteList.includes(to.path)) {
    next()
    return
  }

  // 没有token，跳转到登录页
  if (!token) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  // 有token，但是用户信息不存在，获取用户信息
  if (!userStore.userInfo) {
    try {
      await userStore.getUserInfo()
    } catch {
      // 获取用户信息失败，说明token过期，跳转到登录页
      $message.error('登录已过期，请重新登录')
      userStore.clearUserState()
      permissionStore.resetPermission()
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
  }

  // 如果路由还没有加载，生成可访问的路由
  if (!permissionStore.routesLoaded && userStore.userInfo) {
    try {
      // 根据用户角色生成路由
      const routes = await permissionStore.generateRoutes(userStore.userInfo.role)
      // 动态添加路由
      routes.forEach((route) => {
        router.addRoute(route)
      })
      // 重定向到当前路径，确保路由已经加载
      next({ ...to, replace: true })
      return
    } catch {
      // 生成路由失败，跳转到首页
      $message.error('获取权限失败，请重新登录')
      next({ path: '/' })
      return
    }
  }

  const requiredPermission = to.meta?.permission
  if (!canAccessRoutePermission(permissionStore, requiredPermission)) {
    next({ path: '/403', query: { redirect: to.fullPath } })
    return
  }

  // 路由存在，正常访问
  next()
})

router.afterEach((to) => {
  // 设置页面标题
  document.title = (to.meta?.title as string) || 'Arche'
})
