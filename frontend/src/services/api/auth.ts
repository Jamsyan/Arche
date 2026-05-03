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
  const userInfoBase = {
    id: baseUser?.id || '',
    username: baseUser?.username || '',
    nickname: baseUser?.nickname || baseUser?.username || '',
    role: baseUser?.role || (baseUser?.level === 0 ? 'admin' : 'user'),
    permissions: baseUser?.permissions || (baseUser?.level === 0 ? ['*'] : [])
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
    const base = {
      id: String(raw.id || ''),
      username: String(raw.username || ''),
      nickname: String(raw.nickname || raw.username || ''),
      role: raw.role || (raw.level === 0 ? 'admin' : 'user'),
      permissions: raw.permissions || (raw.level === 0 ? ['*'] : [])
    }
    return raw.avatar ? { ...base, avatar: raw.avatar as string } : base
  })
