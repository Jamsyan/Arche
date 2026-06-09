<script setup lang="ts">
/**
 * WatchHistoryStack — 继续观看 · Peek 布局
 *
 * 一张主卡完整展示，下一张从右侧露出封面一角。
 * 点击箭头切换，主卡滑出、下一张滑入成为新主卡。
 */
import { computed, ref } from 'vue'
import type { BlogPost } from '@/services/api'
import PostCard from './PostCard.vue'

export interface WatchHistoryItem {
  post: BlogPost
  progress?: number
  lastReadAt?: string
}

const props = withDefaults(
  defineProps<{
    items: WatchHistoryItem[]
  }>(),
  {}
)

const emit = defineEmits<{
  open: [item: WatchHistoryItem]
}>()

const dedupedItems = computed(() => {
  const seen = new Set<string>()
  return props.items.filter((item) => {
    if (seen.has(item.post.id)) return false
    seen.add(item.post.id)
    return true
  })
})

const CARD_W = 260
const PEEK = 56

const focusIndex = ref(0)
const maxFocus = computed(() => Math.max(0, dedupedItems.value.length - 1))

function goPrev() {
  focusIndex.value = Math.max(0, focusIndex.value - 1)
}

function goNext() {
  focusIndex.value = Math.min(maxFocus.value, focusIndex.value + 1)
}

function cardTranslate(index: number): string {
  const focus = focusIndex.value
  if (index === focus) return 'translateX(0)'
  if (index === focus - 1) return `translateX(-${CARD_W - PEEK}px)`
  if (index === focus + 1) return `translateX(${CARD_W - PEEK}px)`
  return `translateX(${index < focus ? -CARD_W : CARD_W}px)`
}

function isCardVisible(index: number): boolean {
  return Math.abs(index - focusIndex.value) <= 1
}

function estimateDuration(post: BlogPost): string {
  const text = post.content || ''
  const len = text.replace(/<[^>]+>/g, '').length
  const mins = Math.max(1, Math.ceil(len / 300))
  return `${mins} 分钟`
}

function cardZIndex(index: number): number {
  return index === focusIndex.value ? 2 : 1
}
</script>

<template>
  <section class="watch-history">
    <div class="section-head">
      <div class="section-title-group">
        <span class="section-icon">&#9654;</span>
        <h3 class="section-title">继续观看</h3>
      </div>
      <div class="section-actions">
        <span class="section-hint">{{ dedupedItems.length }} 个未读完</span>
        <button class="nav-btn" :disabled="focusIndex <= 0" @click="goPrev" aria-label="上一张">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path
              d="M15 18L9 12L15 6"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
        <button
          class="nav-btn"
          :disabled="focusIndex >= maxFocus"
          @click="goNext"
          aria-label="下一张"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path
              d="M9 18L15 12L9 6"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>

    <div class="peek-viewport">
      <div class="peek-track">
        <div
          v-for="(item, index) in dedupedItems"
          :key="item.post.id"
          v-show="isCardVisible(index)"
          class="peek-card"
          :style="{
            transform: cardTranslate(index),
            zIndex: cardZIndex(index)
          }"
          @click="emit('open', item)"
        >
          <PostCard
            mode="cover"
            :post="item.post"
            :meta-progress="item.progress"
            :meta-duration="estimateDuration(item.post)"
          />
        </div>
      </div>
      <div class="edge-peek"></div>
    </div>
  </section>
</template>

<style scoped>
.watch-history {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  user-select: none;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2px;
}

.section-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  font-size: 10px;
  color: var(--primary-color);
  opacity: 0.7;
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-right: 4px;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-color);
  background: var(--surface-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.nav-btn:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
  background: var(--primary-light-color);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.peek-viewport {
  position: relative;
  overflow: hidden;
  height: 190px;
}

.peek-track {
  position: relative;
  height: 170px;
  top: 10px;
}

.peek-card {
  position: absolute;
  left: 0;
  top: 0;
  width: 260px;
  height: 170px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  box-shadow:
    0 4px 16px -6px rgba(26, 24, 23, 0.15),
    0 1px 4px -2px rgba(26, 24, 23, 0.08);
  transition:
    transform 0.4s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.3s ease;
}

.peek-card:hover {
  box-shadow:
    0 0 0 2px var(--primary-color),
    0 4px 16px -6px rgba(26, 24, 23, 0.15),
    0 1px 4px -2px rgba(26, 24, 23, 0.08);
}

.edge-peek {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 60px;
  pointer-events: none;
  z-index: 3;
  background: linear-gradient(to right, transparent, var(--bg-color) 85%);
}

:global(.dark) .peek-card:hover {
  box-shadow:
    0 0 0 2px var(--primary-color),
    0 4px 16px -6px rgba(0, 0, 0, 0.45),
    0 1px 4px -2px rgba(0, 0, 0, 0.25);
}
</style>
