import { del, get, post, put, type RequestConfig } from '../request'
import type { ApiListParams, Paginated } from './types/common'

export interface AdminUser {
  id: string
  email?: string
  username: string
  nickname: string
  avatar?: string
  role: string
  permissions: string[]
  is_active?: boolean
  level?: number
  created_at?: string
}

export interface UsersQueryParams extends ApiListParams {
  status?: string
}

export interface UpdateUserPayload {
  level?: number
  is_active?: boolean
}

export interface CreateAdminUserPayload {
  email: string
  username: string
  password: string
  level?: number
}

export const getUsersApi = (params?: UsersQueryParams, config?: RequestConfig) =>
  get<Paginated<AdminUser>>('/auth/users', params, config)

export const getUserDetailApi = (userId: string, config?: RequestConfig) =>
  get<AdminUser>(`/auth/users/${userId}`, undefined, config)

export const updateUserApi = (userId: string, payload: UpdateUserPayload, config?: RequestConfig) =>
  put<AdminUser>(`/auth/users/${userId}`, payload, config)

export const deleteUserApi = (userId: string, config?: RequestConfig) =>
  del<void>(`/auth/users/${userId}`, undefined, config)

export const disableUserApi = (userId: string, config?: RequestConfig) =>
  post<void>(`/auth/users/${userId}/disable`, undefined, config)

export const enableUserApi = (userId: string, config?: RequestConfig) =>
  post<void>(`/auth/users/${userId}/enable`, undefined, config)

export const createAdminUserApi = (payload: CreateAdminUserPayload, config?: RequestConfig) =>
  post<AdminUser>('/auth/admin/users', payload, config)
