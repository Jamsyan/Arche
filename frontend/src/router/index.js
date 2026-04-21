import { createRouter, createWebHistory } from 'vue-router'
import { loadComponent } from './component-registry.js'

const routes = [
  { path: '/', component: () => import('../components/blog/Home.vue') },
  { path: '/post/:slug', component: () => import('../components/blog/Post.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

/**
 * Navigation guard: if user is authenticated, allow route access.
 * If route requires a specific role, check before entering.
 * Routes for platform/admin are added dynamically after login.
 */
router.beforeEach(async (to) => {
  if (to.meta.role) {
    // Lazy-load role-based routes on demand
    const loader = loadComponent(to.meta.role, to.meta.component)
    if (!loader) return '/login'
  }
})

export default router
