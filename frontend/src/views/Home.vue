<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NInput, NSelect, NTag, NRadioGroup, NRadioButton, NPagination, useMessage } from 'naive-ui'
import { getBlogPostsApi, getBlogTagsApi, type BlogPost } from '@/services/api'
import { useViewMode } from '@/composables/useViewMode'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const loading = ref(false)
const posts = ref<BlogPost[]>([])
const total = ref(0)
const page = ref(Number(route.query.page || 1))
const q = ref(String(route.query.q || ''))
const tag = ref(String(route.query.tag || ''))
const sortBy = ref(String(route.query.sort_by || 'created_at'))
const tags = ref<string[]>([])
const { viewMode } = useViewMode('blog-feed-view-mode', 'detail')

const sortOptions = [
  { label: '最新发布', value: 'created_at' },
  { label: '最多浏览', value: 'views' },
  { label: '最多点赞', value: 'likes' }
]

const tagOptions = computed(() => ['全部', ...tags.value])

const fetchTags = async () => {
  const res = await getBlogTagsApi({ page: 1, page_size: 100 }, { silent: true })
  tags.value = (res.list || []).map((item) => item.name)
}

const fetchPosts = async () => {
  loading.value = true
  try {
    const params: Record<string, string | number> = {
      page: page.value,
      page_size: 10,
      sort_by: sortBy.value
    }
    if (q.value) params.q = q.value
    if (tag.value) params.tag = tag.value
    const res = await getBlogPostsApi(params)
    posts.value = res.list || []
    total.value = res.total || 0
  } catch {
    message.error('加载博客列表失败')
  } finally {
    loading.value = false
  }
}

const syncQuery = () => {
  router.replace({
    query: {
      ...route.query,
      page: String(page.value),
      q: q.value || undefined,
      tag: tag.value || undefined,
      sort_by: sortBy.value,
      view: viewMode.value
    }
  })
}

const openPost = (post: BlogPost) => {
  router.push(`/blog/${post.slug}`)
}

watch([q, tag, sortBy, page], () => {
  syncQuery()
  fetchPosts()
})

onMounted(async () => {
  await fetchTags()
  await fetchPosts()
})
</script>

<template>
  <div class="home-page">
    <h2 class="page-title">博客首页</h2>
    <div class="toolbar card-glass">
      <NInput v-model:value="q" placeholder="搜索文章标题或正文" clearable />
      <NSelect v-model:value="sortBy" :options="sortOptions" />
      <NRadioGroup v-model:value="viewMode">
        <NRadioButton value="compact">精简行</NRadioButton>
        <NRadioButton value="detail">详情行</NRadioButton>
        <NRadioButton value="card">卡片</NRadioButton>
      </NRadioGroup>
    </div>

    <div class="tag-row">
      <NTag
        v-for="tagName in tagOptions"
        :key="tagName"
        checkable
        :checked="(tagName === '全部' && !tag) || tag === tagName"
        @update:checked="() => (tag = tagName === '全部' ? '' : tagName)"
      >
        {{ tagName }}
      </NTag>
    </div>

    <div v-if="posts.length === 0" class="empty card-glass">暂无文章，先去注册并发布第一篇吧。</div>

    <div v-else-if="viewMode === 'compact'" class="compact-list">
      <div v-for="post in posts" :key="post.id" class="compact-item card-glass" @click="openPost(post)">
        <div class="left">
          <h3>{{ post.title }}</h3>
          <div class="meta">
            <NTag v-for="tagName in (post.tags || []).slice(0, 2)" :key="tagName" size="small">
              {{ tagName }}
            </NTag>
          </div>
        </div>
        <div class="right">{{ post.created_at?.slice(0, 10) || '-' }}</div>
      </div>
    </div>

    <div v-else-if="viewMode === 'detail'" class="detail-list">
      <article v-for="post in posts" :key="post.id" class="detail-item card-glass" @click="openPost(post)">
        <h3>{{ post.title }}</h3>
        <p class="excerpt">{{ post.content?.slice(0, 180) || '暂无摘要' }}</p>
        <div class="footer">
          <div class="meta">
            <span>{{ post.author_username || '匿名' }}</span>
            <span>👍 {{ post.likes || 0 }}</span>
            <span>{{ post.created_at?.slice(0, 10) || '-' }}</span>
          </div>
        </div>
      </article>
    </div>

    <div v-else class="card-grid">
      <article v-for="post in posts" :key="post.id" class="card-item card-glass" @click="openPost(post)">
        <h3>{{ post.title }}</h3>
        <p>{{ post.content?.slice(0, 120) || '暂无摘要' }}</p>
        <div class="meta">{{ post.created_at?.slice(0, 10) || '-' }}</div>
      </article>
    </div>

    <div class="pager">
      <NPagination
        :page="page"
        :item-count="total"
        :page-size="10"
        show-quick-jumper
        @update:page="(val: number) => (page = val)"
      />
    </div>
  </div>
</template>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.page-title {
  margin: 0;
  font-size: 28px;
  color: var(--text-primary);
}
.toolbar {
  display: grid;
  grid-template-columns: 1fr 180px auto;
  gap: 12px;
  padding: 12px;
}
.tag-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.pager {
  display: flex;
  justify-content: center;
  padding: 8px 0 16px;
}
.empty {
  padding: 28px;
  text-align: center;
  color: var(--text-secondary);
}
.compact-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.compact-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
}
.left h3 {
  margin: 0 0 8px;
}
.meta {
  display: flex;
  gap: 8px;
}
.right {
  color: var(--text-tertiary);
}
.detail-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.detail-item {
  padding: 16px;
  cursor: pointer;
}
.excerpt {
  margin: 10px 0;
  color: var(--text-secondary);
}
.footer {
  display: flex;
  justify-content: space-between;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.card-item {
  padding: 16px;
  cursor: pointer;
}
.card-item h3 {
  margin: 0 0 8px;
}
.card-item p {
  margin: 0 0 10px;
  color: var(--text-secondary);
}
@media (max-width: 900px) {
  .toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
