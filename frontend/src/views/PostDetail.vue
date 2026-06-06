<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  getPostBySlugApi,
  getPostCommentsApi,
  createPostCommentApi,
  likePostApi,
  addFavoriteApi,
  removeFavoriteApi,
  getFavoriteStatusApi,
  type BlogPost,
  type BlogComment
} from '@/services/api'
import { useUserStore } from '@/store/modules/user'
import PostDetail from '@/components/blog/PostDetail.vue'
import LikeButton from '@/components/blog/LikeButton.vue'
import FavoriteButton from '@/components/blog/FavoriteButton.vue'
import CommentForm from '@/components/blog/CommentForm.vue'
import CommentList from '@/components/blog/CommentList.vue'

const route = useRoute()
const message = useMessage()
const userStore = useUserStore()

const post = ref<BlogPost | null>(null)
const comments = ref<BlogComment[]>([])
const liked = ref(false)
const favorited = ref(false)
const posting = ref(false)
const loading = ref(true)

const isLoggedIn = computed(() => userStore.isLoggedIn)
const commentsCount = computed(() => comments.value.length)

const fetchPost = async () => {
  loading.value = true
  try {
    const detail = await getPostBySlugApi(String(route.params.slug || ''))
    post.value = detail
    const [commentsRes] = await Promise.all([
      getPostCommentsApi(detail.id, { page: 1, page_size: 50 }, { silent: true })
    ])
    comments.value = commentsRes.list || []
    if (isLoggedIn.value) {
      try {
        const favStatus = await getFavoriteStatusApi(detail.id, {
          silent: true,
          skipAuthLogout: true
        })
        favorited.value = favStatus.favorited
      } catch {
        // 静默
      }
    }
  } catch {
    message.error('加载帖子失败')
  } finally {
    loading.value = false
  }
}

const toggleLike = async () => {
  if (!post.value || !isLoggedIn.value) return
  try {
    await likePostApi(post.value.id, { silent: true })
    liked.value = !liked.value
    post.value.likes = (post.value.likes || 0) + (liked.value ? 1 : -1)
  } catch {
    message.error('操作失败')
  }
}

const toggleFavorite = async () => {
  if (!post.value || !isLoggedIn.value) return
  try {
    if (favorited.value) {
      await removeFavoriteApi(post.value.id, { silent: true })
      favorited.value = false
      message.success('已取消收藏')
    } else {
      await addFavoriteApi(post.value.id, { silent: true })
      favorited.value = true
      message.success('已收藏')
    }
  } catch {
    message.error('操作失败')
  }
}

const submitComment = async (content: string) => {
  if (!post.value) return
  posting.value = true
  try {
    await createPostCommentApi(post.value.id, { content }, { silent: true })
    message.success('评论成功')
    const res = await getPostCommentsApi(
      post.value.id,
      { page: 1, page_size: 50 },
      { silent: true }
    )
    comments.value = res.list || []
  } catch {
    message.error('评论失败')
  } finally {
    posting.value = false
  }
}

onMounted(fetchPost)
</script>

<template>
  <!-- 加载态 -->
  <div v-if="loading" class="loading-state">
    <div class="ink-loading" />
    <p class="loading-text">加载中……</p>
  </div>

  <!-- 内容 -->
  <div v-else-if="post" class="post-detail-page">
    <!-- 文章内容 -->
    <PostDetail :post="post" />

    <!-- 操作栏 -->
    <div class="section-card actions-card">
      <div class="action-buttons">
        <LikeButton
          :count="post.likes || 0"
          :active="liked"
          :disabled="!isLoggedIn"
          @toggle="toggleLike"
        />
        <div class="action-sep" />
        <FavoriteButton :active="favorited" :disabled="!isLoggedIn" @toggle="toggleFavorite" />
      </div>
    </div>

    <!-- 评论区 -->
    <div class="section-card comments-card">
      <div class="comments-header">
        <h3 class="comments-title">评论</h3>
        <span class="comments-badge">{{ commentsCount }}</span>
      </div>

      <CommentForm v-if="isLoggedIn" :loading="posting" @submit="submitComment" />
      <div v-else class="login-hint">
        <span class="login-hint-icon">⟡</span>
        登录后即可发表评论
      </div>

      <div class="comments-divider" />

      <CommentList :comments="comments" />
    </div>
  </div>
</template>

<style scoped>
/* ── 页面布局 ── */
.post-detail-page {
  max-width: 760px;
  margin: 0 auto;
  padding: var(--spacing-2xl) var(--spacing-md) var(--spacing-4xl);
}

/* ── 通用卡片 ── */
.section-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  animation: section-enter 0.5s var(--ease-out-smooth) both;
}

.section-card:nth-child(2) {
  animation-delay: 0.1s;
}

.section-card:nth-child(3) {
  animation-delay: 0.2s;
}

@keyframes section-enter {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── 操作栏 ── */
.actions-card {
  padding: var(--spacing-md) var(--spacing-lg);
  margin: var(--spacing-lg) 0;
  display: flex;
  align-items: center;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.action-sep {
  width: 1px;
  height: 20px;
  background: var(--divider-color);
}

/* ── 评论区 ── */
.comments-card {
  padding: var(--spacing-lg);
}

.comments-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.comments-title {
  margin: 0;
  font-size: 16px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.comments-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  border-radius: var(--radius-full);
  background: var(--primary-light-color);
  color: var(--primary-color);
  font-size: 12px;
  font-weight: var(--font-weight-semibold);
  font-variant-numeric: tabular-nums;
}

.comments-divider {
  height: 1px;
  margin: var(--spacing-md) 0;
  background: var(--divider-color);
}

.login-hint {
  text-align: center;
  padding: var(--spacing-lg) 0;
  font-size: 13px;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.login-hint-icon {
  font-size: 16px;
  opacity: 0.5;
}

/* ── 加载态 ── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  gap: var(--spacing-md);
}

.loading-text {
  font-size: 14px;
  color: var(--text-tertiary);
}
</style>
