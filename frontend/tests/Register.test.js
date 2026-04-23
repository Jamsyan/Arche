/**
 * 测试 Register.vue：表单验证（邮箱、密码、确认密码）。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Register from '../src/components/auth/Register.vue'
import * as authModule from '../src/router/auth.js'

// Top-level mock - hoisted automatically
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

const arcoStubs = {
  'a-form': { template: '<form @submit.prevent="$emit(\'submit\')"><slot /></form>' },
  'a-form-item': { template: '<div><slot /></div>' },
  'a-input': { template: '<input />' },
  'a-input-password': { template: '<input type="password" />' },
  'a-alert': { template: '<div class="alert"><slot /></div>' },
  'a-button': { template: '<button><slot /></button>' },
  'a-typography-text': { template: '<span><slot /></span>' },
}

describe('Register.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('邮箱验证', () => {
    it('无效邮箱显示错误', async () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue({
        register: vi.fn(),
      })
      const wrapper = mount(Register, { global: { stubs: arcoStubs } })
      wrapper.vm.form.email = 'not-an-email'
      wrapper.vm.form.password = '123456'
      wrapper.vm.form.confirmPassword = '123456'
      await wrapper.vm.handleRegister()
      expect(wrapper.vm.error).toBe('请输入有效的邮箱地址')
    })
  })

  describe('密码验证', () => {
    it('密码不一致显示错误', async () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue({
        register: vi.fn(),
      })
      const wrapper = mount(Register, { global: { stubs: arcoStubs } })
      wrapper.vm.form.email = 'a@b.com'
      wrapper.vm.form.password = '123456'
      wrapper.vm.form.confirmPassword = '654321'
      await wrapper.vm.handleRegister()
      expect(wrapper.vm.error).toBe('两次输入的密码不一致')
    })

    it('密码过短显示错误', async () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue({
        register: vi.fn(),
      })
      const wrapper = mount(Register, { global: { stubs: arcoStubs } })
      wrapper.vm.form.email = 'a@b.com'
      wrapper.vm.form.password = '123'
      wrapper.vm.form.confirmPassword = '123'
      await wrapper.vm.handleRegister()
      expect(wrapper.vm.error).toBe('密码至少 6 位')
    })
  })

  describe('注册成功', () => {
    it('跳转 /platform', async () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue({
        register: vi.fn().mockResolvedValue({ ok: true }),
      })
      const wrapper = mount(Register, { global: { stubs: arcoStubs } })
      wrapper.vm.form.email = 'a@b.com'
      wrapper.vm.form.username = 'test'
      wrapper.vm.form.password = '123456'
      wrapper.vm.form.confirmPassword = '123456'
      await wrapper.vm.handleRegister()
      expect(mockPush).toHaveBeenCalledWith('/platform')
    })
  })
})
