<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { NCard, NGrid, NGi, NDataTable, NAlert } from 'naive-ui'
import { getMyPostsApi, getPostCommentsApi, type BlogPost } from '@/services/api'

interface MetricRow {
  key: string
  title: string
  status: string
  comments: number
  likes: number
  createdAt: string
}

const loading = ref(false)
const rows = ref<MetricRow[]>([])
const totalPosts = ref(0)
const totalComments = ref(0)
const totalLikes = ref(0)

const columns = [
  { title: '标题', key: 'title' },
  { title: '状态', key: 'status' },
  {
    title: '评论数',
    key: 'comments',
    sorter: (a: MetricRow, b: MetricRow) => a.comments - b.comments
  },
  { title: '点赞', key: 'likes', sorter: (a: MetricRow, b: MetricRow) => a.likes - b.likes },
  { title: '创建时间', key: 'createdAt' }
]

const statCards = computed(() => [
  { label: '文章总数', value: totalPosts.value },
  { label: '总评论', value: totalComments.value },
  { label: '总点赞', value: totalLikes.value }
])

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getMyPostsApi(
      { page: 1, page_size: 50 },
      { silent: true, skipAuthLogout: true }
    )
    const list = res.list || []
    totalPosts.value = list.length

    const commentTotals = await Promise.all(
      list.map(async (post: BlogPost) => {
        const comments = await getPostCommentsApi(
          post.id,
          { page: 1, page_size: 1 },
          { silent: true, skipAuthLogout: true }
        )
        return {
          post,
          comments: comments.total || 0
        }
      })
    )

    rows.value = commentTotals.map(({ post, comments }) => ({
      key: post.id,
      title: post.title,
      status: post.status ?? 'pending',
      comments,
      likes: post.likes || 0,
      createdAt: post.created_at?.slice(0, 10) || '-'
    }))

    totalComments.value = rows.value.reduce((sum, item) => sum + item.comments, 0)
    totalLikes.value = rows.value.reduce((sum, item) => sum + item.likes, 0)
  } catch {
    rows.value = []
    totalPosts.value = 0
    totalComments.value = 0
    totalLikes.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="creator-dashboard">
    <div class="page-heading">
      <h2>创作者看板</h2>
    </div>

    <NAlert type="info" style="margin-bottom: 12px">
      TODO：后端补充 analytics 接口后，将聚合逻辑替换为 `/blog/analytics/*`。
    </NAlert>

    <NGrid :cols="3" :x-gap="12">
      <NGi v-for="card in statCards" :key="card.label">
        <div class="section-card stat-card">
          <div class="stat-label">{{ card.label }}</div>
          <div class="stat-value">{{ card.value }}</div>
        </div>
      </NGi>
    </NGrid>

    <div class="section-card" style="margin-top: 12px; padding: 0">
      <NCard
        :loading="loading"
        title="内容表现排行（近 50 篇）"
        :bordered="false"
        style="background: transparent"
      >
        <NDataTable :columns="columns" :data="rows" />
      </NCard>
    </div>
  </div>
</template>

<style scoped>
.creator-dashboard {
  max-width: 100%;
}

.page-heading {
  margin-bottom: 16px;
}

.page-heading h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.section-card {
  background: var(--surface-color);
  border: var(--glass-border);
  border-radius: var(--radius-md);
  backdrop-filter: blur(4px);
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.stat-label {
  color: var(--text-secondary);
  margin-bottom: 6px;
  font-size: 14px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}
</style>
