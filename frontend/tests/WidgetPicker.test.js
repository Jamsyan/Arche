/**
 * 测试 WidgetPicker.vue：分类渲染、添加事件。
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import WidgetPicker from '../src/components/dashboard/WidgetPicker.vue'

const arcoStubs = {
  'a-button': { template: '<button @click="$emit(\'click\')"><slot /></button>' },
  'icon-apps': true,
  'icon-left': true,
}

describe('WidgetPicker.vue', () => {
  it('渲染所有 widget 分类', () => {
    const wrapper = mount(WidgetPicker, {
      global: { stubs: arcoStubs },
    })
    expect(wrapper.vm.categories).toBeDefined()
    expect(Object.keys(wrapper.vm.categories).length).toBeGreaterThan(0)
  })

  it('点击添加按钮触发 add 事件', async () => {
    const wrapper = mount(WidgetPicker, {
      global: { stubs: arcoStubs },
    })
    const firstCategory = Object.keys(wrapper.vm.categories)[0]
    const firstWidget = wrapper.vm.categories[firstCategory][0]
    wrapper.vm.add(firstWidget.type)
    expect(wrapper.emitted('add')).toBeTruthy()
    expect(wrapper.emitted('add')[0]).toEqual([firstWidget.type])
  })

  it('点击关闭按钮触发 close 事件', async () => {
    const wrapper = mount(WidgetPicker, {
      global: { stubs: arcoStubs },
    })
    await wrapper.find('.collapse-btn').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
