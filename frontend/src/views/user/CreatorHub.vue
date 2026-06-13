<template>
  <div class="creator-hub">
    <!-- 顶部用户信息 -->
    <div class="user-header">
      <div class="user-avatar-wrap">
        <img v-if="userInfo.avatar" :src="userInfo.avatar" class="user-avatar" alt="avatar" />
        <div v-else class="user-avatar user-avatar--fallback">
          {{ userInitials }}
        </div>
        <div class="user-level-badge">P{{ userInfo.level ?? 5 }}</div>
      </div>
      <div class="user-info">
        <div class="user-name-row">
          <span class="user-nickname">{{ userInfo.nickname || userInfo.username }}</span>
          <span class="user-id-divider">|</span>
          <span class="user-id">@{{ userInfo.username }}</span>
        </div>
        <div class="user-bio">{{ userInfo.bio || '这个人很懒，什么都没写…' }}</div>
        <div class="user-stats">
          <span class="user-stat">
            <span class="user-stat-value">{{ stats.totalLikes }}</span>
            <span class="user-stat-label">总点赞</span>
          </span>
          <span class="user-stat-divider" />
          <span class="user-stat">
            <span class="user-stat-value">{{ stats.totalComments }}</span>
            <span class="user-stat-label">总评论</span>
          </span>
          <span class="user-stat-divider" />
          <span class="user-stat">
            <span class="user-stat-value">{{ stats.totalViews }}</span>
            <span class="user-stat-label">总阅读</span>
          </span>
        </div>
      </div>
    </div>

    <!-- 快捷操作卡片（弹性横排） -->
    <div class="action-row">
      <div class="action-card" @click="goDrafts">
        <div class="action-card-icon">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M12 20h9" />
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
          </svg>
        </div>
        <div class="action-card-body">
          <span class="action-card-title">草稿箱</span>
          <span v-if="stats.draftCount > 0" class="action-card-badge">{{ stats.draftCount }}</span>
        </div>
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="action-card-arrow"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </div>

      <div class="action-card" @click="handleImportFile">
        <div class="action-card-icon">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </div>
        <div class="action-card-body">
          <span class="action-card-title">从文件导入</span>
        </div>
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="action-card-arrow"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
        <input
          ref="fileInputRef"
          type="file"
          accept=".txt,.md"
          style="display: none"
          @change="handleFileSelected"
        />
      </div>

      <div class="action-card action-card--primary" @click="goCreate">
        <div class="action-card-icon">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="16" />
            <line x1="8" y1="12" x2="16" y2="12" />
          </svg>
        </div>
        <div class="action-card-body">
          <span class="action-card-title">创建帖子</span>
        </div>
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="action-card-arrow"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </div>
    </div>

    <!-- 最近草稿 -->
    <div v-if="recentDrafts.length > 0" class="recent-section">
      <h2 class="section-title">继续编辑草稿</h2>
      <div class="draft-grid">
        <div
          v-for="draft in recentDrafts"
          :key="draft.id"
          class="draft-card"
          @click="continueDraft(draft.id)"
        >
          <div class="draft-card-body">
            <span class="draft-card-title">{{ draft.title || '无标题' }}</span>
            <span class="draft-card-meta">{{ formatTime(draft.created_at) }}</span>
          </div>
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="draft-card-arrow"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </div>
      </div>
    </div>

    <!-- 加载 -->
    <div v-if="pageLoading" class="hub-loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { getMyPostsApi, uploadPostFileApi, getUserInfoApi, type BlogPost } from '@/services/api'

const router = useRouter()
const message = useMessage()

const fileInputRef = ref<HTMLInputElement | null>(null)
const pageLoading = ref(true)

// ── 用户信息 ──

interface UserProfile {
  username: string
  nickname: string
  avatar?: string
  bio?: string
  level?: number
}

const userInfo = ref<UserProfile>({ username: '', nickname: '' })

const userInitials = computed(() => {
  const name = userInfo.value.nickname || userInfo.value.username
  return name.charAt(0).toUpperCase()
})

// ── 统计数据 ──

interface CreatorStats {
  totalPosts: number
  draftCount: number
  publishedCount: number
  totalLikes: number
  totalComments: number
  totalViews: number
}

const stats = ref<CreatorStats>({
  totalPosts: 0,
  draftCount: 0,
  publishedCount: 0,
  totalLikes: 0,
  totalComments: 0,
  totalViews: 0
})

const recentDrafts = ref<BlogPost[]>([])

onMounted(async () => {
  await Promise.all([fetchUserInfo(), fetchStats()])
  pageLoading.value = false
})

async function fetchUserInfo() {
  try {
    const data = await getUserInfoApi()
    userInfo.value = {
      username: data.username || '',
      nickname: data.nickname || data.username || '',
      avatar: data.avatar,
      bio: data.bio,
      level: data.level ?? 5
    }
  } catch {
    // fallback: 使用 localStorage 中的缓存或默认值
    userInfo.value = { username: '用户', nickname: '用户' }
  }
}

async function fetchStats() {
  try {
    const res = await getMyPostsApi(
      { page: 1, page_size: 100 },
      { silent: true, skipAuthLogout: true }
    )
    const list = res.list || []
    let draftCount = 0,
      publishedCount = 0
    let totalLikes = 0,
      totalComments = 0,
      totalViews = 0
    const drafts: BlogPost[] = []

    for (const post of list) {
      totalLikes += post.like_count || 0
      totalComments += post.comment_count || 0
      totalViews += post.views || 0
      if (post.status === 'draft') {
        draftCount++
        drafts.push(post)
      } else if (post.status === 'published') {
        publishedCount++
      }
    }

    stats.value = {
      totalPosts: list.length,
      draftCount,
      publishedCount,
      totalLikes,
      totalComments,
      totalViews
    }
    recentDrafts.value = drafts
      .sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
      .slice(0, 5)
  } catch {
    // silent
  }
}

// ── 操作 ──

function goCreate() {
  router.push('/create/new')
}
function goDrafts() {
  router.push('/posts?status=draft')
}
function continueDraft(postId: string) {
  router.push(`/posts/${postId}/edit`)
}
function handleImportFile() {
  fileInputRef.value?.click()
}

async function handleFileSelected(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  try {
    const result = await uploadPostFileApi(file, { silent: true })
    const data = result as any
    router.push(
      `/create/new?title=${encodeURIComponent(data.title || '')}&content=${encodeURIComponent(data.content || '')}&tags=${encodeURIComponent(JSON.stringify(data.tags || []))}&cover_url=${encodeURIComponent(data.cover_url || '')}`
    )
    message.success('文件解析成功，正在打开编辑器')
  } catch {
    message.error('文件导入失败，请重试')
  } finally {
    input.value = ''
  }
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
.creator-hub {
  padding: 40px 48px;
  max-width: 1200px;
  margin: 0 auto;
}

/* ── 用户信息头 ── */
.user-header {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 36px;
}

.user-avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.user-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  background: var(--primary-color, #b83a2a);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.user-level-badge {
  position: absolute;
  bottom: -2px;
  right: -4px;
  background: var(--surface-color, #fff);
  border: 2px solid var(--primary-color, #b83a2a);
  color: var(--primary-color, #b83a2a);
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 10px;
  line-height: 1.4;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.user-nickname {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color, #222);
}

.user-id-divider {
  color: var(--border-color, #ddd);
  font-weight: 200;
  font-size: 1.1rem;
}

.user-id {
  font-size: 0.9375rem;
  color: var(--text-tertiary, #999);
}

.user-bio {
  font-size: 0.875rem;
  color: var(--text-secondary, #666);
  margin-bottom: 12px;
  line-height: 1.5;
}

.user-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-stat {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.user-stat-value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-color, #333);
}

.user-stat-label {
  font-size: 0.8125rem;
  color: var(--text-tertiary, #999);
}

.user-stat-divider {
  width: 1px;
  height: 14px;
  background: var(--border-color, #e8e6e4);
}

/* ── 操作卡片（弹性横排） ── */
.action-row {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: var(--surface-color, #fff);
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
  min-width: 0;
}

.action-card:hover {
  border-color: var(--primary-color, #b83a2a);
  background: var(--primary-light-color, rgba(184, 58, 42, 0.08));
}

.action-card--primary {
  background: var(--primary-color, #b83a2a);
  border-color: transparent;
}

.action-card--primary:hover {
  background: var(--primary-hover-color, rgba(214, 74, 58, 0.08));
  border-color: transparent;
}

.action-card--primary .action-card-title,
.action-card--primary .action-card-arrow,
.action-card--primary .action-card-icon {
  color: #fff;
}

.action-card-icon {
  flex-shrink: 0;
  color: var(--primary-color, #b83a2a);
  display: flex;
  align-items: center;
}

.action-card-body {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.action-card-title {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--text-color, #333);
  white-space: nowrap;
}

.action-card-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 22px;
  padding: 0 7px;
  background: var(--primary-color, #b83a2a);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 11px;
}

.action-card-arrow {
  flex-shrink: 0;
  color: var(--text-muted, #bbb);
  transition: transform 0.15s;
}

.action-card:hover .action-card-arrow {
  transform: translateX(3px);
  color: var(--primary-color, #b83a2a);
}

/* ── 最近草稿 ── */
.recent-section {
  margin-bottom: 40px;
}
.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color, #333);
  margin: 0 0 14px;
}
.draft-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 8px;
}
.draft-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: var(--surface-color, #fff);
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
}
.draft-card:hover {
  border-color: var(--primary-color, #b83a2a);
  box-shadow: 0 2px 8px rgba(184, 58, 42, 0.08);
}
.draft-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}
.draft-card-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color, #333);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.draft-card-meta {
  font-size: 0.75rem;
  color: var(--text-tertiary, #999);
}
.draft-card-arrow {
  flex-shrink: 0;
  color: var(--text-muted, #bbb);
}
.draft-card:hover .draft-card-arrow {
  color: var(--primary-color, #b83a2a);
}

.hub-loading {
  text-align: center;
  padding: 80px;
  color: var(--text-tertiary, #999);
}
</style>
