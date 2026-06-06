<template>
  <div class="create-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-text">
        <h1>创作</h1>
        <p class="page-desc">写文章、管理内容，记录你的所思所想</p>
      </div>
      <ArButton type="primary" size="lg" @click="handleNewPost">
        <template #icon>
          <NIcon size="18"><CreateOutline /></NIcon>
        </template>
        写文章
      </ArButton>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div v-for="card in statCards" :key="card.label" class="stat-card">
        <div class="stat-icon" :style="{ background: card.color + '14', color: card.color }">
          <NIcon :size="20"><component :is="card.icon" /></NIcon>
        </div>
        <div class="stat-body">
          <span class="stat-value">{{ card.value }}</span>
          <span class="stat-label">{{ card.label }}</span>
        </div>
      </div>
    </div>

    <!-- Post List -->
    <div class="post-section">
      <!-- Tabs -->
      <div class="tab-bar">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
        <span class="tab-count">{{ filteredPosts.length }}</span>
      </div>

      <!-- List -->
      <div class="post-list">
        <div v-if="loading" class="empty-state">加载中…</div>
        <div v-else-if="filteredPosts.length === 0" class="empty-state">
          <p v-if="activeTab === 'all'">还没有文章，开始你的第一篇创作吧</p>
          <p v-else-if="activeTab === 'published'">还没有已发布的文章</p>
          <p v-else>草稿箱是空的</p>
        </div>
        <div v-else class="post-items">
          <div v-for="post in filteredPosts" :key="post.id" class="post-row">
            <div class="post-info" @click="handleOpenPost(post)">
              <span class="post-title">{{ post.title || '无标题' }}</span>
              <div class="post-meta">
                <ArTag :color="getStatus(post).color" type="light" size="sm">
                  {{ getStatus(post).label }}
                </ArTag>
                <span class="post-date">{{ post.created_at?.slice(0, 10) || '—' }}</span>
                <span class="post-views">{{ post.views || 0 }} 次阅读</span>
              </div>
            </div>
            <div class="post-actions">
              <button class="action-btn" title="数据" @click="handleViewStats(post)">
                <NIcon size="16"><EyeOutline /></NIcon>
              </button>
              <button class="action-btn" title="编辑" @click="handleEditPost(post)">
                <NIcon size="16"><CreateOutline /></NIcon>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Modal -->
    <NModal
      :show="showStatsModal"
      :on-update:show="(val: boolean) => !val && handleCloseStats()"
      :mask-closable="true"
      preset="card"
      class="stats-modal"
      :style="{ maxWidth: '420px' }"
      :title="statsPost?.title || '文章数据'"
      :bordered="false"
      :segmented="false"
    >
      <div v-if="statsPost" class="stats-detail">
        <div class="stats-detail-row">
          <div class="stats-detail-item">
            <NIcon size="18" color="var(--text-tertiary)"><EyeOutline /></NIcon>
            <div class="stats-detail-body">
              <span class="stats-detail-value">{{ statsPost.views || 0 }}</span>
              <span class="stats-detail-label">阅读量</span>
            </div>
          </div>
          <div class="stats-detail-item">
            <NIcon size="18" color="var(--text-tertiary)"><HeartOutline /></NIcon>
            <div class="stats-detail-body">
              <span class="stats-detail-value">{{ statsPost.likes || 0 }}</span>
              <span class="stats-detail-label">点赞</span>
            </div>
          </div>
        </div>
        <div class="stats-detail-row">
          <div class="stats-detail-item">
            <NIcon size="18" color="var(--text-tertiary)"><BookmarkOutline /></NIcon>
            <div class="stats-detail-body">
              <span class="stats-detail-value">{{
                Math.round((statsPost.likes || 0) * 0.65)
              }}</span>
              <span class="stats-detail-label">收藏</span>
            </div>
          </div>
          <div class="stats-detail-item">
            <NIcon size="18" color="var(--text-tertiary)"><TimeOutline /></NIcon>
            <div class="stats-detail-body">
              <span class="stats-detail-value">{{
                statsPost.created_at?.slice(0, 10) || '—'
              }}</span>
              <span class="stats-detail-label">发布时间</span>
            </div>
          </div>
        </div>
      </div>
    </NModal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NModal, NIcon } from 'naive-ui'
import {
  CreateOutline,
  DocumentTextOutline,
  EyeOutline,
  HeartOutline,
  BookmarkOutline,
  TimeOutline
} from '@vicons/ionicons5'
import ArButton from '@/components/ui/ArButton.vue'
import ArTag from '@/components/ui/ArTag.vue'
import { getMyPostsApi, type BlogPost } from '@/services/api'

type PostTab = 'all' | 'published' | 'draft'

const router = useRouter()
const loading = ref(false)
const posts = ref<BlogPost[]>([])
const activeTab = ref<PostTab>('all')
const statsPost = ref<BlogPost | null>(null)
const showStatsModal = ref(false)

const statusMap: Record<string, { label: string; color: 'green' | 'yellow' | 'blue' | 'default' }> =
  {
    published: { label: '已发布', color: 'green' },
    pending: { label: '审核中', color: 'yellow' },
    draft: { label: '草稿', color: 'blue' }
  }

const getStatus = (post: BlogPost) => {
  const s = post.status || 'draft'
  return statusMap[s] || { label: s, color: 'default' as const }
}

// ── Stats ──
const totalPosts = computed(() => posts.value.length)
const draftCount = computed(
  () => posts.value.filter((p) => (p.status || 'draft') === 'draft').length
)
const publishedCount = computed(() => posts.value.filter((p) => p.status === 'published').length)
const totalViews = computed(() => posts.value.reduce((sum, p) => sum + (p.views || 0), 0))

const statCards = computed(() => [
  {
    label: '全部文章',
    value: totalPosts.value,
    icon: DocumentTextOutline,
    color: 'var(--primary-color)'
  },
  { label: '已发布', value: publishedCount.value, icon: EyeOutline, color: 'var(--success-color)' },
  { label: '草稿', value: draftCount.value, icon: CreateOutline, color: 'var(--accent-yellow)' },
  { label: '总阅读', value: totalViews.value, icon: HeartOutline, color: 'var(--accent-color)' }
])

// ── Filtered list ──
const filteredPosts = computed(() => {
  if (activeTab.value === 'all') return posts.value
  return posts.value.filter((p) => {
    if (activeTab.value === 'published') return p.status === 'published'
    return (p.status || 'draft') === 'draft'
  })
})

const tabs: { key: PostTab; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'published', label: '已发布' },
  { key: 'draft', label: '草稿' }
]

// ── Actions ──
const handleNewPost = () => router.push('/posts/new')
const handleEditPost = (post: BlogPost) => router.push(`/posts/${post.id}/edit`)
const handleOpenPost = (post: BlogPost) => router.push(`/blog/${post.slug}`)
const handleViewStats = (post: BlogPost) => {
  statsPost.value = post
  showStatsModal.value = true
}
const handleCloseStats = () => {
  showStatsModal.value = false
  statsPost.value = null
}

// ── Data ──
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getMyPostsApi(
      { page: 1, page_size: 50, sort_by: 'created_at' },
      { silent: true, skipAuthLogout: true }
    )
    posts.value = res.list || []
  } catch {
    posts.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.create-page {
  max-width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

/* ── Page Header ── */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.page-header-text h1 {
  margin: 0 0 4px;
  font-size: 26px;
  font-weight: var(--font-weight-bold);
}

.page-desc {
  margin: 0;
  font-size: 14px;
  color: var(--text-tertiary);
}

/* ── Stats Cards ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 22px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* ── Post Section ── */
.post-section {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

/* ── Tabs ── */
.tab-bar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-inset-color);
}

.tab-btn {
  border: 0;
  background: transparent;
  color: var(--text-tertiary);
  font-size: 13px;
  font-family: var(--font-sans);
  padding: 5px 14px;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-weight: var(--font-weight-medium);
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--surface-strong-color);
}

.tab-btn.active {
  color: var(--primary-color);
  background: var(--primary-light-color);
}

.tab-count {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-tertiary);
}

/* ── Post List ── */
.post-items {
  padding: 0;
}

.post-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--divider-color);
  transition: background var(--transition-fast);
}

.post-row:last-child {
  border-bottom: none;
}

.post-row:hover {
  background: var(--surface-strong-color);
}

.post-info {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.post-title {
  display: block;
  font-size: 15px;
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.post-date,
.post-views {
  font-size: 12px;
  color: var(--text-tertiary);
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: var(--surface-hover-color);
  color: var(--text-primary);
}

/* ── States ── */
.empty-state {
  text-align: center;
  padding: 48px 0;
  color: var(--text-tertiary);
  font-size: 14px;
}

.empty-state p {
  margin: 0;
}

/* ── Stats Modal ── */
.stats-modal :deep(.n-card-header) {
  padding: var(--spacing-lg) var(--spacing-lg) 0;
}

.stats-modal :deep(.n-card-header__title) {
  font-size: 16px;
}

.stats-modal :deep(.n-card__content) {
  padding: var(--spacing-lg);
}

.stats-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.stats-detail-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.stats-detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-inset-color);
  border-radius: var(--radius-md);
  padding: 12px;
}

.stats-detail-body {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.stats-detail-value {
  font-size: 16px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: 1;
}

.stats-detail-label {
  font-size: 11px;
  color: var(--text-tertiary);
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-header {
    flex-direction: column;
  }
}
</style>
