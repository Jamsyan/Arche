import { createRouter, createWebHistory } from 'vue-router'
import { staticRoutes } from './modules/static'
export { roleRoutes } from './modules/role'

const router = createRouter({
  history: createWebHistory(),
  routes: staticRoutes
})

export default router
