/**
 * Component Registry - P0~P5 等级映射到组件。
 * 等级数字越小权限越高，高等级自动拥有低等级全部组件。
 * Vite 按 dynamic import 自动分割 chunk，
 * 低等级用户不会下载高等级组件的代码。
 */

// 每个等级独有的组件（不继承低等级）
const registry = {
  5: {
    BlogHome: () => import('../components/blog/Home.vue'),
    BlogPost: () => import('../components/blog/Post.vue'),
  },
  4: {
    BlogComment: () => import('../components/blog/Comment.vue'),
  },
  3: {
    BlogEditor: () => import('../components/blog/Editor.vue'),
  },
  2: {
    FileUpload: () => import('../components/platform/FileUpload.vue'),
  },
  1: {
    GitHubProxy: () => import('../components/github/Repo.vue'),
    P1Storage: () => import('../components/platform/P1Storage.vue'),
    ModerationPanel: () => import('../components/blog/Moderation.vue'),
  },
  0: {
    CrawlerDashboard: () => import('../components/ops/CrawlerDashboard.vue'),
    CloudTraining: () => import('../components/ops/CloudTraining.vue'),
    AssetManagement: () => import('../components/ops/AssetManagement.vue'),
    AdminPanel: () => import('../components/admin/AdminPanel.vue'),
    UserManagement: () => import('../components/admin/UserManagement.vue'),
  },
}

/**
 * 获取指定等级及以下所有可用的组件。
 * 等级 P5(最大) → P0(最小)，逐级合并。
 * @param {number} userLevel - 用户等级 0~5
 * @returns {object} 合并后的组件映射
 */
export function getAvailableComponents(userLevel) {
  const result = {}
  // 从 P5 开始合并到用户等级
  for (let lvl = 5; lvl >= (userLevel ?? 5); lvl--) {
    if (registry[lvl]) {
      Object.assign(result, registry[lvl])
    }
  }
  return result
}

/**
 * 创建 Vue 异步组件加载器。
 * @param {number} userLevel - 用户等级
 * @param {string} name - 组件名
 * @returns {Function|null} dynamic import 函数，无权限返回 null
 */
export function loadComponent(userLevel, name) {
  const available = getAvailableComponents(userLevel)
  return available[name] || null
}
