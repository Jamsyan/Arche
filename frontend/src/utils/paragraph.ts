/**
 * HTML → paragraphs 解析引擎。
 *
 * 将 TipTap/富文本编辑器输出的 HTML 按块级标签拆分为段落数组，
 * 适配后端 BlogParagraph 表结构。
 */

export interface ParsedParagraph {
  content: string
  type: 'text' | 'heading' | 'code' | 'quote' | 'image'
  /** 仅 type=heading 时，提取的标题文字 */
  heading?: string
  /** 仅 type=image 时，提取的图片 URL */
  media_url?: string
}

// ── 卡片编辑器类型 ──

/** 卡片编辑器中的段落卡片类型 */
export type CardType =
  | 'text' // 正文段落
  | 'quote' // 引用
  | 'code' // 代码块
  | 'image' // 图片

/** 卡片编辑器中的段落卡片 */
export interface CardData {
  id: string
  type: CardType
  content: string
  /** 仅 image 类型 */
  media_url?: string
}

const CARD_TYPES: { type: CardType; label: string }[] = [
  { type: 'text', label: '正文' },
  { type: 'quote', label: '引用' },
  { type: 'code', label: '代码' },
  { type: 'image', label: '图片' }
]

export { CARD_TYPES }

let _cardIdCounter = 0
function generateCardId(): string {
  return `card_${Date.now().toString(36)}_${++_cardIdCounter}`
}

/**
 * 将 Markdown 文本按空行分割为段落卡片数组。
 *
 * 规则：
 * - 按空行（\n\n+）分割段落
 * - 代码块（```）内部不分割
 * - 根据首行内容自动推断卡片类型
 * - 首行 `# ` 标记为 title
 * - 首个 `> ` 块标记为 abstract，后续的 > 块标记为 quote
 * - `## ` / `### ` 标记为对应标题级别
 * - ``` 块标记为 code
 * - ![alt](url) 标记为 image
 * - 其余为 text
 */
export function parseMdToCards(md: string): CardData[] {
  if (!md || !md.trim()) return []

  const lines = md.split('\n')
  const cards: CardData[] = []
  let currentBlock: string[] = []
  let inCodeBlock = false

  function flushBlock() {
    if (currentBlock.length === 0) return
    const raw = currentBlock.join('\n')
    const content = raw.trim()
    if (!content) return

    const firstLine = currentBlock[0]?.trimStart() ?? ''
    let type: CardType = 'text'

    if (inCodeBlock) {
      type = 'code'
    } else if (firstLine.startsWith('> ')) {
      type = 'quote'
    } else if (/^!\[.*\]\(.*\)/.test(firstLine)) {
      type = 'image'
    }

    cards.push({ id: generateCardId(), type, content })
    currentBlock = []
  }

  for (const line of lines) {
    // 代码块边界检测
    if (/^```/.test(line.trimStart())) {
      if (inCodeBlock) {
        // 代码块结束
        currentBlock.push(line)
        flushBlock()
        inCodeBlock = false
      } else {
        // 代码块开始
        flushBlock()
        inCodeBlock = true
        currentBlock.push(line)
      }
      continue
    }

    if (inCodeBlock) {
      currentBlock.push(line)
      continue
    }

    // 空行 → 分割段落
    if (line.trim() === '') {
      flushBlock()
      continue
    }

    currentBlock.push(line)
  }

  // 刷新最后一段
  if (inCodeBlock) {
    flushBlock()
  } else {
    flushBlock()
  }

  return cards
}

/** 块级标签选择器，按解析优先级排列 */
const BLOCK_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'blockquote', 'figure', 'p']

/**
 * 将 HTML 字符串解析为段落数组。
 * 基于 DOM 解析，比正则更可靠。
 *
 * @param html 编辑器输出的 HTML
 * @returns 结构化段落数组
 */
export function parseHtmlToParagraphs(html: string): ParsedParagraph[] {
  if (!html || !html.trim()) return []

  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const body = doc.body

  const paragraphs: ParsedParagraph[] = []

  let currentTextBuffer: string[] = []

  /** 将累积的纯文本段落推入结果数组 */
  function flushTextBuffer() {
    const text = currentTextBuffer
      .map((s) => s.trim())
      .filter(Boolean)
      .join('\n\n')
    if (text) {
      paragraphs.push({ content: text, type: 'text' })
    }
    currentTextBuffer = []
  }

  // 递归遍历子节点
  function traverse(node: Node) {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.textContent?.trim()
      if (text) {
        currentTextBuffer.push(text)
      }
      return
    }

    if (node.nodeType === Node.ELEMENT_NODE) {
      const el = node as HTMLElement
      const tag = el.tagName.toLowerCase()

      // 处理已知块级标签
      if (BLOCK_TAGS.includes(tag)) {
        flushTextBuffer()

        if (tag === 'pre') {
          // code 段落：取 innerText 去除首尾换行
          const code = el.textContent?.trim() ?? ''
          if (code) {
            paragraphs.push({ content: code, type: 'code' })
          }
          return
        }

        if (tag === 'blockquote') {
          const quote = el.innerHTML.trim()
          if (quote) {
            paragraphs.push({ content: quote, type: 'quote' })
          }
          // blockquote 内部子节点不再单独遍历
          return
        }

        if (tag === 'figure') {
          const img = el.querySelector('img')
          if (img) {
            const src = img.getAttribute('src') ?? ''
            const caption = el.querySelector('figcaption')?.textContent?.trim() ?? ''
            // 将 caption 作为 content，src 作为 media_url
            paragraphs.push({
              content: caption,
              type: 'image',
              media_url: src
            })
          }
          // figure 内部不再遍历
          return
        }

        if (tag.startsWith('h') && tag.length === 2 && /[1-6]/.test(tag[1]!)) {
          const headingText = el.textContent?.trim() ?? ''
          if (headingText) {
            paragraphs.push({
              content: headingText,
              type: 'heading',
              heading: headingText
            })
          }
          return
        }

        // 对于 <p> 以及其他块级标签，遍历其子节点收集文字内容
        if (tag === 'p') {
          currentTextBuffer.push(el.innerHTML.trim())
          return
        }
      }

      // 对于非块级标签（如 <div>、<span> 等）或未匹配的标签，递归遍历子节点
      for (let i = 0; i < node.childNodes.length; i++) {
        traverse(node.childNodes[i]!)
      }
    }
  }

  // 遍历 body 的所有直接子节点
  for (let i = 0; i < body.childNodes.length; i++) {
    traverse(body.childNodes[i]!)
  }

  // 刷新剩余的文本缓冲区
  flushTextBuffer()

  return paragraphs
}
