import { del, get, post, put, type RequestConfig } from '../request'
import type { ApiListParams, BatchActionPayload, BackendPaginated, Paginated } from './types/common'

export interface BlogPost {
  id: string
  slug: string
  title: string
  content: string
  tags: string[]
  status?: string
  created_at?: string
  updated_at?: string
  author_username?: string
  likes?: number
  views?: number
}

export interface BlogComment {
  id: string
  post_id: string
  content: string
  user_id: string
  created_at?: string
}

export interface BlogTag {
  id?: string
  name: string
  count?: number
}

export interface CreatePostPayload {
  title: string
  content: string
  tags?: string[]
  access_level?: number
}

export interface UpdatePostPayload {
  title?: string
  content?: string
}

export interface CreateCommentPayload {
  content: string
  parent_id?: string
}

export interface CreateReportPayload {
  post_id: string
  reason?: string
}

export interface BlogListParams extends ApiListParams {
  q?: string
  tag?: string
  sort_by?: string
  status?: string
}

const normalizePaginated = <T>(raw: BackendPaginated<T>): Paginated<T> => ({
  total: raw.total || 0,
  page: raw.page || 1,
  page_size: raw.page_size || 20,
  list: raw.list || raw.items || []
})

export const getBlogPostsApi = (params?: BlogListParams, config?: RequestConfig) =>
  get<BackendPaginated<BlogPost>>('/blog/posts', params, config).then(normalizePaginated)

export const getMyPostsApi = (params?: BlogListParams, config?: RequestConfig) =>
  get<BackendPaginated<BlogPost>>('/blog/my-posts', params, config).then(normalizePaginated)

export const getPostByIdApi = (postId: string, config?: RequestConfig) =>
  get<BlogPost>(`/blog/posts/by-id/${postId}`, undefined, config)

export const getPostBySlugApi = (slug: string, config?: RequestConfig) =>
  get<BlogPost>(`/blog/posts/${slug}`, undefined, config)

export const createPostApi = (payload: CreatePostPayload, config?: RequestConfig) =>
  post<BlogPost>('/blog/posts', payload, config)

export const updatePostApi = (postId: string, payload: UpdatePostPayload, config?: RequestConfig) =>
  put<BlogPost>(`/blog/posts/${postId}`, payload, config)

export const deletePostApi = (postId: string, config?: RequestConfig) =>
  del<void>(`/blog/posts/${postId}`, undefined, config)

export const getPostCommentsApi = (
  postId: string,
  params?: ApiListParams,
  config?: RequestConfig
) =>
  get<BackendPaginated<BlogComment>>(`/blog/posts/${postId}/comments`, params, config).then(
    normalizePaginated
  )

export const createPostCommentApi = (
  postId: string,
  payload: CreateCommentPayload,
  config?: RequestConfig
) => post<BlogComment>(`/blog/posts/${postId}/comments`, payload, config)

export const likePostApi = (postId: string, config?: RequestConfig) =>
  post<void>(`/blog/posts/${postId}/like`, undefined, config)

export const addFavoriteApi = (postId: string, config?: RequestConfig) =>
  post<void>(`/blog/favorites/${postId}`, undefined, config)

export const removeFavoriteApi = (postId: string, config?: RequestConfig) =>
  del<void>(`/blog/favorites/${postId}`, undefined, config)

export const getFavoritePostsApi = (params?: ApiListParams, config?: RequestConfig) =>
  get<BackendPaginated<BlogPost>>('/blog/favorites', params, config).then(normalizePaginated)

export const getFavoriteStatusApi = (postId: string, config?: RequestConfig) =>
  get<{ favorited: boolean }>(`/blog/posts/${postId}/favorite-status`, undefined, config)

export const createReportApi = (payload: CreateReportPayload, config?: RequestConfig) =>
  post<void>('/blog/reports', payload, config)

export const getBlogTagsApi = (params?: ApiListParams, config?: RequestConfig) =>
  get<BackendPaginated<BlogTag>>('/blog/tags', params, config).then(normalizePaginated)

export const createBlogTagApi = (name: string, config?: RequestConfig) =>
  post<BlogTag>('/blog/tags', undefined, { ...(config || {}), params: { name } })

export const addPostTagApi = (postId: string, name: string, config?: RequestConfig) =>
  post<void>(`/blog/posts/${postId}/tags`, undefined, { ...(config || {}), params: { name } })

export const removePostTagApi = (postId: string, tagName: string, config?: RequestConfig) =>
  del<void>(`/blog/posts/${postId}/tags/${tagName}`, undefined, config)

export const getPostsByTagApi = (tagName: string, params?: ApiListParams, config?: RequestConfig) =>
  get<BackendPaginated<BlogPost>>(`/blog/posts/by-tag/${tagName}`, params, config).then(
    normalizePaginated
  )

export const getModerationPendingApi = (params?: ApiListParams, config?: RequestConfig) =>
  get<BackendPaginated<BlogPost>>('/blog/moderation/pending', params, config).then(
    normalizePaginated
  )

export const approvePostApi = (postId: string, config?: RequestConfig) =>
  post<void>(`/blog/moderation/${postId}/approve`, undefined, config)

export const rejectPostApi = (postId: string, config?: RequestConfig) =>
  post<void>(`/blog/moderation/${postId}/reject`, undefined, config)

export const batchApproveApi = (payload: BatchActionPayload, config?: RequestConfig) =>
  post<void>('/blog/moderation/batch-approve', payload, config)

export const batchRejectApi = (payload: BatchActionPayload, config?: RequestConfig) =>
  post<void>('/blog/moderation/batch-reject', payload, config)
