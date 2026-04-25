import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      layout: 'guest', // 公开布局
      requiresAuth: false // 不需要登录
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
    path: '/:pathMatch(.*)*',
    component: () => import('../views/NotFound.vue'),
    meta: {
      layout: 'guest',
      requiresAuth: false
    }
  }
]

// 角色路由配置，不同角色可以访问的路由
export const roleRoutes = {
  guest: [], // 访客没有额外路由
  user: [
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('@/views/user/Profile.vue'),
      meta: {
        title: '个人中心',
        layout: 'user', // 用户布局
        requiresAuth: true
      }
    },
    {
      path: '/posts',
      name: 'Posts',
      component: () => import('@/views/user/Posts.vue'),
      meta: {
        title: '我的文章',
        layout: 'user',
        requiresAuth: true
      }
    }
  ],
  admin: [
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('@/views/admin/Admin.vue'),
      meta: {
        title: '管理后台',
        layout: 'admin', // 管理员布局
        requiresAuth: true,
        role: 'admin'
      },
      redirect: '/admin/users',
      children: [
        {
          path: 'users',
          name: 'AdminUsers',
          component: () => import('@/views/admin/Users.vue'),
          meta: {
            title: '用户管理',
            layout: 'admin',
            requiresAuth: true,
            role: 'admin'
          }
        },
        {
          path: 'plugins',
          name: 'AdminPlugins',
          component: () => import('@/views/admin/Plugins.vue'),
          meta: {
            title: '插件管理',
            layout: 'admin',
            requiresAuth: true,
            role: 'admin'
          }
        }
      ]
    }
  ]
}

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
