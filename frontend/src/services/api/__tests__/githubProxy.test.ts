import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../../request', () => ({ get: vi.fn(), post: vi.fn() }))
beforeEach(() => {
  vi.clearAllMocks()
})

describe('githubProxy API', () => {
  it('getGithubProxyHealthApi', async () => {
    const { getGithubProxyHealthApi } = await import('../githubProxy')
    const { get } = await import('../../request')
    vi.mocked(get).mockResolvedValue({ http: { available: true } })
    await getGithubProxyHealthApi()
    expect(get).toHaveBeenCalledWith('/github/health/status', undefined, undefined)
  })

  it('clearGithubProxyCacheApi', async () => {
    const { clearGithubProxyCacheApi } = await import('../githubProxy')
    const { post } = await import('../../request')
    vi.mocked(post).mockResolvedValue(undefined)
    await clearGithubProxyCacheApi()
    expect(post).toHaveBeenCalledWith('/github/cache/clear', undefined, undefined)
  })

  it('proxyGithubRawApi 拼接 path 和 mode', async () => {
    const { proxyGithubRawApi } = await import('../githubProxy')
    const { get } = await import('../../request')
    vi.mocked(get).mockResolvedValue('content')
    await proxyGithubRawApi('owner/repo/file.txt', 'http')
    expect(get).toHaveBeenCalledWith('/github/raw/owner/repo/file.txt', { mode: 'http' }, undefined)
  })
})
