/**
 * Component Registry - Maps role to dynamically-imported components.
 *
 * Key design: components are lazy-loaded via dynamic imports.
 * Vite splits them into separate chunks. A user who never gets
 * a certain role never downloads that chunk's JS.
 */

const registry = {
  blog: {
    Home: () => import('./components/blog/Home.vue'),
    Post: () => import('./components/blog/Post.vue'),
  },
  user: {
    Dashboard: () => import('./components/platform/Dashboard.vue'),
  },
  admin: {
    AdminPanel: () => import('./components/admin/AdminPanel.vue'),
    UserManagement: () => import('./components/admin/UserManagement.vue'),
  }
}

/**
 * Get the list of component names available for a given role.
 */
export function getAvailableComponents(role) {
  // Blog components are always available
  const base = registry.blog
  const roleComponents = registry[role] || {}
  return { ...base, ...roleComponents }
}

/**
 * Create a Vue async component for the given role + component name.
 * Returns null if the component is not available for this role.
 */
export function loadComponent(role, name) {
  const available = getAvailableComponents(role)
  return available[name] || null
}
