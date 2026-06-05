<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NDataTable, NIcon, NTag, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import {
  AppsOutline,
  ListOutline,
  PersonOutline,
  PricetagOutline,
  ReorderThreeOutline,
  SearchOutline
} from '@vicons/ionicons5'
import { PostCard } from '@/components/blog'
import { getBlogPostsApi, type BlogPost } from '@/services/api/blog'
import type { MockExploreItem } from '@/services/mock/types'

type ExploreFilterMode = 'tag' | 'author'
type ExploreViewMode = 'card' | 'wide-row' | 'compact-row'

const filterMode = ref<ExploreFilterMode>('tag')
const selectedTags = ref<string[]>([])
const tagFilter = ref('')
const selectedAuthors = ref<string[]>([])
const authorFilter = ref('')
const contentSearch = ref('')
const viewMode = ref<ExploreViewMode>('card')

const router = useRouter()
const route = useRoute()

const message = useMessage()
const exploreItems = ref<MockExploreItem[]>([])
const allTags = ref<string[]>([])
const allAuthors = ref<string[]>([])
const loading = ref(false)

const convertBlogPostToExploreItem = (post: BlogPost, index: number): MockExploreItem => {
  const gradientCovers = [
    'linear-gradient(135deg, #f2dfc7, #dcbca0)',
    'linear-gradient(135deg, #d9c8b0, #9f8169)',
    'linear-gradient(135deg, #e8d7bf, #c0a688)',
    'linear-gradient(135deg, #d0c2b1, #8f7560)'
  ]
  return {
    id: index + 1,
    title: post.title || '',
    author: post.author_username || '匿名',
    tags: post.tags || [],
    date: (post.created_at || '').slice(0, 10),
    likes: post.likes || 0,
    favorites: Math.max(1, Math.round((post.likes || 0) * 0.65)),
    content: post.content || '',
    excerpt: (post.content || '').slice(0, 60) || '',
    cover: gradientCovers[index % gradientCovers.length] ?? ''
  }
}

const fetchExploreData = async () => {
  loading.value = true
  try {
    const result = await getBlogPostsApi({ page: 1, page_size: 20, sort_by: 'created_at' })
    if (result.list && result.list.length > 0) {
      exploreItems.value = result.list.map(convertBlogPostToExploreItem)
      const tagSet = new Set<string>()
      const authorSet = new Set<string>()
      result.list.forEach((post) => {
        ;(post.tags || []).forEach((tag) => tagSet.add(tag))
        if (post.author_username) authorSet.add(post.author_username)
      })
      allTags.value = ['全部', ...Array.from(tagSet)]
      allAuthors.value = ['全部作者', ...Array.from(authorSet)]
    } else {
      exploreItems.value = []
      allTags.value = ['全部']
      allAuthors.value = ['全部作者']
    }
  } catch {
    message.error('获取文章列表失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // 从 URL 读取初始筛选参数
  const q = route.query
  if (q.mode === 'tag' || q.mode === 'author') filterMode.value = q.mode
  if (q.tags) selectedTags.value = String(q.tags).split(',').filter(Boolean)
  if (q.authors) selectedAuthors.value = String(q.authors).split(',').filter(Boolean)
  if (q.view === 'card' || q.view === 'wide-row' || q.view === 'compact-row')
    viewMode.value = q.view
  if (q.q) contentSearch.value = String(q.q)

  await fetchExploreData()
})

watch(
  [filterMode, selectedTags, selectedAuthors, viewMode, contentSearch],
  () => {
    const query: Record<string, string> = {}
    if (filterMode.value !== 'tag') query.mode = filterMode.value
    if (selectedTags.value.length > 0) query.tags = selectedTags.value.join(',')
    if (selectedAuthors.value.length > 0) query.authors = selectedAuthors.value.join(',')
    if (viewMode.value !== 'card') query.view = viewMode.value
    if (contentSearch.value) query.q = contentSearch.value

    const keys = Object.keys(query)
    router.replace(keys.length ? { path: route.path, query } : { path: route.path })
  },
  { deep: true }
)

const isOptionChecked = (option: string) => {
  if (filterMode.value === 'tag') {
    return option === '全部' ? selectedTags.value.length === 0 : selectedTags.value.includes(option)
  }
  return option === '全部作者'
    ? selectedAuthors.value.length === 0
    : selectedAuthors.value.includes(option)
}

const toggleSidebarOption = (option: string) => {
  if (filterMode.value === 'tag') {
    if (option === '全部') {
      selectedTags.value = []
      return
    }
    selectedTags.value = selectedTags.value.includes(option)
      ? selectedTags.value.filter((tag) => tag !== option)
      : [...selectedTags.value, option]
    return
  }
  if (option === '全部作者') {
    selectedAuthors.value = []
    return
  }
  selectedAuthors.value = selectedAuthors.value.includes(option)
    ? selectedAuthors.value.filter((author) => author !== option)
    : [...selectedAuthors.value, option]
}

type CompoundFilterChip = {
  type: '标签' | '用户'
  value: string
  isDefault: boolean
}

const activeCompoundFilters = computed<CompoundFilterChip[]>(() => [
  ...(selectedTags.value.length > 0
    ? selectedTags.value.map((value) => ({ type: '标签' as const, value, isDefault: false }))
    : [{ type: '标签' as const, value: '全部', isDefault: true }]),
  ...(selectedAuthors.value.length > 0
    ? selectedAuthors.value.map((value) => ({ type: '用户' as const, value, isDefault: false }))
    : [{ type: '用户' as const, value: '全部作者', isDefault: true }])
])

function toBlogPost(item: MockExploreItem): BlogPost {
  return {
    id: String(item.id),
    slug: item.title,
    title: item.title,
    content: item.content || item.excerpt,
    tags: item.tags,
    author_username: item.author,
    created_at: item.date,
    likes: item.likes,
    views: 0
  }
}

const handleOpenItem = (post: BlogPost) => {
  router.push(`/blog/${post.slug}`)
}

const removeCompoundFilter = (type: '标签' | '用户', value: string) => {
  if (type === '标签') {
    selectedTags.value = selectedTags.value.filter((tag) => tag !== value)
    return
  }
  selectedAuthors.value = selectedAuthors.value.filter((author) => author !== value)
}

const handleCompoundFilterChipClick = (chip: CompoundFilterChip) => {
  if (chip.isDefault) {
    if (chip.type === '标签') {
      selectedTags.value = []
      return
    }
    selectedAuthors.value = []
    return
  }
  removeCompoundFilter(chip.type, chip.value)
}

const visibleTags = computed(() => {
  const filterValue = tagFilter.value.trim().toLowerCase()
  if (!filterValue) {
    return allTags.value
  }
  return allTags.value.filter((tag) => tag.toLowerCase().includes(filterValue))
})

const visibleAuthors = computed(() => {
  const filterValue = authorFilter.value.trim().toLowerCase()
  if (!filterValue) {
    return allAuthors.value
  }
  return allAuthors.value.filter((author) => author.toLowerCase().includes(filterValue))
})

const filteredItems = computed(() => {
  let list = [...exploreItems.value]
  const keyword = contentSearch.value.trim().toLowerCase()
  if (keyword) {
    list = list.filter(
      (item) =>
        item.title.toLowerCase().includes(keyword) ||
        item.excerpt.toLowerCase().includes(keyword) ||
        item.author.toLowerCase().includes(keyword)
    )
  }

  if (selectedAuthors.value.length > 0) {
    list = list.filter((item) => selectedAuthors.value.includes(item.author))
  }

  if (selectedTags.value.length > 0) {
    list = list.filter((item) => item.tags.some((tag: string) => selectedTags.value.includes(tag)))
  }

  list.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  return list
})

const compactColumns: DataTableColumns<any> = [
  {
    title: '作者',
    key: 'author',
    width: 120,
    filterOptions: allAuthors.value
      .filter((author) => author !== '全部作者')
      .map((author) => ({ label: author, value: author })),
    filter: (value, row) => row.author === value
  },
  {
    title: '标题',
    key: 'title',
    minWidth: 220,
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: '点赞',
    key: 'likes',
    width: 88,
    sorter: (a, b) => a.likes - b.likes
  },
  {
    title: '收藏',
    key: 'favorites',
    width: 88,
    sorter: (a, b) => a.favorites - b.favorites
  },
  {
    title: '热度',
    key: 'heat',
    width: 88,
    sorter: (a, b) => a.heat - b.heat
  },
  {
    title: '创建时间',
    key: 'createdAt',
    width: 140,
    sorter: (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
  }
]

const compactRows = computed(() =>
  filteredItems.value.map((item) => ({
    key: item.id,
    createdAt: item.date,
    heat: item.likes * 2 + item.favorites,
    ...item
  }))
)
</script>

<template>
  <div class="explore-page">
    <section class="explore-body">
      <aside class="tag-sidebar">
        <div class="filter-combo">
          <div class="combo-top">
            <NIcon class="search-leading-icon" size="16" aria-hidden="true">
              <SearchOutline />
            </NIcon>
            <input
              class="search-input"
              type="search"
              :value="filterMode === 'tag' ? tagFilter : authorFilter"
              :placeholder="filterMode === 'tag' ? '筛选标签' : '筛选作者'"
              @input="
                (e) =>
                  filterMode === 'tag'
                    ? (tagFilter = (e.target as HTMLInputElement).value)
                    : (authorFilter = (e.target as HTMLInputElement).value)
              "
            />
          </div>
          <div class="combo-bottom">
            <div
              class="combo-bottom-inner"
              :class="filterMode === 'tag' ? 'mode-tag' : 'mode-author'"
            >
              <button
                class="mode-button"
                :class="{ active: filterMode === 'tag' }"
                type="button"
                @click="filterMode = 'tag'"
              >
                <NIcon size="14" aria-hidden="true">
                  <PricetagOutline />
                </NIcon>
                <span>标签</span>
              </button>
              <button
                class="mode-button"
                :class="{ active: filterMode === 'author' }"
                type="button"
                @click="filterMode = 'author'"
              >
                <NIcon size="14" aria-hidden="true">
                  <PersonOutline />
                </NIcon>
                <span>用户</span>
              </button>
            </div>
          </div>
        </div>
        <Transition name="tag-stack-panel" mode="out-in">
          <div :key="filterMode" class="tag-stack">
            <NTag
              v-for="option in filterMode === 'tag' ? visibleTags : visibleAuthors"
              :key="option"
              checkable
              :checked="isOptionChecked(option)"
              class="stack-tag"
              @update:checked="() => toggleSidebarOption(option)"
            >
              {{ option }}
            </NTag>
          </div>
        </Transition>
      </aside>

      <main class="content">
        <section class="content-search-panel">
          <div class="content-search-row">
            <NIcon class="search-leading-icon content-search-icon" size="16" aria-hidden="true">
              <SearchOutline />
            </NIcon>
            <input
              v-model.trim="contentSearch"
              class="content-search-input"
              type="search"
              placeholder="搜索内容"
            />
          </div>
        </section>
        <section class="content-display-panel">
          <div class="display-filter-bar">
            <TransitionGroup name="compound-chip" tag="div" class="compound-filter-tabs">
              <button
                v-for="chip in activeCompoundFilters"
                :key="`${chip.type}-${chip.value}`"
                type="button"
                class="compound-chip"
                :class="{ 'is-default': chip.isDefault }"
                @click="handleCompoundFilterChipClick(chip)"
              >
                {{ chip.type }}: {{ chip.value }}{{ chip.isDefault ? '' : ' ×' }}
              </button>
            </TransitionGroup>
            <div class="view-switch" :class="viewMode">
              <button
                type="button"
                :class="{ active: viewMode === 'card' }"
                @click="viewMode = 'card'"
                aria-label="卡片视图"
                title="卡片视图"
              >
                <NIcon size="15" aria-hidden="true">
                  <AppsOutline />
                </NIcon>
              </button>
              <button
                type="button"
                :class="{ active: viewMode === 'wide-row' }"
                @click="viewMode = 'wide-row'"
                aria-label="宽行视图"
                title="宽行视图"
              >
                <NIcon size="15" aria-hidden="true">
                  <ListOutline />
                </NIcon>
              </button>
              <button
                type="button"
                :class="{ active: viewMode === 'compact-row' }"
                @click="viewMode = 'compact-row'"
                aria-label="窄行视图"
                title="窄行视图"
              >
                <NIcon size="15" aria-hidden="true">
                  <ReorderThreeOutline />
                </NIcon>
              </button>
            </div>
          </div>
          <Transition name="view-mode" mode="out-in">
            <NDataTable
              v-if="viewMode === 'compact-row'"
              key="compact-row-table"
              class="compact-table"
              :columns="compactColumns"
              :data="compactRows"
              :row-key="(row: any) => row.key"
              :pagination="{
                pageSize: 10,
                pageSizes: [],
                showSizePicker: false,
                showQuickJumper: false
              }"
            />
            <div v-else key="blog-card-list" class="display-list" :class="`mode-${viewMode}`">
              <PostCard
                v-for="item in filteredItems"
                :key="item.id"
                :post="toBlogPost(item)"
                :layout="viewMode === 'wide-row' ? 'list' : 'grid'"
                :show-cover="viewMode === 'card'"
                :show-excerpt="true"
                @open="handleOpenItem"
              />
            </div>
          </Transition>
        </section>
      </main>
    </section>
  </div>
</template>

<style scoped>
.explore-page {
  width: min(1200px, 100%);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--layout-gap);
  font-family: var(--font-sans);
}

.header {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-lg);
  align-items: center;
}

.header-title p {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.header-title h1 {
  margin: 6px 0 0;
  font-size: 28px;
}

.explore-body {
  display: grid;
  grid-template-columns: minmax(280px, 300px) minmax(0, 1fr);
  gap: var(--layout-gap);
  overflow: visible;
  align-items: start;
}

.tag-sidebar {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  gap: var(--spacing-md);
  width: 100%;
  max-width: 320px;
  min-height: 360px;
  padding: var(--spacing-md);
  box-sizing: border-box;
  position: sticky;
  top: 87px;
  align-self: start;
  max-height: calc(100vh - 87px);
  overflow-y: auto;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
}

.filter-combo {
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 100%;
  max-width: 250px;
  min-height: 0;
  margin: var(--spacing-sm) 5px;
}

.combo-top {
  width: 100%;
  height: 52px;
  background: var(--bg-inset-color);
  border-radius: var(--radius-full) var(--radius-lg) 0 var(--radius-full);
  border: 1px solid var(--border-color);
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: nowrap;
  text-align: left;
  padding: 0 10px;
  position: relative;
}

.combo-top::after {
  position: absolute;
  right: 0;
  bottom: -1px;
  width: 56%;
  height: 2px;
  background: var(--bg-inset-color);
  content: '';
}

.search-leading-icon {
  position: absolute;
  left: 22px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
  transition: color var(--transition-normal);
}

.combo-bottom {
  width: 56%;
  height: 46px;
  align-self: flex-end;
  background: var(--bg-inset-color);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  border: 1px solid var(--border-color);
  border-top-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
}

.combo-bottom-inner {
  width: 127px;
  height: 75%;
  background: var(--surface-inset-color);
  border-radius: var(--radius-full);
  transform: translateY(-2px);
  border: 1px solid var(--border-color);
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  padding: 3px;
  box-sizing: border-box;
  position: relative;
}

.combo-bottom-inner::before {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: calc(50% - 3px);
  height: calc(100% - 6px);
  border-radius: var(--radius-full);
  background: var(--primary-color);
  transition: transform 0.28s ease;
  z-index: 0;
}

.combo-bottom-inner.mode-author::before {
  transform: translateX(100%);
}

.mode-button {
  height: 100%;
  border: 0;
  border-radius: var(--radius-full);
  background: transparent;
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: color var(--transition-normal);
  position: relative;
  z-index: 1;
}

.mode-button.active {
  color: #fff;
}

.search-input {
  width: 100%;
  max-width: 237px;
  height: 40px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-color);
  background: var(--surface-color);
  padding: 0 14px 0 38px;
  color: var(--text-primary);
  outline: none;
  font-size: 13px;
  text-align: left;
  transition:
    border-color var(--transition-normal),
    box-shadow var(--transition-normal),
    background var(--transition-normal),
    transform var(--transition-normal);
}

.search-input:focus {
  border-color: var(--primary-color);
  box-shadow:
    0 0 0 3px var(--primary-light-color),
    0 8px 20px rgba(58, 90, 74, 0.16);
  background: var(--surface-color);
  transform: translateY(-1px);
}

.combo-top:focus-within .search-leading-icon {
  color: var(--primary-color);
}

.tag-stack {
  display: flex;
  flex-wrap: wrap;
  flex: 1;
  gap: var(--spacing-sm);
  overflow-y: auto;
  min-height: 0;
  width: 100%;
  max-width: 250px;
  margin: 5px;
  padding: var(--spacing-md);
  box-sizing: border-box;
  align-content: flex-start;
  background: var(--bg-inset-color);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.stack-tag {
  margin: 0;
}

.tag-stack-panel-enter-active,
.tag-stack-panel-leave-active {
  transition:
    opacity var(--transition-normal),
    transform var(--transition-normal);
}

.tag-stack-panel-enter-from,
.tag-stack-panel-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

.content {
  min-height: 360px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.content-search-panel {
  padding: 0;
  border: 0;
  background: transparent;
}

.content-search-row {
  position: relative;
}

.content-search-icon {
  left: 14px;
}

.content-search-input {
  width: 100%;
  height: 40px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-color);
  background: var(--surface-color);
  padding: 0 14px 0 38px;
  color: var(--text-primary);
  outline: none;
  font-size: 13px;
  transition:
    border-color var(--transition-normal),
    box-shadow var(--transition-normal),
    background var(--transition-normal),
    transform var(--transition-normal);
}

.content-search-input:focus {
  border-color: var(--primary-color);
  box-shadow:
    0 0 0 3px var(--primary-light-color),
    0 8px 20px rgba(58, 90, 74, 0.16);
  background: var(--surface-color);
  transform: translateY(-1px);
}

.content-search-row:focus-within .content-search-icon {
  color: var(--primary-color);
}

.content-display-panel {
  flex: 1;
  min-height: 0;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  background: var(--surface-color);
  padding: var(--content-padding);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.display-filter-bar {
  display: flex;
  align-items: end;
  gap: 6px;
  flex-wrap: wrap;
}

.compound-filter-tabs {
  min-height: 30px;
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  flex-wrap: wrap;
}

.compound-chip {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-full);
  background: var(--bg-inset-color);
  color: var(--text-primary);
  padding: 4px 10px;
  font-size: 12px;
  cursor: pointer;
  font-family: var(--font-sans);
}

.compound-chip:hover {
  background: var(--surface-inset-color);
}

.compound-chip.is-default {
  border-style: dashed;
  color: var(--text-secondary);
  background: var(--bg-color);
}

.compound-chip.is-default:hover {
  background: var(--bg-inset-color);
}

.compound-chip-enter-active,
.compound-chip-leave-active {
  transition: all var(--transition-normal);
}

.compound-chip-enter-from,
.compound-chip-leave-to {
  opacity: 0;
  transform: translateY(4px) scale(0.96);
}

.compound-chip-move {
  transition: transform var(--transition-normal);
}

.view-mode-enter-active,
.view-mode-leave-active {
  transition: all var(--transition-normal);
}

.view-mode-enter-from,
.view-mode-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.view-switch {
  margin-left: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-full);
  background: var(--bg-inset-color);
  display: inline-flex;
  padding: 2px;
  gap: 2px;
}

.view-switch button {
  border: 0;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius-full);
  width: 32px;
  height: 28px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.view-switch button.active {
  background: var(--primary-color);
  color: #fff;
}

.display-list {
  flex: 1;
  min-height: 0;
  overflow: auto;
  scrollbar-gutter: stable;
  display: grid;
  gap: var(--spacing-sm);
}

.display-list.mode-card {
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
}

.display-list.mode-wide-row {
  grid-template-columns: 1fr;
}

.compact-table {
  min-height: 0;
}

.compact-table :deep(.n-data-table) {
  --n-td-color: var(--surface-color);
  --n-td-color-hover: var(--surface-strong-color);
  --n-th-color: var(--surface-inset-color);
  --n-border-color: var(--border-color);
  --n-th-text-color: var(--text-secondary);
  --n-td-text-color: var(--text-primary);
}

.compact-table :deep(.n-data-table .n-data-table-wrapper),
.compact-table :deep(.n-data-table .n-scrollbar-container),
.compact-table :deep(.n-data-table .n-data-table-base-table) {
  background: var(--surface-color);
  border-radius: var(--radius-md);
}

.compact-table :deep(.n-data-table thead th) {
  background: var(--surface-inset-color) !important;
  color: var(--text-secondary) !important;
}

.compact-table :deep(.n-data-table tbody td) {
  background: var(--surface-color) !important;
  color: var(--text-primary) !important;
}

.compact-table :deep(.n-data-table tbody tr:hover td) {
  background: var(--surface-strong-color) !important;
}

.compact-table :deep(.n-data-table-tbody > .n-data-table-tr) {
  animation: table-row-enter 0.28s ease both;
}

.compact-table :deep(.n-data-table-tbody > .n-data-table-tr:nth-child(1)) {
  animation-delay: 0.03s;
}

.compact-table :deep(.n-data-table-tbody > .n-data-table-tr:nth-child(2)) {
  animation-delay: 0.06s;
}

.compact-table :deep(.n-data-table-tbody > .n-data-table-tr:nth-child(3)) {
  animation-delay: 0.09s;
}

.compact-table :deep(.n-data-table-tbody > .n-data-table-tr:nth-child(n + 4)) {
  animation-delay: 0.12s;
}

@keyframes table-row-enter {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1100px) {
  .header {
    flex-direction: column;
    align-items: stretch;
  }

  .tag-sidebar {
    min-height: 360px;
  }

  .tag-stack {
    max-height: 180px;
  }
}
</style>
