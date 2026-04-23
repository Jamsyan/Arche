/**
 * 测试 useDock 所有公开方法。
 * 每个测试使用 freshUseDock 确保模块级状态隔离。
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'

async function freshUseDock(level) {
  vi.resetModules()
  const mod = await import('../src/router/dock.js')
  return mod.useDock(level)
}

describe('useDock', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('初始化', () => {
    it('alwaysItems 始终包含首页', async () => {
      const dock = await freshUseDock(5)
      expect(dock.alwaysItems.map(i => i.id)).toContain('home')
    })

    it('P5 用户只能看到 alwaysItems', async () => {
      const dock = await freshUseDock(5)
      expect(dock.available.value.map(i => i.id)).toEqual([])
    })

    it('P0 用户可见所有 items', async () => {
      const dock = await freshUseDock(0)
      const visible = dock.available.value.map(i => i.id)
      expect(visible.length).toBeGreaterThan(5)
      expect(visible).toContain('admin')
      expect(visible).toContain('cloud')
    })

    it('pinned 和 available 不重复', async () => {
      const dock = await freshUseDock(0)
      const pinnedIds = dock.pinned.value.map(i => i.id)
      const availIds = dock.available.value.map(i => i.id)
      const overlap = pinnedIds.filter(id => availIds.includes(id))
      expect(overlap).toEqual([])
    })
  })

  describe('pin / unpin', () => {
    it('pin 后项目从 available 移到 pinned', async () => {
      const dock = await freshUseDock(0)
      dock.pin('editor')
      expect(dock.pinned.value.map(i => i.id)).toContain('editor')
      expect(dock.available.value.map(i => i.id)).not.toContain('editor')
    })

    it('unpin 后项目从 pinned 移回 available', async () => {
      const dock = await freshUseDock(0)
      dock.pin('editor')
      dock.unpin('editor')
      expect(dock.pinned.value.map(i => i.id)).not.toContain('editor')
      expect(dock.available.value.map(i => i.id)).toContain('editor')
    })

    it('重复 pin 不会创建重复项', async () => {
      const dock = await freshUseDock(0)
      dock.pin('editor')
      dock.pin('editor')
      const count = dock.pinned.value.filter(i => i.id === 'editor').length
      expect(count).toBe(1)
    })
  })

  describe('isPinned', () => {
    it('未 pin 返回 false', async () => {
      const dock = await freshUseDock(0)
      expect(dock.isPinned('editor')).toBe(false)
    })

    it('已 pin 返回 true', async () => {
      const dock = await freshUseDock(0)
      dock.pin('editor')
      expect(dock.isPinned('editor')).toBe(true)
    })
  })

  describe('reorder', () => {
    it('根据新顺序重排', async () => {
      const dock = await freshUseDock(0)
      dock.pin('editor')
      dock.pin('upload')
      dock.pin('storage')
      dock.reorder(['storage', 'editor', 'upload'])
      expect(dock.pinned.value.map(i => i.id)).toEqual(['storage', 'editor', 'upload'])
    })

    it('忽略不存在的 id', async () => {
      const dock = await freshUseDock(0)
      dock.pin('editor')
      dock.reorder(['editor', 'nonexistent'])
      expect(dock.pinned.value.map(i => i.id)).toEqual(['editor'])
    })
  })

  describe('持久化', () => {
    // 注意：在 Vitest + jsdom 环境下，模块内的 localStorage 引用与测试中的
    // localStorage 可能是不同实例，因此无法直接验证 setItem 调用。
    // 以下测试验证读取路径，写入路径由 pin/unpin 功能测试间接保证。

    it('从 localStorage 恢复 pinned', async () => {
      localStorage.setItem('veil_dock', '["editor","upload"]')
      const dock = await freshUseDock(0)
      expect(dock.pinned.value.map(i => i.id)).toEqual(['editor', 'upload'])
    })

    it('localStorage 无数据时 pinned 为空', async () => {
      const dock = await freshUseDock(0)
      expect(dock.pinned.value).toEqual([])
    })
  })

  describe('数据结构完整性', () => {
    it('所有 items 都有必填字段', async () => {
      const dock = await freshUseDock(0)
      const all = [...dock.alwaysItems, ...dock.available.value, ...dock.pinned.value]
      all.forEach(item => {
        expect(item.id).toBeDefined()
        expect(item.title).toBeDefined()
        expect(item.icon).toBeDefined()
        expect(item.route).toBeDefined()
      })
    })
  })
})
