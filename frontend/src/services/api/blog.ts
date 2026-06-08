import { del, get, post, put, type RequestConfig } from '../request'
import {
  normalizePaginated,
  type ApiListParams,
  type BatchActionPayload,
  type BackendPaginated
} from './types/common'

export interface BlogPost {
  id: string
  slug: string
  title: string
  content: string
  cover_url?: string
  source_url?: string
  source_name?: string
  tags: string[]
  required_level?: number
  status?: string
  created_at?: string
  updated_at?: string
  author_username?: string
  likes?: number
  views?: number
  paragraphs?: Paragraph[]
}

export interface Paragraph {
  index: number
  content: string
}

export interface BlogComment {
  id: string
  post_id: string
  content: string
  author_id: string
  author_username?: string
  paragraph_index?: number
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
  required_level?: number
  cover_url?: string
}

export interface UpdatePostPayload {
  title?: string
  content?: string
  tags?: string[]
  required_level?: number
  cover_url?: string
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

export interface LikeStatus {
  liked: boolean
  count: number
}

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

export const getParagraphCommentsApi = (
  postId: string,
  paragraphIndex: number,
  params?: ApiListParams,
  config?: RequestConfig
) =>
  get<BackendPaginated<BlogComment>>(
    `/blog/posts/${postId}/paragraph-comments/${paragraphIndex}`,
    params,
    config
  ).then(normalizePaginated)

export const createParagraphCommentApi = (
  postId: string,
  paragraphIndex: number,
  payload: CreateCommentPayload,
  config?: RequestConfig
) =>
  post<BlogComment>(`/blog/posts/${postId}/paragraph-comments/${paragraphIndex}`, payload, config)

export const getLikeStatusApi = (postId: string, config?: RequestConfig) =>
  get<LikeStatus>(`/blog/posts/${postId}/like-status`, undefined, config)

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

export const uploadPostFileApi = (file: File, config?: RequestConfig) => {
  const formData = new FormData()
  formData.append('file', file)
  return post<BlogPost>('/blog/upload-file', formData, {
    ...config,
    headers: { ...config?.headers, 'Content-Type': 'multipart/form-data' }
  })
}
