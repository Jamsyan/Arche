import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/services/request', () => ({ get: vi.fn(), post: vi.fn() }))
beforeEach(() => {
  vi.clearAllMocks()
})

describe('crawler API', () => {
  it('getCrawlerStatusApi', async () => {
    const { getCrawlerStatusApi } = await import('@/services/api/crawler')
    const { get } = await import('@/services/request')
    vi.mocked(get).mockResolvedValue({ running: false })
    await getCrawlerStatusApi()
    expect(get).toHaveBeenCalledWith('/crawler/status', undefined, undefined)
  })

  it('startCrawlerApi', async () => {
    const { startCrawlerApi } = await import('@/services/api/crawler')
    const { post } = await import('@/services/request')
    vi.mocked(post).mockResolvedValue(undefined)
    await startCrawlerApi()
    expect(post).toHaveBeenCalledWith('/crawler/start', undefined, undefined)
  })

  it('getCrawlerRecordsApi', async () => {
    const { getCrawlerRecordsApi } = await import('@/services/api/crawler')
    const { get } = await import('@/services/request')
    vi.mocked(get).mockResolvedValue({ items: [], total: 0 })
    await getCrawlerRecordsApi({ page: 1, page_size: 20 })
    expect(get).toHaveBeenCalledWith('/crawler/records', { page: 1, page_size: 20 }, undefined)
  })

  it('getCrawlerRecordApi 拼接 ID', async () => {
    const { getCrawlerRecordApi } = await import('@/services/api/crawler')
    const { get } = await import('@/services/request')
    vi.mocked(get).mockResolvedValue({ id: 'rec-1', url: 'https://example.com' })
    await getCrawlerRecordApi('rec-1')
    expect(get).toHaveBeenCalledWith('/crawler/records/rec-1', undefined, undefined)
  })

  it('addCrawlerSeedApi 封装 url', async () => {
    const { addCrawlerSeedApi } = await import('@/services/api/crawler')
    const { post } = await import('@/services/request')
    vi.mocked(post).mockResolvedValue(undefined)
    await addCrawlerSeedApi('https://example.com')
    expect(post).toHaveBeenCalledWith('/crawler/seeds', { url: 'https://example.com' }, undefined)
  })
})
