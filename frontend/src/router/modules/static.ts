import type { RouteRecordRaw } from 'vue-router'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import PostDetail from '@/views/PostDetail.vue'
import Explore from '@/views/Explore.vue'
import About from '@/views/About.vue'
import NotFound from '@/views/NotFound.vue'
import Forbidden from '@/views/Forbidden.vue'
import Console from '@/views/user/Console.vue'
import Profile from '@/views/user/Profile.vue'
import Posts from '@/views/user/Posts.vue'
import PostEditor from '@/views/user/PostEditor.vue'
import CreatorDashboard from '@/views/user/CreatorDashboard.vue'
import Admin from '@/views/admin/Admin.vue'
import AdminUsers from '@/views/admin/Users.vue'
import AdminPlugins from '@/views/admin/Plugins.vue'
import AdminSystemMonitor from '@/views/admin/SystemMonitor.vue'
import ModerationPosts from '@/views/admin/ModerationPosts.vue'
import OssAdmin from '@/views/admin/OssAdmin.vue'
import ConfigAdmin from '@/views/admin/ConfigAdmin.vue'
import CrawlerAdmin from '@/views/admin/CrawlerAdmin.vue'
import AssetAdmin from '@/views/admin/AssetAdmin.vue'
import { API_PERMISSION } from '@/constants/permissions'

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
    path: '/console',
    name: 'Console',
    component: Console,
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
    meta: {
      layout: 'guest',
      requiresAuth: false
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
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
    component: Posts,
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
    component: PostEditor,
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
    component: PostEditor,
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
    component: CreatorDashboard,
    meta: {
      title: '创作者看板',
      layout: 'guest',
      requiresAuth: true,
      console: true,
      permission: API_PERMISSION.BLOG_POSTS_READ
    }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: {
      title: '管理后台',
      layout: 'guest',
      requiresAuth: true,
      console: true,
      level: 0,
      permission: API_PERMISSION.AUTH_USERS_LIST
    },
    redirect: '/admin/users',
    children: [
      {
        path: 'users',
        name: 'AdminUsers',
        component: AdminUsers,
        meta: {
          title: '用户管理',
          layout: 'guest',
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
          layout: 'guest',
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
          layout: 'guest',
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
          layout: 'guest',
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
          layout: 'guest',
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
          layout: 'guest',
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
          layout: 'guest',
          requiresAuth: true,
          level: 0,
          permission: API_PERMISSION.ASSETS_READ
        }
      },
      {
        path: 'moderation/pending',
        name: 'AdminModerationPending',
        redirect: { name: 'AdminModerationPosts' },
        meta: {
          title: '帖子管理',
          layout: 'guest',
          requiresAuth: true,
          level: 0,
          permission: API_PERMISSION.BLOG_POSTS_MODERATE
        }
      },
      {
        path: 'moderation/posts',
        name: 'AdminModerationPosts',
        component: ModerationPosts,
        meta: {
          title: '帖子管理',
          layout: 'guest',
          requiresAuth: true,
          level: 0,
          permission: API_PERMISSION.BLOG_POSTS_MODERATE
        }
      }
    ]
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
