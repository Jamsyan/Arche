<template>
  <div class="post-home">
    <div class="layout-main">
      <!-- 左侧：标签列表 -->
      <aside class="tag-sidebar">
        <div class="tag-header">
          <icon-bookmark class="tag-icon" />
          <span>标签</span>
          <span class="tag-count">{{ allTags.length }}</span>
        </div>
        <div class="tag-list">
          <div
            class="tag-item"
            :class="{ active: selectedTag === '' }"
            @click="clearTag"
          >
            <icon-home class="tag-item-icon" />
            <span>全部</span>
          </div>
          <div
            v-for="tag in allTags"
            :key="tag.id"
            class="tag-item"
            :class="{ active: selectedTag === tag.name }"
            @click="selectTag(tag.name)"
          >
            <a-tag size="small" color="arcoblue">{{ tag.post_count || 0 }}</a-tag>
            <span class="tag-name">{{ tag.name }}</span>
          </div>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="content-main">
        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="toolbar-left">
            <span class="result-count">共 {{ total }} 篇</span>
            <div class="toolbar-search">
              <a-input-search
                v-model="searchQuery"
                placeholder="搜索文章..."
                search-button
                size="small"
                @search="onSearch"
                style="width: 200px"
              />
            </div>
          </div>
          <a-space>
            <!-- 视图切换 -->
            <a-radio-group v-model="viewMode" type="button" size="small">
              <a-radio value="compact">
                <icon-list :size="14" />
              </a-radio>
              <a-radio value="normal">
                <icon-menu :size="14" />
              </a-radio>
              <a-radio value="card">
                <icon-apps :size="14" />
              </a-radio>
            </a-radio-group>
          </a-space>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <a-spin size="large" />
        </div>

        <!-- 空状态 -->
        <a-empty v-else-if="posts.length === 0" description="暂无文章" />

        <!-- 紧凑型列表 -->
        <div v-else-if="viewMode === 'compact'" class="post-list-compact">
          <div
            v-for="item in posts"
            :key="item.slug"
            class="post-item-compact"
            @click="goToPost(item.slug)"
          >
            <div class="post-compact-main">
              <a-avatar :size="24" class="post-author-avatar">
                {{ (item.author_username || 'U')[0].toUpperCase() }}
              </a-avatar>
              <span class="post-author">{{ item.author_username }}</span>
              <span class="post-title-compact">{{ item.title }}</span>
            </div>
            <div class="post-compact-meta">
              <span class="meta-item">
                <icon-clock-circle :size="12" />
                {{ formatDate(item.created_at) }}
              </span>
              <span class="meta-item">
                <icon-thumb-up :size="12" />
                {{ item.likes || 0 }}
              </span>
            </div>
          </div>
        </div>

        <!-- 普通列表 -->
        <div v-else-if="viewMode === 'normal'" class="post-list-normal">
          <div
            v-for="item in posts"
            :key="item.slug"
            class="post-item-normal"
            @click="goToPost(item.slug)"
          >
            <div class="post-normal-header">
              <a-avatar :size="28" class="post-author-avatar">
                {{ (item.author_username || 'U')[0].toUpperCase() }}
              </a-avatar>
              <div class="post-normal-info">
                <span class="post-author">{{ item.author_username }}</span>
                <span class="post-time">{{ formatDate(item.created_at) }}</span>
              </div>
              <LevelBadge :level="getLevel(item.quality_score)" />
            </div>
            <h3 class="post-title-normal">{{ item.title }}</h3>
            <p class="post-excerpt">{{ item.excerpt || item.content?.slice(0, 100) + '...' }}</p>
            <div class="post-normal-footer">
              <a-space size="medium">
                <span class="meta-item">
                  <icon-eye :size="12" />
                  {{ item.views || 0 }}
                </span>
                <span class="meta-item">
                  <icon-thumb-up :size="12" />
                  {{ item.likes || 0 }}
                </span>
              </a-space>
              <a-tag
                v-for="tag in (item.tags || []).slice(0, 2)"
                :key="tag.name"
                size="small"
                color="arcoblue"
              >
                {{ tag.name }}
              </a-tag>
            </div>
          </div>
        </div>

        <!-- 卡片视图 -->
        <div v-else class="post-list-card">
          <div
            v-for="item in posts"
            :key="item.slug"
            class="post-item-card"
            @click="goToPost(item.slug)"
          >
            <div class="post-card-cover" v-if="false">
              <!-- 未来：封面图 -->
            </div>
            <div class="post-card-body">
              <div class="post-card-header">
                <a-avatar :size="32" class="post-author-avatar">
                  {{ (item.author_username || 'U')[0].toUpperCase() }}
                </a-avatar>
                <div class="post-card-author">
                  <span class="post-author">{{ item.author_username }}</span>
                  <span class="post-time">{{ formatDate(item.created_at) }}</span>
                </div>
              </div>
              <h3 class="post-title-card">{{ item.title }}</h3>
              <p class="post-excerpt">{{ item.excerpt || item.content?.slice(0, 80) + '...' }}</p>
              <div class="post-card-footer">
                <a-space size="large">
                  <span class="meta-item">
                    <icon-eye :size="12" />
                    {{ item.views || 0 }}
                  </span>
                  <span class="meta-item">
                    <icon-thumb-up :size="12" />
                    {{ item.likes || 0 }}
                  </span>
                </a-space>
                <LevelBadge :level="getLevel(item.quality_score)" />
              </div>
              <div class="post-card-tags" v-if="item.tags?.length > 0">
                <a-tag
                  v-for="tag in item.tags.slice(0, 3)"
                  :key="tag.name"
                  size="small"
                  color="arcoblue"
                >
                  {{ tag.name }}
                </a-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrap" v-if="total > pageSize">
          <a-pagination
            :total="total"
            :current="page"
            :page-size="pageSize"
            @change="onPageChange"
            show-total
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { blog } from '../../api'
import LevelBadge from '../LevelBadge.vue'
import {
  IconList,
  IconMenu,
  IconApps,
  IconBookmark,
  IconHome,
  IconClockCircle,
  IconThumbUp,
  IconEye,
} from '@arco-design/web-vue/es/icon'

const router = useRouter()

// 状态
const posts = ref([])
const loading = ref(true)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchQuery = ref('')
const viewMode = ref('normal') // compact | normal | card

// 标签
const allTags = ref([])
const tagsLoading = ref(false)
const selectedTag = ref('')

// 加载标签
async function fetchTags() {
  tagsLoading.value = true
  try {
    const data = await blog.listTags({ page: 1, page_size: 500 })
    allTags.value = (data?.items || [])
  } catch {
    allTags.value = []
  } finally {
    tagsLoading.value = false
  }
}

// 加载帖子
async function fetchPosts() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      sort_by: 'created_at',
    }
    if (searchQuery.value) {
      params.q = searchQuery.value
    }
    if (selectedTag.value) {
      params.tag = selectedTag.value
    }
    const data = await blog.listPosts(params)
    posts.value = data.items || []
    total.value = data.total || 0
  } catch {
    posts.value = []
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  fetchPosts()
}

function onPageChange(p) {
  page.value = p
  fetchPosts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function selectTag(tagName) {
  selectedTag.value = tagName
  page.value = 1
  fetchPosts()
}

function clearTag() {
  selectedTag.value = ''
  page.value = 1
  fetchPosts()
}

function goToPost(slug) {
  router.push(`/post/${slug}`)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

function getLevel(qualityScore) {
  const score = qualityScore ?? 0
  if (score >= 5) return 0
  if (score >= 4) return 1
  if (score >= 3) return 2
  if (score >= 2) return 3
  if (score >= 1) return 4
  return 5
}

watch([page], () => {
  fetchPosts()
})

onMounted(() => {
  fetchPosts()
  fetchTags()
})
</script>

<style scoped>
.post-home {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 主布局 - 三栏顶边 */
.layout-main {
  flex: 1;
  display: grid;
  grid-template-columns: 200px 1fr;
  min-height: 0;
}

/* 标签侧边栏 - 带右边框分隔 */
.tag-sidebar {
  height: 100%;
  overflow-y: auto;
  border-right: 1px solid var(--color-border-1);
  padding: 0 16px;
  background: var(--color-bg-1);
}

.tag-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 0 12px;
  font-weight: 600;
  color: var(--color-text-2);
  border-bottom: 1px solid var(--color-border-1);
  margin-bottom: 8px;
}

.tag-icon {
  width: 16px;
  height: 16px;
  color: var(--color-primary);
}

.tag-count {
  margin-left: auto;
  font-size: 12px;
  color: var(--color-text-4);
  font-weight: normal;
}

.tag-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-bottom: 16px;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--color-text-2);
  transition: all 0.15s;
}

.tag-item:hover {
  background: var(--color-fill-2);
  color: var(--color-text-1);
}

.tag-item.active {
  background: var(--color-primary-light-1);
  color: var(--color-primary);
  font-weight: 500;
}

.tag-item-icon {
  width: 14px;
  height: 14px;
}

.tag-name {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 内容区 */
.content-main {
  min-width: 0;
  padding: 0 24px;
  background: var(--color-bg-1);
}

/* 工具栏 */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 16px 0 12px;
  border-bottom: 1px solid var(--color-border-1);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.result-count {
  font-size: 14px;
  color: var(--color-text-3);
}

.toolbar-search :deep(.arco-input-search .arco-input-wrapper) {
  border-radius: 16px;
  background: var(--color-fill-2);
  border-color: var(--color-border-1);
}

.toolbar-search :deep(.arco-input-search .arco-input-wrapper:focus-within) {
  border-color: var(--primary-light-3);
  background: var(--color-bg-1);
  box-shadow: 0 2px 8px rgba(92, 61, 46, 0.1);
}

.toolbar-search :deep(.arco-input-search .arco-btn) {
  border-radius: 0 16px 16px 0;
  background: var(--primary);
  border-color: var(--primary);
}

/* 加载状态 */
.loading-state {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

/* 紧凑型列表 */
.post-list-compact {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: var(--color-border-1);
  border-radius: 8px;
  overflow: hidden;
}

.post-item-compact {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: white;
  cursor: pointer;
  transition: background 0.15s;
}

.post-item-compact:hover {
  background: var(--color-fill-2);
}

.post-compact-main {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.post-author-avatar {
  background: var(--color-primary-light-3);
  color: var(--color-primary);
  font-size: 10px;
  flex-shrink: 0;
}

.post-author {
  font-size: 13px;
  color: var(--color-text-3);
  flex-shrink: 0;
}

.post-title-compact {
  font-size: 14px;
  color: var(--color-text-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-compact-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

/* 普通列表 */
.post-list-normal {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-item-normal {
  background: white;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.post-item-normal:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transform: translateY(-1px);
}

.post-normal-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.post-normal-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.post-time {
  font-size: 12px;
  color: var(--color-text-4);
}

.post-title-normal {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-1);
}

.post-excerpt {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--color-text-3);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.post-normal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 卡片视图 */
.post-list-card {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.post-item-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.post-item-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.post-card-cover {
  height: 120px;
  background: linear-gradient(135deg, var(--color-primary-light-2), var(--color-primary-light-3));
}

.post-card-body {
  padding: 16px;
}

.post-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.post-card-author {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.post-title-card {
  margin: 0 0 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.post-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* 通用样式 */
.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-3);
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--color-border-1);
}

/* 响应式 */
@media (max-width: 768px) {
  .layout-main {
    grid-template-columns: 1fr;
  }
  .tag-sidebar {
    display: none;
  }
}
</style>
