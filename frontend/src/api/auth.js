/**
 * 认证相关 API
 * @module api/auth
 */
import { get, post } from './request.js'

/**
 * @typedef {Object} LoginBody
 * @property {string} identity
 * @property {string} password
 */
/**
 * @typedef {Object} LoginData
 * @property {string} access_token
 * @property {any} user
 */

/**
 * @typedef {Object} RegisterBody
 * @property {string} email
 * @property {string} username
 * @property {string} password
 */

/**
 * 登录
 * @param {LoginBody} body
 * @returns {Promise<LoginData>}
 */
export function login(body) {
  return post('/api/auth/login', body)
}

/**
 * 注册
 * @param {RegisterBody} body
 * @returns {Promise<{user: any}>}
 */
export function register(body) {
  return post('/api/auth/register', body)
}

/**
 * 登出
 * @returns {Promise<void>}
 */
export function logout() {
  return post('/api/auth/logout')
}

/**
 * 获取当前用户信息
 * @returns {Promise<any>}
 */
export function me() {
  return get('/api/auth/me')
}

/**
 * 获取用户列表
 * @param {Object} [params]
 * @param {string} [params.page]
 * @param {string} [params.page_size]
 * @param {string} [params.status]
 * @returns {Promise<any>}
 */
export function listUsers(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/auth/users${qs}`)
}

/**
 * 获取单个用户
 * @param {string} id
 * @returns {Promise<any>}
 */
export function getUser(id) {
  return get(`/api/auth/users/${id}`)
}

/**
 * 禁用用户
 * @param {string} id
 * @returns {Promise<void>}
 */
export function disableUser(id) {
  return post(`/api/auth/users/${id}/disable`)
}

/**
 * 启用用户
 * @param {string} id
 * @returns {Promise<void>}
 */
export function enableUser(id) {
  return post(`/api/auth/users/${id}/enable`)
}

/**
 * 管理端用户列表
 * @param {Object} [params]
 * @returns {Promise<any>}
 */
export function adminUsers(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/auth/admin/users${qs}`)
}

/**
 * 更新用户
 * @param {string} id
 * @param {Object} body
 * @returns {Promise<any>}
 */
export function updateUser(id, body) {
  return post(`/api/auth/users/${id}`, body)
}
