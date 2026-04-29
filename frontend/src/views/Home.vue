<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NIcon, NPagination, NTag, useMessage } from 'naive-ui'
import {
  BookmarkOutline,
  FlameOutline,
  HeartOutline,
  PersonOutline,
  ShareSocialOutline
} from '@vicons/ionicons5'
import { getBlogPostsApi, type BlogPost } from '@/services/api'
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

const fallbackPosts: BlogPost[] = [
  {
    id: 'demo-1',
    slug: 'demo-spring-notes',
    title: '春日来信：把普通日子写成可回放的片段',
    content:
      '这是首页示例内容。接口暂不可用时，用它来保证首屏轮播和列表不空白。你可以把生活中那些没有“结果”的瞬间，写成会发光的过程。',
    tags: ['时光', '生活观察'],
    author_username: '锦年志编辑部',
    views: 3251,
    likes: 248,
    created_at: '2026-04-01'
  },
  {
    id: 'demo-2',
    slug: 'demo-midnight-reading',
    title: '午夜阅读手记：在慢节奏里重建表达力',
    content:
      '你不需要一次写完一个伟大故事，只要每天留下三行真实感受。时间会把这些片段自动拼成你的个人年鉴。',
    tags: ['阅读', '成长记录'],
    author_username: '林深',
    views: 2987,
    likes: 206,
    created_at: '2026-03-28'
  },
  {
    id: 'demo-3',
    slug: 'demo-city-walk',
    title: '城市漫游计划：一张地图，七天观察练习',
    content:
      '用“地点-人物-情绪”三要素去记录城市，每一次散步都能变成创作素材。这是一个可复制的轻量化习惯模型。',
    tags: ['旅行笔记', '创作灵感'],
    author_username: '阿野',
    views: 2654,
    likes: 192,
    created_at: '2026-03-20'
  },
  {
    id: 'demo-4',
    slug: 'demo-photo-story',
    title: '影像日志模板：一图一句，建立你的视觉年轮',
    content: '拍照不只是“打卡”，更是构建记忆的索引系统。示例模板可直接套用到每日记录与项目复盘。',
    tags: ['摄影', '学习札记'],
    author_username: '苏河',
    views: 2338,
    likes: 176,
    created_at: '2026-03-12'
  },
  {
    id: 'demo-5',
    slug: 'demo-dev-journal',
    title: '工程师也写生活：把技术思维变成日常叙事',
    content:
      '把“问题-假设-验证”这种工程习惯迁移到生活记录，你会更容易看见成长轨迹，也更容易持续输出。',
    tags: ['技术实践', '心情随笔'],
    author_username: '南渡',
    views: 2140,
    likes: 153,
    created_at: '2026-03-05'
  },
  {
    id: 'demo-6',
    slug: 'demo-weekly-review',
    title: '周记复盘法：15 分钟完成一周沉淀',
    content:
      '每周固定一个时间窗口，把高光、低谷和改进点写下来。长期坚持后，你会得到一份极具个人价值的成长档案。',
    tags: ['成长记录', '学习札记'],
    author_username: '岚',
    views: 1986,
    likes: 139,
    created_at: '2026-02-27'
  }
]

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

const applyFallbackData = () => {
  posts.value = fallbackPosts
  hotPosts.value = fallbackPosts.slice(0, 6)
  total.value = fallbackPosts.length
  hotIndex.value = 0
}

const fetchPosts = async () => {
  loading.value = true
  try {
    const [latestRes, hotRes] = await Promise.all([
      getBlogPostsApi({
        page: page.value,
        page_size: 12,
        sort_by: 'created_at'
      }),
      getBlogPostsApi({
        page: 1,
        page_size: 6,
        sort_by: 'views'
      })
    ])
    const latestList = filterByAccess(latestRes.list || [])
    const hotList = filterByAccess(hotRes.list || [])
    if (latestList.length === 0 && hotList.length === 0) {
      applyFallbackData()
      return
    }
    posts.value = latestList.length > 0 ? latestList : fallbackPosts
    hotPosts.value = hotList.length > 0 ? hotList : posts.value.slice(0, 6)
    total.value = latestRes.total || posts.value.length
    hotIndex.value = 0
  } catch {
    applyFallbackData()
    message.warning('接口暂不可用，已展示示例内容')
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
const hotGroupCount = computed(() => hotGroups.value.length)
const latestPosts = computed(() => posts.value.slice(0, 6))
const quickPosts = computed(() => posts.value.slice(6, 12))

const openPost = (post: BlogPost) => {
  if (post.id.startsWith('demo-')) {
    message.info('当前为示例内容，待接口恢复后可点击进入真实文章')
    return
  }
  router.push(`/blog/${post.slug}`)
}

const getAuthorName = (post: BlogPost) => post.author_username || '匿名作者'

const getAuthorAvatarUrl = (post: BlogPost) => {
  const maybePost = post as BlogPost & { author_avatar?: string; avatar?: string }
  return maybePost.author_avatar || maybePost.avatar || ''
}

const getCoverUrl = (post: BlogPost) =>
  `https://picsum.photos/seed/${encodeURIComponent(post.slug || post.id)}/280/360`

const getShareCount = (post: BlogPost) => Math.max(1, Math.round((post.views || 0) / 18))

const getFavoriteCount = (post: BlogPost) => Math.max(1, Math.round((post.likes || 0) * 0.65))

const startHotTimer = () => {
  if (hotTimer) {
    clearInterval(hotTimer)
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
      class="hero-carousel card-glass"
      :style="{ '--hot-interval': `${HOT_ROTATE_INTERVAL_MS}ms` }"
    >
      <Transition name="hero-slide" mode="out-in">
        <div :key="hotIndex" class="hero-track">
          <article
            v-for="post in currentHotGroup"
            :key="post.id"
            class="hero-card"
            @click="openPost(post)"
          >
            <p class="hero-tag">精选推荐</p>
            <h2>{{ post.title }}</h2>
            <p class="hero-excerpt">{{ post.content?.slice(0, 120) || '暂无摘要' }}</p>
            <div class="hero-meta">
              <span>{{ post.author_username || '匿名' }}</span>
              <span>👁 {{ post.views || 0 }}</span>
              <span>👍 {{ post.likes || 0 }}</span>
            </div>
          </article>
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
        <article
          v-for="post in latestPosts"
          :key="post.id"
          class="post-card card-glass"
          @click="openPost(post)"
        >
          <div class="post-author">
            <span class="author-avatar">
              <img
                v-if="getAuthorAvatarUrl(post)"
                class="author-avatar-image"
                :src="getAuthorAvatarUrl(post)"
                :alt="`${getAuthorName(post)} 头像`"
                loading="lazy"
              >
              <NIcon v-else size="14" aria-hidden="true">
                <PersonOutline />
              </NIcon>
            </span>
            <span class="author-name">@{{ getAuthorName(post) }}</span>
          </div>
          <div class="post-main">
            <div class="post-left">
              <h4>{{ post.title }}</h4>
              <p class="post-excerpt">{{ post.content?.slice(0, 96) || '暂无摘要' }}</p>
            </div>
            <div class="post-cover">
              <img
                class="cover-image"
                :src="getCoverUrl(post)"
                :alt="`${post.title} 封面`"
                loading="lazy"
              >
              <span class="cover-tag">{{ (post.tags || [])[0] || '日志' }}</span>
              <span class="cover-date">{{ post.created_at?.slice(0, 10) || '-' }}</span>
            </div>
          </div>
          <footer class="post-footer">
            <div class="post-actions">
              <span class="action-chip" title="点赞">
                <NIcon size="16"><HeartOutline /></NIcon>
                <em>{{ post.likes || 0 }}</em>
              </span>
              <span class="action-chip" title="收藏">
                <NIcon size="16"><BookmarkOutline /></NIcon>
                <em>{{ getFavoriteCount(post) }}</em>
              </span>
              <span class="action-chip" title="分享">
                <NIcon size="16"><ShareSocialOutline /></NIcon>
                <em>{{ getShareCount(post) }}</em>
              </span>
              <span class="action-chip action-chip-hot" title="热度">
                <NIcon size="16"><FlameOutline /></NIcon>
                <em>{{ post.views || 0 }}</em>
              </span>
            </div>
          </footer>
        </article>
      </div>
    </section>

    <section v-if="quickPosts.length > 0" class="post-section">
      <div class="section-head">
        <h3>继续浏览</h3>
      </div>
      <div class="quick-list">
        <article
          v-for="post in quickPosts"
          :key="post.id"
          class="quick-item"
          @click="openPost(post)"
        >
          <div>
            <h4>{{ post.title }}</h4>
            <div class="quick-tags">
              <NTag v-for="tag in (post.tags || []).slice(0, 2)" :key="tag" size="small">
                {{ tag }}
              </NTag>
            </div>
          </div>
          <span>{{ post.created_at?.slice(0, 10) || '-' }}</span>
        </article>
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
  gap: 18px;
  padding: 0 0 18px;
}

.hero-carousel {
  min-height: 240px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hero-track {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.hero-card {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  background: rgba(255, 250, 241, 0.72);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 180px;
  cursor: pointer;
}

.hero-tag {
  margin: 0;
  font-size: 12px;
  color: var(--text-tertiary);
  letter-spacing: 0.08em;
}

.hero-card h2 {
  margin: 0;
  font-size: 24px;
  line-height: 1.35;
}

.hero-excerpt {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.hero-meta {
  display: flex;
  gap: 12px;
  color: var(--text-tertiary);
  font-size: 12px;
  margin-top: auto;
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
  border-radius: 999px;
  border: none;
  padding: 0;
  background: rgba(154, 90, 47, 0.26);
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.25s ease;
}

.dot:hover {
  transform: scale(1.08);
}

.dot-fill {
  display: block;
  width: 100%;
  height: 100%;
  border-radius: inherit;
  background: rgba(154, 90, 47, 0.55);
  transform: scale(0.65);
  transition: transform 0.25s ease;
}

.dot.active .dot-fill {
  background: var(--primary-color);
  transform: scale(1);
}

.hero-slide-enter-active,
.hero-slide-leave-active {
  transition:
    opacity 0.4s ease,
    transform 0.4s ease;
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
  gap: 10px;
}

.latest-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 12px;
}

.post-card {
  position: relative;
  isolation: isolate;
  cursor: pointer;
  border: 1px solid var(--border-color);
  padding: 14px;
  display: grid;
  grid-template-rows: 24px minmax(0, 1fr) 52px;
  gap: 10px;
  min-height: 286px;
  transform: translateZ(0);
  backface-visibility: hidden;
  will-change: box-shadow, border-color;
  transition:
    box-shadow 0.28s ease,
    border-color 0.28s ease;
}

.post-card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid rgba(154, 90, 47, 0.24);
  box-shadow: 0 10px 22px rgba(67, 45, 28, 0.12);
  opacity: 0;
  transform: translateY(0);
  transition:
    opacity 0.28s ease,
    transform 0.28s ease;
  pointer-events: none;
  z-index: -1;
}

.post-card:hover {
  border-color: rgba(154, 90, 47, 0.34);
  box-shadow: 0 12px 24px rgba(67, 45, 28, 0.16);
}

.post-card:hover::after {
  opacity: 1;
  transform: translateY(-3px);
}

.post-main {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 120px;
  gap: 14px;
  align-items: start;
  min-height: 152px;
}

.post-left {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-width: 0;
  min-height: 152px;
}

.post-author {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 24px;
  min-width: 0;
}

.post-card h4 {
  margin: 0;
  font-size: 17px;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: calc(1em * 1.35 * 2);
}

.post-excerpt {
  margin: 14px 0 0;
  color: rgba(47, 38, 29, 0.7);
  line-height: 22px;
  font-size: 13px;
  font-weight: 500;
  background: rgba(154, 90, 47, 0.08);
  border-left: 3px solid rgba(154, 90, 47, 0.34);
  border-radius: 8px;
  padding: 10px 10px 10px 12px;
  font-family: 'PingFang SC', 'Microsoft YaHei UI', 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
  display: block;
  overflow: hidden;
  align-self: end;
  max-height: calc(22px * 3 + 20px);
}

.post-footer {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  align-items: center;
  min-height: 40px;
  padding-top: 8px;
  border-top: 1px solid rgba(47, 38, 29, 0.12);
  color: var(--text-tertiary);
  font-size: 12px;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: rgba(154, 90, 47, 0.14);
  border: 1px solid rgba(154, 90, 47, 0.24);
  color: rgba(111, 63, 34, 0.65);
}

.author-avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.author-name {
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
}

.post-actions {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  min-width: 0;
}

.action-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 3px 6px;
  border-radius: 999px;
  border: 1px solid rgba(47, 38, 29, 0.12);
  background: rgba(255, 250, 241, 0.9);
  color: rgba(47, 38, 29, 0.72);
  line-height: 1;
  min-width: 0;
}

.action-chip em {
  font-style: normal;
  font-size: 11px;
  font-weight: 600;
}

.action-chip-hot {
  color: var(--primary-color);
  border-color: rgba(154, 90, 47, 0.24);
  background: rgba(154, 90, 47, 0.1);
}

.post-cover {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid rgba(255, 250, 241, 0.56);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px;
  min-height: 152px;
}

.cover-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

.post-cover::after {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(
    180deg,
    rgba(15, 23, 42, 0.1) 0%,
    rgba(15, 23, 42, 0.32) 62%,
    rgba(15, 23, 42, 0.5) 100%
  );
}

.cover-tag {
  position: relative;
  z-index: 2;
  align-self: flex-start;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.94);
  background: rgba(15, 23, 42, 0.32);
  border-radius: 999px;
  padding: 2px 8px;
}

.cover-date {
  position: relative;
  z-index: 2;
  align-self: flex-end;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.88);
}

.quick-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-item {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.quick-item h4 {
  margin: 0 0 8px;
  font-size: 16px;
}

.quick-tags {
  display: flex;
  gap: 8px;
}

.quick-item > span {
  color: var(--text-tertiary);
  font-size: 12px;
  white-space: nowrap;
}

.pager {
  display: flex;
  justify-content: center;
  padding-top: 6px;
}

.empty {
  color: var(--text-tertiary);
  padding: 14px 0;
}

@media (max-width: 680px) {
  .hero-track {
    grid-template-columns: 1fr;
  }

  .hero-card h2 {
    font-size: 21px;
  }

  .latest-grid {
    grid-template-columns: 1fr;
  }

  .post-main {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .post-card {
    grid-template-rows: auto auto auto;
    min-height: unset;
  }

  .post-cover {
    min-height: 78px;
    flex-direction: row;
    align-items: center;
  }

  .post-footer {
    grid-template-columns: minmax(0, 1fr);
    min-height: unset;
  }

  .post-actions {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .action-chip {
    justify-content: flex-start;
  }

  .quick-item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
