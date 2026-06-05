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
    path: 'plugins',
    name: 'AdminPlugins',
    component: () => import('@/views/admin/Plugins.vue'),
    meta: {
      title: '插件管理',
      layout: 'guest',
      console: true,
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.ASSETS_READ
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
    path: 'oss',
    name: 'AdminOss',
    component: () => import('@/views/admin/OssAdmin.vue'),
    meta: {
      title: 'OSS 存储',
      layout: 'guest',
      console: true,
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.SYSTEM_READ
    }
  },
  {
    path: 'config',
    name: 'AdminConfig',
    component: () => import('@/views/admin/ConfigAdmin.vue'),
    meta: {
      title: '配置管理',
      layout: 'guest',
      console: true,
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.CONFIG_READ
    }
  },
  {
    path: 'crawler',
    name: 'AdminCrawler',
    component: () => import('@/views/admin/CrawlerAdmin.vue'),
    meta: {
      title: '爬虫管理',
      layout: 'guest',
      console: true,
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.CRAWLER_READ
    }
  },
  {
    path: 'assets',
    name: 'AdminAssets',
    component: () => import('@/views/admin/AssetAdmin.vue'),
    meta: {
      title: '资产目录',
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
