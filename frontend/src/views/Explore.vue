<script setup lang="ts">
import { computed, defineComponent, h, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { NIcon, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import {
  AppsOutline,
  ListOutline,
  PersonOutline,
  PricetagOutline,
  ReorderThreeOutline,
  SearchOutline
} from '@vicons/ionicons5'
import ProTable from '@/components/ProTable.vue'

type ExploreFilterMode = 'tag' | 'author'
type ExploreViewMode = 'card' | 'wide-row' | 'compact-row'

const filterMode = ref<ExploreFilterMode>('tag')
const selectedTags = ref<string[]>([])
const tagFilter = ref('')
const selectedAuthors = ref<string[]>([])
const authorFilter = ref('')
const contentSearch = ref('')
const viewMode = ref<ExploreViewMode>('card')

const allTags = ref([
  '全部',
  '时光',
  '成长记录',
  '学习札记',
  '生活观察',
  '创作灵感',
  '技术实践',
  '旅行笔记',
  '摄影',
  '电影',
  '阅读',
  '心情随笔'
])

const allAuthors = ref([
  '全部作者',
  '锦年志编辑部',
  '林深',
  '阿野',
  '苏河',
  '南渡',
  '岚',
  '青禾',
  '江月',
  '秋迟'
])

const mockItems = ref([
  {
    id: 1,
    title: '春日河畔散记',
    author: '林深',
    tags: ['时光', '生活观察'],
    date: '2026-04-28',
    likes: 36,
    favorites: 12,
    content:
      '清晨的河面有一层薄雾，风从桥洞里穿过来，带着一点潮湿和青草气息。沿着石阶慢慢往下走，脚边的水纹被阳光切成碎片。后来我在长椅上坐了很久，看骑行的人一阵阵掠过，像时间被不断轻轻翻页。傍晚回程时，天空变成温柔的橙灰色，城市一下子慢下来。',
    excerpt: '记录周末在河边散步时的光影与心绪。',
    cover: 'linear-gradient(135deg, #f2dfc7, #dcbca0)'
  },
  {
    id: 2,
    title: '晚风与胶片',
    author: '青禾',
    tags: ['摄影', '时光'],
    date: '2026-04-18',
    likes: 92,
    favorites: 48,
    content:
      '那卷过期胶片在抽屉里躺了很久，冲洗出来的时候颗粒比预期更粗，色偏也很明显。可正是这种不稳定，让街角霓虹和路人的背影都像旧电影的片段。拍摄那天风很大，手抖得厉害，很多画面轻微虚焦，却意外地贴近记忆里的真实感。',
    excerpt: '一卷过期胶片拍出的意外颗粒感，反而更贴近记忆。',
    cover: 'linear-gradient(135deg, #d9c8b0, #9f8169)'
  },
  {
    id: 3,
    title: '学习札记：响应式布局',
    author: '苏河',
    tags: ['学习札记', '技术实践'],
    date: '2026-03-29',
    likes: 57,
    favorites: 21,
    content:
      '这次把页面从固定栅格改成响应式之后，最大的感受是“先定义结构，再谈样式”。我把主体分成导航、内容、辅助区三层，并用最小断点逐步增强，而不是一开始追求大屏精致。这样做的好处是，小屏体验稳定，大屏只是在此基础上获得更舒展的排版。',
    excerpt: '从网格到弹性布局，整理一套可复用的页面骨架。',
    cover: 'linear-gradient(135deg, #e8d7bf, #c0a688)'
  },
  {
    id: 4,
    title: '山城夜色速写',
    author: '阿野',
    tags: ['旅行笔记', '生活观察'],
    date: '2026-03-03',
    likes: 18,
    favorites: 9,
    content:
      '山城的夜色总带一点潮气，霓虹在坡道和台阶上被拉成长条，像湿润空气里的荧光笔触。站在高处往下看，车灯沿着弯路缓慢流动，远处偶尔传来模糊的音乐和人声。很多瞬间并不壮观，却有一种很私人的安静感，适合被慢慢记下来。',
    excerpt: '潮湿空气里的霓虹像被晕开的颜料。',
    cover: 'linear-gradient(135deg, #d0c2b1, #8f7560)'
  }
])

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

const WideExcerptCell = defineComponent({
  name: 'WideExcerptCell',
  props: {
    text: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const scroller = ref<HTMLElement | null>(null)
    const canScroll = ref(false)
    const thumbTop = ref(0)
    const thumbHeight = ref(0)
    let resizeObserver: ResizeObserver | null = null

    const updateThumb = () => {
      const el = scroller.value
      if (!el) return

      const scrollRange = el.scrollHeight - el.clientHeight
      canScroll.value = scrollRange > 1

      if (!canScroll.value) {
        thumbTop.value = 0
        thumbHeight.value = 0
        return
      }

      const trackHeight = el.clientHeight - 4
      const nextThumbHeight = Math.max(18, (el.clientHeight / el.scrollHeight) * trackHeight)
      const maxThumbTop = Math.max(0, trackHeight - nextThumbHeight)

      thumbHeight.value = nextThumbHeight
      thumbTop.value = (el.scrollTop / scrollRange) * maxThumbTop
    }

    onMounted(() => {
      nextTick(updateThumb)
      if (scroller.value) {
        resizeObserver = new ResizeObserver(updateThumb)
        resizeObserver.observe(scroller.value)
      }
    })

    onBeforeUnmount(() => {
      resizeObserver?.disconnect()
    })

    watch(
      () => props.text,
      () => {
        void nextTick(updateThumb)
      }
    )

    return () =>
      h('div', { class: ['wide-excerpt-cell', { 'is-scrollable': canScroll.value }] }, [
        h(
          'div',
          {
            ref: scroller,
            class: 'wide-excerpt-scroll',
            onScroll: updateThumb
          },
          props.text
        ),
        h('span', { class: 'wide-excerpt-track', 'aria-hidden': 'true' }, [
          h('span', {
            class: 'wide-excerpt-thumb',
            style: {
              height: `${thumbHeight.value}px`,
              transform: `translateY(${thumbTop.value}px)`
            }
          })
        ])
      ])
  }
})

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
  let list = [...mockItems.value]
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

const wideColumns: DataTableColumns<any> = [
  {
    title: '标题',
    key: 'title',
    minWidth: 260,
    render: (row) =>
      h('div', { class: 'wide-title-cell' }, [
        h('div', { class: 'wide-title-main' }, row.title),
        h('div', { class: 'wide-title-sub' }, `作者 ${row.author} · 创建于 ${row.createdAt}`)
      ])
  },
  {
    title: '摘要',
    key: 'excerpt',
    minWidth: 320,
    render: (row) => h(WideExcerptCell, { text: row.previewText })
  },
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
    title: '创建时间',
    key: 'createdAt',
    width: 140,
    sorter: (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
  }
]

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

const wideRows = computed(() =>
  filteredItems.value.map((item) => ({
    key: item.id,
    createdAt: item.date,
    previewText: (item.content || item.excerpt).slice(0, 180),
    ...item
  }))
)
</script>

<template>
  <div class="explore-page">
    <section class="explore-body">
      <aside class="tag-sidebar card-glass">
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

      <main class="content card-glass">
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
            <ProTable
              v-if="viewMode === 'compact-row'"
              key="compact-row-table"
              class="compact-table"
              :columns="compactColumns"
              :data="compactRows"
              row-key="key"
              :page-size="10"
              :show-size-picker="false"
              :show-quick-jumper="false"
            />
            <ProTable
              v-else-if="viewMode === 'wide-row'"
              key="wide-row-table"
              class="wide-table"
              :columns="wideColumns"
              :data="wideRows"
              row-key="key"
              :page-size="10"
              :show-size-picker="false"
              :show-quick-jumper="false"
            />
            <div v-else key="card-list" class="display-list" :class="`mode-${viewMode}`">
              <article v-for="item in filteredItems" :key="item.id" class="display-item">
                <div class="item-cover" :style="{ background: item.cover }" />
                <div class="item-main">
                  <h4>{{ item.title }}</h4>
                  <p>{{ item.excerpt }}</p>
                  <div class="meta">
                    作者 {{ item.author }} · {{ item.date }} · 点赞 {{ item.likes }} · 收藏
                    {{ item.favorites }}
                  </div>
                </div>
              </article>
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
  gap: 16px;
}

.header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
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
  gap: 16px;
  overflow: visible;
  align-items: start;
}

.tag-sidebar {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  gap: 17px;
  width: 100%;
  max-width: 320px;
  min-height: 360px;
  padding: 10px 5px;
  box-sizing: border-box;
  position: sticky;
  top: 87px;
  align-self: start;
  max-height: calc(100vh - 87px);
  overflow-y: auto;
}

.filter-combo {
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 100%;
  max-width: 250px;
  min-height: 0;
  margin: 10px 5px 5px;
}

.combo-top {
  width: 100%;
  height: 52px;
  background: rgba(252, 242, 228, 0.96);
  border-radius: 40px 20px 0 40px;
  border: 1px solid rgba(130, 95, 65, 0.22);
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
  background: rgba(252, 242, 228, 0.96);
  content: '';
}

.search-leading-icon {
  position: absolute;
  left: 22px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
  transition: color 0.25s ease;
}

.combo-bottom {
  width: 56%;
  height: 46px;
  align-self: flex-end;
  background: rgba(251, 240, 226, 0.95);
  border-radius: 0 0 20px 20px;
  border: 1px solid rgba(130, 95, 65, 0.22);
  border-top-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
}

.combo-bottom-inner {
  width: 127px;
  height: 75%;
  background: rgba(255, 246, 233, 0.96);
  border-radius: 40px;
  transform: translateY(-2px);
  border: 1px solid rgba(123, 84, 52, 0.2);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.42),
    inset 0 -1px 2px rgba(95, 63, 38, 0.2),
    inset 0 0 0 1px rgba(123, 84, 52, 0.12);
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
  border-radius: 999px;
  background: rgba(111, 63, 34, 0.72);
  transition: transform 0.28s ease;
  z-index: 0;
}

.combo-bottom-inner.mode-author::before {
  transform: translateX(100%);
}

.mode-button {
  height: 100%;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: color 0.22s ease;
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
  background: rgba(255, 246, 233, 0.9);
  padding: 0 14px 0 38px;
  color: var(--text-primary);
  outline: none;
  font-size: 13px;
  text-align: left;
  transition:
    border-color 0.3s ease,
    box-shadow 0.3s ease,
    background 0.3s ease,
    transform 0.3s ease;
}

.search-input:focus {
  border-color: var(--primary-color);
  box-shadow:
    0 0 0 3px var(--primary-light-color),
    0 8px 20px rgba(111, 63, 34, 0.16);
  background: rgba(255, 248, 236, 0.96);
  transform: translateY(-1px);
}

.combo-top:focus-within .search-leading-icon {
  color: var(--primary-color);
}

.tag-stack {
  display: flex;
  flex-wrap: wrap;
  flex: 1;
  gap: 8px;
  overflow-y: auto;
  min-height: 0;
  width: 100%;
  max-width: 250px;
  margin: 5px 5px 10px;
  padding: 10px;
  box-sizing: border-box;
  align-content: flex-start;
  background: rgba(251, 240, 226, 0.95);
  border-radius: 16px;
  border: 1px solid rgba(130, 95, 65, 0.22);
  box-shadow: none;
}

.stack-tag {
  margin: 0;
  border-radius: 999px;
  background: rgba(255, 249, 240, 0.98);
  border-color: rgba(145, 105, 72, 0.18);
  box-shadow:
    0 1px 2px rgba(69, 44, 24, 0.22),
    0 3px 8px rgba(69, 44, 24, 0.12);
  transition:
    background 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.stack-tag:hover {
  transform: translateY(-1px);
  background: rgba(255, 247, 236, 1);
  box-shadow:
    0 2px 4px rgba(69, 44, 24, 0.24),
    0 5px 10px rgba(69, 44, 24, 0.14);
}

:deep(.stack-tag.n-tag--checked) {
  border-radius: 999px;
  box-shadow:
    0 0 0 1px rgba(59, 130, 246, 0.15),
    0 8px 18px rgba(59, 130, 246, 0.2);
}

.tag-stack-panel-enter-active,
.tag-stack-panel-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
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
  gap: 12px;
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
  background: rgba(255, 250, 241, 0.92);
  padding: 0 14px 0 38px;
  color: var(--text-primary);
  outline: none;
  font-size: 13px;
  transition:
    border-color 0.3s ease,
    box-shadow 0.3s ease,
    background 0.3s ease,
    transform 0.3s ease;
}

.content-search-input:focus {
  border-color: var(--primary-color);
  box-shadow:
    0 0 0 3px var(--primary-light-color),
    0 8px 20px rgba(111, 63, 34, 0.16);
  background: rgba(255, 250, 241, 0.98);
  transform: translateY(-1px);
}

.content-search-row:focus-within .content-search-icon {
  color: var(--primary-color);
}

.content-display-panel {
  flex: 1;
  min-height: 0;
  border-radius: 14px;
  border: 1px solid rgba(130, 95, 65, 0.12);
  background: rgba(255, 250, 241, 0.62);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
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
  border: 1px solid rgba(130, 95, 65, 0.2);
  border-radius: 999px;
  background: rgba(255, 248, 236, 0.92);
  color: var(--text-primary);
  padding: 4px 10px;
  font-size: 12px;
  cursor: pointer;
}

.compound-chip:hover {
  background: rgba(255, 244, 229, 0.98);
}

.compound-chip.is-default {
  border-style: dashed;
  color: var(--text-secondary);
  background: rgba(255, 246, 233, 0.88);
}

.compound-chip.is-default:hover {
  background: rgba(255, 242, 225, 0.94);
}

.compound-chip-enter-active,
.compound-chip-leave-active {
  transition: all 0.26s ease;
}

.compound-chip-enter-from,
.compound-chip-leave-to {
  opacity: 0;
  transform: translateY(4px) scale(0.96);
}

.compound-chip-move {
  transition: transform 0.26s ease;
}

.view-mode-enter-active,
.view-mode-leave-active {
  transition: all 0.22s ease;
}

.view-mode-enter-from,
.view-mode-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.view-switch {
  margin-left: auto;
  border: 1px solid rgba(130, 95, 65, 0.2);
  border-radius: 999px;
  background: rgba(255, 248, 236, 0.9);
  display: inline-flex;
  padding: 2px;
  gap: 2px;
}

.view-switch button {
  border: 0;
  background: transparent;
  color: var(--text-secondary);
  border-radius: 999px;
  width: 32px;
  height: 28px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.view-switch button.active {
  background: rgba(111, 63, 34, 0.72);
  color: #fff;
}

.display-list {
  flex: 1;
  min-height: 0;
  overflow: auto;
  scrollbar-gutter: stable;
  display: grid;
  gap: 8px;
}

.display-list.mode-card {
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
}

.display-list.mode-wide-row,
.display-list.mode-compact-row {
  grid-template-columns: 1fr;
}

.display-item {
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: 12px;
  background: rgba(255, 251, 244, 0.92);
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  animation: card-item-enter 0.32s ease both;
  will-change: opacity, transform;
}

.display-item:nth-child(1) {
  animation-delay: 0.03s;
}

.display-item:nth-child(2) {
  animation-delay: 0.06s;
}

.display-item:nth-child(3) {
  animation-delay: 0.09s;
}

.display-item:nth-child(4) {
  animation-delay: 0.12s;
}

.display-item:nth-child(n + 5) {
  animation-delay: 0.14s;
}

.item-cover {
  display: none;
}

.item-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.display-item h4 {
  margin: 0;
  font-size: 14px;
}

.display-item p {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.display-item .meta {
  font-size: 12px;
  color: var(--text-tertiary);
}

.display-list.mode-card .display-item {
  padding: 0;
  overflow: hidden;
  gap: 0;
}

.display-list.mode-card .item-cover {
  display: block;
  height: 124px;
  width: 100%;
}

.display-list.mode-card .item-main {
  padding: 10px 12px;
}

.display-list.mode-wide-row .display-item {
  padding: 10px 12px;
}

.display-list.mode-wide-row .item-cover {
  display: none;
}

.compact-table {
  min-height: 0;
}

.compact-table :deep(.n-data-table) {
  --n-td-color: rgba(255, 249, 240, 0.9);
  --n-td-color-hover: rgba(255, 244, 229, 0.95);
  --n-th-color: rgba(246, 236, 223, 0.95);
  --n-border-color: rgba(130, 95, 65, 0.16);
  --n-th-text-color: var(--text-secondary);
  --n-td-text-color: var(--text-primary);
}

.compact-table :deep(.n-data-table .n-data-table-wrapper),
.compact-table :deep(.n-data-table .n-scrollbar-container),
.compact-table :deep(.n-data-table .n-data-table-base-table) {
  background: rgba(255, 248, 236, 0.78);
  border-radius: 10px;
}

.compact-table :deep(.n-data-table thead th) {
  background: rgba(246, 236, 223, 0.96) !important;
  color: var(--text-secondary) !important;
}

.compact-table :deep(.n-data-table tbody td) {
  background: rgba(255, 249, 240, 0.9) !important;
  color: var(--text-primary) !important;
}

.compact-table :deep(.n-data-table tbody tr:hover td) {
  background: rgba(255, 244, 229, 0.95) !important;
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

.wide-table {
  min-height: 0;
}

.wide-table :deep(.n-data-table) {
  --n-td-color: rgba(255, 249, 240, 0.9);
  --n-td-color-hover: rgba(255, 244, 229, 0.95);
  --n-th-color: rgba(246, 236, 223, 0.95);
  --n-border-color: rgba(130, 95, 65, 0.16);
  --n-th-text-color: var(--text-secondary);
  --n-td-text-color: var(--text-primary);
}

.wide-table :deep(.n-data-table .n-data-table-wrapper),
.wide-table :deep(.n-data-table .n-scrollbar-container),
.wide-table :deep(.n-data-table .n-data-table-base-table) {
  background: rgba(255, 248, 236, 0.78);
  border-radius: 10px;
}

.wide-table :deep(.n-data-table thead th) {
  background: rgba(246, 236, 223, 0.96) !important;
  color: var(--text-secondary) !important;
}

.wide-table :deep(.n-data-table tbody td) {
  background: rgba(255, 249, 240, 0.9) !important;
  color: var(--text-primary) !important;
  vertical-align: top;
  padding-top: 10px;
  padding-bottom: 10px;
}

.wide-table :deep(.n-data-table tbody tr:hover td) {
  background: rgba(255, 244, 229, 0.95) !important;
}

.wide-table :deep(.n-data-table-tbody > .n-data-table-tr) {
  animation: table-row-enter 0.28s ease both;
}

.wide-table :deep(.n-data-table-tbody > .n-data-table-tr:nth-child(1)) {
  animation-delay: 0.03s;
}

.wide-table :deep(.n-data-table-tbody > .n-data-table-tr:nth-child(2)) {
  animation-delay: 0.06s;
}

.wide-table :deep(.n-data-table-tbody > .n-data-table-tr:nth-child(3)) {
  animation-delay: 0.09s;
}

.wide-table :deep(.n-data-table-tbody > .n-data-table-tr:nth-child(n + 4)) {
  animation-delay: 0.12s;
}

.wide-table :deep(.wide-title-cell) {
  display: flex;
  flex-direction: column;
  gap: 4px;
  line-height: 1.45;
  height: 100%;
}

.wide-table :deep(.wide-title-main) {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.wide-table :deep(.wide-title-sub) {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: auto;
  padding-top: 6px;
}

.wide-table :deep(.wide-excerpt-cell) {
  position: relative;
  max-height: 72px;
}

.wide-table :deep(.wide-excerpt-scroll) {
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-secondary);
  white-space: normal;
  word-break: break-word;
  max-height: 72px;
  overflow-y: auto;
  padding-right: 14px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.wide-table :deep(.wide-excerpt-scroll::-webkit-scrollbar) {
  display: none;
}

.wide-table :deep(.wide-excerpt-track) {
  position: absolute;
  top: 2px;
  right: 2px;
  bottom: 2px;
  width: 8px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.18s ease;
}

.wide-table :deep(.wide-excerpt-cell.is-scrollable .wide-excerpt-track) {
  opacity: 0.72;
}

.wide-table :deep(.wide-excerpt-track::before) {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 1px;
  border-radius: 999px;
  background: rgba(130, 95, 65, 0.18);
  content: '';
  transform: translateX(-50%);
}

.wide-table :deep(.wide-excerpt-thumb) {
  position: absolute;
  top: 0;
  right: 3px;
  width: 2px;
  border-radius: 999px;
  background: rgba(130, 95, 65, 0.46);
  transition:
    right 0.18s ease,
    width 0.18s ease,
    background-color 0.18s ease;
  will-change: transform, height;
}

.wide-table :deep(.wide-excerpt-cell:hover .wide-excerpt-thumb) {
  right: 2px;
  width: 4px;
  background: rgba(130, 95, 65, 0.62);
}

@keyframes card-item-enter {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
