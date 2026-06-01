<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { NButton, NDivider, NIcon, NInput, NTag, useMessage } from 'naive-ui'
import {
  HeartOutline,
  Heart,
  BookmarkOutline,
  Bookmark,
  ChatbubbleOutline,
  SendOutline
} from '@vicons/ionicons5'
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

const route = useRoute()
const message = useMessage()
const userStore = useUserStore()

const post = ref<BlogPost | null>(null)
const comments = ref<BlogComment[]>([])
const newComment = ref('')
const liked = ref(false)
const favorited = ref(false)
const posting = ref(false)

const isLoggedIn = computed(() => userStore.isLoggedIn)
const userInitial = computed(
  () => (userStore.userInfo?.nickname || userStore.userInfo?.username || '?')[0]
)

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

const submitComment = async () => {
  if (!post.value || !newComment.value.trim()) return
  posting.value = true
  try {
    await createPostCommentApi(
      post.value.id,
      { content: newComment.value.trim() },
      { silent: true }
    )
    message.success('评论成功')
    newComment.value = ''
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
    <article class="section-card post-card">
      <h1 class="post-title">{{ post.title }}</h1>
      <div class="post-meta">
        <span class="author">{{ post.author_username || '匿名' }}</span>
        <span class="dot">·</span>
        <span>{{ post.created_at?.slice(0, 10) || '-' }}</span>
        <span v-if="post.views !== undefined" class="dot">·</span>
        <span v-if="post.views !== undefined">{{ post.views }} 阅读</span>
      </div>
      <div class="tags-row">
        <NTag v-for="tag in post.tags || []" :key="tag" size="small" :bordered="false">
          {{ tag }}
        </NTag>
      </div>
      <NDivider style="margin: 12px 0" />
      <div class="post-content">{{ post.content }}</div>
    </article>

    <div class="section-card actions-card">
      <div class="action-buttons">
        <NButton
          :disabled="!isLoggedIn"
          quaternary
          :type="liked ? 'primary' : 'default'"
          @click="toggleLike"
        >
          <template #icon>
            <NIcon><component :is="liked ? Heart : HeartOutline" /></NIcon>
          </template>
          {{ post.likes || 0 }}
        </NButton>
        <NButton
          :disabled="!isLoggedIn"
          quaternary
          :type="favorited ? 'primary' : 'default'"
          @click="toggleFavorite"
        >
          <template #icon>
            <NIcon><component :is="favorited ? Bookmark : BookmarkOutline" /></NIcon>
          </template>
          {{ favorited ? '已收藏' : '收藏' }}
        </NButton>
        <span class="comment-count">
          <NIcon size="16"><ChatbubbleOutline /></NIcon>
          {{ comments.length }} 评论
        </span>
      </div>
    </div>

    <div class="section-card comments-card">
      <h3 class="comments-title">评论</h3>

      <div v-if="isLoggedIn" class="comment-form">
        <div class="form-avatar">{{ userInitial }}</div>
        <div class="form-input">
          <NInput
            v-model:value="newComment"
            type="textarea"
            :rows="2"
            placeholder="写下你的评论……"
            class="themed-input"
          />
          <div class="form-action">
            <NButton size="small" type="primary" :loading="posting" @click="submitComment">
              <template #icon
                ><NIcon><SendOutline /></NIcon
              ></template>
              发表评论
            </NButton>
          </div>
        </div>
      </div>
      <div v-else class="login-hint">
        <span>登录后即可发表评论</span>
      </div>

      <NDivider style="margin: 16px 0" />

      <div v-if="comments.length > 0" class="comment-list">
        <div v-for="c in comments" :key="c.id" class="comment-item">
          <div class="comment-avatar">{{ (c.user_id || '?')[0].toUpperCase() }}</div>
          <div class="comment-body">
            <div class="comment-header">
              <span class="comment-user">{{ c.user_id?.slice(0, 8) || '匿名' }}</span>
              <span class="comment-time">{{ (c.created_at || '').slice(0, 10) }}</span>
            </div>
            <div class="comment-content">{{ c.content }}</div>
          </div>
        </div>
      </div>
      <div v-else class="no-comments">
        <span>暂无评论，快来抢沙发吧</span>
      </div>
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
  background: rgba(255, 248, 236, 0.72);
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-md);
  backdrop-filter: blur(4px);
}
.post-card {
  padding: 28px;
  margin-bottom: 16px;
}
.post-title {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
}
.post-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 10px;
}
.post-meta .author {
  color: var(--text-secondary);
  font-weight: 500;
}
.dot {
  color: var(--text-quaternary);
  margin: 0 2px;
}
.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.post-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
}
.actions-card {
  padding: 12px 20px;
  margin-bottom: 16px;
}
.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}
.comment-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-tertiary);
  margin-left: auto;
}
.comments-card {
  padding: 20px;
}
.comments-title {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
.comment-form {
  display: flex;
  gap: 10px;
}
.form-avatar {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  background: var(--primary-color);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
}
.form-input {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.form-action {
  display: flex;
  justify-content: flex-end;
}
.login-hint {
  text-align: center;
  padding: 12px 0;
  font-size: 13px;
  color: var(--text-tertiary);
}
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.comment-item {
  display: flex;
  gap: 10px;
}
.comment-avatar {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: rgba(130, 95, 65, 0.12);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}
.comment-body {
  flex: 1;
  min-width: 0;
}
.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.comment-user {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}
.comment-time {
  font-size: 11px;
  color: var(--text-quaternary);
}
.comment-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
}
.no-comments {
  text-align: center;
  padding: 24px 0;
  font-size: 13px;
  color: var(--text-tertiary);
}
.loading-state {
  text-align: center;
  padding: 60px 0;
  color: var(--text-tertiary);
}
</style>
