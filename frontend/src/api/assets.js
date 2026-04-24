/**
 * 资产管理相关 API
 * @module api/assets
 */
import { get } from './request.js'

/**
 * 获取资产列表
 * @param {Object} [params]
 * @param {string} [params.page]
 * @param {string} [params.page_size]
 * @param {string} [params.asset_type]
 * @returns {Promise<any>}
 */
export function list(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/assets${qs}`)
}

/**
 * 搜索资产
 * @param {Object} params
 * @param {string} params.keyword
 * @returns {Promise<any>}
 */
export function search(params) {
  const qs = '?' + new URLSearchParams(params).toString()
  return get(`/api/assets/search${qs}`)
}

/**
 * 获取资产统计
 * @returns {Promise<any>}
 */
export function stats() {
  return get('/api/assets/stats')
}
