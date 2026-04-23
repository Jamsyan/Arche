/**
 * 测试 TodoPanel.vue：todo 过滤、ack。
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import TodoPanel from '../src/components/dashboard/TodoPanel.vue'
import * as authModule from '../src/router/auth.js'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ path: '/' }),
}))

const arcoStubs = {
  'a-tag': { template: '<span><slot /></span>' },
  'a-button': { template: '<button><slot /></button>' },
  'icon-pushpin': true,
  'icon-check': true,
  'icon-bug': true,
  'icon-check-circle': true,
  'icon-storage': true,
}

describe('TodoPanel.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    vi.spyOn(authModule, 'useAuth').mockReturnValue({
      authHeaders: () => ({}),
    })
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  describe('activeTodos', () => {
    it('未被 ack 的 todo 显示在 activeTodos', () => {
      const wrapper = shallowMount(TodoPanel, { global: { stubs: arcoStubs } })
      wrapper.vm.todos = [
        { id: 't1', title: 'T1', desc: 'D1', icon: null, priority: 'high' },
      ]
      expect(wrapper.vm.activeTodos.length).toBe(1)
    })

    it('已 ack 的 todo 不显示在 activeTodos', () => {
      const wrapper = shallowMount(TodoPanel, { global: { stubs: arcoStubs } })
      wrapper.vm.todos = [
        { id: 't1', title: 'T1', desc: 'D1', icon: null, priority: 'high' },
      ]
      wrapper.vm.ack('t1')
      expect(wrapper.vm.activeTodos.length).toBe(0)
    })
  })

  describe('ack', () => {
    it('ack 后 todo 从 activeTodos 移除', () => {
      const wrapper = shallowMount(TodoPanel, { global: { stubs: arcoStubs } })
      wrapper.vm.todos = [
        { id: 't1', title: 'T1', desc: 'D1', icon: null, priority: 'high' },
      ]
      expect(wrapper.vm.activeTodos.length).toBe(1)
      wrapper.vm.ack('t1')
      expect(wrapper.vm.activeTodos.length).toBe(0)
    })
  })

  describe('addTodo', () => {
    it('手动添加的 todo 有 manual_ 前缀', () => {
      const wrapper = shallowMount(TodoPanel, { global: { stubs: arcoStubs } })
      wrapper.vm.addTodo({ title: 'Manual', desc: 'M', icon: null })
      const manualTodo = wrapper.vm.todos.find(t => t.id.startsWith('manual_'))
      expect(manualTodo).toBeDefined()
      expect(manualTodo.title).toBe('Manual')
    })

    it('手动添加的 todo 不会被自动检测替换', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ code: 'ok', data: {} }),
        })
      )
      const wrapper = shallowMount(TodoPanel, { global: { stubs: arcoStubs } })
      wrapper.vm.addTodo({ title: 'Manual', desc: 'M', icon: null })
      await wrapper.vm.detectTodos()
      const manualTodo = wrapper.vm.todos.find(t => t.id.startsWith('manual_'))
      expect(manualTodo).toBeDefined()
      expect(manualTodo.title).toBe('Manual')
    })
  })
})
