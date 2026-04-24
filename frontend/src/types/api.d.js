/**
 * @file API 类型定义
 * 使用 JSDoc 为所有 API 响应提供类型提示
 * IDE（如 VS Code）会根据这些 @typedef 提供自动补全
 */

/**
 * @typedef {Object} PaginatedResponse
 * @property {any[]} items
 * @property {number} total
 * @property {number} [page]
 * @property {number} [page_size]
 */

/**
 * @typedef {Object} ApiResponse
 * @property {string} code
 * @property {any} [data]
 * @property {string} [message]
 */

/**
 * @typedef {Object} User
 * @property {string} id
 * @property {string} username
 * @property {string} email
 * @property {number} level
 * @property {'active'|'disabled'} [status]
 * @property {string} [created_at]
 */

/**
 * @typedef {Object} BlogPost
 * @property {string} id
 * @property {string} title
 * @property {string} slug
 * @property {string} [content]
 * @property {string} [excerpt]
 * @property {string} author_id
 * @property {string} [author_username]
 * @property {string} [cover_image]
 * @property {string} [access_level]
 * @property {string[]} [tags]
 * @property {string} [created_at]
 * @property {string} [updated_at]
 * @property {number} [views]
 * @property {number} [likes]
 * @property {number} [comments_count]
 */

/**
 * @typedef {Object} SystemSummary
 * @property {number} cpu_percent
 * @property {Object} memory
 * @property {number} memory.total
 * @property {number} memory.used
 * @property {number} memory.free
 * @property {Object} disk
 * @property {Object} network
 * @property {string} [uptime]
 */

/**
 * @typedef {Object} CrawlerStatus
 * @property {boolean} running
 * @property {number} uptimeSeconds
 * @property {number} activeTasks
 * @property {number} queueSize
 * @property {number} seedsCount
 * @property {number} pagesCrawled
 * @property {number} pagesRejected
 * @property {Object} domainsActive
 */

/**
 * @typedef {Object} CrawlerStats
 * @property {number} totalCrawled
 * @property {Object} byType
 * @property {Object} byDomain
 */

/**
 * @typedef {Object} CloudStats
 * @property {number} running_jobs
 * @property {number} running_instances
 */

/**
 * @typedef {Object} TrainingJob
 * @property {string} id
 * @property {string} name
 * @property {string} [creator_id]
 * @property {string} [status]
 * @property {string} [dataset_id]
 * @property {string} [repo_id]
 * @property {string} [created_at]
 * @property {string} [updated_at]
 */

/**
 * @typedef {Object} OssStats
 * @property {number} total_files
 * @property {number} total_size
 * @property {number} total_users
 */

/**
 * @typedef {Object} AssetStats
 * @property {number} total
 * @property {Object} byType
 */
