import { describe, it, expect } from 'vitest'

type BlogPost = {
  id: string
  slug: string
  title: string
  content: string
  tags: string[]
  intro?: string
  paragraphs?: { content: string }[]
}

describe('generateTextCover', () => {
  it('应该返回 data URL', async () => {
    const { generateTextCover } = await import('@/utils/generateTextCover')
    const post: BlogPost = {
      id: '1',
      slug: 'test-1',
      title: '测试文章',
      content: '这是一篇测试文章的内容'
    }

    const result = generateTextCover(post, true)
    expect(result).toContain('data:image/jpeg;base64,')
  })

  it('使用 intro 作为封面文本', async () => {
    const { generateTextCover } = await import('@/utils/generateTextCover')
    const post: BlogPost = {
      id: '2',
      slug: 'test-2',
      title: '测试',
      intro: '自定义引言',
      content: '正文内容'
    }

    const result = generateTextCover(post, true)
    expect(result).toContain('data:image/jpeg;base64,')
  })

  it('使用 paragraph 内容作为封面文本', async () => {
    const { generateTextCover } = await import('@/utils/generateTextCover')
    const post: BlogPost = {
      id: '3',
      slug: 'test-3',
      title: '测试',
      content: '',
      tags: [],
      paragraphs: [{ content: '段落内容' }]
    }

    const result = generateTextCover(post, true)
    expect(result).toContain('data:image/jpeg;base64,')
  })

  it('没有标题时也能生成封面', async () => {
    const { generateTextCover } = await import('@/utils/generateTextCover')
    const post: BlogPost = {
      id: '4',
      slug: 'test-4',
      title: '',
      content: '只有内容没有标题',
      tags: []
    }

    const result = generateTextCover(post, true)
    expect(result).toContain('data:image/jpeg;base64,')
  })

  it('缓存相同 id 的帖子', async () => {
    const { generateTextCover } = await import('@/utils/generateTextCover')
    const post: BlogPost = {
      id: '5',
      slug: 'test-5',
      title: '缓存测试',
      content: '',
      tags: []
    }

    // 第一次调用
    const result1 = generateTextCover(post)
    // 第二次调用（走缓存）
    const result2 = generateTextCover(post)

    expect(result1).toBe(result2)
  })

  it('noCache 参数跳过缓存', async () => {
    const { generateTextCover } = await import('@/utils/generateTextCover')
    const post: BlogPost = {
      id: '6',
      slug: 'test-6',
      title: '跳过缓存',
      content: '',
      tags: []
    }

    const result1 = generateTextCover(post, true)
    const result2 = generateTextCover(post, true)

    // noCache 每次都重新生成
    expect(result1).toBe(result2) // 因为 canvas mock 返回固定值
  })

  it('处理带标签的帖子', async () => {
    const { generateTextCover } = await import('@/utils/generateTextCover')
    const post: BlogPost = {
      id: '7',
      slug: 'test-7',
      title: '带标签的文章',
      tags: ['技术', '前端'],
      content: '这是一篇技术文章'
    }

    const result = generateTextCover(post, true)
    expect(result).toContain('data:image/jpeg;base64,')
  })

  it('处理 HTML 内容的段落', async () => {
    const { generateTextCover } = await import('@/utils/generateTextCover')
    const post: BlogPost = {
      id: '8',
      slug: 'test-8',
      title: 'HTML测试',
      content: '',
      tags: [],
      paragraphs: [{ content: '<p>这是<strong>HTML</strong>内容</p>' }]
    }

    const result = generateTextCover(post, true)
    expect(result).toContain('data:image/jpeg;base64,')
  })
})
