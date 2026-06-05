import type { RouteRecordRaw } from 'vue-router'
import Admin from '@/views/admin/Admin.vue'
import AdminUsers from '@/views/admin/Users.vue'
import AdminPlugins from '@/views/admin/Plugins.vue'
import AdminSystemMonitor from '@/views/admin/SystemMonitor.vue'
import OssAdmin from '@/views/admin/OssAdmin.vue'
import ConfigAdmin from '@/views/admin/ConfigAdmin.vue'
import CrawlerAdmin from '@/views/admin/CrawlerAdmin.vue'
import AssetAdmin from '@/views/admin/AssetAdmin.vue'
import ModerationPosts from '@/views/admin/ModerationPosts.vue'
import { API_PERMISSION } from '@/constants/permissions'

const children: RouteRecordRaw[] = [
  {
    path: 'users',
    name: 'AdminUsers',
    component: AdminUsers,
    meta: {
      title: '用户管理',
      layout: 'admin',
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.AUTH_USERS_LIST
    }
  },
  {
    path: 'plugins',
    name: 'AdminPlugins',
    component: AdminPlugins,
    meta: {
      title: '插件管理',
      layout: 'admin',
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.ASSETS_READ
    }
  },
  {
    path: 'system',
    name: 'AdminSystemMonitor',
    component: AdminSystemMonitor,
    meta: {
      title: '系统监控',
      layout: 'admin',
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.SYSTEM_READ
    }
  },
  {
    path: 'oss',
    name: 'AdminOss',
    component: OssAdmin,
    meta: {
      title: 'OSS 存储',
      layout: 'admin',
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.SYSTEM_READ
    }
  },
  {
    path: 'config',
    name: 'AdminConfig',
    component: ConfigAdmin,
    meta: {
      title: '配置管理',
      layout: 'admin',
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.CONFIG_READ
    }
  },
  {
    path: 'crawler',
    name: 'AdminCrawler',
    component: CrawlerAdmin,
    meta: {
      title: '爬虫管理',
      layout: 'admin',
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.CRAWLER_READ
    }
  },
  {
    path: 'assets',
    name: 'AdminAssets',
    component: AssetAdmin,
    meta: {
      title: '资产目录',
      layout: 'admin',
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.ASSETS_READ
    }
  },
  {
    path: 'moderation/posts',
    name: 'AdminModerationPosts',
    component: ModerationPosts,
    meta: {
      title: '帖子管理',
      layout: 'admin',
      requiresAuth: true,
      level: 0,
      permission: API_PERMISSION.BLOG_POSTS_MODERATE
    }
  }
]

export const roleRoutes: Record<'guest' | 'user' | 'admin', RouteRecordRaw[]> = {
  guest: [],
  user: [],
  admin: [
    {
      path: '/admin',
      name: 'Admin',
      component: Admin,
      meta: { title: '管理后台', layout: 'admin', requiresAuth: true, level: 0 },
      redirect: '/admin/moderation/posts',
      children
    }
  ]
}
