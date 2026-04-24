/**
 * 管理端相关 API
 * @module api/admin
 */
import { get, post, put } from './request.js'

/**
 * 获取配置列表
 * @returns {Promise<any>}
 */
export function configList() {
  return get('/api/admin/config')
}

/**
 * 获取单个配置
 * @param {string} key
 * @returns {Promise<any>}
 */
export function configGet(key) {
  return get(`/api/admin/config/${encodeURIComponent(key)}`)
}

/**
 * 设置单个配置
 * @param {string} key
 * @param {Object} body
 * @returns {Promise<any>}
 */
export function configSet(key, body) {
  return put(`/api/admin/config/${encodeURIComponent(key)}`, body)
}

/**
 * 重载配置
 * @returns {Promise<void>}
 */
export function configReload() {
  return post('/api/admin/config/reload')
}
