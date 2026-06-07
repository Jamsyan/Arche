<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NPagination, useMessage } from 'naive-ui'
import { getBlogPostsApi, type BlogPost } from '@/services/api/blog'
import { PostCard, HeroCarousel } from '@/components/blog'
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
const HOT_ROTATE_INTERVAL_MS = 12000

const filterByAccess = (list: BlogPost[]) =>
  userStore.token ? list : list.filter((item) => (item.required_level ?? 5) >= 5)

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

const latestPosts = computed(() => posts.value.slice(0, 6))
const quickPosts = computed(() => posts.value.slice(6, 12))

const openPost = (post: BlogPost) => {
  if (post.id.startsWith('demo-')) {
    message.info('当前为示例内容，待接口恢复后可点击进入真实文章')
    return
  }
  router.push(`/blog/${post.slug}`)
}

watch(page, async () => {
  syncQuery()
  await fetchPosts()
})

onMounted(async () => {
  await fetchPosts()
})
</script>

<template>
  <div class="home-page">
    <HeroCarousel v-if="hotPosts.length > 0" :posts="hotPosts" :interval="HOT_ROTATE_INTERVAL_MS" />

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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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

@media (max-width: 680px) {
  .latest-grid {
    grid-template-columns: 1fr;
  }
}
</style>
