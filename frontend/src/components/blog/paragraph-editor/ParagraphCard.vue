<template>
  <div
    class="paragraph-card"
    :class="[`card--${card.type}`, { 'card--focused': isFocused }]"
  >
    <div class="card-body">
      <div class="card-main">
        <!-- 顶栏：类型选择 + 操作按钮 -->
        <div class="card-toolbar">
          <div class="card-toolbar-left">
            <select class="card-type-select" :value="card.type" @change="onTypeChange">
              <option v-for="ct in cardTypes" :key="ct.type" :value="ct.type">
                {{ ct.label }}
              </option>
            </select>
          </div>
          <div class="card-toolbar-right">
            <button class="card-btn" title="上移" @click="$emit('move', index, index - 1)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="18 15 12 9 6 15" />
              </svg>
            </button>
            <button class="card-btn" title="下移" @click="$emit('move', index, index + 1)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>
            <button class="card-btn" title="上方插入" @click="$emit('insert', index)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
            </button>
            <button class="card-btn card-btn--danger" title="删除" @click="$emit('delete', index)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 内容编辑区 -->
        <div
          ref="contentRef"
          class="card-content"
          :class="{ 'card-content--empty': !card.content }"
          :contenteditable="true"
          :placeholder="placeholderText"
          @input="onContentInput"
          @focus="isFocused = true"
          @blur="isFocused = false"
          v-html="renderedContent"
        />
      </div>

      <!-- 右侧拖拽把手 -->
      <div class="card-drag-handle" title="拖拽排序">
        <span class="drag-dot" />
        <span class="drag-dot" />
        <span class="drag-dot" />
        <span class="drag-dot" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { CardData, CardType } from '@/utils/paragraph'
import { CARD_TYPES } from '@/utils/paragraph'

const props = defineProps<{
  card: CardData
  index: number
}>()

const emit = defineEmits<{
  update: [index: number, data: Partial<CardData>]
  move: [from: number, to: number]
  insert: [afterIndex: number]
  delete: [index: number]
}>()

const cardTypes = CARD_TYPES
const isFocused = ref(false)
const contentRef = ref<HTMLDivElement>()

const placeholderText = computed(() => {
  const map: Record<string, string> = {
    text: '输入正文内容…',
    quote: '输入引用内容…',
    code: '输入代码…',
    image: '输入图片 Markdown 或 URL…'
  }
  return map[props.card.type] || '输入内容…'
})

/** 渲染内容：code 类型显示纯文本，image 类型显示图片预览，其余显示 HTML */
const renderedContent = computed(() => {
  const { type, content } = props.card
  if (!content) return ''

  if (type === 'code') {
    return escapeHtml(content)
  }
  if (type === 'image') {
    const match = content.match(/!\[.*?\]\((.*?)\)/)
    if (match) {
      return `<div class="image-preview"><img src="${escapeHtml(match[1]!)}" alt="" /><div class="image-caption">${escapeHtml(content)}</div></div>`
    }
    return escapeHtml(content)
  }
  return content
})

function onTypeChange(e: Event) {
  const val = (e.target as HTMLSelectElement).value as CardType
  emit('update', props.index, { type: val })
}

function onContentInput(e: Event) {
  const el = e.target as HTMLDivElement
  const content = el.innerHTML
  emit('update', props.index, { content })
}

function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
</script>

<style scoped>
.paragraph-card {
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 8px;
  background: var(--bg-color, #fff);
  overflow: hidden;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.paragraph-card:hover {
  border-color: var(--border-hover, #c8c6c4);
}

.paragraph-card.card--focused {
  border-color: var(--primary-color, #7c3aed);
  box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.1);
}

/* ── 卡片主体：内容区 + 右侧拖拽把手 ── */

.card-body {
  display: flex;
  align-items: stretch;
}

.card-main {
  flex: 1;
  min-width: 0;
}

/* ── 类型特殊样式 ── */

.card--quote {
  border-left: 3px solid var(--quote-border, #7c3aed);
}

.card--quote .card-content {
  color: var(--quote-color, #555);
  font-style: italic;
  padding-left: 12px;
}

.card--code {
  background: var(--code-bg, #1a1a1a);
  border-color: var(--code-border, #333);
}

.card--code .card-content {
  font-family: 'Cascadia Code', 'Fira Code', monospace;
  font-size: 0.875rem;
  color: var(--code-color, #e0e0e0);
  white-space: pre;
}

/* ── 工具栏 ── */

.card-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  background: var(--toolbar-bg, #fafafa);
  border-bottom: 1px solid var(--border-color, #e8e6e4);
  user-select: none;
}

.card-toolbar-left,
.card-toolbar-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-type-select {
  font-size: 0.75rem;
  padding: 2px 6px;
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 4px;
  background: var(--bg-color, #fff);
  color: var(--text-color, #333);
  cursor: pointer;
  outline: none;
}

.card-type-select:focus {
  border-color: var(--primary-color, #7c3aed);
}

.card-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-muted, #999);
  cursor: pointer;
  transition:
    background 0.15s,
    color 0.15s;
}

.card-btn:hover {
  background: var(--hover-bg, #f0f0f0);
  color: var(--text-color, #333);
}

.card-btn--danger:hover {
  background: var(--danger-bg, #fef2f2);
  color: var(--danger-color, #ef4444);
}

/* ── 内容区 ── */

.card-content {
  min-height: 48px;
  padding: 12px 16px;
  font-size: 0.9375rem;
  line-height: 1.7;
  color: var(--text-color, #333);
  outline: none;
  word-break: break-word;
}

.card-content--empty::before {
  content: attr(placeholder);
  color: var(--placeholder-color, #bbb);
  pointer-events: none;
}

/* 图片预览 */
:deep(.image-preview) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

:deep(.image-preview img) {
  max-width: 100%;
  max-height: 240px;
  border-radius: 4px;
  object-fit: contain;
  background: var(--image-bg, #f0f0f0);
}

:deep(.image-caption) {
  font-size: 0.8125rem;
  color: var(--text-muted, #999);
}

/* ── 右侧拖拽把手 ── */

.card-drag-handle {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 24px;
  cursor: grab;
  background: var(--toolbar-bg, #fafafa);
  border-left: 1px solid var(--border-color, #e8e6e4);
  transition: background 0.15s;
  flex-shrink: 0;
}

.card-drag-handle:hover {
  background: var(--hover-bg, #f0f0f0);
}

.card-drag-handle:active {
  cursor: grabbing;
}

.drag-dot {
  display: block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--text-muted, #bbb);
  transition: background 0.15s;
}

.card-drag-handle:hover .drag-dot {
  background: var(--text-secondary, #666);
}
</style>
