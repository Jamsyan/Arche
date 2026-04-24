/**
 * GitHub 相关 API
 * @module api/github
 */
import { post } from './request.js'
import { get } from './request.js'

/**
 * 搜索仓库
 * @param {Object} params
 * @param {string} params.q
 * @param {string} [params.per_page]
 * @returns {Promise<any>}
 */
export function searchRepos(params) {
  const qs = '?' + new URLSearchParams(params).toString()
  return get(`/api/github/search/repositories${qs}`)
}

/**
 * 清除缓存
 * @returns {Promise<void>}
 */
export function clearCache() {
  return post('/api/github/cache/clear')
}
