import type { RouteRecordRaw } from 'vue-router'
import { API_PERMISSION } from '@/constants/permissions'

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
        requiresAuth: true,
        permission: API_PERMISSION.AUTH_ME,
        icon: 'PersonOutline'
      }
    },
    {
      path: '/posts',
      name: 'Posts',
      component: () => import('@/views/user/Posts.vue'),
      meta: {
        title: '我的文章',
        layout: 'user',
        requiresAuth: true,
        permission: API_PERMISSION.BLOG_POSTS_READ,
        icon: 'DocumentTextOutline'
      }
    },
    {
      path: '/posts/new',
      name: 'PostCreate',
      component: () => import('@/views/user/PostEditor.vue'),
      meta: {
        title: '新建文章',
        layout: 'user',
        requiresAuth: true,
        permission: API_PERMISSION.BLOG_POSTS_WRITE,
        icon: 'CreateOutline',
        menu: false
      }
    },
    {
      path: '/posts/:id/edit',
      name: 'PostEdit',
      component: () => import('@/views/user/PostEditor.vue'),
      meta: {
        title: '编辑文章',
        layout: 'user',
        requiresAuth: true,
        permission: API_PERMISSION.BLOG_POSTS_WRITE,
        icon: 'CreateOutline',
        menu: false
      }
    },
    {
      path: '/creator',
      name: 'CreatorDashboard',
      component: () => import('@/views/user/CreatorDashboard.vue'),
      meta: {
        title: '创作者看板',
        layout: 'user',
        requiresAuth: true,
        permission: API_PERMISSION.BLOG_POSTS_READ,
        icon: 'InformationCircleOutline'
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
        role: 'admin',
        permission: API_PERMISSION.AUTH_USERS_LIST,
        menu: false
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
            role: 'admin',
            permission: API_PERMISSION.AUTH_USERS_LIST,
            icon: 'PeopleOutline'
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
            role: 'admin',
            permission: API_PERMISSION.ASSETS_READ,
            icon: 'AppsOutline'
          }
        },
        {
          path: 'moderation/pending',
          name: 'AdminModerationPending',
          component: () => import('@/views/admin/ModerationPending.vue'),
          meta: {
            title: '待审核帖子',
            layout: 'admin',
            requiresAuth: true,
            role: 'admin',
            permission: API_PERMISSION.BLOG_POSTS_MODERATE,
            icon: 'CheckmarkCircleOutline'
          }
        },
        {
          path: 'moderation/posts',
          name: 'AdminModerationPosts',
          component: () => import('@/views/admin/ModerationPosts.vue'),
          meta: {
            title: '帖子管理',
            layout: 'admin',
            requiresAuth: true,
            role: 'admin',
            permission: API_PERMISSION.BLOG_POSTS_MODERATE,
            icon: 'DocumentTextOutline'
          }
        }
      ]
    }
  ]
}
