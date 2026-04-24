/**
 * 系统相关 API
 * @module api/system
 */
import { get } from './request.js'

/**
 * 获取系统摘要
 * @returns {Promise<any>}
 */
export function summary() {
  return get('/api/system/summary')
}

/**
 * 获取进程列表
 * @param {Object} [params]
 * @param {string} [params.limit]
 * @param {string} [params.sort_by]
 * @returns {Promise<any>}
 */
export function processes(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/system/processes${qs}`)
}
