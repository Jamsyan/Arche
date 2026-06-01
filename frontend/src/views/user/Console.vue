<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NCard, NButton, NGrid, NGi, NTag, NIcon } from 'naive-ui'
import { CreateOutline, DocumentTextOutline } from '@vicons/ionicons5'
import { getMyPostsApi, type BlogPost } from '@/services/api'

const loading = ref(false)
const recentPosts = ref<BlogPost[]>([])
const totalPosts = ref(0)

const statCards = [
  {
    label: '我的文章',
    value: totalPosts,
    icon: DocumentTextOutline,
    color: 'var(--primary-color)'
  },
  { label: '草稿箱', value: 0, icon: CreateOutline, color: 'var(--accent-color)' }
]

const statusMap: Record<
  string,
  { label: string; type: 'success' | 'warning' | 'info' | 'default' }
> = {
  published: { label: '已发布', type: 'success' },
  pending: { label: '审核中', type: 'warning' },
  draft: { label: '草稿', type: 'info' }
}

const getStatus = (post: BlogPost) => {
  const s = post.status || 'draft'
  return statusMap[s] || { label: s, type: 'default' as const }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getMyPostsApi(
      { page: 1, page_size: 5, sort_by: 'created_at' },
      { silent: true, skipAuthLogout: true }
    )
    recentPosts.value = res.list || []
    totalPosts.value = res.total || recentPosts.value.length
    statCards[0]!.value = totalPosts
    statCards[1]!.value = recentPosts.value.filter((p) => p.status === 'draft').length
  } catch {
    recentPosts.value = []
    totalPosts.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="console-page">
    <div class="page-heading">
      <h2>控制台</h2>
      <p class="page-desc">管理你的内容与创作</p>
    </div>

    <NGrid :cols="2" :x-gap="12" :y-gap="12" class="stats-grid">
      <NGi v-for="card in statCards" :key="card.label">
        <div class="glass-card stat-card">
          <div class="stat-inner">
            <div class="stat-icon" :style="{ background: card.color + '18', color: card.color }">
              <NIcon :size="22"><component :is="card.icon" /></NIcon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ card.value }}</span>
              <span class="stat-label">{{ card.label }}</span>
            </div>
          </div>
        </div>
      </NGi>
    </NGrid>

    <NCard title="最近文章" :loading="loading" class="section-card" :bordered="false">
      <div v-if="recentPosts.length === 0" class="empty-state">
        <p>还没有文章，开始你的第一篇创作吧</p>
        <NButton type="primary" @click="$router.push('/posts/new')">写文章</NButton>
      </div>
      <div v-else class="post-list">
        <div v-for="post in recentPosts" :key="post.id" class="post-row">
          <div class="post-info">
            <span class="post-title" @click="$router.push(`/posts/${post.slug || post.id}`)">
              {{ post.title }}
            </span>
            <NTag size="tiny" :type="getStatus(post).type" :bordered="false">
              {{ getStatus(post).label }}
            </NTag>
          </div>
          <div class="post-meta">
            <span>{{ (post.created_at || '').slice(0, 10) }}</span>
            <span v-if="post.likes !== undefined">{{ post.likes }} 赞</span>
            <span v-if="post.views !== undefined">{{ post.views }} 阅读</span>
          </div>
        </div>
      </div>
    </NCard>
  </div>
</template>

<style scoped>
.console-page {
  max-width: 100%;
}

.page-heading {
  margin-bottom: 20px;
}

.page-heading h2 {
  margin: 0 0 4px;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.page-desc {
  margin: 0;
  font-size: 14px;
  color: var(--text-tertiary);
}

.stats-grid {
  margin-bottom: 20px;
}

.glass-card {
  background: rgba(255, 248, 236, 0.72);
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-md);
  padding: 16px;
  backdrop-filter: blur(4px);
}

.stat-card {
  display: flex;
  align-items: center;
}

.stat-inner {
  display: flex;
  align-items: center;
  gap: 14px;
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

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.section-card {
  background: rgba(255, 248, 236, 0.72);
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-md);
  backdrop-filter: blur(4px);
}

.post-list {
  display: flex;
  flex-direction: column;
}

.post-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(130, 95, 65, 0.1);
}

.post-row:last-child {
  border-bottom: none;
}

.post-info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.post-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-title:hover {
  color: var(--primary-color);
}

.post-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 0;
  color: var(--text-tertiary);
}

.empty-state p {
  margin: 0;
}
</style>
