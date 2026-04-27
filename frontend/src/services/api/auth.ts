// 认证相关接口
import { get, post, type RequestConfig } from '../request'

// 登录参数
export interface LoginParams {
  identity: string
  password: string
}

// 用户信息
export interface UserInfo {
  id: string
  username: string
  nickname: string
  avatar?: string
  role: string
  permissions: string[]
}

// 登录响应
export interface LoginResponse {
  token: string
  refresh_token?: string
  userInfo: UserInfo
}

// 登录
export const loginApi = (params: LoginParams, config?: RequestConfig) =>
  post<LoginResponse>('/auth/login', params, config)

// 登出
export const logoutApi = (config?: RequestConfig) => post<void>('/auth/logout', undefined, config)

// 获取当前用户信息
export const getUserInfoApi = (config?: RequestConfig) =>
  get<UserInfo>('/auth/me', undefined, config)
