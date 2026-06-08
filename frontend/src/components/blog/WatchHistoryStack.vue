<script setup lang="ts">
import { ref } from 'vue'
import type { BlogPost } from '@/services/api'

export interface WatchHistoryItem {
  post: BlogPost
  progress?: number
  lastReadAt?: string
}

const props = withDefaults(
  defineProps<{
    items: WatchHistoryItem[]
    direction?: 'ltr' | 'rtl'
  }>(),
  { direction: 'ltr' }
)

const emit = defineEmits<{
  open: [item: WatchHistoryItem]
}>()

const hoveredIndex = ref<number | null>(null)

const VISIBLE = 56 // visible width per card before next card starts
const BLUR_END = 4 // last N cards start blurring

function getCardStyle(index: number) {
  const total = props.items.length
  const isHovered = hoveredIndex.value === index
  const dist = hoveredIndex.value !== null ? Math.abs(hoveredIndex.value - index) : 99
  const isNear = dist >= 1 && dist <= 2

  // Base horizontal offset
  let offsetX = index * VISIBLE
  if (props.direction === 'rtl') {
    offsetX = -(total - 1 - index) * VISIBLE
  }

  // Vertical lift & scale
  let translateY = 0
  let scale = 1
  const zIndex = isHovered ? total + 1 : isNear ? total : index

  if (isHovered) {
    translateY = -28
    scale = 1.18
  } else if (isNear) {
    translateY = -10
    scale = 1.05
  }

  // Edge blur → cards at the far end visually dissolve
  const fromEnd = props.direction === 'rtl' ? index : total - 1 - index
  let filter = 'none'
  let opacity = 1

  if (fromEnd < BLUR_END && !isHovered) {
    const t = 1 - fromEnd / BLUR_END // 0 → 1
    filter = `blur(${t * 3}px)`
    opacity = 1 - t * 0.35
  }

  return {
    transform: `translateX(${offsetX}px) translateY(${translateY}px) scale(${scale})`,
    zIndex,
    filter,
    opacity
  }
}

// Dynamic gradient pair for placeholder covers
const gradientPool = [
  ['#f2dfc7', '#dcbca0'],
  ['#d9c8b0', '#9f8169'],
  ['#e8d7bf', '#c0a688'],
  ['#d0c2b1', '#8f7560'],
  ['#c4b5a0', '#7d6855']
] as const

function placeholderGradient(index: number) {
  const [a, b] = gradientPool[index % gradientPool.length]
  return `linear-gradient(135deg, ${a}, ${b})`
}
</script>

<template>
  <section class="watch-history" :class="`dir-${direction}`">
    <div class="section-head">
      <h3 class="section-title">继续观看</h3>
    </div>
    <div class="stack-viewport" @mouseleave="hoveredIndex = null">
      <div class="stack-track">
        <div
          v-for="(item, index) in items"
          :key="item.post.id"
          class="stack-card"
          :style="getCardStyle(index)"
          @mouseenter="hoveredIndex = index"
          @click="emit('open', item)"
        >
          <div
            class="card-cover"
            :style="{
              backgroundImage: item.post.cover_url
                ? `url(${item.post.cover_url})`
                : placeholderGradient(index)
            }"
          />
          <div class="card-body">
            <span class="card-title">{{ item.post.title }}</span>
            <span class="card-meta">
              {{ item.progress != null ? `已读 ${item.progress}%` : '未读' }}
              <template v-if="item.lastReadAt"> · {{ item.lastReadAt }} </template>
            </span>
          </div>
        </div>
      </div>

      <!-- Edge fade mask -->
      <div class="edge-mask" :class="direction === 'rtl' ? 'mask-left' : 'mask-right'" />
    </div>
  </section>
</template>

<style scoped>
.watch-history {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.section-head h3 {
  margin: 0;
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

/* ── Viewport clips overflow ── */
.stack-viewport {
  position: relative;
  overflow: hidden;
  height: 180px; /* 130px card + 50px hover lift room */
}

.stack-track {
  position: relative;
  height: 130px;
  top: 12px; /* vertical centering offset */
}

/* ── Individual card ── */
.stack-card {
  position: absolute;
  left: 0;
  top: 0;
  width: 180px;
  height: 130px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--surface-color);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  cursor: pointer;
  transition:
    transform 0.32s var(--ease-out-spring),
    filter 0.3s ease,
    opacity 0.3s ease,
    box-shadow 0.25s ease;
}

.stack-card:hover {
  box-shadow: var(--shadow-lg);
}

.card-cover {
  width: 100%;
  height: 70px;
  background-size: cover;
  background-position: center;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 6px 10px 8px;
}

.card-title {
  font-size: 12px;
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  font-size: 11px;
  color: var(--text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Edge fade mask ── */
.edge-mask {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 80px;
  pointer-events: none;
  z-index: 1;
}

.mask-right {
  right: 0;
  background: linear-gradient(to right, transparent, var(--bg-color) 85%);
}

.mask-left {
  left: 0;
  background: linear-gradient(to left, transparent, var(--bg-color) 85%);
}
</style>
