/**
 * 测试 WidgetCanvas.vue：挂载、pinnedIds(Set)、addWidget/removeWidget。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import WidgetCanvas from '../src/components/dashboard/WidgetCanvas.vue'

// Mock sortablejs at module level
vi.mock('sortablejs', () => ({ default: { create: vi.fn() } }))

const arcoStubs = {
  'a-tooltip': { template: '<span><slot /></span>' },
}

describe('WidgetCanvas.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.removeItem('veil_dashboard_widgets')
  })

  describe('挂载', () => {
    it('正常挂载不报错', () => {
      const wrapper = mount(WidgetCanvas, {
        props: { pinnedIds: new Set(), onTogglePin: () => {} },
        global: { stubs: arcoStubs },
      })
      expect(wrapper.vm).toBeDefined()
    })

    it('空状态显示提示信息', () => {
      const wrapper = mount(WidgetCanvas, {
        props: { pinnedIds: new Set(), onTogglePin: () => {} },
        global: { stubs: arcoStubs },
      })
      expect(wrapper.text()).toContain('从右侧 Widget 库拖拽卡片到此处')
    })
  })

  describe('pinnedIds 兼容性', () => {
    it('接受 Set 作为 pinnedIds', () => {
      const pinnedIds = new Set(['w_1', 'w_2'])
      const wrapper = mount(WidgetCanvas, {
        props: { pinnedIds, onTogglePin: () => {} },
        global: { stubs: arcoStubs },
      })
      expect(wrapper.vm.isPinned('w_1')).toBe(true)
      expect(wrapper.vm.isPinned('w_999')).toBe(false)
    })

    it('isPinned 不抛异常', () => {
      const wrapper = mount(WidgetCanvas, {
        props: { pinnedIds: new Set(), onTogglePin: () => {} },
        global: { stubs: arcoStubs },
      })
      expect(() => wrapper.vm.isPinned('any_id')).not.toThrow()
    })
  })

  describe('addWidget', () => {
    it('添加 widget 后 widgetInstances 增加', () => {
      const wrapper = mount(WidgetCanvas, {
        props: { pinnedIds: new Set(), onTogglePin: () => {} },
        global: { stubs: arcoStubs },
      })
      wrapper.vm.addWidget('system-cpu')
      expect(wrapper.vm.widgetInstances.length).toBe(1)
      expect(wrapper.vm.widgetInstances[0].type).toBe('system-cpu')
    })

    it('添加的 widget 有 id', () => {
      const wrapper = mount(WidgetCanvas, {
        props: { pinnedIds: new Set(), onTogglePin: () => {} },
        global: { stubs: arcoStubs },
      })
      wrapper.vm.addWidget('system-cpu')
      expect(wrapper.vm.widgetInstances[0].id).toBeDefined()
      expect(typeof wrapper.vm.widgetInstances[0].id).toBe('string')
    })
  })

  describe('removeWidget', () => {
    it('移除后 widgetInstances 减少', () => {
      const wrapper = mount(WidgetCanvas, {
        props: { pinnedIds: new Set(), onTogglePin: () => {} },
        global: { stubs: arcoStubs },
      })
      wrapper.vm.addWidget('system-cpu')
      const id = wrapper.vm.widgetInstances[0].id
      wrapper.vm.removeWidget(id)
      expect(wrapper.vm.widgetInstances.length).toBe(0)
    })
  })

  describe('togglePin', () => {
    it('调用 onTogglePin 传递 id', () => {
      const onTogglePin = vi.fn()
      const wrapper = mount(WidgetCanvas, {
        props: { pinnedIds: new Set(), onTogglePin },
        global: { stubs: arcoStubs },
      })
      wrapper.vm.togglePin('w_test')
      expect(onTogglePin).toHaveBeenCalledWith('w_test')
    })
  })
})
