/**
 * Widget Registry — 定义所有可用 Widget 类型。
 * 类型 → 组件懒加载映射，供 Dashboard 动态渲染。
 */

const WIDGET_DEFS = [
  {
    type: 'system-cpu',
    title: 'CPU 使用率',
    icon: 'IconDashboard',
    category: '系统监控',
    component: () => import('./SystemCpuWidget.vue'),
  },
  {
    type: 'system-memory',
    title: '内存使用',
    icon: 'IconDashboard',
    category: '系统监控',
    component: () => import('./SystemMemoryWidget.vue'),
  },
  {
    type: 'system-disk',
    title: '磁盘使用',
    icon: 'IconDashboard',
    category: '系统监控',
    component: () => import('./SystemDiskWidget.vue'),
  },
  {
    type: 'system-network',
    title: '网络 I/O',
    icon: 'IconDashboard',
    category: '系统监控',
    component: () => import('./SystemNetworkWidget.vue'),
  },
  {
    type: 'system-processes',
    title: 'Top 进程',
    icon: 'IconDesktop',
    category: '系统监控',
    component: () => import('./SystemProcessesWidget.vue'),
  },
  {
    type: 'system-uptime',
    title: '运行时长',
    icon: 'IconDashboard',
    category: '系统监控',
    component: () => import('./SystemUptimeWidget.vue'),
  },
  {
    type: 'crawler-status',
    title: '爬虫状态',
    icon: 'IconBug',
    category: '运维',
    component: () => import('./CrawlerStatusWidget.vue'),
  },
  {
    type: 'crawler-stats',
    title: '爬取统计',
    icon: 'IconBug',
    category: '运维',
    component: () => import('./CrawlerStatsWidget.vue'),
  },
  {
    type: 'oss-stats',
    title: '存储统计',
    icon: 'IconStorage',
    category: '存储',
    component: () => import('./OssStatsWidget.vue'),
  },
  {
    type: 'oss-top-users',
    title: '存储 Top 用户',
    icon: 'IconStorage',
    category: '存储',
    component: () => import('./OssTopUsersWidget.vue'),
  },
  {
    type: 'cloud-jobs',
    title: '训练任务',
    icon: 'IconCloud',
    category: '运维',
    component: () => import('./CloudJobsWidget.vue'),
  },
  {
    type: 'asset-stats',
    title: '资产统计',
    icon: 'IconApps',
    category: '运维',
    component: () => import('./AssetStatsWidget.vue'),
  },
  {
    type: 'user-stats',
    title: '用户统计',
    icon: 'IconUser',
    category: '管理',
    component: () => import('./UserStatsWidget.vue'),
  },
]

/**
 * 按 category 分组的 Widget 列表，供 Picker 使用。
 */
export function getWidgetCategories() {
  const cats = {}
  for (const w of WIDGET_DEFS) {
    if (!cats[w.category]) cats[w.category] = []
    cats[w.category].push(w)
  }
  return cats
}

/**
 * 根据 type 获取 Widget 组件加载函数。
 */
export function getWidgetComponent(type) {
  return WIDGET_DEFS.find(w => w.type === type)
}

/**
 * 获取所有 Widget 定义（供 Picker 拖拽用）。
 */
export function getAllWidgets() {
  return WIDGET_DEFS
}
