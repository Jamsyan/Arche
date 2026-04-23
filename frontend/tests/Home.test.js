/**
 * 测试 Home.vue（博客首页）：getLevel、排序、筛选。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, shallowMount } from '@vue/test-utils'
import Home from '../src/components/blog/Home.vue'

const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

const arcoStubs = {
  'a-radio-group': { template: '<div><slot /></div>' },
  'a-radio': { template: '<div><slot /></div>' },
  'a-select': { template: '<div><slot /></div>' },
  'a-option': { template: '<div><slot /></div>' },
  'a-button': { template: '<button><slot /></button>' },
  'a-card': { template: '<div><slot /></div>' },
  'a-card-meta': { template: '<div><slot /></div>' },
  'a-avatar': { template: '<div><slot /></div>' },
  'a-space': { template: '<span><slot /></span>' },
  'a-tag': { template: '<span><slot /></span>' },
  'a-pagination': { template: '<div><slot /></div>' },
  'a-empty': { template: '<div><slot /></div>' },
  'a-spin': { template: '<div />' },
  'a-switch': { template: '<div><slot /></div>' },
}

describe('Home.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    globalThis.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ code: 'ok', data: { items: [], total: 0 } }),
      })
    )
  })

  describe('getLevel', () => {
    it('分数 >=5 返回 0', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      expect(wrapper.vm.getLevel(5)).toBe(0)
      expect(wrapper.vm.getLevel(10)).toBe(0)
    })

    it('分数 4 返回 1', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      expect(wrapper.vm.getLevel(4)).toBe(1)
    })

    it('分数 3 返回 2', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      expect(wrapper.vm.getLevel(3)).toBe(2)
    })

    it('分数 2 返回 3', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      expect(wrapper.vm.getLevel(2)).toBe(3)
    })

    it('分数 1 返回 4', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      expect(wrapper.vm.getLevel(1)).toBe(4)
    })

    it('分数 0 返回 5', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      expect(wrapper.vm.getLevel(0)).toBe(5)
    })

    it('null 分数返回 5', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      expect(wrapper.vm.getLevel(null)).toBe(5)
    })
  })

  describe('初始化', () => {
    it('初始加载状态为 true', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      expect(wrapper.vm.loading).toBe(true)
    })
  })

  describe('排序', () => {
    it('默认排序为 created_at', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      expect(wrapper.vm.sortBy).toBe('created_at')
    })
  })

  describe('标签筛选', () => {
    it('选择标签后 page 重置为 1', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      wrapper.vm.page = 5
      wrapper.vm.onTagChange()
      expect(wrapper.vm.page).toBe(1)
    })

    it('清除标签后 page 重置为 1', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      wrapper.vm.selectedTag = 'vue'
      wrapper.vm.page = 5
      wrapper.vm.clearTag()
      expect(wrapper.vm.selectedTag).toBe('')
      expect(wrapper.vm.page).toBe(1)
    })
  })

  describe('文章跳转', () => {
    it('goToPost 跳转到正确路径', () => {
      const wrapper = shallowMount(Home, { global: { stubs: arcoStubs } })
      wrapper.vm.goToPost('my-post')
      expect(mockPush).toHaveBeenCalledWith('/post/my-post')
    })
  })
})
