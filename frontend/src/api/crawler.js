/**
 * 爬虫相关 API
 * @module api/crawler
 */
import { get, post } from './request.js'

/**
 * 获取爬虫状态
 * @returns {Promise<any>}
 */
export function status() {
  return get('/api/crawler/status')
}

/**
 * 获取爬虫统计
 * @returns {Promise<any>}
 */
export function stats() {
  return get('/api/crawler/stats')
}

/**
 * 启动爬虫
 * @returns {Promise<void>}
 */
export function start() {
  return post('/api/crawler/start')
}

/**
 * 停止爬虫
 * @returns {Promise<void>}
 */
export function stop() {
  return post('/api/crawler/stop')
}

/**
 * 获取抓取记录
 * @param {Object} [params]
 * @param {string} [params.page]
 * @param {string} [params.page_size]
 * @returns {Promise<any>}
 */
export function records(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/crawler/records${qs}`)
}

/**
 * 添加种子 URL
 * @param {{ url: string }} body
 * @returns {Promise<void>}
 */
export function addSeed(body) {
  return post('/api/crawler/seeds', body)
}
