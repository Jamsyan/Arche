import type { RouteRecordRaw } from 'vue-router'

export const roleRoutes: Record<'guest' | 'user' | 'admin', RouteRecordRaw[]> = {
  guest: [],
  user: [
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('@/views/user/Profile.vue'),
      meta: {
        title: '个人中心',
        layout: 'user',
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
        layout: 'admin',
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
