<template>
  <div class="post-detail">
    <a-spin :loading="loading" style="width: 100%">
      <template v-if="post">
        <!-- 文章头部 -->
        <a-page-header
          :title="post.title"
          :subtitle="formatDate(post.created_at)"
          style="padding: 0; margin-bottom: 16px"
        >
          <template #extra>
            <a-space>
              <a-tag color="arcoblue">
                <icon-eye /> {{ post.views || 0 }} 阅读
              </a-tag>
              <LevelBadge :level="getLevel(post.quality_score)" />
            </a-space>
          </template>
        </a-page-header>

        <!-- 作者信息 -->
        <a-space style="margin-bottom: 20px">
          <a-avatar :size="32" style="background-color: var(--color-primary-light-4)">
            {{ (post.author_username || 'U')[0].toUpperCase() }}
          </a-avatar>
          <span>{{ post.author_username || '匿名用户' }}</span>
        </a-space>

        <!-- 文章内容 -->
        <a-card :bordered="false" style="margin-bottom: 24px">
          <pre class="post-content">{{ post.content }}</pre>
        </a-card>

        <!-- 操作栏 -->
        <a-divider />
        <a-row justify="space-between" align="center">
          <a-space>
            <a-button
              :type="liked ? 'primary' : 'secondary'"
              @click="toggleLike"
            >
              <template #icon><icon-thumb-up /></template>
              {{ liked ? '已点赞' : '点赞' }}
            </a-button>
          </a-space>
        </a-row>

        <!-- 评论区 -->
        <a-divider>评论</a-divider>

        <!-- 发表评论 -->
        <a-comment
          v-if="isAuthenticated"
          :avatar="userAvatar"
        >
          <template #actions>
            <a-button type="primary" size="small" @click="submitComment">
              发表评论
            </a-button>
          </template>
          <template #content>
            <a-textarea
              v-model="commentContent"
              :auto-size="{ minRows: 2, maxRows: 6 }"
              placeholder="写下你的评论..."
            />
          </template>
        </a-comment>
        <a-alert v-else type="warning" style="margin-bottom: 16px">
          登录后才能发表评论
        </a-alert>

        <!-- 评论列表 -->
        <div v-if="comments.length > 0" style="margin-top: 16px">
          <a-comment
            v-for="comment in rootComments"
            :key="comment.id"
            :avatar="getCommentAvatar(comment)"
            :author="getCommentAuthor(comment)"
            :content="comment.content"
            :datetime="formatDate(comment.created_at)"
          >
            <template #actions>
              <a-button type="text" size="mini" @click="toggleReply(comment)">
                回复
              </a-button>
            </template>

            <!-- 回复输入框 -->
            <div v-if="replyingTo === comment.id" style="margin-top: 8px">
              <a-space direction="vertical" style="width: 100%">
                <a-textarea
                  v-model="replyContents[comment.id]"
                  :auto-size="{ minRows: 1, maxRows: 3 }"
                  placeholder="回复..."
                />
                <a-space>
                  <a-button type="primary" size="mini" @click="submitReply(comment.id)">
                    发送
                  </a-button>
                  <a-button size="mini" @click="replyingTo = null">取消</a-button>
                </a-space>
              </a-space>
            </div>

            <!-- 子评论 -->
            <template v-if="getReplies(comment.id).length > 0">
              <a-comment
                v-for="reply in getReplies(comment.id)"
                :key="reply.id"
                :avatar="getCommentAvatar(reply)"
                :author="getCommentAuthor(reply)"
                :content="reply.content"
                :datetime="formatDate(reply.created_at)"
                style="margin-left: 40px"
              />
            </template>
          </a-comment>
        </div>
        <a-empty v-else description="暂无评论" />
      </template>

      <a-result v-if="!loading && !post" status="404" title="文章不存在" subtitle="该文章可能已被删除">
        <template #extra>
          <a-button type="primary" @click="$router.push('/')">返回首页</a-button>
        </template>
      </a-result>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../../router/auth.js'
import LevelBadge from '../LevelBadge.vue'
import { Message } from '@arco-design/web-vue'

const route = useRoute()
const { isAuthenticated, user, authHeaders } = useAuth()

const post = ref(null)
const loading = ref(true)
const liked = ref(false)
const comments = ref([])
const commentContent = ref('')
const replyingTo = ref(null)
const replyContents = ref({})

const userAvatar = computed(() => {
  if (user.value?.username) {
    return user.value.username[0].toUpperCase()
  }
  return 'U'
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
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

function getCommentAuthor(comment) {
  return comment.author_username || `用户 ${comment.author_id.slice(0, 8)}`
}

function getCommentAvatar(comment) {
  return (comment.author_username || 'U')[0].toUpperCase()
}

const rootComments = computed(() =>
  comments.value.filter((c) => !c.parent_id)
)

function getReplies(parentId) {
  return comments.value.filter((c) => c.parent_id === parentId)
}

async function fetchPost() {
  loading.value = true
  try {
    const res = await fetch(`/api/blog/posts/${route.params.slug}`)
    const result = await res.json()
    if (result.code === 'ok') {
      post.value = result.data
    }
  } catch {
    Message.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

async function fetchComments() {
  try {
    const res = await fetch(`/api/blog/posts/${post.value.id}/comments`)
    const result = await res.json()
    if (result.code === 'ok') {
      comments.value = result.data.items || []
    }
  } catch {
    // 评论加载失败不影响主内容
  }
}

async function toggleLike() {
  if (!isAuthenticated.value) {
    Message.warning('请先登录')
    return
  }
  try {
    const res = await fetch(`/api/blog/posts/${post.value.id}/like`, {
      method: 'POST',
      headers: authHeaders(),
    })
    const result = await res.json()
    if (result.code === 'ok') {
      liked.value = result.data.action === 'liked'
      Message.success(liked.value ? '点赞成功' : '已取消点赞')
    }
  } catch {
    Message.error('操作失败')
  }
}

async function submitComment() {
  if (!commentContent.value.trim()) {
    Message.warning('评论内容不能为空')
    return
  }
  try {
    const res = await fetch(`/api/blog/posts/${post.value.id}/comments`, {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ content: commentContent.value, parent_id: null }),
    })
    const result = await res.json()
    if (result.code === 'ok') {
      Message.success('评论成功')
      commentContent.value = ''
      await fetchComments()
    } else {
      Message.error(result.message || '评论失败')
    }
  } catch {
    Message.error('评论失败')
  }
}

function toggleReply(comment) {
  if (replyingTo.value === comment.id) {
    replyingTo.value = null
  } else {
    replyingTo.value = comment.id
    if (!replyContents.value[comment.id]) {
      replyContents.value[comment.id] = ''
    }
  }
}

async function submitReply(parentId) {
  const content = replyContents.value[parentId]
  if (!content?.trim()) {
    Message.warning('回复内容不能为空')
    return
  }
  try {
    const res = await fetch(`/api/blog/posts/${post.value.id}/comments`, {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ content, parent_id: parentId }),
    })
    const result = await res.json()
    if (result.code === 'ok') {
      Message.success('回复成功')
      replyContents.value[parentId] = ''
      replyingTo.value = null
      await fetchComments()
    } else {
      Message.error(result.message || '回复失败')
    }
  } catch {
    Message.error('回复失败')
  }
}

onMounted(async () => {
  await fetchPost()
  if (post.value) {
    await fetchComments()
  }
})
</script>

<style scoped>
.post-detail {
  max-width: 760px;
  margin: 0 auto;
}
.post-content {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  line-height: 1.8;
  font-size: 15px;
  margin: 0;
}
</style>
