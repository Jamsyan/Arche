import type { RouteRecordRaw } from 'vue-router'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import PostDetail from '@/views/PostDetail.vue'
import Explore from '@/views/Explore.vue'
import About from '@/views/About.vue'
import Create from '@/views/Create.vue'
import Assets from '@/views/Assets.vue'
import Scheduler from '@/views/Scheduler.vue'
import GitHub from '@/views/GitHub.vue'
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
    path: '/create',
    name: 'Create',
    component: Create,
    meta: { title: '创作', layout: 'guest', requiresAuth: true }
  },
  {
    path: '/assets',
    name: 'Assets',
    component: Assets,
    meta: { title: '素材库', layout: 'guest', requiresAuth: true }
  },
  {
    path: '/scheduler',
    name: 'Scheduler',
    component: Scheduler,
    meta: { title: '调度器', layout: 'guest', requiresAuth: true }
  },
  {
    path: '/github',
    name: 'GitHub',
    component: GitHub,
    meta: { title: 'GitHub', layout: 'guest', requiresAuth: false }
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
    meta: {
      title: '个人中心',
      layout: 'guest',
      requiresAuth: true,
      permission: API_PERMISSION.AUTH_ME
    }
  },
  {
    path: '/posts',
    name: 'Posts',
    component: () => import('@/views/user/Posts.vue'),
    meta: {
      title: '我的文章',
      layout: 'guest',
      requiresAuth: true,
      permission: API_PERMISSION.BLOG_POSTS_READ
    }
  },
  {
    path: '/posts/new',
    name: 'PostCreate',
    component: () => import('@/views/user/PostEditor.vue'),
    meta: {
      title: '新建文章',
      layout: 'guest',
      requiresAuth: true,
      permission: API_PERMISSION.BLOG_POSTS_WRITE
    }
  },
  {
    path: '/posts/:id/edit',
    name: 'PostEdit',
    component: () => import('@/views/user/PostEditor.vue'),
    meta: {
      title: '编辑文章',
      layout: 'guest',
      requiresAuth: true,
      permission: API_PERMISSION.BLOG_POSTS_WRITE
    }
  },
  {
    path: '/creator',
    name: 'CreatorDashboard',
    component: () => import('@/views/user/CreatorDashboard.vue'),
    meta: {
      title: '创作者看板',
      layout: 'guest',
      requiresAuth: true,
      permission: API_PERMISSION.BLOG_POSTS_READ
    }
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
  // ====== 控制台 & 管理后台（嵌套路由，侧边栏不销毁） ======
  {
    path: '/console',
    component: () => import('@/layouts/ConsoleLayout.vue'),
    meta: { layout: 'guest', requiresAuth: true, level: 0 },
    children: [
      {
        path: '',
        name: 'Console',
        component: () => import('@/views/user/Console.vue'),
        meta: { title: '控制台首页' }
      },
      {
        path: '/admin/users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UsersOverview.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: '/admin/content',
        name: 'AdminContent',
        component: () => import('@/views/admin/ContentOverview.vue'),
        meta: { title: '内容管理' }
      },
      {
        path: '/admin/ops',
        name: 'AdminOps',
        component: () => import('@/views/admin/OpsOverview.vue'),
        meta: { title: '运维管理' }
      },
      // 子页面
      {
        path: '/admin/users/list',
        name: 'AdminUsersList',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: '用户列表', permission: 'auth:users:list' }
      },
      {
        path: '/admin/users/assets',
        name: 'AdminUsersAssets',
        component: () => import('@/views/admin/AssetsOverview.vue'),
        meta: { title: '资产管理' }
      },
      {
        path: '/admin/content/moderation',
        name: 'AdminContentModeration',
        component: () => import('@/views/admin/ModerationPosts.vue'),
        meta: { title: '帖子审核', permission: 'blog:posts:moderate' }
      },
      {
        path: '/admin/ops/system',
        name: 'AdminOpsSystem',
        component: () => import('@/views/admin/SystemMonitor.vue'),
        meta: { title: '系统监控', permission: 'system:read' }
      },
      {
        path: '/admin/ops/storage',
        name: 'AdminOpsStorage',
        component: () => import('@/views/admin/QuotaManagement.vue'),
        meta: { title: 'OSS 存储管理' }
      },
      {
        path: '/admin/ops/config',
        name: 'AdminOpsConfig',
        component: () => import('@/views/admin/ResourceAdmin.vue'),
        meta: { title: '运行时配置', permission: 'assets:read' }
      }
    ]
  },
  // ====== 托管任务 ======
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/Tasks.vue'),
    meta: { title: '托管任务', layout: 'guest', requiresAuth: true }
  },
  {
    path: '/tasks/crawler',
    name: 'TasksCrawler',
    component: () => import('@/views/Tasks.vue'),
    meta: { title: '爬虫管理', layout: 'guest', requiresAuth: true }
  },
  {
    path: '/tasks/cloud',
    name: 'TasksCloud',
    component: () => import('@/views/Tasks.vue'),
    meta: { title: '云训练管理', layout: 'guest', requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
    meta: { layout: 'guest', requiresAuth: false }
  }
]
