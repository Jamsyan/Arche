<script setup lang="ts">
/**
 * ArWheelPicker — 横向滚轮选择器
 *
 * iOS 风格的水平滚轮选择器，支持：
 * - 滚轮逐项切换 + 平滑动画
 * - 拖拽释放后惯性动量减速
 * - 循环滚动（复制渲染，视觉无限）
 * - 实时选中（滚到哪选到哪）
 * - 3D 圆柱透视（中间大、两边小、渐隐）
 * - 鼠标拖拽 + 滚轮 + 点击选中
 * - 自动吸附到最近项
 */
import { computed, onMounted, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    options: string[]
    modelValue: string
    title?: string
  }>(),
  { title: '' }
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const viewportRef = ref<HTMLElement | null>(null)

// 3 份复制实现视觉循环滚动
const displayOptions = computed(() => [...props.options, ...props.options, ...props.options])

// ── 拖拽状态 ──
let isDragging = false
let dragStartX = 0
let dragStartScroll = 0
let dragLastX = 0
let dragVelocity = 0

// ── 动量状态（仅拖拽释放后） ──
let momentum = 0
let momentumRaf: number | null = null

const FRICTION = 0.9
const VELOCITY_THRESHOLD = 0.5
let transformTick = false

// ── 内部变更守卫 ──
// 当组件内部（滚动动画中）emit 值时设为 true，
// 防止 watch 回调又调 scrollTo 形成回路
let internalChange = false
let changeTimer: ReturnType<typeof setTimeout> | null = null

const markInternal = () => {
  internalChange = true
  if (changeTimer) clearTimeout(changeTimer)
  changeTimer = setTimeout(() => {
    internalChange = false
  }, 500)
}

/** 滚动到指定选项（总是定位到中间那份拷贝） */
const scrollTo = (value: string, behavior: 'auto' | 'smooth' | 'instant' = 'smooth') => {
  const el = viewportRef.value
  if (!el) return
  const items = [...el.querySelectorAll<HTMLElement>(`[data-value="${value}"]`)]
  if (items.length === 0) return
  // 选中间那份拷贝，确保视觉上居中
  const target = items[Math.floor(items.length / 2)]
  target.scrollIntoView({ behavior, inline: 'center', block: 'nearest' })
}

/** 吸附到最近选项（动量结束后调用） */
const snapToClosest = () => {
  const el = viewportRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  let closest: HTMLElement | null = null
  let closestDist = Infinity
  for (const item of el.querySelectorAll<HTMLElement>('[data-value]')) {
    const r = item.getBoundingClientRect()
    const dist = Math.abs(r.left + r.width / 2 - centerX)
    if (dist < closestDist) {
      closestDist = dist
      closest = item
    }
  }
  if (closest) {
    const val = closest.dataset.value
    if (val && val !== props.modelValue) {
      markInternal()
      emit('update:modelValue', val)
    }
    scrollTo(val ?? props.modelValue, 'smooth')
  }
}

/** 动量惯性循环（仅在拖拽释放后调用） */
const applyMomentum = () => {
  if (momentumRaf) cancelAnimationFrame(momentumRaf)
  const step = () => {
    if (Math.abs(momentum) < VELOCITY_THRESHOLD) {
      momentum = 0
      snapToClosest()
      return
    }
    if (viewportRef.value) viewportRef.value.scrollLeft += momentum
    momentum *= FRICTION
    momentumRaf = requestAnimationFrame(step)
  }
  step()
}

/** 更新 3D 透视变换（根据距中心距离缩放 + 渐隐） */
const updateTransforms = () => {
  const el = viewportRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const items = el.querySelectorAll<HTMLElement>('.ar-wheel-picker__item')
  let closest: HTMLElement | null = null
  let closestDist = Infinity

  items.forEach((item) => {
    const r = item.getBoundingClientRect()
    const itemCenter = r.left + r.width / 2
    const dist = Math.abs(itemCenter - centerX)
    const maxDist = rect.width / 2 + 30
    const t = Math.min(dist / maxDist, 1)
    const scale = 1 - t * 0.28
    const opacity = 1 - t * 0.55
    item.style.transform = `scale(${Math.max(scale, 0.72)})`
    item.style.opacity = String(Math.max(opacity, 0.45))
    if (dist < closestDist) {
      closestDist = dist
      closest = item
    }
  })

  // 实时选中：非内部变更期间，最近项直接高亮
  if (closest && !internalChange) {
    const val = closest.dataset.value
    if (val && val !== props.modelValue) {
      markInternal()
      emit('update:modelValue', val)
    }
  }
}

// ── 事件处理 ──

const onWheel = (e: WheelEvent) => {
  e.preventDefault()
  const idx = props.options.indexOf(props.modelValue)
  if (idx === -1) return
  const dir = e.deltaY > 0 ? 1 : -1
  const len = props.options.length
  const next = (((idx + dir) % len) + len) % len
  const target = props.options[next]
  // 立即 emit + 标记内部变更，阻止动画过程中的 updateTransforms 覆盖
  if (target !== props.modelValue) {
    markInternal()
    emit('update:modelValue', target)
  }
  scrollTo(target, 'smooth')
}

const onScroll = () => {
  if (!transformTick) {
    requestAnimationFrame(() => {
      updateTransforms()
      transformTick = false
    })
    transformTick = true
  }
}

const onDragStart = (e: MouseEvent) => {
  isDragging = true
  dragStartX = e.clientX
  dragStartScroll = viewportRef.value?.scrollLeft ?? 0
  dragLastX = e.clientX
  dragVelocity = 0
}

const onDragMove = (e: MouseEvent) => {
  if (!isDragging) return
  const dx = e.clientX - dragLastX
  dragVelocity = dx
  dragLastX = e.clientX
  if (viewportRef.value) {
    viewportRef.value.scrollLeft = dragStartScroll - (e.clientX - dragStartX)
  }
}

const onDragEnd = () => {
  if (!isDragging) return
  isDragging = false
  if (Math.abs(dragVelocity) > 1) {
    momentum = -dragVelocity * 1.5
    applyMomentum()
  } else {
    snapToClosest()
  }
}

const onItemClick = (value: string) => {
  if (value === props.modelValue) return
  markInternal()
  emit('update:modelValue', value)
  scrollTo(value, 'smooth')
}

// ── 生命周期 ──

/** 确保挂载后滚动到当前选中项 */
const ensureScrollToValue = () => {
  const el = viewportRef.value
  if (!el) return
  requestAnimationFrame(() => {
    scrollTo(props.modelValue, 'instant')
    requestAnimationFrame(() => updateTransforms())
  })
}

watch(viewportRef, (el) => {
  if (el) ensureScrollToValue()
})

onMounted(() => {
  if (viewportRef.value) ensureScrollToValue()
})

watch(
  () => props.modelValue,
  (val) => {
    if (internalChange) return
    scrollTo(val, 'smooth')
  }
)
</script>

<template>
  <div class="ar-wheel-picker" :title="title">
    <div
      ref="viewportRef"
      class="ar-wheel-picker__viewport"
      @wheel.prevent="onWheel"
      @scroll="onScroll"
      @mousedown="onDragStart"
      @mousemove="onDragMove"
      @mouseup="onDragEnd"
      @mouseleave="onDragEnd"
    >
      <div class="ar-wheel-picker__track">
        <div
          v-for="(opt, i) in displayOptions"
          :key="`${i}-${opt}`"
          class="ar-wheel-picker__item"
          :class="{ active: opt === modelValue }"
          :data-value="opt"
          @click="onItemClick(opt)"
        >
          <slot name="item" :option="opt" :active="opt === modelValue">
            {{ opt }}
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ar-wheel-picker {
  position: relative;
  width: 170px;
  height: 36px;
}

.ar-wheel-picker__viewport {
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
  cursor: grab;
  -webkit-overflow-scrolling: touch;
}

.ar-wheel-picker__viewport::-webkit-scrollbar {
  display: none;
}

.ar-wheel-picker__viewport:active {
  cursor: grabbing;
}

.ar-wheel-picker__track {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 calc(50% - 18px);
  gap: 4px;
}

.ar-wheel-picker__item {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: var(--font-weight-semibold);
  background: var(--bg-color);
  border: 1.5px solid var(--border-color);
  color: var(--text-tertiary);
  transition:
    transform 0.08s ease,
    opacity 0.08s ease;
  cursor: pointer;
  user-select: none;
  transform: scale(0.72);
  opacity: 0.45;
}

.ar-wheel-picker__item.active {
  transform: scale(1);
  opacity: 1;
  background: var(--primary-color);
  color: #fff;
  border: 2px solid #fff;
  box-shadow:
    0 0 0 1.5px var(--primary-color),
    0 2px 6px rgba(0, 0, 0, 0.12);
}

.ar-wheel-picker__item:hover:not(.active) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}
</style>
