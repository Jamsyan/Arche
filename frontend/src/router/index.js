import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from './auth.js'

// 公共路由（无需登录）
const publicRoutes = [
  {
    path: '/',
    name: 'blog-home',
    component: () => import('../components/blog/Home.vue'),
  },
  {
    path: '/post/:slug',
    name: 'blog-post',
    component: () => import('../components/blog/Post.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../components/auth/Login.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../components/auth/Register.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes: publicRoutes,
})

/**
 * 添加等级路由的辅助函数。
 * 自动附加 meta.requiredLevel 供路由守卫校验。
 */
function guarded(path, name, component, requiredLevel, children = []) {
  return {
    path,
    name,
    component,
    meta: { requiredLevel },
    children,
  }
}

// 等级路由（需登录，按权限动态添加）
const authRoutes = [
  // P4+（注册用户）：仪表盘
  guarded('/platform', 'platform',
    () => import('../components/platform/Dashboard.vue'),
    4, [
      {
        path: '',
        name: 'dashboard',
        component: () => import('../components/platform/Dashboard.vue'),
        meta: { requiredLevel: 4 },
      },
    ]),

  // P3+（初级用户）：博客编辑器
  guarded('/editor', 'blog-editor',
    () => import('../components/blog/Editor.vue'),
    3),

  // P2+（中级用户）：文件上传
  guarded('/upload', 'file-upload',
    () => import('../components/platform/FileUpload.vue'),
    2),

  // P1+（部分开放）：GitHub 代理、P1 存储、审核面板
  guarded('/github', 'github-proxy',
    () => import('../components/github/Repo.vue'),
    1),
  guarded('/storage', 'p1-storage',
    () => import('../components/platform/P1Storage.vue'),
    1),
  guarded('/moderation', 'moderation',
    () => import('../components/blog/Moderation.vue'),
    1),

  // P0（最高权限）：运维面板、管理后台
  guarded('/ops/crawler', 'crawler-dashboard',
    () => import('../components/ops/CrawlerDashboard.vue'),
    0),
  guarded('/ops/cloud', 'cloud-training',
    () => import('../components/ops/CloudTraining.vue'),
    0),
  guarded('/ops/assets', 'asset-management',
    () => import('../components/ops/AssetManagement.vue'),
    0),
  guarded('/admin', 'admin-panel',
    () => import('../components/admin/AdminPanel.vue'),
    0),
  guarded('/admin/users', 'user-management',
    () => import('../components/admin/UserManagement.vue'),
    0),
]

// 将所有等级路由添加到 router
for (const route of authRoutes) {
  router.addRoute(route)
}

// 全局前置守卫
router.beforeEach((to) => {
  const { level } = useAuth()

  // 已登录状态访问登录/注册页，重定向到首页
  if (to.name === 'login' || to.name === 'register') {
    if (level.value !== null) return '/'
    return
  }

  // 检查等级权限
  if (to.meta.requiredLevel !== undefined) {
    if (level.value === null) return '/login'
    // 数字越小权限越高，用户 level <= requiredLevel 即可访问
    if (level.value > to.meta.requiredLevel) return '/'
  }
})

export default router
