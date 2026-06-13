import type { BlogPost } from '@/services/api'

/**
 * 摘要为空时，用帖子元信息作为替代展示。
 * 按优先级拼接 available 的字段，用 " · " 分隔。
 */
export function buildExcerptFallback(post: BlogPost): string {
  const parts: string[] = []
  const intro = post.introduction
  if (intro?.difficulty_level) parts.push(intro.difficulty_level)
  if (post.category_id) parts.push(post.category_id)
  if (parts.length > 0) return parts.join(' · ')
  return ''
}
