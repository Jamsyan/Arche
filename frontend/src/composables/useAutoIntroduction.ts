/**
 * useAutoIntroduction — 根据段落内容自动生成引言。
 *
 * 监听段落变化，提取：
 * - abstract: 首个非空 text 段落的前 80 字
 * - key_points: heading 段落列表
 * - reading_time: 按字数 / 300 估算
 * - difficulty_level: 按平均句长简单分级
 *
 * 不搞复杂算法，够用就行。生成的引言供用户参考确认，不自动覆盖。
 */
import { computed, type Ref } from 'vue'
import type { ParsedParagraph } from '@/utils/paragraph'

export interface AutoIntroduction {
  abstract?: string
  key_points?: string[]
  reading_time?: number
  difficulty_level?: string
}

/**
 * 根据段落数组自动计算引言信息。
 * 纯函数，无副作用，可在 composable 或保存流程中直接调用。
 */
export function computeIntroduction(paragraphs: ParsedParagraph[]): AutoIntroduction {
  const result: AutoIntroduction = {}

  // 1. abstract: 取首个非空 text 段落的前 80 字
  const firstText = paragraphs.find((p) => p.type === 'text' && p.content.trim().length > 0)
  if (firstText) {
    const cleaned = firstText.content.replace(/<[^>]*>/g, '').trim()
    if (cleaned) {
      result.abstract = cleaned.slice(0, 80)
    }
  }

  // 2. key_points: 提取 heading 段落
  const headings = paragraphs
    .filter((p) => p.type === 'heading' && p.heading)
    .map((p) => p.heading!)
  if (headings.length > 0) {
    result.key_points = headings
  }

  // 3. reading_time: 按中文字数 + 英文单词估算
  const totalText = paragraphs
    .filter((p) => p.type !== 'image')
    .map((p) => p.content)
    .join(' ')
  const cnChars = (totalText.match(/[\u4e00-\u9fff]/g) || []).length
  const enWords = (totalText.match(/[a-zA-Z]+/g) || []).length
  const totalWords = cnChars + enWords
  if (totalWords > 0) {
    result.reading_time = Math.max(1, Math.round(totalWords / 300))
  }

  // 4. difficulty_level: 按平均句长简单分级
  const sentences = totalText
    .split(/[。！？.!?]/)
    .map((s) => s.trim())
    .filter(Boolean)
  if (sentences.length > 0) {
    const avgLen = totalWords / sentences.length
    if (avgLen > 40) {
      result.difficulty_level = 'advanced'
    } else if (avgLen > 20) {
      result.difficulty_level = 'intermediate'
    } else {
      result.difficulty_level = 'beginner'
    }
  }

  return result
}

/**
 * useAutoIntroduction — 响应式 composable 版本。
 * 传入段落 ref，自动计算并返回引言 ref。
 */
export function useAutoIntroduction(paragraphs: Ref<ParsedParagraph[]>) {
  const introduction = computed(() => computeIntroduction(paragraphs.value))
  return { introduction }
}
