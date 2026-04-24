/**
 * 监控相关 API
 * @module api/monitor
 */
import { get } from './request.js'

/**
 * 获取默认监控模板
 * @returns {Promise<any>}
 */
export function defaultTemplate() {
  return get('/api/monitor/default')
}

/**
 * 获取监控模板列表
 * @returns {Promise<any>}
 */
export function templates() {
  return get('/api/monitor/templates')
}

/**
 * 获取单个模板
 * @param {string} id
 * @returns {Promise<any>}
 */
export function template(id) {
  return get(`/api/monitor/templates/${id}`)
}

/**
 * 获取系统 QPS
 * @returns {Promise<any>}
 */
export function systemQps() {
  return get('/api/monitor/system/qps')
}

/**
 * 获取系统内存
 * @returns {Promise<any>}
 */
export function systemMemory() {
  return get('/api/monitor/system/memory')
}
