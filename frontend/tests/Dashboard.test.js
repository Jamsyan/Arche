/**
 * 测试 Dashboard.vue：渲染、pinnedIds(Set)、togglePin。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import Dashboard from '../src/components/platform/Dashboard.vue'
import * as authModule from '../src/router/auth.js'

vi.mock('vue-router', () => ({
  useRoute: () => ({ path: '/platform' }),
  useRouter: () => ({ push: vi.fn() }),
}))

const arcoStubs = {
  'a-button': { template: '<button><slot /></button>' },
  'a-tag': { template: '<span><slot /></span>' },
  'a-progress': { template: '<div />' },
  'a-modal': {
    props: ['visible', 'title', 'width', 'footer'],
    template: '<div class="mock-modal"><slot /></div>',
  },
}

const mockAuth = {
  loadUser: vi.fn().mockResolvedValue(undefined),
  user: ref({ id: 1, username: 'testuser', email: 'a@b.com', created_at: '2024-01-01', level: 0 }),
  level: ref(0),
  authHeaders: () => ({ Authorization: 'Bearer tok' }),
}

describe('Dashboard.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    globalThis.fetch = vi.fn(() => Promise.resolve({ ok: false }))
  })

  describe('渲染', () => {
    it('正常挂载不报错', () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue(mockAuth)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      expect(wrapper.vm).toBeDefined()
    })
  })

  describe('pinnedIds 类型', () => {
    it('pinnedIds 是 Set 类型', () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue(mockAuth)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      // 在 script setup 中，ref 被自动解包，所以 wrapper.vm.pinnedIds 就是 Set 本身
      // 但 shallowMount 不执行 setup 中的赋值，我们用 mount
      // 实际上 setup 中的 const pinnedIds = ref(new Set()) 是同步执行的
      // wrapper.vm.pinnedIds 应该是 Set 实例
      expect(wrapper.vm.pinnedIds).toBeInstanceOf(Set)
    })

    it('Set 上 has 方法正常工作', () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue(mockAuth)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      wrapper.vm.pinnedIds.add('w_test')
      expect(wrapper.vm.pinnedIds.has('w_test')).toBe(true)
      expect(wrapper.vm.pinnedIds.has('w_fake')).toBe(false)
    })
  })

  describe('togglePin', () => {
    it('pin 一个 widget', () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue(mockAuth)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      wrapper.vm.togglePin('w_1')
      expect(wrapper.vm.pinnedIds.has('w_1')).toBe(true)
    })

    it('取消 pin 一个 widget', () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue(mockAuth)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      wrapper.vm.pinnedIds.add('w_2')
      wrapper.vm.togglePin('w_2')
      expect(wrapper.vm.pinnedIds.has('w_2')).toBe(false)
    })
  })

  describe('卡片数据', () => {
    it('creatorCards 有 3 张卡', () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue(mockAuth)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      expect(wrapper.vm.creatorCards.length).toBe(3)
    })

    it('taskCards 包含管理员面板(P0)', () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue(mockAuth)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      const ids = wrapper.vm.taskCards.map(c => c.id)
      expect(ids).toContain('admin')
    })

    it('taskCards 不含管理员面板(非P0)', () => {
      const authNonAdmin = { ...mockAuth, level: ref(5) }
      vi.spyOn(authModule, 'useAuth').mockReturnValue(authNonAdmin)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      const ids = wrapper.vm.taskCards.map(c => c.id)
      expect(ids).not.toContain('admin')
    })

    it('所有卡片都有 id、icon、title、onClick、body', () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue(mockAuth)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      const allCards = [...wrapper.vm.creatorCards, ...wrapper.vm.taskCards]
      allCards.forEach(card => {
        expect(card.id).toBeDefined()
        expect(card.icon).toBeDefined()
        expect(card.title).toBeDefined()
        expect(typeof card.onClick).toBe('function')
        expect(typeof card.body).toBe('function')
      })
    })

    it('卡片 id 不重复', () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue(mockAuth)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      const allIds = [
        ...wrapper.vm.creatorCards.map(c => c.id),
        ...wrapper.vm.taskCards.map(c => c.id),
      ]
      const uniqueIds = new Set(allIds)
      expect(uniqueIds.size).toBe(allIds.length)
    })
  })

  describe('formatDate', () => {
    it('有效日期正常格式化', () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue(mockAuth)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      const result = wrapper.vm.formatDate('2024-06-15')
      expect(result).not.toBe('未知')
    })

    it('空值返回未知', () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue(mockAuth)
      const wrapper = mount(Dashboard, {
        global: {
          stubs: arcoStubs,
          config: { isCustomElement: (tag) => tag === 'img' || tag.startsWith('icon-') },
        },
      })
      expect(wrapper.vm.formatDate(null)).toBe('未知')
      expect(wrapper.vm.formatDate('')).toBe('未知')
    })
  })
})
