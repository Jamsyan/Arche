<script setup lang="ts">
/**
 * ArWheelPicker — 横向滚轮选择器
 *
 * 物理引擎驱动的 iOS 风格滚轮选择器：
 * - 连续速度模型，非离散跳转
 * - 摩擦力减速 + 惯性动量
 * - CSS translateX 控制位置，RAF 驱动
 * - 3 份拷贝 + 边界复位实现无限循环
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

// 每项宽度 = 36px + 4px gap
const ITEM_STEP = 40

// 3 份复制实现视觉循环滚动
const displayOptions = computed(() => [...props.options, ...props.options, ...props.options])

// ── 物理引擎状态 ──
let offsetX = 0
let velocity = 0
let physicsRaf: number | null = null

// 物理常量
const FRICTION = 0.88 // 每帧速度衰减
const VELOCITY_THRESHOLD = 0.3 // 停止阈值
const WHEEL_IMPULSE = 18 // 滚轮每 tick 施加的速度
const DRAG_VELOCITY_SCALE = 1.2 // 拖拽释放后速度倍率
const DRAG_VELOCITY_THRESHOLD = 2 // 拖拽触发惯性的最小速度

// ── 内部变更守卫 ──
let internalChange = false
let changeTimer: ReturnType<typeof setTimeout> | null = null

const markInternal = () => {
  internalChange = true
  if (changeTimer) clearTimeout(changeTimer)
  changeTimer = setTimeout(() => {
    internalChange = false
  }, 100)
}

// ── 工具函数 ──

const getTrack = (): HTMLElement | null =>
  (viewportRef.value?.querySelector('.ar-wheel-picker__track') as HTMLElement) ?? null

const applyOffset = () => {
  const track = getTrack()
  if (track) track.style.transform = `translateX(${offsetX}px)`
}

/** 当前居中项在 3 份拷贝数组中的索引 */
const getVirtualIndex = (): number => {
  const el = viewportRef.value
  if (!el) return props.options.length
  return Math.round((el.offsetWidth / 2 - offsetX - 18) / ITEM_STEP)
}

/** 居中指定索引所需的 offset */
const getOffsetForIndex = (vi: number): number => {
  const el = viewportRef.value
  if (!el) return 0
  return el.offsetWidth / 2 - (vi * ITEM_STEP + 18)
}

/** 边界复位：进入第 1 份或第 3 份拷贝时立即跳回中间份 */
const checkBoundary = () => {
  const vi = getVirtualIndex()
  const len = props.options.length
  if (vi < len) {
    offsetX -= len * ITEM_STEP
    applyOffset()
  } else if (vi >= len * 2) {
    offsetX += len * ITEM_STEP
    applyOffset()
  }
}

/** 发射当前居中项 */
const emitCurrentValue = () => {
  if (internalChange) return
  const vi = getVirtualIndex()
  const len = props.options.length
  const idx = ((vi % len) + len) % len
  const val = props.options[idx]
  if (val && val !== props.modelValue) {
    markInternal()
    emit('update:modelValue', val)
  }
}

/** 吸附到最近的网格位置 */
const snapToClosest = () => {
  const vi = getVirtualIndex()
  offsetX = getOffsetForIndex(vi)
  applyOffset()
  checkBoundary()
  updateTransforms()
  emitCurrentValue()
}

// ── 物理引擎主循环 ──

const stopPhysics = () => {
  if (physicsRaf !== null) {
    cancelAnimationFrame(physicsRaf)
    physicsRaf = null
  }
}

const startPhysics = () => {
  if (physicsRaf) return
  const step = () => {
    const nearZero = Math.abs(velocity) < VELOCITY_THRESHOLD
    if (nearZero && isAtGrid()) {
      velocity = 0
      physicsRaf = null
      snapToClosest()
      return
    }

    offsetX += velocity
    velocity *= FRICTION
    // 防止微小速度震荡
    if (Math.abs(velocity) < VELOCITY_THRESHOLD && !nearZero) {
      velocity = 0
    }

    applyOffset()
    checkBoundary()
    updateTransforms()
    physicsRaf = requestAnimationFrame(step)
  }
  step()
}

const isAtGrid = (): boolean => {
  const vi = getVirtualIndex()
  const snapOffset = getOffsetForIndex(vi)
  return Math.abs(offsetX - snapOffset) < 0.5
}

// ── 滚轮事件 ──
const onWheel = (e: WheelEvent) => {
  e.preventDefault()
  velocity += Math.sign(e.deltaY) * WHEEL_IMPULSE
  startPhysics()
}

// ── 拖拽 ──
let isDragging = false
let dragStartX = 0
let dragStartOffset = 0
let dragLastX = 0
let dragVelocity = 0

const onDragStart = (e: MouseEvent) => {
  isDragging = true
  dragStartX = e.clientX
  dragStartOffset = offsetX
  dragLastX = e.clientX
  dragVelocity = 0
  stopPhysics()
  document.addEventListener('mousemove', onDragMove)
  document.addEventListener('mouseup', onDragEnd)
}

const onDragMove = (e: MouseEvent) => {
  if (!isDragging) return
  const dx = e.clientX - dragLastX
  dragVelocity = dx
  dragLastX = e.clientX
  offsetX = dragStartOffset + (e.clientX - dragStartX)
  applyOffset()
  updateTransforms()
}

const onDragEnd = () => {
  document.removeEventListener('mousemove', onDragMove)
  document.removeEventListener('mouseup', onDragEnd)
  if (!isDragging) return
  isDragging = false
  if (Math.abs(dragVelocity) > DRAG_VELOCITY_THRESHOLD) {
    velocity = -dragVelocity * DRAG_VELOCITY_SCALE
    startPhysics()
  } else {
    snapToClosest()
  }
}

// ── 点击选中（传实际索引确保正确方向） ──
const onItemClick = (value: string, vi: number) => {
  if (value === props.modelValue) return
  stopPhysics()
  offsetX = getOffsetForIndex(vi)
  markInternal()
  emit('update:modelValue', value)
  applyOffset()
  checkBoundary()
  updateTransforms()
}

// ── 3D 透视变换 ──
const updateTransforms = () => {
  const el = viewportRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const items = el.querySelectorAll<HTMLElement>('.ar-wheel-picker__item')

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
  })
}

// ── 生命周期 ──

const initToValue = (value: string) => {
  const len = props.options.length
  const idx = props.options.indexOf(value)
  if (idx === -1) return
  const vi = len + idx
  offsetX = getOffsetForIndex(vi)
  applyOffset()
  requestAnimationFrame(() => updateTransforms())
}

watch(viewportRef, (el) => {
  if (el) initToValue(props.modelValue)
})

onMounted(() => {
  if (viewportRef.value) initToValue(props.modelValue)
})

watch(
  () => props.modelValue,
  (val) => {
    if (internalChange) return
    const len = props.options.length
    const idx = props.options.indexOf(val)
    if (idx === -1) return
    const vi = len + idx
    offsetX = getOffsetForIndex(vi)
    applyOffset()
    checkBoundary()
    updateTransforms()
  }
)
</script>

<template>
  <div class="ar-wheel-picker" :title="title">
    <div
      ref="viewportRef"
      class="ar-wheel-picker__viewport"
      @wheel.prevent="onWheel"
      @mousedown="onDragStart"
    >
      <div class="ar-wheel-picker__track">
        <div
          v-for="(opt, i) in displayOptions"
          :key="`${i}-${opt}`"
          class="ar-wheel-picker__item"
          :class="{ active: opt === modelValue }"
          :data-value="opt"
          @click="onItemClick(opt, i)"
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
  overflow: hidden;
  cursor: grab;
  -webkit-user-select: none;
  user-select: none;
}

.ar-wheel-picker__viewport:active {
  cursor: grabbing;
}

.ar-wheel-picker__track {
  display: flex;
  align-items: center;
  height: 100%;
  gap: 4px;
  will-change: transform;
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
