<template>
  <div class="moderation-panel">
    <a-page-header
      title="审核面板"
      subtitle="待审核的文章列表（仅 P0 可见）"
      style="padding: 0; margin-bottom: 16px"
    />

    <a-table
      :columns="columns"
      :data="posts"
      :loading="loading"
      :pagination="pagination"
      row-key="id"
      @page-change="onPageChange"
    >
      <template #title="{ record }">
        <a-link @click="$router.push(`/post/${record.slug}`)">
          {{ record.title }}
        </a-link>
      </template>

      <template #author="{ record }">
        <a-space>
          <a-avatar :size="24" style="background-color: var(--color-primary-light-4)">
            {{ (record.author_username || 'U')[0].toUpperCase() }}
          </a-avatar>
          <span>{{ record.author_username || '匿名用户' }}</span>
        </a-space>
      </template>

      <template #level="{ record }">
        <LevelBadge :level="getLevel(record.quality_score)" />
      </template>

      <template #created_at="{ record }">
        {{ formatDate(record.created_at) }}
      </template>

      <template #actions="{ record }">
        <a-space>
          <a-button type="outline" size="mini" status="success" @click="approve(record)">
            <template #icon><icon-check /></template>
            通过
          </a-button>
          <a-button type="outline" size="mini" status="danger" @click="reject(record)">
            <template #icon><icon-close /></template>
            拒绝
          </a-button>
        </a-space>
      </template>
    </a-table>

    <a-empty v-if="!loading && posts.length === 0" description="暂无待审核文章" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../router/auth.js'
import { Message, Modal } from '@arco-design/web-vue'
import LevelBadge from '../LevelBadge.vue'

const router = useRouter()
const { authHeaders } = useAuth()

const posts = ref([])
const loading = ref(true)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const pagination = {
  showTotal: true,
  pageSize: 20,
}

const columns = [
  { title: '标题', dataIndex: 'title', slotName: 'title' },
  { title: '作者', slotName: 'author' },
  { title: '质量等级', slotName: 'level' },
  { title: '浏览量', dataIndex: 'views', width: 80 },
  { title: '提交时间', dataIndex: 'created_at', slotName: 'created_at', width: 160 },
  { title: '操作', slotName: 'actions', width: 160, fixed: 'right' },
]

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
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

async function fetchPendingPosts() {
  loading.value = true
  try {
    const res = await fetch(
      `/api/blog/moderation/pending?page=${page.value}&page_size=${pageSize.value}`,
      { headers: authHeaders() }
    )
    const result = await res.json()
    if (result.code === 'ok') {
      const data = result.data || {}
      posts.value = data.items || []
      total.value = data.total || 0
      pagination.total = total.value
    } else {
      Message.error(result.message || '加载失败')
    }
  } catch {
    Message.error('网络错误')
  } finally {
    loading.value = false
  }
}

function onPageChange(p) {
  page.value = p
  fetchPendingPosts()
}

async function approve(record) {
  Modal.confirm({
    title: '确认通过',
    content: `确定通过文章《${record.title}》的审核吗？`,
    okText: '通过',
    cancelText: '取消',
    onOk: async () => {
      try {
        const res = await fetch(
          `/api/blog/moderation/${record.id}/approve`,
          { method: 'POST', headers: authHeaders() }
        )
        const result = await res.json()
        if (result.code === 'ok') {
          Message.success('审核通过')
          await fetchPendingPosts()
        } else {
          Message.error(result.message || '操作失败')
        }
      } catch {
        Message.error('网络错误')
      }
    },
  })
}

async function reject(record) {
  Modal.confirm({
    title: '确认拒绝',
    content: `确定拒绝文章《${record.title}》的审核吗？`,
    okText: '拒绝',
    cancelText: '取消',
    buttonProps: { status: 'danger' },
    onOk: async () => {
      try {
        const res = await fetch(
          `/api/blog/moderation/${record.id}/reject`,
          { method: 'POST', headers: authHeaders() }
        )
        const result = await res.json()
        if (result.code === 'ok') {
          Message.success('已拒绝')
          await fetchPendingPosts()
        } else {
          Message.error(result.message || '操作失败')
        }
      } catch {
        Message.error('网络错误')
      }
    },
  })
}

onMounted(() => {
  fetchPendingPosts()
})
</script>

<style scoped>
.moderation-panel {
  max-width: 1000px;
  margin: 0 auto;
}
.moderation-panel :deep(.arco-table) {
  border-radius: var(--border-radius-large);
  overflow: hidden;
}
</style>
