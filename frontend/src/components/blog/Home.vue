<template>
  <div class="post-list">
    <div class="layout-3col">
      <!-- 左侧：功能面板 -->
      <aside class="sidebar-left">
        <div class="panel">
          <div class="panel-title">
            <icon-sort class="panel-icon" />
            排序
          </div>
          <a-radio-group v-model="sortBy" type="button" size="small" direction="vertical">
            <a-radio value="created_at">最新</a-radio>
            <a-radio value="views">最热</a-radio>
          </a-radio-group>
        </div>

        <div class="panel">
          <div class="panel-title">
            <icon-filter class="panel-icon" />
            筛选
          </div>
          <div class="panel-hint">暂无筛选条件</div>
        </div>

        <div class="panel">
          <div class="panel-title">
            <icon-list class="panel-icon" />
            统计
          </div>
          <div class="stat-row">
            <span>总文章</span>
            <span class="stat-value">{{ total }}</span>
          </div>
          <div class="stat-row">
            <span>每页</span>
            <span class="stat-value">{{ pageSize }}</span>
          </div>
        </div>
      </aside>

      <!-- 中间：文章主体 -->
      <main class="content-main">
        <div v-if="loading" class="loading-state">
          <a-spin />
        </div>

        <a-empty v-else-if="posts.length === 0" description="暂无文章" />

        <div v-else class="post-feed">
          <a-card
            v-for="item in posts"
            :key="item.slug"
            hoverable
            class="post-card"
            @click="goToPost(item.slug)"
          >
            <a-card-meta :title="item.title" :description="item.excerpt || item.content?.slice(0, 120) + '...'">
              <template #avatar>
                <a-avatar :size="36" :style="{ backgroundColor: 'var(--color-primary-light-3)' }">
                  {{ (item.author_username || 'U')[0].toUpperCase() }}
                </a-avatar>
              </template>
            </a-card-meta>
            <template #actions>
              <a-space size="small">
                <span class="stat-item">
                  <icon-eye />
                  {{ item.views || 0 }}
                </span>
                <span class="stat-item">
                  <icon-thumb-up />
                  {{ item.likes || 0 }}
                </span>
                <LevelBadge :level="getLevel(item.quality_score)" />
                <span class="stat-item stat-time">
                  <icon-clock-circle />
                  {{ formatDate(item.created_at) }}
                </span>
              </a-space>
            </template>
          </a-card>
        </div>

        <a-pagination
          v-if="total > pageSize"
          :total="total"
          :current="page"
          :page-size="pageSize"
          simple
          class="pagination"
          @change="onPageChange"
        />
      </main>

      <!-- 右侧：开放功能 -->
      <aside class="sidebar-right">
        <div class="panel">
          <div class="panel-title">
            <icon-settings class="panel-icon" />
            阅读偏好
          </div>
          <a-switch v-model="paragraphComment" size="small">
            <template #checked>开</template>
            <template #unchecked>关</template>
          </a-switch>
          <div class="panel-hint">段落评论（开发中）</div>
        </div>

        <div class="panel">
          <div class="panel-title">
            <icon-bulb class="panel-icon" />
            提示
          </div>
          <div class="panel-hint">点击文章卡片进入详情</div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LevelBadge from '../LevelBadge.vue'
import {
  IconSort,
  IconFilter,
  IconList,
  IconSettings,
  IconBulb,
} from '@arco-design/web-vue/es/icon'

const router = useRouter()
const posts = ref([])
const loading = ref(true)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('created_at')
const paragraphComment = ref(false)

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
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

function goToPost(slug) {
  router.push(`/post/${slug}`)
}

async function fetchPosts() {
  loading.value = true
  try {
    const res = await fetch(
      `/api/blog/posts?page=${page.value}&page_size=${pageSize.value}&sort_by=${sortBy.value}`
    )
    const result = await res.json()
    const data = result.data || {}
    posts.value = data.items || []
    total.value = data.total || 0
  } catch {
    posts.value = []
  } finally {
    loading.value = false
  }
}

watch([page, sortBy], () => {
  fetchPosts()
})

function onPageChange(p) {
  page.value = p
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.layout-3col {
  display: grid;
  grid-template-columns: 180px 1fr 180px;
  gap: 24px;
  align-items: start;
}

/* 侧栏面板 */
.sidebar-left,
.sidebar-right {
  position: sticky;
  top: 80px;
}
.panel {
  background: var(--color-bg-1);
  border: 1px solid var(--color-border-1);
  border-radius: var(--border-radius-large);
  padding: 16px;
  margin-bottom: 12px;
}
.panel-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-2);
  margin-bottom: 12px;
}
.panel-icon {
  width: 14px;
  height: 14px;
  color: var(--color-text-3);
}
.panel-hint {
  font-size: 12px;
  color: var(--color-text-4);
  margin-top: 4px;
}
.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--color-text-2);
  padding: 4px 0;
}
.stat-row + .stat-row {
  border-top: 1px solid var(--color-border-1);
}
.stat-value {
  font-weight: 600;
  color: var(--color-text-1);
}

/* 中间主体 */
.content-main {
  min-width: 0;
}
.post-feed {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.post-card {
  cursor: pointer;
}
.post-card :deep(.arco-card-body) {
  padding: 16px 20px;
}
.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--color-text-3);
}
.stat-time {
  margin-left: 4px;
}
.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
.loading-state {
  display: flex;
  justify-content: center;
  padding: 48px 0;
}

/* 响应式：窄屏隐藏侧栏 */
@media (max-width: 900px) {
  .layout-3col {
    grid-template-columns: 1fr;
  }
  .sidebar-left,
  .sidebar-right {
    display: none;
  }
}
</style>
