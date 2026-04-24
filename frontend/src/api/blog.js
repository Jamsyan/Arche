/**
 * 博客相关 API
 * @module api/blog
 */
import { get, post, put, del } from './request.js'

/**
 * 获取帖子列表
 * @param {Object} [params]
 * @param {string} [params.page]
 * @param {string} [params.page_size]
 * @param {string} [params.tag]
 * @param {string} [params.search]
 * @param {string} [params.status]
 * @param {string} [params.author_id]
 * @returns {Promise<any>}
 */
export function listPosts(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/blog/posts${qs}`)
}

/**
 * 获取单个帖子（按 slug）
 * @param {string} slug
 * @returns {Promise<any>}
 */
export function getPost(slug) {
  return get(`/api/blog/posts/${slug}`)
}

/**
 * 获取单个帖子（按 id）
 * @param {string} id
 * @returns {Promise<any>}
 */
export function getPostById(id) {
  return get(`/api/blog/posts/by-id/${id}`)
}

/**
 * 创建帖子
 * @param {{ title: string, content: string, tags?: string[], access_level?: string }} body
 * @returns {Promise<any>}
 */
export function createPost(body) {
  return post('/api/blog/posts', body)
}

/**
 * 更新帖子
 * @param {string} id
 * @param {{ title: string, content: string, tags?: string[], access_level?: string }} body
 * @returns {Promise<any>}
 */
export function updatePost(id, body) {
  return put(`/api/blog/posts/${id}`, body)
}

/**
 * 获取标签列表
 * @param {Object} [params]
 * @returns {Promise<any>}
 */
export function listTags(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/blog/tags${qs}`)
}

/**
 * 创建标签
 * @param {{ name: string }} body
 * @returns {Promise<any>}
 */
export function createTag(body) {
  return post('/api/blog/tags', body)
}

/**
 * 获取我的帖子
 * @param {Object} [params]
 * @returns {Promise<any>}
 */
export function myPosts(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/blog/my-posts${qs}`)
}

/**
 * 获取收藏列表
 * @param {Object} [params]
 * @returns {Promise<any>}
 */
export function favorites(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/blog/favorites${qs}`)
}

/**
 * 检查收藏状态
 * @param {string} postId
 * @returns {Promise<any>}
 */
export function favoriteStatus(postId) {
  return get(`/api/blog/posts/${postId}/favorite-status`)
}

/**
 * 收藏帖子
 * @param {string} postId
 * @returns {Promise<void>}
 */
export function addFavorite(postId) {
  return post(`/api/blog/favorites/${postId}`)
}

/**
 * 获取评论列表
 * @param {string} postId
 * @returns {Promise<any>}
 */
export function comments(postId) {
  return get(`/api/blog/posts/${postId}/comments`)
}

/**
 * 点赞帖子
 * @param {string} postId
 * @returns {Promise<void>}
 */
export function likePost(postId) {
  return post(`/api/blog/posts/${postId}/like`)
}

/**
 * 添加评论
 * @param {string} postId
 * @param {{ content: string }} body
 * @returns {Promise<any>}
 */
export function addComment(postId, body) {
  return post(`/api/blog/posts/${postId}/comments`, body)
}

/**
 * 删除评论
 * @param {string} postId
 * @param {{ comment_id: string }} body
 * @returns {Promise<void>}
 */
export function deleteComment(postId, body) {
  return del(`/api/blog/posts/${postId}/comments`, body)
}

/**
 * 删除帖子
 * @param {string} postId
 * @returns {Promise<void>}
 */
export function deletePost(postId) {
  return del(`/api/blog/posts/${postId}`)
}

/**
 * 上报举报
 * @param {{ post_id: string, reason: string }} body
 * @returns {Promise<void>}
 */
export function reportPost(body) {
  return post('/api/blog/reports', body)
}

/**
 * 获取待审核列表
 * @param {Object} [params]
 * @returns {Promise<any>}
 */
export function moderationPending(params) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  return get(`/api/blog/moderation/pending${qs}`)
}

/**
 * 批量通过审核
 * @param {{ ids: string[] }} body
 * @returns {Promise<void>}
 */
export function batchApprove(body) {
  return post('/api/blog/moderation/batch-approve', body)
}

/**
 * 批量拒绝审核
 * @param {{ ids: string[] }} body
 * @returns {Promise<void>}
 */
export function batchReject(body) {
  return post('/api/blog/moderation/batch-reject', body)
}

/**
 * 通过单条审核
 * @param {string} id
 * @returns {Promise<void>}
 */
export function approvePost(id) {
  return post(`/api/blog/moderation/${id}/approve`)
}

/**
 * 拒绝单条审核
 * @param {string} id
 * @returns {Promise<void>}
 */
export function rejectPost(id) {
  return post(`/api/blog/moderation/${id}/reject`)
}

/**
 * 导入帖子
 * @param {FormData} body
 * @returns {Promise<any>}
 */
export function importPost(body) {
  return fetch('/api/blog/import', {
    method: 'POST',
    body,
  }).then(res => res.json())
}
