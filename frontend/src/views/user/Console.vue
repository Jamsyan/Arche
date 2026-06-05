<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { NIcon } from 'naive-ui'
import { CreateOutline, DocumentTextOutline } from '@vicons/ionicons5'
import { getMyPostsApi, type BlogPost } from '@/services/api'
import { PostCard } from '@/components/blog'
import ArButton from '@/components/ui/ArButton.vue'
import ArTag from '@/components/ui/ArTag.vue'

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
    color: 'var(--accent-yellow)'
  }
])

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

    <div class="stats-grid">
      <div v-for="card in statCards" :key="card.label" class="section-card stat-card">
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
    </div>

    <div class="section-card">
      <div class="card-header">
        <span class="card-header-title">最近文章</span>
      </div>
      <div v-if="loading" class="loading-state">
        <span>加载中……</span>
      </div>
      <div v-else-if="recentPosts.length === 0" class="empty-state">
        <p>还没有文章，开始你的第一篇创作吧</p>
        <ArButton type="primary" @click="$router.push('/posts/new')">写文章</ArButton>
      </div>
      <div v-else>
        <div v-for="post in recentPosts" :key="post.id" class="console-item-row">
          <PostCard
            :post="post"
            layout="compact"
            :show-excerpt="false"
            @open="$router.push(`/blog/${post.slug}`)"
          />
          <ArTag :color="getStatus(post).color" type="light" size="sm">
            {{ getStatus(post).label }}
          </ArTag>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.console-page {
  max-width: 100%;
}

.page-heading {
  margin-bottom: var(--spacing-lg);
}

.page-heading h2 {
  margin: 0 0 4px;
  font-size: 24px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.page-desc {
  margin: 0;
  font-size: 14px;
  color: var(--text-tertiary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: var(--spacing-lg);
}

.section-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
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
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.card-header {
  margin-bottom: var(--spacing-md);
}

.card-header-title {
  font-size: 16px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.console-item-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.console-item-row + .console-item-row {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--divider-color);
}

.console-item-row :deep(.blog-card) {
  flex: 1;
}

.loading-state {
  text-align: center;
  padding: 40px 0;
  color: var(--text-tertiary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: 40px 0;
  color: var(--text-tertiary);
}

.empty-state p {
  margin: 0;
}
</style>
