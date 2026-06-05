import type { RouteRecordRaw } from 'vue-router'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import PostDetail from '@/views/PostDetail.vue'
import Explore from '@/views/Explore.vue'
import About from '@/views/About.vue'
import NotFound from '@/views/NotFound.vue'
import Forbidden from '@/views/Forbidden.vue'
import { API_PERMISSION } from '@/constants/permissions'

export const staticRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { layout: 'guest', requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { layout: 'guest', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { layout: 'guest', requiresAuth: false }
  },
  {
    path: '/explore',
    name: 'Explore',
    component: Explore,
    meta: { layout: 'guest', requiresAuth: false }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: { layout: 'guest', requiresAuth: false }
  },
  {
    path: '/console',
    name: 'Console',
    component: () => import('@/views/user/Console.vue'),
    meta: { title: '控制台', layout: 'guest', requiresAuth: true, console: true }
  },
  {
    path: '/blog/:slug',
    name: 'PostDetail',
    component: PostDetail,
    meta: { layout: 'guest', requiresAuth: false }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/user/Profile.vue'),
    meta: { title: '个人中心', layout: 'guest', requiresAuth: true, console: true, permission: API_PERMISSION.AUTH_ME }
  },
  {
    path: '/posts',
    name: 'Posts',
    component: () => import('@/views/user/Posts.vue'),
    meta: { title: '我的文章', layout: 'guest', requiresAuth: true, console: true, permission: API_PERMISSION.BLOG_POSTS_READ }
  },
  {
    path: '/posts/new',
    name: 'PostCreate',
    component: () => import('@/views/user/PostEditor.vue'),
    meta: { title: '新建文章', layout: 'guest', requiresAuth: true, console: true, permission: API_PERMISSION.BLOG_POSTS_WRITE }
  },
  {
    path: '/posts/:id/edit',
    name: 'PostEdit',
    component: () => import('@/views/user/PostEditor.vue'),
    meta: { title: '编辑文章', layout: 'guest', requiresAuth: true, console: true, permission: API_PERMISSION.BLOG_POSTS_WRITE }
  },
  {
    path: '/creator',
    name: 'CreatorDashboard',
    component: () => import('@/views/user/CreatorDashboard.vue'),
    meta: { title: '创作者看板', layout: 'guest', requiresAuth: true, console: true, permission: API_PERMISSION.BLOG_POSTS_READ }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/admin/Admin.vue'),
    meta: { title: '管理后台', layout: 'guest', requiresAuth: true, console: true, level: 0, permission: API_PERMISSION.AUTH_USERS_LIST },
    redirect: '/admin/users',
    children: [
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: '用户管理', layout: 'guest', requiresAuth: true, level: 0, permission: API_PERMISSION.AUTH_USERS_LIST }
      },
      {
        path: 'plugins',
        name: 'AdminPlugins',
        component: () => import('@/views/admin/Plugins.vue'),
        meta: { title: '插件管理', layout: 'guest', requiresAuth: true, level: 0, permission: API_PERMISSION.ASSETS_READ }
      },
      {
        path: 'system',
        name: 'AdminSystemMonitor',
        component: () => import('@/views/admin/SystemMonitor.vue'),
        meta: { title: '系统监控', layout: 'guest', requiresAuth: true, level: 0, permission: API_PERMISSION.SYSTEM_READ }
      },
      {
        path: 'oss',
        name: 'AdminOss',
        component: () => import('@/views/admin/OssAdmin.vue'),
        meta: { title: 'OSS 存储', layout: 'guest', requiresAuth: true, level: 0, permission: API_PERMISSION.SYSTEM_READ }
      },
      {
        path: 'config',
        name: 'AdminConfig',
        component: () => import('@/views/admin/ConfigAdmin.vue'),
        meta: { title: '配置管理', layout: 'guest', requiresAuth: true, level: 0, permission: API_PERMISSION.CONFIG_READ }
      },
      {
        path: 'crawler',
        name: 'AdminCrawler',
        component: () => import('@/views/admin/CrawlerAdmin.vue'),
        meta: { title: '爬虫管理', layout: 'guest', requiresAuth: true, level: 0, permission: API_PERMISSION.CRAWLER_READ }
      },
      {
        path: 'assets',
        name: 'AdminAssets',
        component: () => import('@/views/admin/AssetAdmin.vue'),
        meta: { title: '资产目录', layout: 'guest', requiresAuth: true, level: 0, permission: API_PERMISSION.ASSETS_READ }
      },
      {
        path: 'moderation/posts',
        name: 'AdminModerationPosts',
        component: () => import('@/views/admin/ModerationPosts.vue'),
        meta: { title: '帖子管理', layout: 'guest', requiresAuth: true, level: 0, permission: API_PERMISSION.BLOG_POSTS_MODERATE }
      }
    ]
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: Forbidden,
    meta: { title: '无权限访问', layout: 'guest', requiresAuth: false }
  },
  {
    path: '/404',
    name: 'NotFound',
    component: NotFound,
    meta: { title: '页面未找到', layout: 'guest', requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
    meta: { layout: 'guest', requiresAuth: false }
  }
]
