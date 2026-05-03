import type { RouteRecordRaw } from 'vue-router'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import PostDetail from '@/views/PostDetail.vue'
import Explore from '@/views/Explore.vue'
import About from '@/views/About.vue'
import NotFound from '@/views/NotFound.vue'
import Forbidden from '@/views/Forbidden.vue'

export const staticRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      layout: 'guest',
      requiresAuth: false
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      layout: 'guest',
      requiresAuth: false
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      layout: 'guest',
      requiresAuth: false
    }
  },
  {
    path: '/explore',
    name: 'Explore',
    component: Explore,
    meta: {
      layout: 'guest',
      requiresAuth: false
    }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: {
      layout: 'guest',
      requiresAuth: false
    }
  },
  {
    path: '/blog/:slug',
    name: 'PostDetail',
    component: PostDetail,
    meta: {
      layout: 'guest',
      requiresAuth: false
    }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: Forbidden,
    meta: {
      title: '无权限访问',
      layout: 'guest',
      requiresAuth: false
    }
  },
  {
    path: '/404',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: '页面未找到',
      layout: 'guest',
      requiresAuth: false
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
    meta: {
      layout: 'guest',
      requiresAuth: false
    }
  }
]
