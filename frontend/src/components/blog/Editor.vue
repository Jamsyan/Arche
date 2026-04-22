<template>
  <div class="post-editor">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.back()" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <h1 class="page-title">{{ isEdit ? '编辑文章' : '发布新文章' }}</h1>
      </div>
    </div>

    <a-form
      :model="form"
      layout="vertical"
      @submit="handleSubmit"
    >
      <a-form-item label="标题" field="title" :rules="[{ required: true, message: '请输入标题' }]">
        <a-input
          v-model="form.title"
          placeholder="请输入文章标题"
          :max-length="256"
          show-word-limit
        />
      </a-form-item>

      <a-form-item label="内容" field="content" :rules="[{ required: true, message: '请输入内容' }]">
        <a-textarea
          v-model="form.content"
          placeholder="使用 Markdown 格式编写内容..."
          :auto-size="{ minRows: 12, maxRows: 30 }"
        />
      </a-form-item>

      <a-form-item>
        <a-space>
          <a-button type="primary" html-type="submit" :loading="submitting">
            {{ isEdit ? '更新文章' : '发布文章' }}
          </a-button>
          <a-button @click="resetForm">重置</a-button>
        </a-space>
      </a-form-item>
    </a-form>

    <a-alert v-if="!isAuthenticated" type="warning" style="margin-top: 16px">
      请先登录后再发布文章
    </a-alert>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../../router/auth.js'
import { Message } from '@arco-design/web-vue'

const router = useRouter()
const route = useRoute()
const { isAuthenticated, authHeaders } = useAuth()

const form = ref({
  title: '',
  content: '',
})
const submitting = ref(false)
const isEdit = ref(false)

onMounted(() => {
  if (route.params.id) {
    isEdit.value = true
    Message.info('编辑模式（加载文章内容待实现）')
  }
})

function resetForm() {
  form.value = { title: '', content: '' }
}

async function handleSubmit() {
  if (!isAuthenticated.value) {
    Message.warning('请先登录')
    router.push('/login')
    return
  }

  if (!form.value.title?.trim()) {
    Message.warning('请输入标题')
    return
  }
  if (!form.value.content?.trim()) {
    Message.warning('请输入内容')
    return
  }

  submitting.value = true
  try {
    const url = isEdit.value
      ? `/api/blog/posts/${route.params.id}`
      : '/api/blog/posts'
    const method = isEdit.value ? 'PUT' : 'POST'

    const body = {}
    if (form.value.title) body.title = form.value.title
    if (form.value.content) body.content = form.value.content

    const res = await fetch(url, {
      method,
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    const result = await res.json()

    if (result.code === 'ok') {
      Message.success(isEdit.value ? '更新成功，文章重新进入审核' : '发布成功，文章等待审核')
      router.push('/platform')
    } else {
      Message.error(result.message || '操作失败')
    }
  } catch {
    Message.error('网络错误，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.post-editor {
  max-width: 760px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }
.post-editor :deep(.arco-form-item-label) {
  font-weight: 500;
}
</style>
