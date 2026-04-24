<template>
  <div class="moderation-panel">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.push('/monitor')" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <h1 class="page-title">审核面板</h1>
      </div>
      <a-space>
        <a-button
          v-if="selectedKeys.length > 0"
          type="primary"
          size="small"
          status="success"
          @click="batchApprove"
        >
          批量通过 ({{ selectedKeys.length }})
        </a-button>
        <a-button
          v-if="selectedKeys.length > 0"
          type="primary"
          size="small"
          status="danger"
          @click="batchReject"
        >
          批量拒绝 ({{ selectedKeys.length }})
        </a-button>
      </a-space>
    </div>

    <a-table
      :columns="columns"
      :data="posts"
      :loading="loading"
      :pagination="pagination"
      :row-selection="{ type: 'checkbox', showCheckedAll: true, onlyCurrent: false }"
      row-key="id"
      @page-change="onPageChange"
      @selection-change="onSelectionChange"
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
import { blog } from '../../api'
import { Message, Modal } from '@arco-design/web-vue'
import LevelBadge from '../LevelBadge.vue'
import { IconArrowLeft, IconCheck, IconClose } from '@arco-design/web-vue/es/icon'

const router = useRouter()

const posts = ref([])
const loading = ref(true)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedKeys = ref([])

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
    const data = await blog.moderationPending({ page: page.value, page_size: pageSize.value })
    posts.value = data.items || []
    total.value = data.total || 0
    pagination.total = total.value
  } catch (err) {
    Message.error(err.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function onPageChange(p) {
  page.value = p
  fetchPendingPosts()
}

function onSelectionChange(keys) {
  selectedKeys.value = keys
}

async function batchApprove() {
  if (selectedKeys.value.length === 0) return
  Modal.confirm({
    title: '确认批量通过',
    content: `确定通过选中的 ${selectedKeys.value.length} 篇文章吗？`,
    okText: '通过',
    cancelText: '取消',
    onOk: async () => {
      try {
        await blog.batchApprove({ ids: selectedKeys.value })
        Message.success('批量通过成功')
        selectedKeys.value = []
        await fetchPendingPosts()
      } catch (err) {
        Message.error(err.message || '操作失败')
      }
    },
  })
}

async function batchReject() {
  if (selectedKeys.value.length === 0) return
  Modal.confirm({
    title: '确认批量拒绝',
    content: `确定拒绝选中的 ${selectedKeys.value.length} 篇文章吗？`,
    okText: '拒绝',
    cancelText: '取消',
    buttonProps: { status: 'danger' },
    onOk: async () => {
      try {
        await blog.batchReject({ ids: selectedKeys.value })
        Message.success('批量拒绝成功')
        selectedKeys.value = []
        await fetchPendingPosts()
      } catch (err) {
        Message.error(err.message || '操作失败')
      }
    },
  })
}

async function approve(record) {
  Modal.confirm({
    title: '确认通过',
    content: `确定通过文章《${record.title}》的审核吗？`,
    okText: '通过',
    cancelText: '取消',
    onOk: async () => {
      try {
        await blog.approvePost(record.id)
        Message.success('审核通过')
        await fetchPendingPosts()
      } catch (err) {
        Message.error(err.message || '操作失败')
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
        await blog.rejectPost(record.id)
        Message.success('已拒绝')
        await fetchPendingPosts()
      } catch (err) {
        Message.error(err.message || '操作失败')
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
.page-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
}
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }
.page-subtitle { font-size: 13px; color: var(--color-text-4); }
.moderation-panel :deep(.arco-table) {
  border-radius: var(--border-radius-large);
  overflow: hidden;
}
</style>
