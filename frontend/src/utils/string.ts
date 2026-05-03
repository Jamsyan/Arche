// 字符串处理工具函数

/**
 * 驼峰命名转短横线命名
 * @param str 驼峰字符串
 */
export function camelToKebab(str: string): string {
  return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase()
}

/**
 * 短横线命名转驼峰命名
 * @param str 短横线字符串
 */
export function kebabToCamel(str: string): string {
  return str.replace(/-(\w)/g, (_, c) => c.toUpperCase())
}

/**
 * 首字母大写
 * @param str 字符串
 */
export function capitalize(str: string): string {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * 首字母小写
 * @param str 字符串
 */
export function lowercaseFirst(str: string): string {
  if (!str) return ''
  return str.charAt(0).toLowerCase() + str.slice(1)
}

/**
 * 截断字符串，超出部分用省略号显示
 * @param str 字符串
 * @param length 最大长度
 * @param suffix 后缀，默认是...
 */
export function truncate(str: string, length: number, suffix = '...'): string {
  if (!str) return ''
  if (str.length <= length) return str
  return str.slice(0, length) + suffix
}

/**
 * 在无 DOMParser 环境下迭代剥离标签（直至稳定），避免单次正则遗留残缺标签。
 */
function stripHtmlIterative(raw: string): string {
  let s = raw
  for (let i = 0; i < 32; i++) {
    const next = s
      .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '')
      .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]{0,800}>/g, '')
    if (next === s) break
    s = next
  }
  return s.replace(/</g, '')
}

/**
 * 移除字符串中的 HTML，返回纯文本（优先用 DOMParser 解析，避免不完整的标签清理）。
 * @param str 包含 HTML 的字符串
 */
export function stripHtml(str: string): string {
  if (!str) return ''
  if (typeof DOMParser !== 'undefined') {
    try {
      const doc = new DOMParser().parseFromString(str, 'text/html')
      const text = doc.body?.textContent
      if (text != null) return text
    } catch {
      /* 回退到迭代剥离 */
    }
  }
  return stripHtmlIterative(str)
}

/**
 * 生成随机字符串
 * @param length 字符串长度
 */
export function randomString(length: number): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

/**
 * 手机号码脱敏
 * @param phone 手机号码
 */
export function maskPhone(phone: string): string {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

/**
 * 邮箱脱敏
 * @param email 邮箱地址
 */
export function maskEmail(email: string): string {
  if (!email || !email.includes('@')) return email
  const parts = email.split('@')
  const username = parts[0]
  const domain = parts[1]
  if (!username || !domain || username.length <= 2) return email
  return `${username.charAt(0)}***${username.charAt(username.length - 1)}@${domain}`
}
