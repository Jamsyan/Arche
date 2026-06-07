<script setup lang="ts">
/**
 * HeroCarousel — iOS 后台式卡片堆叠轮播。
 *
 * 核心视觉：中间一张完整主卡（A1），左右 B1/C1 清晰可读但微模糊，
 * 两侧卡片一层叠一层无限延伸，遵循近大远小透视规律。
 *
 * 实现：
 * - 透视投影算法（位置 + 缩放各用独立因子）
 * - CSS filter blur 实现"失焦"效果
 * - 5 份拷贝 + 提前边界复位实现平滑无限循环
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useSpring } from '@/utils/spring'
import { getCoverGradient } from '@/utils/cover'
import type { BlogPost } from '@/services/api'

const props = withDefaults(
  defineProps<{
    posts: BlogPost[]
    interval?: number
  }>(),
  { interval: 12000 }
)

const router = useRouter()
const sceneRef = ref<HTMLElement | null>(null)

// ── 常量 ──
const CARD_W = 280
// 透视参数：位置因子大 → 散布快，缩放因子小 → 衰减慢
const POS_FACTOR = 0.47 // 位置透视因子（n=1 时偏移 ~180px）
const SCALE_FACTOR = 0.18 // 缩放透视因子（n=1 时 scale ~0.85）
const MAX_SPREAD = 560

// 5 份拷贝 → 更大缓冲空间，边界复位更平滑
const COPIES = 5
const displayPosts = computed(() => {
  if (props.posts.length === 0) return []
  const result: BlogPost[] = []
  for (let c = 0; c < COPIES; c++) {
    result.push(...props.posts)
  }
  return result
})
const N = computed(() => props.posts.length)

// ── 弹簧驱动索引（从正中间份开始） ──
const MID = Math.floor(COPIES / 2)
const targetIdx = ref(MID * N.value)
const { value: animatedIdx, jump } = useSpring(targetIdx, {
  stiffness: 160,
  damping: 22,
  precision: 0.3
})

// ── 场景尺寸 ──
const sceneW = ref(800)
const sceneH = computed(() => Math.max(240, (CARD_W * 3) / 4 + 40))

// ── 所有卡片的堆叠变换 ──
// 位置：position = sign * maxSpread * (1 - 1/(1 + |n| * posFactor))
// 缩放：scale = 1 / (1 + |n| * scaleFactor)
// 模糊：blur 从 n±0.5 开始递增，B1/C1 微模糊
// 阴影：三层 box-shadow 模拟"卡片放在地板上的感觉"
const cardStates = computed(() => {
  const cw = CARD_W
  return displayPosts.value.map((_, i) => {
    const n = i - animatedIdx.value
    const abs = Math.abs(n)
    const sign = Math.sign(n) || 1

    // ── 位置（近大远小非线性） ──
    const t = 1 - 1 / (1 + abs * POS_FACTOR)
    const xOffset = sign * t * MAX_SPREAD

    // ── 缩放 ──
    const scale = 1 / (1 + abs * SCALE_FACTOR)

    // ── 透明度（二次曲线：B1/C1 完全 opaque，远处快速趋零） ──
    // 保证边界跳转时远处卡片 opacity ≈ 0，跳变不可见
    const opacity = 1 / (1 + Math.pow(Math.max(0, abs - 0.8), 2) * 1.8)

    // ── 模糊（远处彻底模糊，配合低 opacity 淹没跳变） ──
    const blurAmt = abs <= 0.5 ? 0 : Math.min(8, (abs - 0.5) * 2.2)

    // ── 居中 ──
    const transformX = xOffset - cw / 2

    // ── 地板阴影：三层 shadow 随距离衰减，产生"卡片放在地上的感觉" ──
    const si = Math.max(0, 1 - abs * 0.25)
    const shadow = [
      `0 ${(1.5 * scale).toFixed(1)}px ${(4 * scale).toFixed(1)}px rgba(26,24,23,${(0.05 * si).toFixed(3)})`,
      `0 ${(6 * scale).toFixed(1)}px ${(18 * scale).toFixed(1)}px rgba(26,24,23,${(0.08 * si).toFixed(3)})`,
      `0 ${(18 * scale).toFixed(1)}px ${(50 * scale).toFixed(1)}px rgba(26,24,23,${(0.06 * si).toFixed(3)})`
    ].join(', ')

    return {
      transform: `translateX(${transformX}px) translateY(-50%) scale(${scale})`,
      filter: blurAmt > 0 ? `blur(${blurAmt}px)` : 'none',
      boxShadow: shadow,
      opacity,
      zIndex: Math.max(0, 10 - Math.round(abs)),
      pe: (abs < 1.5 ? 'auto' : 'none') as 'auto' | 'none'
    }
  })
})

function showOverlay(i: number): boolean {
  return Math.abs(i - Math.round(animatedIdx.value)) <= 1
}

function getCardState(i: number) {
  return cardStates.value[i] ?? {}
}

function cardAtMain(i: number): boolean {
  return i === Math.round(animatedIdx.value)
}

// ── 交互 ──
function openPost(post: BlogPost) {
  if (post.id.startsWith('demo-')) return
  router.push(`/blog/${post.slug}`)
}

function handleCardClick(post: BlogPost, i: number) {
  const diff = i - Math.round(animatedIdx.value)
  if (diff === 0) {
    openPost(post)
  } else if (Math.abs(diff) === 1) {
    targetIdx.value = i
  }
}

function goNext() {
  if (N.value <= 1) return
  targetIdx.value = targetIdx.value + 1
  resetTimer()
}

function goPrev() {
  if (N.value <= 1) return
  targetIdx.value = targetIdx.value - 1
  resetTimer()
}

function goTo(cardIdx: number) {
  targetIdx.value = cardIdx
  resetTimer()
}

// ── 边界复位（无缝跳转，无弹簧反弹） ──
// 用 jump() 同时跳过 current + target，不反转弹簧方向
// 关键：Math.round() 确保跳转到整数位置，避免小数累计偏移
watch(animatedIdx, (pos) => {
  const len = N.value
  if (len <= 1) return
  if (pos < len * 1.8) {
    jump(Math.round(pos) + len)
  } else if (pos >= len * 3.2) {
    jump(Math.round(pos) - len)
  }
})

// ── 封面样式 ──
function coverStyle(post: BlogPost) {
  if (post.cover_url) {
    return {
      backgroundImage: `url(${post.cover_url})`,
      backgroundSize: 'cover' as const,
      backgroundPosition: 'center' as const
    }
  }
  return { background: getCoverGradient(post) }
}

// ── 自动轮播 ──
let timer: ReturnType<typeof setInterval> | null = null

function startTimer() {
  stopTimer()
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  if (N.value <= 1) return
  timer = setInterval(goNext, props.interval)
}
function stopTimer() {
  if (timer !== null) {
    clearInterval(timer)
    timer = null
  }
}
function resetTimer() {
  stopTimer()
  startTimer()
}
function onMouseEnter() {
  stopTimer()
}
function onMouseLeave() {
  startTimer()
}

function updateSceneW() {
  sceneW.value = sceneRef.value?.offsetWidth ?? 800
}

onMounted(() => {
  updateSceneW()
  startTimer()
})
onBeforeUnmount(() => {
  stopTimer()
})
</script>

<template>
  <section class="hero-carousel" @mouseenter="onMouseEnter" @mouseleave="onMouseLeave">
    <div ref="sceneRef" class="carousel-scene" :style="{ height: sceneH + 'px' }">
      <div class="mask-left" />
      <div class="mask-right" />

      <div class="card-stack">
        <article
          v-for="(post, i) in displayPosts"
          :key="'c-' + i"
          class="carousel-card"
          :class="{ 'is-main': cardAtMain(i) }"
          :style="getCardState(i)"
          @click="handleCardClick(post, i)"
        >
          <div class="card-cover" :style="coverStyle(post)">
            <div class="card-shine" />
          </div>
          <div v-if="showOverlay(i)" class="card-overlay">
            <div class="overlay-content">
              <span class="overlay-author">{{ post.author_username || '匿名' }}</span>
              <h3 class="overlay-title">{{ post.title }}</h3>
            </div>
          </div>
        </article>
      </div>

      <button v-if="N > 1" class="nav-arrow nav-prev" aria-label="上一张" @click="goPrev">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>
      <button v-if="N > 1" class="nav-arrow nav-next" aria-label="下一张" @click="goNext">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>
    </div>

    <div v-if="N > 1" class="carousel-dots">
      <button
        v-for="(_, index) in posts"
        :key="index"
        class="dot"
        :class="{ active: Math.round(animatedIdx) % N === index }"
        :aria-label="`切换到第 ${index + 1} 张`"
        type="button"
        @click="goTo(MID * N + index)"
      >
        <span class="dot-fill" />
      </button>
    </div>
  </section>
</template>

<style scoped>
.hero-carousel {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--content-padding);
  overflow: hidden;
  user-select: none;
}

.carousel-scene {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-stack {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 0;
  height: 0;
}

.carousel-card {
  position: absolute;
  left: 0;
  top: 0;
  width: 280px;
  aspect-ratio: 4 / 3;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  will-change: transform, opacity, filter;
  backface-visibility: hidden;
  -webkit-font-smoothing: antialiased;
  transition: filter 0.3s ease;
}

.carousel-card:hover {
  filter: brightness(1.05);
}

.carousel-card:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.card-cover {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  border-radius: inherit;
}

.card-shine {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.08) 0%,
    transparent 40%,
    transparent 60%,
    rgba(255, 255, 255, 0.03) 100%
  );
  pointer-events: none;
}

/* ── 文字叠覆 ── */
.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 50%, rgba(26, 24, 23, 0.75) 100%);
  display: flex;
  align-items: flex-end;
  padding: var(--spacing-lg);
  pointer-events: none;
}

.overlay-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.overlay-author {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
  font-weight: var(--font-weight-medium);
}

.overlay-title {
  margin: 0;
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: #fff;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.mask-left,
.mask-right {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 60px;
  z-index: 100;
  pointer-events: none;
}

.mask-left {
  left: 0;
  background: linear-gradient(to right, var(--surface-color) 0%, transparent 100%);
}
.mask-right {
  right: 0;
  background: linear-gradient(to left, var(--surface-color) 0%, transparent 100%);
}

.nav-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-color);
  background: color-mix(in srgb, var(--surface-color) 85%, transparent);
  backdrop-filter: blur(8px);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  transition:
    background var(--transition-normal),
    color var(--transition-normal),
    transform var(--transition-normal);
  opacity: 0;
  pointer-events: none;
}

.carousel-scene:hover .nav-arrow {
  opacity: 1;
  pointer-events: auto;
}
.nav-arrow:hover {
  background: var(--surface-color);
  color: var(--primary-color);
  transform: translateY(-50%) scale(1.08);
}
.nav-prev {
  left: var(--spacing-md);
}
.nav-next {
  right: var(--spacing-md);
}

.carousel-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  border: none;
  padding: 0;
  background: color-mix(in srgb, var(--primary-color) 26%, transparent);
  cursor: pointer;
  overflow: hidden;
  transition: transform var(--transition-normal);
}

.dot:hover {
  transform: scale(1.08);
}

.dot-fill {
  display: block;
  width: 100%;
  height: 100%;
  border-radius: inherit;
  background: color-mix(in srgb, var(--primary-color) 55%, transparent);
  transform: scale(0.65);
  transition: transform var(--transition-normal);
}

.dot.active .dot-fill {
  background: var(--primary-color);
  transform: scale(1);
}

@media (max-width: 680px) {
  .carousel-card {
    width: 200px;
  }
  .overlay-title {
    font-size: 14px;
  }
  .mask-left,
  .mask-right {
    width: 30px;
  }
}
</style>
