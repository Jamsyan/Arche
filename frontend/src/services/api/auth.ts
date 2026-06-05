// 认证相关接口
import { get, post, type RequestConfig } from '../request'

// 登录参数
export interface LoginParams {
  identity: string
  password: string
}

export interface RegisterParams {
  email: string
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
  level?: number
  created_at?: string
}

interface RawUserInfo extends Partial<UserInfo> {
  level?: number
}

// 登录响应
export interface LoginResponse {
  token?: string
  access_token?: string
  refresh_token?: string
  userInfo?: RawUserInfo
  user?: RawUserInfo
}

const normalizeLoginResponse = (raw: LoginResponse) => {
  const token = raw.token || raw.access_token || ''
  const baseUser = raw.userInfo || raw.user
  const userLevel = baseUser?.level ?? 5
  const userInfoBase = {
    id: baseUser?.id || '',
    username: baseUser?.username || '',
    nickname: baseUser?.nickname || baseUser?.username || '',
    role: baseUser?.role || '',
    level: userLevel,
    permissions: baseUser?.permissions || []
  }
  const userInfo: UserInfo = baseUser?.avatar
    ? { ...userInfoBase, avatar: baseUser.avatar }
    : userInfoBase

  return {
    token,
    refresh_token: raw.refresh_token,
    userInfo
  }
}

// 登录
export const loginApi = (params: LoginParams, config?: RequestConfig) =>
  post<LoginResponse>('/auth/login', params, config).then(normalizeLoginResponse)

// 注册
export const registerApi = (params: RegisterParams, config?: RequestConfig) =>
  post<LoginResponse>('/auth/register', params, config).then(normalizeLoginResponse)

// 登出
export const logoutApi = (config?: RequestConfig) => post<void>('/auth/logout', undefined, config)

// 获取当前用户信息
export const getUserInfoApi = (config?: RequestConfig) =>
  get<Record<string, any>>('/auth/me', undefined, config).then((raw) => {
    const base: Record<string, any> = {
      id: String(raw.id || ''),
      username: String(raw.username || ''),
      nickname: String(raw.nickname || raw.username || ''),
      role: raw.role || '',
      level: raw.level ?? 5,
      permissions: raw.permissions || [],
    }
    if (raw.created_at != null) base.created_at = String(raw.created_at)
    if (raw.avatar) base.avatar = String(raw.avatar)
    return base as UserInfo
  })
