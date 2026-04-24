/**
 * 云训练相关 API
 * @module api/cloud
 */
import { get, post, put, del } from './request.js'

/**
 * 获取云平台统计
 * @returns {Promise<any>}
 */
export function stats() {
  return get('/api/cloud/stats')
}

/**
 * 获取训练任务列表
 * @param {Object} [params]
 * @param {string} [params.page]
 * @param {string} [params.page_size]
 * @param {string} [params.status]
 * @returns {Promise<any>}
 */
export function listJobs(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/cloud/jobs${qs}`)
}

/**
 * 创建训练任务
 * @param {Object} body
 * @returns {Promise<any>}
 */
export function createJob(body) {
  return post('/api/cloud/jobs', body)
}

/**
 * 启动训练任务
 * @param {string} id
 * @returns {Promise<void>}
 */
export function launchJob(id) {
  return post(`/api/cloud/jobs/${id}/launch`)
}

/**
 * 开始任务（resume）
 * @param {string} id
 * @returns {Promise<void>}
 */
export function startJob(id) {
  return post(`/api/cloud/jobs/${id}/start`)
}

/**
 * 停止任务
 * @param {string} id
 * @returns {Promise<void>}
 */
export function stopJob(id) {
  return post(`/api/cloud/jobs/${id}/stop`)
}

/**
 * 删除任务
 * @param {string} id
 * @returns {Promise<void>}
 */
export function deleteJob(id) {
  return del(`/api/cloud/jobs/${id}`)
}

/**
 * 获取任务日志
 * @param {string} id
 * @param {Object} [params]
 * @param {string} [params.lines]
 * @returns {Promise<any>}
 */
export function jobLogs(id, params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/cloud/jobs/${id}/logs${qs}`)
}

/**
 * 获取任务步骤
 * @param {string} id
 * @returns {Promise<any>}
 */
export function jobSteps(id) {
  return get(`/api/cloud/jobs/${id}/steps`)
}

/**
 * 获取制品列表
 * @param {Object} [params]
 * @param {string} [params.page]
 * @param {string} [params.page_size]
 * @param {string} [params.job_id]
 * @returns {Promise<any>}
 */
export function listArtifacts(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/cloud/artifacts${qs}`)
}

/**
 * 下载制品
 * @param {string} id
 * @returns {Promise<any>}
 */
export function downloadArtifact(id) {
  return get(`/api/cloud/artifacts/${id}/download`)
}

/**
 * 删除制品
 * @param {string} id
 * @returns {Promise<void>}
 */
export function deleteArtifact(id) {
  return del(`/api/cloud/artifacts/${id}`)
}

/**
 * 创建数据集
 * @param {Object} body
 * @returns {Promise<any>}
 */
export function createDataset(body) {
  return post('/api/cloud/datasets', body)
}

/**
 * 获取数据集列表
 * @param {Object} [params]
 * @param {string} [params.page]
 * @param {string} [params.page_size]
 * @returns {Promise<any>}
 */
export function listDatasets(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/cloud/datasets${qs}`)
}

/**
 * 同步数据集
 * @param {string} id
 * @returns {Promise<any>}
 */
export function syncDataset(id) {
  return post(`/api/cloud/datasets/${id}/sync`)
}

/**
 * 删除数据集
 * @param {string} id
 * @returns {Promise<void>}
 */
export function deleteDataset(id) {
  return del(`/api/cloud/datasets/${id}`)
}

/**
 * 创建代码仓库
 * @param {Object} body
 * @returns {Promise<any>}
 */
export function createRepo(body) {
  return post('/api/cloud/repos', body)
}

/**
 * 更新代码仓库
 * @param {string} id
 * @param {Object} body
 * @returns {Promise<any>}
 */
export function updateRepo(id, body) {
  return put(`/api/cloud/repos/${id}`, body)
}

/**
 * 获取代码仓库列表
 * @param {Object} [params]
 * @param {string} [params.page]
 * @param {string} [params.page_size]
 * @returns {Promise<any>}
 */
export function listRepos(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/cloud/repos${qs}`)
}

/**
 * 同步仓库
 * @param {string} id
 * @returns {Promise<any>}
 */
export function syncRepo(id) {
  return post(`/api/cloud/repos/${id}/sync`)
}

/**
 * 删除仓库
 * @param {string} id
 * @returns {Promise<void>}
 */
export function deleteRepo(id) {
  return del(`/api/cloud/repos/${id}`)
}
