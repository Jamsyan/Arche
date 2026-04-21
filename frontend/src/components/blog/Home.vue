<template>
  <div class="post-list">
    <a-page-header title="博客文章" subtitle="最新文章列表" style="padding: 0; margin-bottom: 16px" />

    <a-row justify="end" style="margin-bottom: 16px">
      <a-space>
        <span>排序：</span>
        <a-radio-group v-model="sortBy" type="button">
          <a-radio value="created_at">最新发布</a-radio>
          <a-radio value="views">最多阅读</a-radio>
        </a-radio-group>
      </a-space>
    </a-row>

    <a-list :loading="loading" :data="posts" :pagination="false" bordered>
      <template #item="{ item }">
        <a-list-item>
          <a-card hoverable class="post-card" @click="goToPost(item.slug)">
            <a-card-meta :title="item.title" :description="item.excerpt || item.content?.slice(0, 120) + '...'">
              <template #avatar>
                <a-avatar :size="40" :style="{ backgroundColor: '#165DFF' }">
                  {{ (item.author_username || 'U')[0].toUpperCase() }}
                </a-avatar>
              </template>
            </a-card-meta>
            <template #actions>
              <a-space>
                <a-tag color="arcoblue" size="small">
                  <template #icon><icon-eye /></template>
                  {{ item.views || 0 }}
                </a-tag>
                <a-tag color="purple" size="small">
                  <template #icon><icon-thumb-up /></template>
                  {{ item.likes || 0 }}
                </a-tag>
                <LevelBadge :level="getLevel(item.quality_score)" />
                <a-space size="mini">
                  <icon-clock-circle />
                  <span>{{ formatDate(item.created_at) }}</span>
                </a-space>
              </a-space>
            </template>
          </a-card>
        </a-list-item>
      </template>
    </a-list>

    <a-pagination
      v-if="total > pageSize"
      :total="total"
      :current="page"
      :page-size="pageSize"
      show-total
      style="margin-top: 20px; justify-content: center; display: flex"
      @change="onPageChange"
    />

    <a-empty v-if="!loading && posts.length === 0" description="暂无文章" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LevelBadge from '../LevelBadge.vue'

const router = useRouter()
const posts = ref([])
const loading = ref(true)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('created_at')

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
.post-card {
  cursor: pointer;
  margin-bottom: 12px;
}
.post-card :deep(.arco-card-body) {
  padding: 16px;
}
</style>
