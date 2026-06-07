import { describe, it, expect } from 'vitest'
import { formatDate, isToday } from '../date'

describe('formatDate', () => {
  it('Date 对象格式化', () => {
    const d = new Date(2024, 0, 15, 14, 30, 45)
    expect(formatDate(d)).toBe('2024-01-15 14:30:45')
  })

  it('时间戳格式化', () => {
    const ts = new Date(2024, 5, 1, 9, 5, 3).getTime()
    expect(formatDate(ts)).toBe('2024-06-01 09:05:03')
  })

  it('日期字符串格式化', () => {
    expect(formatDate('2024-12-25T10:00:00', 'YYYY-MM-DD')).toBe('2024-12-25')
  })

  it('自定义格式', () => {
    const d = new Date(2024, 0, 1, 8, 0, 0)
    expect(formatDate(d, 'YYYY/MM/DD HH:mm')).toBe('2024/01/01 08:00')
    expect(formatDate(d, 'HH:mm:ss')).toBe('08:00:00')
  })

  it('无效日期返回空字符串', () => {
    expect(formatDate(null as unknown as Date)).toBe('')
    expect(formatDate('invalid-date')).toBe('')
    expect(formatDate(new Date('invalid'))).toBe('')
  })
})

describe('isToday', () => {
  it('今天返回 true', () => {
    expect(isToday(new Date())).toBe(true)
  })

  it('非今天返回 false', () => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    expect(isToday(yesterday)).toBe(false)
  })
})
