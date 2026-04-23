/**
 * 测试 component-registry: getAvailableComponents, loadComponent.
 */
import { describe, it, expect } from 'vitest'
import { getAvailableComponents, loadComponent } from '../src/router/component-registry.js'

describe('component-registry', () => {
  describe('getAvailableComponents', () => {
    it('P5 用户只有博客组件', () => {
      const components = getAvailableComponents(5)
      expect(Object.keys(components)).toEqual(['BlogHome', 'BlogPost'])
    })

    it('P4 用户同 P5（P4 无独有组件）', () => {
      const components = getAvailableComponents(4)
      expect(Object.keys(components)).toEqual(['BlogHome', 'BlogPost'])
    })

    it('P3 用户额外获得 BlogEditor', () => {
      const components = getAvailableComponents(3)
      expect(Object.keys(components)).toContain('BlogEditor')
    })

    it('P2 用户额外获得文件上传、GitHub、存储、审核', () => {
      const components = getAvailableComponents(2)
      expect(Object.keys(components)).toContain('FileUpload')
      expect(Object.keys(components)).toContain('GitHubProxy')
      expect(Object.keys(components)).toContain('P1Storage')
      expect(Object.keys(components)).toContain('ModerationPanel')
    })

    it('P0 用户获得所有组件', () => {
      const components = getAvailableComponents(0)
      expect(Object.keys(components)).toContain('AdminPanel')
      expect(Object.keys(components)).toContain('UserManagement')
      expect(Object.keys(components)).toContain('CrawlerDashboard')
      expect(Object.keys(components)).toContain('CloudTraining')
    })

    it('null 等级默认为 P5', () => {
      const components = getAvailableComponents(null)
      expect(Object.keys(components)).toEqual(['BlogHome', 'BlogPost'])
    })
  })

  describe('loadComponent', () => {
    it('有权限返回加载函数', () => {
      const loader = loadComponent(0, 'BlogHome')
      expect(loader).toBeInstanceOf(Function)
    })

    it('无权限返回 null', () => {
      const loader = loadComponent(5, 'AdminPanel')
      expect(loader).toBeNull()
    })

    it('不存在的组件名返回 null', () => {
      const loader = loadComponent(0, 'NonExistent')
      expect(loader).toBeNull()
    })

    it('P5 用户无法加载 AdminPanel', () => {
      const loader = loadComponent(5, 'AdminPanel')
      expect(loader).toBeNull()
    })
  })
})
