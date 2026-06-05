<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NPagination, useMessage } from 'naive-ui'
import { getBlogPostsApi, type BlogPost } from '@/services/api/blog'
import { PostCard } from '@/components/blog'
import { useUserStore } from '@/store/modules/user'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const loading = ref(false)
const posts = ref<BlogPost[]>([])
const hotPosts = ref<BlogPost[]>([])
const total = ref(0)
const page = ref(Number(route.query.page || 1))
const hotIndex = ref(0)
const HOT_ROTATE_INTERVAL_MS = 12000

let hotTimer: ReturnType<typeof setInterval> | null = null

const getAccessLevelNumber = (accessLevel?: string) => {
  if (!accessLevel) {
    return 5
  }
  const normalized = accessLevel.trim().toUpperCase()
  if (!normalized.startsWith('A')) {
    return 5
  }
  const parsed = Number(normalized.slice(1))
  return Number.isFinite(parsed) ? parsed : 5
}

const filterByAccess = (list: BlogPost[]) =>
  userStore.token ? list : list.filter((item) => getAccessLevelNumber(item.access_level) <= 5)

const fetchPosts = async () => {
  loading.value = true
  try {
    const [latestRes, hotRes] = await Promise.all([
      getBlogPostsApi({ page: page.value, page_size: 12, sort_by: 'created_at' }),
      getBlogPostsApi({ page: 1, page_size: 6, sort_by: 'views' })
    ])
    const latestList = filterByAccess(latestRes.list || [])
    const hotList = filterByAccess(hotRes.list || [])
    posts.value = latestList
    hotPosts.value = hotList.length > 0 ? hotList : latestList.slice(0, 6)
    total.value = latestRes.total || 0
    hotIndex.value = 0
  } catch {
    message.error('获取文章列表失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

const syncQuery = () => {
  router.replace({
    query: {
      ...route.query,
      page: String(page.value)
    }
  })
}

const hotGroups = computed(() => {
  const groups: BlogPost[][] = []
  for (let i = 0; i < hotPosts.value.length; i += 2) {
    groups.push(hotPosts.value.slice(i, i + 2))
  }
  return groups
})
const currentHotGroup = computed(() => hotGroups.value[hotIndex.value] || [])
const latestPosts = computed(() => posts.value.slice(0, 6))
const quickPosts = computed(() => posts.value.slice(6, 12))

const openPost = (post: BlogPost) => {
  if (post.id.startsWith('demo-')) {
    message.info('当前为示例内容，待接口恢复后可点击进入真实文章')
    return
  }
  router.push(`/blog/${post.slug}`)
}

const startHotTimer = () => {
  if (hotTimer) {
    clearInterval(hotTimer)
  }
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return
  }
  hotTimer = setInterval(() => {
    if (hotGroups.value.length > 1) {
      hotIndex.value = (hotIndex.value + 1) % hotGroups.value.length
    }
  }, HOT_ROTATE_INTERVAL_MS)
}

const resetHotTimer = () => {
  startHotTimer()
}

const jumpToHot = (index: number) => {
  hotIndex.value = index
  resetHotTimer()
}

watch(page, async () => {
  syncQuery()
  await fetchPosts()
})

onMounted(async () => {
  await fetchPosts()
  startHotTimer()
})

onBeforeUnmount(() => {
  if (hotTimer) {
    clearInterval(hotTimer)
  }
})
</script>

<template>
  <div class="home-page">
    <section
      v-if="currentHotGroup.length > 0"
      class="hero-carousel"
      :style="{ '--hot-interval': `${HOT_ROTATE_INTERVAL_MS}ms` }"
    >
      <Transition name="hero-slide" mode="out-in">
        <div :key="hotIndex" class="hero-track">
          <PostCard
            v-for="post in currentHotGroup"
            :key="post.id"
            :post="post"
            layout="grid"
            @open="openPost(post)"
          />
        </div>
      </Transition>
      <div class="carousel-controls">
        <div class="hot-dots">
          <button
            v-for="(_, index) in hotGroups"
            :key="index"
            class="dot"
            :class="{ active: hotIndex === index }"
            :aria-label="`切换到第 ${index + 1} 组`"
            type="button"
            @click.stop="jumpToHot(index)"
          >
            <span class="dot-fill" />
          </button>
        </div>
      </div>
    </section>

    <section class="post-section">
      <div v-if="latestPosts.length === 0" class="empty">暂无内容</div>
      <div v-else class="latest-grid">
        <div
          v-for="(post, index) in latestPosts"
          :key="post.id"
          class="stagger-item"
          :style="{ animationDelay: `${index * 60}ms` }"
        >
          <PostCard
            :post="post"
            layout="grid"
            :show-cover="true"
            :show-actions="true"
            @open="openPost(post)"
          />
        </div>
      </div>
    </section>

    <section v-if="quickPosts.length > 0" class="post-section">
      <div class="section-head">
        <h3>继续浏览</h3>
      </div>
      <div class="quick-list">
        <PostCard
          v-for="post in quickPosts"
          :key="post.id"
          :post="post"
          layout="compact"
          :show-excerpt="false"
          @open="openPost(post)"
        />
      </div>
    </section>

    <div v-if="total > 12" class="pager">
      <NPagination
        :page="page"
        :item-count="total"
        :page-size="12"
        @update:page="(val: number) => (page = val)"
      />
    </div>
  </div>
</template>

<style scoped>
.home-page {
  width: min(1200px, 100%);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--layout-gap);
  padding: 0 0 var(--spacing-lg);
  font-family: var(--font-sans);
}

.hero-carousel {
  min-height: 240px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--content-padding);
}

.hero-track {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--spacing-md);
}

.carousel-controls {
  display: flex;
  justify-content: center;
  align-items: center;
}

.hot-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
  width: min(520px, 100%);
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

.hero-slide-enter-active,
.hero-slide-leave-active {
  transition:
    opacity var(--transition-slow),
    transform var(--transition-slow);
}

.hero-slide-enter-from {
  opacity: 0;
  transform: translateX(24px);
}

.hero-slide-leave-to {
  opacity: 0;
  transform: translateX(-24px);
}

.post-section {
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

.latest-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--layout-gap);
}

.quick-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.pager {
  display: flex;
  justify-content: center;
  padding-top: var(--spacing-sm);
}

.empty {
  color: var(--text-tertiary);
  padding: var(--spacing-md) 0;
}

@media (prefers-reduced-motion: reduce) {
  .hero-slide-enter-active,
  .hero-slide-leave-active {
    transition: none !important;
  }
}

@media (max-width: 680px) {
  .hero-track {
    grid-template-columns: 1fr;
  }

  .latest-grid {
    grid-template-columns: 1fr;
  }
}
</style>
