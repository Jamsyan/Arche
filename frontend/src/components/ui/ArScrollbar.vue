<script setup lang="ts">
/**
 * ArScrollbar — 通用滚动条组件
 *
 * 跨浏览器统一滚动条行为，支持水平/垂直滚动。
 * - 隐藏原生滚动条，渲染自定义轨道 + 滑块
 * - 鼠标滚轮、点击轨道、拖拽滑块均支持
 * - 悬停/滚动时显示，空闲 autoHide 后渐隐
 */
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    /** 固定高度（垂直滚动时需要） */
    height?: string
    /** 固定宽度 */
    width?: string
    /** 是否启用 auto-hide */
    autoHide?: boolean
    /** 是否显示水平滚动条 */
    showHorizontal?: boolean
    /** 是否显示垂直滚动条 */
    showVertical?: boolean
  }>(),
  {
    height: '',
    width: '',
    autoHide: true,
    showHorizontal: true,
    showVertical: false
  }
)

const emit = defineEmits<{
  scroll: [
    info: { scrollLeft: number; scrollTop: number; scrollPercentX: number; scrollPercentY: number }
  ]
}>()

// ── 引用 ──
const wrapperRef = ref<HTMLElement | null>(null)
const contentRef = ref<HTMLElement | null>(null)

// ── 状态 ──
const isVisible = ref(false)
let hideTimer: ReturnType<typeof setTimeout> | null = null

const thumbX = ref(0) // 滑块位置 (%)
const thumbY = ref(0)
const thumbSizeX = ref(20) // 滑块尺寸 (%)
const thumbSizeY = ref(20)
const isDragging = ref<'x' | 'y' | null>(null)

// ── 更新滑块 ──
function updateThumb() {
  const el = contentRef.value
  if (!el) return
  const sw = el.scrollWidth
  const sh = el.scrollHeight
  const cw = el.clientWidth
  const ch = el.clientHeight

  if (props.showHorizontal) {
    thumbSizeX.value = sw > 0 ? Math.max(10, (cw / sw) * 100) : 100
    thumbX.value = sw > cw ? (el.scrollLeft / (sw - cw)) * (100 - thumbSizeX.value) : 0
  }
  if (props.showVertical) {
    thumbSizeY.value = sh > 0 ? Math.max(10, (ch / sh) * 100) : 100
    thumbY.value = sh > ch ? (el.scrollTop / (sh - ch)) * (100 - thumbSizeY.value) : 0
  }

  emit('scroll', {
    scrollLeft: el.scrollLeft,
    scrollTop: el.scrollTop,
    scrollPercentX: sw > cw ? (el.scrollLeft / (sw - cw)) * 100 : 0,
    scrollPercentY: sh > ch ? (el.scrollTop / (sh - ch)) * 100 : 0
  })

  show()
}

// ── 显示/隐藏 ──
function show() {
  if (!props.autoHide) return
  isVisible.value = true
  if (hideTimer) clearTimeout(hideTimer)
  hideTimer = setTimeout(() => {
    if (!isDragging.value) isVisible.value = false
  }, 2000)
}

function keepVisible() {
  if (props.autoHide) isVisible.value = true
}

function hide() {
  if (props.autoHide && !isDragging.value) isVisible.value = false
}

// ── 鼠标滚轮 ──
function onWheel(e: WheelEvent) {
  const el = contentRef.value
  if (!el) return
  e.preventDefault()
  if (props.showHorizontal) {
    el.scrollBy({ left: e.deltaY, behavior: 'smooth' })
  } else if (props.showVertical) {
    el.scrollBy({ top: e.deltaY, behavior: 'smooth' })
  }
}

// ── 点击轨道跳转 ──
function onTrackClick(axis: 'x' | 'y', e: MouseEvent) {
  const el = contentRef.value
  const track = e.currentTarget as HTMLElement
  if (!el || !track) return
  const rect = track.getBoundingClientRect()
  const ratio = (e.clientX - rect.left) / rect.width
  if (axis === 'x') {
    const maxScroll = el.scrollWidth - el.clientWidth
    el.scrollLeft = ratio * maxScroll
  } else {
    const maxScroll = el.scrollHeight - el.clientHeight
    el.scrollTop = ratio * maxScroll
  }
}

// ── 拖拽滑块 ──
function startDrag(axis: 'x' | 'y', e: MouseEvent) {
  e.preventDefault()
  isDragging.value = axis
  const el = contentRef.value
  if (!el) return
  const startPos = axis === 'x' ? e.clientX : e.clientY
  const startScroll = axis === 'x' ? el.scrollLeft : el.scrollTop
  const maxScroll =
    axis === 'x' ? el.scrollWidth - el.clientWidth : el.scrollHeight - el.clientHeight
  const trackSize =
    axis === 'x'
      ? (e.currentTarget as HTMLElement).parentElement!.getBoundingClientRect().width
      : (e.currentTarget as HTMLElement).parentElement!.getBoundingClientRect().height

  function onMove(ev: MouseEvent) {
    const delta = (axis === 'x' ? ev.clientX : ev.clientY) - startPos
    const thumbSize = axis === 'x' ? thumbSizeX.value : thumbSizeY.value
    const thumbW = (thumbSize / 100) * trackSize
    const scrollPerPx = maxScroll / (trackSize - thumbW)
    if (axis === 'x') {
      el!.scrollLeft = startScroll + delta * scrollPerPx
    } else {
      el!.scrollTop = startScroll + delta * scrollPerPx
    }
  }

  function onUp() {
    isDragging.value = null
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }

  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

// ── 生命周期 ──
onMounted(() => {
  const el = contentRef.value
  if (!el) return
  el.addEventListener('scroll', updateThumb, { passive: true })
  updateThumb()
})

onBeforeUnmount(() => {
  if (hideTimer) clearTimeout(hideTimer)
})
</script>

<template>
  <div
    ref="wrapperRef"
    class="ar-scrollbar"
    :class="{ 'ar-scrollbar--auto-hide': autoHide, 'ar-scrollbar--visible': isVisible }"
    :style="{
      height: height || undefined,
      width: width || undefined
    }"
    @mouseenter="keepVisible"
    @mouseleave="hide"
  >
    <!-- 内容容器（原生滚动隐藏） -->
    <div
      ref="contentRef"
      class="ar-scrollbar__content"
      :class="{
        'ar-scrollbar__content--scroll-x': showHorizontal,
        'ar-scrollbar__content--scroll-y': showVertical
      }"
      @wheel="onWheel"
    >
      <slot />
    </div>

    <!-- 水平滚动条 -->
    <div
      v-if="showHorizontal"
      class="ar-scrollbar__track ar-scrollbar__track--x"
      :class="{ 'ar-scrollbar__track--active': isVisible }"
      @click="onTrackClick('x', $event)"
    >
      <div
        class="ar-scrollbar__thumb ar-scrollbar__thumb--x"
        :class="{ 'ar-scrollbar__thumb--dragging': isDragging === 'x' }"
        :style="{ width: thumbSizeX + '%', left: thumbX + '%' }"
        @mousedown.stop="startDrag('x', $event)"
      />
    </div>

    <!-- 垂直滚动条 -->
    <div
      v-if="showVertical"
      class="ar-scrollbar__track ar-scrollbar__track--y"
      :class="{ 'ar-scrollbar__track--active': isVisible }"
      @click="onTrackClick('y', $event)"
    >
      <div
        class="ar-scrollbar__thumb ar-scrollbar__thumb--y"
        :class="{ 'ar-scrollbar__thumb--dragging': isDragging === 'y' }"
        :style="{ height: thumbSizeY + '%', top: thumbY + '%' }"
        @mousedown.stop="startDrag('y', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
.ar-scrollbar {
  position: relative;
  overflow: hidden;
}

/* ── 内容容器 ── */
.ar-scrollbar__content {
  overflow: hidden;
  scroll-behavior: smooth;
}

.ar-scrollbar__content--scroll-x {
  overflow-x: auto;
  overflow-y: hidden;
}

.ar-scrollbar__content--scroll-y {
  overflow-x: hidden;
  overflow-y: auto;
}

/* 隐藏原生滚动条 */
.ar-scrollbar__content::-webkit-scrollbar {
  width: 0;
  height: 0;
}

.ar-scrollbar__content {
  scrollbar-width: none;
}

/* ── 轨道 ── */
.ar-scrollbar__track {
  position: absolute;
  background: var(--border-color);
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.25s ease;
  cursor: pointer;
}

.ar-scrollbar__track--active {
  opacity: 1;
}

.ar-scrollbar__track--x {
  bottom: 4px;
  left: 4px;
  right: 4px;
  height: 6px;
}

.ar-scrollbar__track--y {
  top: 4px;
  right: 4px;
  bottom: 4px;
  width: 6px;
}

/* ── 滑块 ── */
.ar-scrollbar__thumb {
  position: absolute;
  background: var(--primary-color);
  border-radius: inherit;
  cursor: grab;
  opacity: 0.7;
  transition:
    opacity 0.2s ease,
    height 0.15s ease,
    width 0.15s ease;
  min-width: 20px;
  min-height: 20px;
}

.ar-scrollbar__thumb--dragging,
.ar-scrollbar__thumb:hover {
  opacity: 1;
}

.ar-scrollbar__thumb--x {
  top: 0;
  height: 100%;
}

.ar-scrollbar__thumb--y {
  left: 0;
  width: 100%;
}

/* ── auto-hide ── */
.ar-scrollbar--auto-hide .ar-scrollbar__track {
  opacity: 0;
}

.ar-scrollbar--auto-hide.ar-scrollbar--visible .ar-scrollbar__track {
  opacity: 1;
}

/* ── 深色模式 ── */
:global(.dark) .ar-scrollbar__track {
  background: rgba(230, 225, 218, 0.1);
}
</style>
