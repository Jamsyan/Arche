// 用户管理相关接口
import { get, post, put, del } from '../request'
import type { UserInfo } from './auth'

// 分页查询用户参数
export interface UserQueryParams {
  page: number
  pageSize: number
  username?: string
  status?: number
}

// 分页查询用户响应
export interface UserPageResponse {
  total: number
  list: UserInfo[]
  page: number
  pageSize: number
}

// 创建用户参数
export interface CreateUserParams {
  username: string
  password: string
  nickname: string
  role: string
  status?: number
}

// 更新用户参数
export interface UpdateUserParams extends Partial<CreateUserParams> {
  id: string
}

// 获取用户列表
export const getUserListApi = (params: UserQueryParams): Promise<UserPageResponse> => {
  return get<UserPageResponse>('/user/list', params)
}

// 获取用户详情
export const getUserDetailApi = (id: string): Promise<UserInfo> => {
  return get<UserInfo>(`/user/detail/${id}`)
}

// 创建用户
export const createUserApi = (params: CreateUserParams): Promise<UserInfo> => {
  return post<UserInfo>('/user/create', params)
}

// 更新用户
export const updateUserApi = (params: UpdateUserParams): Promise<UserInfo> => {
  return put<UserInfo>('/user/update', params)
}

// 删除用户
export const deleteUserApi = (id: string): Promise<void> => {
  return del(`/user/delete/${id}`)
}
