<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { NCard, NButton, NGrid, NGi, NTag, NIcon } from 'naive-ui'
import { CreateOutline, DocumentTextOutline } from '@vicons/ionicons5'
import { getMyPostsApi, type BlogPost } from '@/services/api'
import BlogCard from '@/components/blog/BlogCard.vue'

const loading = ref(false)
const recentPosts = ref<BlogPost[]>([])
const totalPosts = ref(0)

const statCards = computed(() => [
  {
    label: '我的文章',
    value: totalPosts.value,
    icon: DocumentTextOutline,
    color: 'var(--primary-color)'
  },
  {
    label: '草稿箱',
    value: recentPosts.value.filter((p) => p.status === 'draft').length,
    icon: CreateOutline,
    color: 'var(--accent-color)'
  }
])

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
    totalPosts.value = res.total ?? recentPosts.value.length
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
      <div v-else>
        <div v-for="post in recentPosts" :key="post.id" class="console-item-row">
          <BlogCard
            :post="post"
            layout="compact"
            :show-excerpt="false"
            @open="$router.push(`/blog/${post.slug}`)"
          />
          <NTag size="tiny" :type="getStatus(post).type" :bordered="false">
            {{ getStatus(post).label }}
          </NTag>
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

.console-item-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.console-item-row :deep(.blog-card) {
  flex: 1;
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
