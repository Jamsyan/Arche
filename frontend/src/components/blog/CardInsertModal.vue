<template>
  <div v-if="visible" class="card-insert-overlay" @click.self="$emit('close')">
    <div class="card-insert-modal">
      <div class="card-insert-header">
        <span class="card-insert-title">选择卡片类型</span>
        <button class="card-insert-close" @click="$emit('close')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
      <div class="card-insert-grid">
        <button
          v-for="ct in cardTypes"
          :key="ct.type"
          class="card-insert-option"
          @click="$emit('select', ct.type)"
        >
          <div class="card-insert-icon">
            <svg v-if="ct.type === 'text'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
              <line x1="3" y1="14" x2="21" y2="14" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
            <svg v-else-if="ct.type === 'quote'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z" />
              <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z" />
            </svg>
            <svg v-else-if="ct.type === 'code'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <polyline points="16 18 22 12 16 6" />
              <polyline points="8 6 2 12 8 18" />
            </svg>
            <svg v-else-if="ct.type === 'image'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
          </div>
          <span class="card-insert-label">{{ ct.label }}</span>
          <span class="card-insert-desc">{{ typeDescriptions[ct.type] }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CARD_TYPES } from '@/utils/paragraph'
import type { CardType } from '@/utils/paragraph'

defineProps<{
  visible: boolean
}>()

defineEmits<{
  select: [type: CardType]
  close: []
}>()

const cardTypes = CARD_TYPES

const typeDescriptions: Record<string, string> = {
  text: '普通正文段落',
  quote: '引用块，左侧有竖线标记',
  code: '代码块，等宽字体深色背景',
  image: '插入图片'
}
</script>

<style scoped>
.card-insert-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.card-insert-modal {
  background: var(--surface-color, #fff);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  width: 480px;
  max-width: 90vw;
  overflow: hidden;
}

.card-insert-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color, #e8e6e4);
}

.card-insert-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color, #333);
}

.card-insert-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-muted, #999);
  cursor: pointer;
  transition: all 0.15s;
}

.card-insert-close:hover {
  background: var(--hover-bg, #f5f5f5);
  color: var(--text-color, #333);
}

.card-insert-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 20px;
}

.card-insert-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 12px;
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 10px;
  background: var(--bg-color, #fff);
  cursor: pointer;
  transition: all 0.15s;
}

.card-insert-option:hover {
  border-color: var(--primary-color, #7c3aed);
  background: var(--primary-light-bg, #f5f3ff);
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.08);
}

.card-insert-icon {
  color: var(--primary-color, #7c3aed);
}

.card-insert-label {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-color, #333);
}

.card-insert-desc {
  font-size: 0.75rem;
  color: var(--text-tertiary, #999);
  text-align: center;
}
</style>
