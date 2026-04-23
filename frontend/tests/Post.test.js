/**
 * 测试 Post.vue：isAuthor、canDelete。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import { ref, nextTick } from 'vue'
import Post from '../src/components/blog/Post.vue'
import * as authModule from '../src/router/auth.js'

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { slug: 'test-post' } }),
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('markdown-it', () => ({
  default: function () {
    return { render: (c) => `<p>${c}</p>` }
  },
}))

const arcoStubs = {
  'a-card': { template: '<div><slot /></div>' },
  'a-card-meta': { template: '<div><slot /></div>' },
  'a-avatar': { template: '<div><slot /></div>' },
  'a-space': { template: '<span><slot /></span>' },
  'a-tag': { template: '<span><slot /></span>' },
  'a-button': { template: '<button><slot /></button>' },
  'a-modal': { template: '<div><slot /></div>' },
  'a-input': { template: '<input />' },
  'a-textarea': { template: '<textarea />' },
  'a-empty': { template: '<div><slot /></div>' },
}

describe('Post.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    globalThis.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          code: 'ok',
          data: {
            id: 1, slug: 'test-post', title: 'Test', content: 'Hello',
            author_id: 1, author_username: 'author', created_at: '2024-01-01',
            views: 0, likes: 0, quality_score: 3, tags: [],
          },
        }),
      })
    )
  })

  describe('用户为空时不崩溃', () => {
    it('user 为 null 时 isAuthor 返回 false', async () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue({
        isAuthenticated: ref(false),
        user: ref(null),
        authHeaders: () => ({}),
        level: ref(5),
      })
      const wrapper = shallowMount(Post, { global: { stubs: arcoStubs } })
      // 等 onMounted 中的 fetch 完成
      await nextTick()
      await new Promise(r => setTimeout(r, 50))
      expect(wrapper.vm.isAuthor).toBe(false)
    })
  })

  describe('isAuthor', () => {
    it('作者 ID 匹配时 isAuthor 为 true', async () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue({
        isAuthenticated: ref(true),
        user: ref({ id: 1, username: 'author' }),
        authHeaders: () => ({}),
        level: ref(5),
      })
      const wrapper = shallowMount(Post, { global: { stubs: arcoStubs } })
      await nextTick()
      await new Promise(r => setTimeout(r, 50))
      expect(wrapper.vm.isAuthor).toBe(true)
    })

    it('作者 ID 不匹配时 isAuthor 为 false', async () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue({
        isAuthenticated: ref(true),
        user: ref({ id: 99, username: 'other' }),
        authHeaders: () => ({}),
        level: ref(5),
      })
      const wrapper = shallowMount(Post, { global: { stubs: arcoStubs } })
      await nextTick()
      await new Promise(r => setTimeout(r, 50))
      expect(wrapper.vm.isAuthor).toBe(false)
    })
  })

  describe('canDelete', () => {
    it('作者是 P0 时可以删除', async () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue({
        isAuthenticated: ref(true),
        user: ref({ id: 1 }),
        authHeaders: () => ({}),
        level: ref(0),
      })
      const wrapper = shallowMount(Post, { global: { stubs: arcoStubs } })
      await nextTick()
      await new Promise(r => setTimeout(r, 50))
      expect(wrapper.vm.canDelete).toBe(true)
    })

    it('非作者非 P0 不可删除', async () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue({
        isAuthenticated: ref(true),
        user: ref({ id: 99 }),
        authHeaders: () => ({}),
        level: ref(5),
      })
      const wrapper = shallowMount(Post, { global: { stubs: arcoStubs } })
      await nextTick()
      await new Promise(r => setTimeout(r, 50))
      expect(wrapper.vm.canDelete).toBe(false)
    })
  })
})
