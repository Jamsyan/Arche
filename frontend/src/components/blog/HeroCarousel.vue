<script setup lang="ts">
/**
 * HeroCarousel — iOS 后台式卡片堆叠轮播。
 *
 * 核心视觉：中间一张完整主卡，两侧卡片一层叠一层无限延伸。
 * 正如 iPhone 后台卡片：第一张完整清晰，后面一张叠一张形成深邃堆叠。
 *
 * 实现方式：
 * - 每张卡片绝对定位，独立 transform
 * - 弹簧驱动当前索引，所有卡片平滑过渡
 * - 每张卡片的偏移量基于距中心的距离，每层仅露出 ~35px 边缘
 * - 3 份拷贝实现无限循环
 */
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
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
const CARD_H_RATIO = 3 / 4 // height = width * ratio (aspect-ratio 4/3)
const PEEK = 35 // 每层露出的边缘宽度 (px)
const STACK_SCALE = 0.88 // 每层递减倍率

// 3 份拷贝
const displayPosts = computed(() => {
  if (props.posts.length === 0) return []
  return [...props.posts, ...props.posts, ...props.posts]
})
const N = computed(() => props.posts.length)

// ── 弹簧驱动索引 ──
const targetIdx = ref(N.value)
const animatedIdx = useSpring(targetIdx, {
  stiffness: 160,
  damping: 22,
  precision: 0.3
})

// ── 场景尺寸 ──
const sceneW = ref(800)
const sceneH = computed(() => Math.max(240, sceneW.value * CARD_H_RATIO * 0.35))

// ── 所有卡片的堆叠变换 ──
// 每张卡片根据 (i - animatedIdx) 计算绝对位置
// 正偏移 → 右侧堆叠，负偏移 → 左侧堆叠
const cardStates = computed(() => {
  const cw = CARD_W
  return displayPosts.value.map((_, i) => {
    const n = i - animatedIdx.value // 连续偏移量
    const abs = Math.abs(n)
    const sign = Math.sign(n) || 1

    // ── 堆叠衰减曲线（iOS 式：每层进度性缩小 + 偏移） ──
    const scale = Math.pow(STACK_SCALE, abs)
    const halfW = (cw * scale) / 2
    // 卡片近侧边缘距中心 = cardHalf + peek * abs
    const nearEdge = cw / 2 + PEEK * abs
    // 卡片中心偏移 = nearEdge - halfW
    const xOffset = sign * (nearEdge - halfW)

    // 透明度：越远越淡
    const opacity = Math.max(0, 1 - abs * 0.13)

    // z-index：越近越高
    const zIndex = Math.max(0, 10 - abs)

    return {
      transform: `translateX(${xOffset}px) translateY(-50%) scale(${scale})`,
      opacity,
      zIndex,
      // 主卡 + 左右各一张可点击
      pe: (abs < 1.5 ? 'auto' : 'none') as 'auto' | 'none'
    }
  })
})

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
      <!-- 侧边渐变遮罩 -->
      <div class="mask-left" />
      <div class="mask-right" />

      <!-- 堆叠卡片层 -->
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
          <div v-if="cardAtMain(i)" class="card-overlay">
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
        @click="goTo(N + index)"
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

/* ── 场景容器 ── */
.carousel-scene {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── 卡片堆叠层 ── */
.card-stack {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 0;
  height: 0;
}

/* ── 单张卡片 ── */
.carousel-card {
  position: absolute;
  left: 0;
  top: 0;
  width: 280px;
  aspect-ratio: 4 / 3;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  will-change: transform, opacity;
  backface-visibility: hidden;
  -webkit-font-smoothing: antialiased;
  box-shadow:
    0 4px 20px rgba(26, 24, 23, 0.12),
    0 1px 4px rgba(26, 24, 23, 0.08);
  transition: filter 0.3s ease;
}

.carousel-card:hover {
  filter: brightness(1.05);
}

.carousel-card.is-main {
  box-shadow:
    0 8px 32px rgba(26, 24, 23, 0.18),
    0 2px 8px rgba(26, 24, 23, 0.1);
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

/* ── 侧边渐变遮罩 ── */
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

/* ── 导航箭头 ── */
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
