import type { RouteRecordRaw } from 'vue-router'

export const roleRoutes: Record<'guest' | 'user' | 'admin', RouteRecordRaw[]> = {
  guest: [],
  user: [],
  admin: []
}
