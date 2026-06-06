<template>
  <Transition name="mode" mode="out-in">
    <!-- Browse mode -->
    <div v-if="!isEditorOpen" key="browse" class="create-page">
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

      <div class="post-section">
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
                </div>
              </div>
              <div class="post-actions">
                <div
                  class="action-btn-wrap"
                  @mouseenter="hoveredPost = post"
                  @mouseleave="hoveredPost = null"
                >
                  <button
                    class="action-btn"
                    title="数据"
                    @click="handleViewStats(post)"
                    @mouseenter="hoveredPost = post"
                  >
                    <NIcon size="16"><EyeOutline /></NIcon>
                  </button>
                  <Transition name="tip">
                    <div
                      v-if="hoveredPost?.id === post.id && (!statsPost || statsPost.id !== post.id)"
                      class="stats-tip"
                      @mouseenter="hoveredPost = post"
                    >
                      <div class="tip-row">
                        <span class="tip-label">阅读</span>
                        <span class="tip-value">{{ post.views || 0 }}</span>
                      </div>
                      <div class="tip-row">
                        <span class="tip-label">点赞</span>
                        <span class="tip-value">{{ post.likes || 0 }}</span>
                      </div>
                    </div>
                  </Transition>
                </div>
                <button class="action-btn" title="编辑" @click="handleEditPost(post)">
                  <NIcon size="16"><CreateOutline /></NIcon>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <NModal
        :show="showStatsModal"
        :on-update:show="(val) => !val && handleCloseStats()"
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

    <!-- Edit mode -->
    <div v-else key="edit" class="edit-layout">
      <aside class="edit-sidebar">
        <button class="sidebar-back" @click="exitEdit">← 返回</button>
        <div class="sidebar-items">
          <button
            v-for="p in filteredPosts"
            :key="p.id"
            class="sidebar-item"
            :class="{ active: !isCreatingNew && p.id === editingPost?.id }"
            @click="switchEditPost(p)"
          >
            <div class="sidebar-item-title">{{ p.title || '无标题' }}</div>
            <div class="sidebar-item-meta">
              <span class="sidebar-item-status" :class="p.status || 'draft'"></span>
              <span>{{ p.created_at?.slice(0, 10) || '' }}</span>
            </div>
          </button>
        </div>
      </aside>

      <main class="edit-main">
        <div class="edit-topbar">
          <div class="edit-topbar-left">
            <template v-if="isCreatingNew">
              <span class="topbar-label">新建文章</span>
            </template>
            <ArTag v-else :color="getStatus(editingPost!).color" type="light">
              {{ getStatus(editingPost!).label }}
            </ArTag>
            <ArWheelPicker
              :options="[...accessLevels]"
              v-model="editorAccess"
              title="帖子可见权限：P0=仅管理员 · P5=所有人可见"
            />
          </div>
          <div class="edit-topbar-tags">
            <div class="topbar-tag-list">
              <ArTag
                v-for="(tag, i) in editorTags"
                :key="i"
                color="primary"
                type="light"
                closable
                @close="removeEditorTag(tag)"
              >
                {{ tag }}
              </ArTag>
            </div>
            <input
              v-model="tagInputValue"
              class="tag-input-inline"
              placeholder="标签"
              @keydown="handleTagKeydown"
            />
          </div>
          <div class="edit-topbar-actions">
            <ArButton type="ghost" @click="exitEdit">取消</ArButton>
            <ArButton type="primary" :loading="saving" :disabled="saving" @click="saveCurrent">
              {{ isCreatingNew ? '发布' : '保存' }}
            </ArButton>
          </div>
        </div>
        <div class="edit-editor">
          <PostEditor
            ref="editorRef"
            :post="isCreatingNew ? null : editingPost"
            :loading="saving"
            hide-footer
            @save="handleSaveComplete"
            @cancel="exitEdit"
          />
        </div>
      </main>
    </div>
  </Transition>
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
import ArWheelPicker from '@/components/ui/ArWheelPicker.vue'
import PostEditor from '@/components/blog/PostEditor.vue'
import { getMyPostsApi, type BlogPost } from '@/services/api'
import { useUserStore } from '@/store/modules/user'

type PostTab = 'all' | 'published' | 'draft'

const router = useRouter()
const userStore = useUserStore()
const editorRef = ref<InstanceType<typeof PostEditor> | null>(null)
const loading = ref(false)
const saving = ref(false)
const posts = ref<BlogPost[]>([])
const activeTab = ref<PostTab>('all')
const isEditorOpen = ref(false)
const isCreatingNew = ref(false)
const editingPost = ref<BlogPost | null>(null)
const tagInputValue = ref('')
const editorTags = ref<string[]>([])
const accessLevels = [0, 1, 2, 3, 4, 5] as const
const editorAccess = ref<number>(userStore.level ?? 5)

const statsPost = ref<BlogPost | null>(null)
const showStatsModal = ref(false)
const hoveredPost = ref<BlogPost | null>(null)

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

// Browse actions
const handleNewPost = () => {
  isCreatingNew.value = true
  editingPost.value = null
  editorTags.value = []
  editorAccess.value = userStore.level ?? 5
  isEditorOpen.value = true
}
const handleOpenPost = (post: BlogPost) => router.push(`/blog/${post.slug}`)

const handleViewStats = (post: BlogPost) => {
  if (statsPost.value?.id === post.id) {
    handleCloseStats()
    return
  }
  statsPost.value = post
  showStatsModal.value = true
}

const handleCloseStats = () => {
  showStatsModal.value = false
  statsPost.value = null
}

// Edit actions
const handleEditPost = (post: BlogPost) => {
  isCreatingNew.value = false
  editingPost.value = post
  editorTags.value = [...(post.tags || [])]
  editorAccess.value = (post.required_level as number) ?? 5
  isEditorOpen.value = true
}

const exitEdit = () => {
  isEditorOpen.value = false
  isCreatingNew.value = false
  editingPost.value = null
  editorTags.value = []
}

const switchEditPost = (post: BlogPost) => {
  isCreatingNew.value = false
  editingPost.value = post
  editorTags.value = [...(post.tags || [])]
  editorAccess.value = (post.required_level as number) ?? 5
}

const saveCurrent = () => {
  editorRef.value?.updateMeta({ tags: editorTags.value, requiredLevel: editorAccess.value })
  editorRef.value?.handleSave()
}

const handleSaveComplete = async () => {
  saving.value = true
  try {
    await fetchData()
  } finally {
    saving.value = false
  }
  exitEdit()
}

// ── Tag helpers ──
const addEditorTag = () => {
  const t = tagInputValue.value.trim()
  if (t && !editorTags.value.includes(t)) {
    editorTags.value.push(t)
  }
  tagInputValue.value = ''
}

const removeEditorTag = (tag: string) => {
  editorTags.value = editorTags.value.filter((t) => t !== tag)
}

const handleTagKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    addEditorTag()
  }
}

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

.post-section {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

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

.post-date {
  font-size: 12px;
  color: var(--text-tertiary);
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.action-btn-wrap {
  position: relative;
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

.stats-tip {
  position: absolute;
  bottom: calc(100% + 6px);
  right: 0;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  white-space: nowrap;
  z-index: 50;
  min-width: 100px;
}

.tip-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
}

.tip-label {
  color: var(--text-tertiary);
}

.tip-value {
  color: var(--text-primary);
  font-weight: var(--font-weight-semibold);
  font-variant-numeric: tabular-nums;
}

.tip-enter-active,
.tip-leave-active {
  transition: all 0.15s ease;
}

.tip-enter-from,
.tip-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

.empty-state {
  text-align: center;
  padding: 48px 0;
  color: var(--text-tertiary);
  font-size: 14px;
}

.empty-state p {
  margin: 0;
}

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

/* Edit mode */
.mode-enter-active,
.mode-leave-active {
  transition: all 0.22s ease;
}

.mode-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.mode-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.topbar-label {
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.edit-layout {
  display: flex;
  gap: 0;
  height: calc(100vh - 56px - var(--content-padding) * 2);
  margin: calc(-1 * var(--content-padding));
  background: var(--surface-color);
  overflow: hidden;
}

.edit-sidebar {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
  background: var(--bg-inset-color);
}

.sidebar-back {
  border: 0;
  border-bottom: 1px solid var(--border-color);
  background: transparent;
  padding: 14px 16px;
  font-size: 14px;
  font-family: var(--font-sans);
  color: var(--text-primary);
  cursor: pointer;
  text-align: left;
  font-weight: var(--font-weight-medium);
  transition: background var(--transition-fast);
  flex-shrink: 0;
}

.sidebar-back:hover {
  background: var(--surface-strong-color);
}

.sidebar-items {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.sidebar-item {
  display: block;
  width: 100%;
  border: 0;
  border-left: 3px solid transparent;
  background: transparent;
  padding: 12px 16px;
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
}

.sidebar-item:hover {
  background: var(--surface-hover-color);
  border-left-color: var(--border-color);
}

.sidebar-item.active {
  background: var(--primary-light-color);
  border-left-color: var(--primary-color);
}

.sidebar-item-title {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-weight: var(--font-weight-medium);
}

.sidebar-item.active .sidebar-item-title {
  color: var(--primary-color);
}

.sidebar-item-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.sidebar-item-status {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.sidebar-item-status.published {
  background: var(--success-color);
}

.sidebar-item-status.draft {
  background: var(--accent-yellow);
}

.sidebar-item-status.pending {
  background: var(--accent-orange, #e8a817);
}

.edit-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.edit-topbar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--surface-color);
  flex-shrink: 0;
  flex-wrap: wrap;
}

.edit-topbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.edit-topbar-tags {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 140px;
}

.topbar-tag-list {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.tag-input-inline {
  border: none;
  border-bottom: 1px solid var(--border-color);
  outline: none;
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 13px;
  padding: 4px 0;
  min-width: 70px;
  flex: 1;
  transition: border-color var(--transition-fast);
}

.tag-input-inline:focus {
  border-bottom-color: var(--primary-color);
}

.tag-input-inline::placeholder {
  color: var(--text-tertiary);
}

.edit-topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.edit-editor {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-header {
    flex-direction: column;
  }

  .edit-sidebar {
    width: 160px;
  }
}
</style>
