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

// 用户信息（level 唯一决定权限：0=管理员，其他=普通用户）
export interface UserInfo {
  id: string
  username: string
  nickname: string
  avatar?: string
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

// 刷新 access token
export const refreshTokenApi = (refresh_token: string, config?: RequestConfig) =>
  post<LoginResponse>('/auth/refresh', { refresh_token }, config).then((raw) => ({
    access_token: raw.access_token || raw.token || ''
  }))

// 登出
export const logoutApi = (config?: RequestConfig) => post<void>('/auth/logout', undefined, config)

// 获取当前用户信息
export const getUserInfoApi = (config?: RequestConfig) =>
  get<Record<string, any>>('/auth/me', undefined, config).then((raw) => {
    const userLevel = raw.level ?? 5
    const base = {
      id: String(raw.id || ''),
      username: String(raw.username || ''),
      nickname: String(raw.nickname || raw.username || ''),
      level: userLevel,
      permissions: userLevel === 0 ? ['*'] : raw.permissions || [],
      created_at: raw.created_at as string | undefined
    }
    return raw.avatar ? { ...base, avatar: raw.avatar as string } : base
  })

// ── 用户管理统计（P0） ──

export interface UserStats {
  total_users: number
  active_users: number
  disabled_users: number
  today_new: number
  by_level: Record<string, number>
  daily_trend: { date: string; count: number }[]
}

export const getUserStatsApi = (config?: RequestConfig) =>
  get<UserStats>('/auth/stats', undefined, config)
