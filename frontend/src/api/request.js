/**
 * API 请求核心封装
 * 统一认证、错误处理、响应格式
 */
import { useAuth } from '../router/auth.js'

/**
 * @typedef {Object} ApiError
 * @property {string} message
 * @property {string} [code]
 */

/**
 * 统一 GET 请求
 * @param {string} url
 * @param {RequestInit} [options]
 * @returns {Promise<any>}
 */
export async function get(url, options = {}) {
  return request(url, { ...options, method: 'GET' })
}

/**
 * 统一 POST 请求
 * @param {string} url
 * @param {any} [body]
 * @param {RequestInit} [options]
 * @returns {Promise<any>}
 */
export async function post(url, body, options = {}) {
  return request(url, {
    ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...options.headers },
    body: body != null ? JSON.stringify(body) : undefined,
  })
}

/**
 * 统一 PUT 请求
 * @param {string} url
 * @param {any} [body]
 * @param {RequestInit} [options]
 * @returns {Promise<any>}
 */
export async function put(url, body, options = {}) {
  return request(url, {
    ...options,
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...options.headers },
    body: body != null ? JSON.stringify(body) : undefined,
  })
}

/**
 * 统一 DELETE 请求
 * @param {string} url
 * @param {RequestInit} [options]
 * @returns {Promise<any>}
 */
export async function del(url, options = {}) {
  return request(url, { ...options, method: 'DELETE' })
}

/**
 * 核心请求函数
 * @param {string} url
 * @param {RequestInit} [options]
 * @returns {Promise<any>}
 */
async function request(url, options = {}) {
  const { authHeaders } = useAuth()
  const headers = authHeaders(options.headers || {})

  const res = await fetch(url, { ...options, headers })

  // 非 2xx 视为网络错误
  if (!res.ok) {
    throw new Error(`网络错误: ${res.status} ${res.statusText}`)
  }

  const data = await res.json()

  // 后端约定 code !== 'ok' 为业务错误
  if (data.code !== 'ok') {
    const err = new Error(data.message || '请求失败')
    err.code = data.code
    err.data = data.data
    throw err
  }

  return data.data
}
