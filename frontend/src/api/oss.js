/**
 * 对象存储相关 API
 * @module api/oss
 */
import { get, post, del } from './request.js'

/**
 * 获取存储统计
 * @param {Object} [params]
 * @param {string} [params.user_scope]
 * @returns {Promise<any>}
 */
export function storageStats(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/oss/storage/stats${qs}`)
}

/**
 * 获取配额信息
 * @returns {Promise<any>}
 */
export function quota() {
  return get('/api/oss/quota')
}

/**
 * 获取我的文件列表
 * @param {Object} [params]
 * @param {string} [params.limit]
 * @param {string} [params.offset]
 * @returns {Promise<any>}
 */
export function myFiles(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/oss/my${qs}`)
}

/**
 * 获取单个文件信息
 * @param {string} id
 * @returns {Promise<any>}
 */
export function fileInfo(id) {
  return get(`/api/oss/files/${id}`)
}

/**
 * 上传文件
 * @param {FormData} body
 * @returns {Promise<any>}
 */
export function upload(body) {
  const { authHeaders } = require('../router/auth.js').useAuth()
  return fetch('/api/oss/upload', {
    method: 'POST',
    headers: authHeaders(),
    body,
  })
}

// ── 管理端 API ──────────────────────────────────────────────

/**
 * 获取文件列表（管理）
 * @param {Object} [params]
 * @returns {Promise<any>}
 */
export function adminFiles(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/oss/admin/files${qs}`)
}

/**
 * 获取配额列表（管理）
 * @param {Object} [params]
 * @returns {Promise<any>}
 */
export function adminQuotas(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/oss/admin/quotas${qs}`)
}

/**
 * 更新配额
 * @param {string} userId
 * @param {Object} body
 * @returns {Promise<void>}
 */
export function updateQuota(userId, body) {
  return post(`/api/oss/admin/quotas/${userId}`, body)
}

/**
 * 获取管理员统计
 * @returns {Promise<any>}
 */
export function adminStats() {
  return get('/api/oss/admin/stats')
}

/**
 * 获取 Top 用户
 * @param {Object} [params]
 * @param {string} [params.limit]
 * @returns {Promise<any>}
 */
export function topUsers(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/oss/admin/stats/top-users${qs}`)
}

/**
 * 获取全局限速配置
 * @returns {Promise<any>}
 */
export function rateLimit() {
  return get('/api/oss/admin/rate-limit')
}

/**
 * 设置全局限速
 * @param {Object} body
 * @returns {Promise<void>}
 */
export function setRateLimit(body) {
  return post('/api/oss/admin/rate-limit', body)
}

/**
 * 获取用户限速
 * @param {string} userId
 * @returns {Promise<any>}
 */
export function userRateLimit(userId) {
  return get(`/api/oss/admin/rate-limit/users/${userId}`)
}

/**
 * 设置用户限速
 * @param {string} userId
 * @param {Object} body
 * @returns {Promise<void>}
 */
export function setUserRateLimit(userId, body) {
  return post(`/api/oss/admin/rate-limit/users/${userId}`, body)
}

/**
 * 清理冷数据
 * @param {Object} [params]
 * @param {string} [params.days]
 * @returns {Promise<void>}
 */
export function evictColdData(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return post(`/api/oss/admin/evict${qs}`)
}

/**
 * 删除文件
 * @param {string} id
 * @returns {Promise<void>}
 */
export function deleteFile(id) {
  return del(`/api/oss/files/${id}`)
}

/**
 * 删除管理端文件
 * @param {string} id
 * @returns {Promise<void>}
 */
export function adminDeleteFile(id) {
  return del(`/api/oss/admin/files/${id}`)
}
