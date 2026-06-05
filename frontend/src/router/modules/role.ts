import type { RouteRecordRaw } from 'vue-router'
import { API_PERMISSION } from '@/constants/permissions'

const children: RouteRecordRaw[] = [
  {
    path: 'users',
    name: 'AdminUsers',
    component: () => import('@/views/admin/Users.vue'),
    meta: {
      title: '用户管理',
      layout: 'guest',
      console: true,
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.AUTH_USERS_LIST
    }
  },
  {
    path: 'system',
    name: 'AdminSystemMonitor',
    component: () => import('@/views/admin/SystemMonitor.vue'),
    meta: {
      title: '系统监控',
      layout: 'guest',
      console: true,
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.SYSTEM_READ
    }
  },
  {
    path: 'resources',
    name: 'AdminResources',
    component: () => import('@/views/admin/ResourceAdmin.vue'),
    meta: {
      title: '资源管理',
      layout: 'guest',
      console: true,
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.ASSETS_READ
    }
  },
  {
    path: 'moderation/posts',
    name: 'AdminModerationPosts',
    component: () => import('@/views/admin/ModerationPosts.vue'),
    meta: {
      title: '帖子管理',
      layout: 'guest',
      console: true,
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.BLOG_POSTS_MODERATE
    }
  }
]

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/admin/Admin.vue'),
    meta: { title: '管理后台', layout: 'guest', console: true, requiresAuth: true, level: 0 },
    redirect: '/admin/moderation/posts',
    children
  }
]
