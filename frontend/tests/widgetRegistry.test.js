/**
 * 测试 widgetRegistry: getWidgetCategories, getWidgetComponent, getAllWidgets.
 */
import { describe, it, expect } from 'vitest'
import {
  getWidgetCategories,
  getWidgetComponent,
  getAllWidgets,
} from '../src/components/dashboard/widgets/widgetRegistry.js'

describe('widgetRegistry', () => {
  describe('getAllWidgets', () => {
    it('返回所有 widget 定义', () => {
      const widgets = getAllWidgets()
      expect(widgets.length).toBeGreaterThan(0)
    })

    it('每个 widget 都有必填字段', () => {
      const widgets = getAllWidgets()
      widgets.forEach(w => {
        expect(w.type).toBeDefined()
        expect(w.title).toBeDefined()
        expect(w.icon).toBeDefined()
        expect(w.category).toBeDefined()
        expect(typeof w.component).toBe('function')
      })
    })
  })

  describe('getWidgetComponent', () => {
    it('已知 type 返回定义', () => {
      const def = getWidgetComponent('system-cpu')
      expect(def).toBeDefined()
      expect(def.type).toBe('system-cpu')
    })

    it('未知 type 返回 undefined', () => {
      const def = getWidgetComponent('nonexistent')
      expect(def).toBeUndefined()
    })
  })

  describe('getWidgetCategories', () => {
    it('返回按 category 分组的对象', () => {
      const cats = getWidgetCategories()
      expect(typeof cats).toBe('object')
      expect(Object.keys(cats).length).toBeGreaterThan(0)
    })

    it('每个 category 都有 widgets 数组', () => {
      const cats = getWidgetCategories()
      for (const [name, widgets] of Object.entries(cats)) {
        expect(Array.isArray(widgets)).toBe(true)
        expect(widgets.length).toBeGreaterThan(0)
        widgets.forEach(w => {
          expect(w.category).toBe(name)
        })
      }
    })

    it('所有 widget 都被分到某个 category', () => {
      const cats = getWidgetCategories()
      const allCategorized = Object.values(cats).flat().map(w => w.type)
      const allWidgets = getAllWidgets().map(w => w.type)
      expect(new Set(allCategorized)).toEqual(new Set(allWidgets))
    })
  })
})
