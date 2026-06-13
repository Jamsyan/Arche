<template>
  <div class="drafts-page">
    <div class="drafts-header">
      <h1 class="drafts-title">草稿箱</h1>
      <p class="drafts-subtitle" v-if="total > 0">共 {{ total }} 篇草稿</p>
    </div>

    <!-- 草稿列表 -->
    <div v-if="drafts.length > 0" class="draft-list">
      <div v-for="draft in drafts" :key="draft.id" class="draft-row">
        <div class="draft-info" @click="continueEdit(draft.id)">
          <span class="draft-title">{{ draft.title || '无标题' }}</span>
          <span class="draft-meta">{{ formatTime(draft.created_at) }}</span>
        </div>
        <div class="draft-actions">
          <button
            class="draft-btn draft-btn--primary"
            @click="publishDraft(draft)"
            :disabled="publishingId === draft.id"
          >
            {{ publishingId === draft.id ? '发布中...' : '发布' }}
          </button>
          <button class="draft-btn draft-btn--edit" @click="continueEdit(draft.id)">编辑</button>
          <button class="draft-btn draft-btn--delete" @click="deleteDraft(draft)">删除</button>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="drafts-empty">
      <p>暂无草稿</p>
      <button class="drafts-empty-btn" @click="$router.push('/create/new')">去创建帖子</button>
    </div>

    <div v-if="loading" class="drafts-loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { getMyPostsApi, deletePostApi, updatePostApi, type BlogPost } from '@/services/api'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

const drafts = ref<BlogPost[]>([])
const total = ref(0)
const loading = ref(true)
const publishingId = ref<string | null>(null)

onMounted(async () => {
  await fetchDrafts()
})

async function fetchDrafts() {
  loading.value = true
  try {
    const res = await getMyPostsApi(
      { page: 1, page_size: 50, status: 'draft' },
      { silent: true, skipAuthLogout: true }
    )
    drafts.value = res.list || []
    total.value = res.total ?? drafts.value.length
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

async function publishDraft(draft: BlogPost) {
  publishingId.value = draft.id
  try {
    await updatePostApi(draft.id, { status: 'pending' } as any)
    message.success('草稿已提交审核')
    drafts.value = drafts.value.filter((d) => d.id !== draft.id)
    total.value = Math.max(0, total.value - 1)
  } catch {
    message.error('发布失败')
  } finally {
    publishingId.value = null
  }
}

function continueEdit(postId: string) {
  router.push(`/posts/${postId}/edit`)
}

function deleteDraft(draft: BlogPost) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除草稿「${draft.title || '无标题'}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deletePostApi(draft.id)
        message.success('草稿已删除')
        drafts.value = drafts.value.filter((d) => d.id !== draft.id)
        total.value = Math.max(0, total.value - 1)
      } catch {
        message.error('删除失败')
      }
    }
  })
}

function formatTime(timeStr?: string): string {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const diff = Date.now() - d.getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} 天前`
  return d.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.drafts-page {
  max-width: 860px;
  margin: 0 auto;
  padding: 32px 24px;
}

.drafts-header {
  margin-bottom: 28px;
}
.drafts-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color, #222);
  margin: 0 0 6px;
}
.drafts-subtitle {
  font-size: 0.9375rem;
  color: var(--text-tertiary, #999);
  margin: 0;
}

.draft-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.draft-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: var(--surface-color, #fff);
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 10px;
  transition: border-color 0.15s;
}
.draft-row:hover {
  border-color: var(--border-hover, #ccc);
}

.draft-info {
  flex: 1;
  min-width: 0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.draft-title {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--text-color, #333);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.draft-meta {
  font-size: 0.8125rem;
  color: var(--text-tertiary, #999);
}

.draft-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.draft-btn {
  padding: 6px 14px;
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 6px;
  font-size: 0.8125rem;
  cursor: pointer;
  background: var(--bg-color, #fff);
  color: var(--text-secondary, #666);
  transition: all 0.15s;
  white-space: nowrap;
}
.draft-btn:hover {
  border-color: var(--primary-color, #b83a2a);
  color: var(--primary-color, #b83a2a);
}
.draft-btn--primary {
  background: var(--primary-color, #b83a2a);
  color: #fff;
  border-color: transparent;
}
.draft-btn--primary:hover {
  background: var(--primary-hover-color, #d44a3a);
  color: #fff;
}
.draft-btn--delete:hover {
  border-color: var(--danger-color, #ef4444);
  color: var(--danger-color, #ef4444);
}

.drafts-empty {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-tertiary, #999);
}
.drafts-empty-btn {
  margin-top: 16px;
  padding: 8px 24px;
  background: var(--primary-color, #b83a2a);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.9375rem;
  cursor: pointer;
}
.drafts-empty-btn:hover {
  background: var(--primary-hover-color, #d44a3a);
}

.drafts-loading {
  text-align: center;
  padding: 80px;
  color: var(--text-tertiary, #999);
}
</style>
