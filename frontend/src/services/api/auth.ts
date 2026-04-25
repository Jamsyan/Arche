// 认证相关接口
import { post, get } from '../request'

// 登录参数
export interface LoginParams {
  username: string
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
  userInfo: UserInfo
}

// 登录
export const loginApi = (params: LoginParams): Promise<LoginResponse> => {
  return post<LoginResponse>('/auth/login', params)
}

// 登出
export const logoutApi = (): Promise<void> => {
  return post('/auth/logout')
}

// 获取当前用户信息
export const getUserInfoApi = (): Promise<UserInfo> => {
  return get<UserInfo>('/auth/info')
}
