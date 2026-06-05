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
import ArDivider from '@/components/ui/ArDivider.vue'

const route = useRoute()
const message = useMessage()
const userStore = useUserStore()

const post = ref<BlogPost | null>(null)
const comments = ref<BlogComment[]>([])
const liked = ref(false)
const favorited = ref(false)
const posting = ref(false)

const isLoggedIn = computed(() => userStore.isLoggedIn)

const fetchPost = async () => {
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
  <div v-if="post" class="post-detail-page">
    <!-- 帖子内容 -->
    <PostDetail :post="post" @like="toggleLike" @favorite="toggleFavorite" />

    <!-- 操作栏 -->
    <div class="section-card actions-card">
      <div class="action-buttons">
        <LikeButton
          :count="post.likes || 0"
          :active="liked"
          :disabled="!isLoggedIn"
          @toggle="toggleLike"
        />
        <FavoriteButton :active="favorited" :disabled="!isLoggedIn" @toggle="toggleFavorite" />
      </div>
    </div>

    <!-- 评论区 -->
    <div class="section-card comments-card">
      <h3 class="comments-title">评论</h3>

      <CommentForm v-if="isLoggedIn" :loading="posting" @submit="submitComment" />
      <div v-else class="login-hint">登录后即可发表评论</div>

      <ArDivider />

      <CommentList :comments="comments" />
    </div>
  </div>
  <div v-else class="loading-state">
    <p>加载中……</p>
  </div>
</template>

<style scoped>
.post-detail-page {
  max-width: 760px;
  margin: 0 auto;
}
.section-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
}
.actions-card {
  padding: var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-md);
  display: flex;
  align-items: center;
}
.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}
.comments-card {
  padding: var(--spacing-lg);
}
.comments-title {
  margin: 0 0 var(--spacing-md);
  font-size: 16px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}
.login-hint {
  text-align: center;
  padding: var(--spacing-md) 0;
  font-size: 13px;
  color: var(--text-tertiary);
}
.loading-state {
  text-align: center;
  padding: 60px 0;
  color: var(--text-tertiary);
}
</style>
