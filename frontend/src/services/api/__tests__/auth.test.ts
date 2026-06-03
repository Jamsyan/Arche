import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../../request', () => ({
  get: vi.fn(),
  post: vi.fn()
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('auth API', () => {
  it('loginApi 发送正确 URL 和参数', async () => {
    const { loginApi } = await import('../auth')
    const { post } = await import('../../request')
    vi.mocked(post).mockResolvedValue({
      token: 'abc',
      userInfo: { id: '1', username: 'u', role: 'user', permissions: [] }
    })

    await loginApi({ identity: 'admin', password: 'pass' })
    expect(post).toHaveBeenCalledWith(
      '/auth/login',
      { identity: 'admin', password: 'pass' },
      undefined
    )
  })

  it('getUserInfoApi 发送正确 URL', async () => {
    const { getUserInfoApi } = await import('../auth')
    const { get } = await import('../../request')
    vi.mocked(get).mockResolvedValue({ id: '1', username: 'admin', level: 0 })

    await getUserInfoApi()
    expect(get).toHaveBeenCalledWith('/auth/me', undefined, undefined)
  })

  it('getUserInfoApi 标准化响应数据', async () => {
    const { getUserInfoApi } = await import('../auth')
    const { get } = await import('../../request')
    vi.mocked(get).mockResolvedValue({ id: '1', username: 'admin', level: 0 })

    const result = await getUserInfoApi()
    expect(result.id).toBe('1')
    expect(result.username).toBe('admin')
    expect(result.level).toBe(0)
    expect(result.role).toBe('')
    expect(result.nickname).toBe('admin')
  })

  it('refreshTokenApi 发送正确请求', async () => {
    const { refreshTokenApi } = await import('../auth')
    const { post } = await import('../../request')
    vi.mocked(post).mockResolvedValue({ access_token: 'new-token' })

    await refreshTokenApi('refresh-123')
    expect(post).toHaveBeenCalledWith('/auth/refresh', { refresh_token: 'refresh-123' }, undefined)
  })
})
