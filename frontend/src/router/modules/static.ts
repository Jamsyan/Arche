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
    path: '/console',
    name: 'Console',
    component: () => import('@/views/user/Console.vue'),
    meta: {
      title: '控制台',
      layout: 'guest',
      requiresAuth: true,
      console: true
    }
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
      console: true,
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
      console: true,
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
      console: true,
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
      console: true,
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
      console: true,
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
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
    meta: { layout: 'guest', requiresAuth: false }
  }
]
