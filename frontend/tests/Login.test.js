/**
 * 测试 Login.vue：登录流程。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Login from '../src/components/auth/Login.vue'
import * as authModule from '../src/router/auth.js'

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

describe('Login.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('表单提交', () => {
    it('登录成功跳转首页', async () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue({
        login: vi.fn().mockResolvedValue({ ok: true }),
      })
      const wrapper = mount(Login, { global: { stubs: arcoStubs } })
      wrapper.vm.form.identity = 'test'
      wrapper.vm.form.password = 'pass'
      await wrapper.vm.handleLogin()
      expect(mockPush).toHaveBeenCalledWith('/')
    })

    it('登录失败显示错误', async () => {
      vi.spyOn(authModule, 'useAuth').mockReturnValue({
        login: vi.fn().mockResolvedValue({ ok: false, error: '密码错误' }),
      })
      const wrapper = mount(Login, { global: { stubs: arcoStubs } })
      wrapper.vm.form.identity = 'test'
      wrapper.vm.form.password = 'wrong'
      await wrapper.vm.handleLogin()
      expect(wrapper.vm.error).toBe('密码错误')
    })
  })
})
