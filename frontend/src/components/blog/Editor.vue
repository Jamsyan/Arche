<template>
  <div class="post-editor">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.back()" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <h1 class="page-title">{{ isEdit ? '编辑文章' : '发布新文章' }}</h1>
      </div>
      <a-space>
        <a-button type="text" @click="triggerImport" size="small">
          <template #icon><icon-upload /></template>
          导入文件
        </a-button>
        <input ref="importInput" type="file" accept=".md,.txt,.docx,.html,.htm" style="display:none" @change="handleImport">
      </a-space>
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

      <a-form-item label="标签">
        <a-select
          v-model="form.tags"
          multiple
          filterable
          allow-create
          placeholder="输入标签后回车添加，最多 50 个"
          :max-tag-count="5"
          :limit="50"
        />
      </a-form-item>

      <a-form-item label="阅读权限">
        <a-select v-model="form.access_level" placeholder="选择可见权限等级">
          <a-option
            v-for="opt in availableAccessLevels"
            :key="opt.value"
            :value="opt.value"
            :label="opt.label"
          />
        </a-select>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../../router/auth.js'
import { Message } from '@arco-design/web-vue'

const router = useRouter()
const route = useRoute()
const { isAuthenticated, authHeaders, userLevel } = useAuth()

const form = ref({
  title: '',
  content: '',
  tags: [],
  access_level: 'A5',
})
const submitting = ref(false)
const isEdit = ref(false)
const loadingEdit = ref(false)
const importInput = ref(null)

// 根据用户等级计算可选的权限等级
const availableAccessLevels = computed(() => {
  const level = userLevel.value ?? 5
  const levels = []
  for (let i = level; i <= 9; i++) {
    if (i <= 5) {
      levels.push({ value: `A${i}`, label: `A${i} — 等级 <= P${i} 可见` })
    } else {
      levels.push({ value: `A${i}`, label: `A${i} — 所有人可见` })
    }
  }
  return levels
})

onMounted(async () => {
  if (route.params.id) {
    isEdit.value = true
    await loadPostContent()
  }
})

async function loadPostContent() {
  loadingEdit.value = true
  try {
    const res = await fetch(`/api/blog/posts/by-id/${route.params.id}`)
    const result = await res.json()
    if (result.code === 'ok' && result.data) {
      form.value.title = result.data.title || ''
      form.value.content = result.data.content || ''
      form.value.tags = (result.data.tags || []).map(t => t.name)
      form.value.access_level = result.data.access_level || 'A5'
    } else {
      Message.error('加载文章内容失败')
    }
  } catch {
    Message.error('加载文章内容失败，网络错误')
  } finally {
    loadingEdit.value = false
  }
}

function resetForm() {
  form.value = { title: '', content: '', tags: [], access_level: 'A5' }
}

function triggerImport() {
  importInput.value?.click()
}

async function handleImport(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (!isAuthenticated.value) {
    Message.warning('请先登录')
    return
  }

  const formData = new FormData()
  formData.append('file', file)
  formData.append('access_level', form.value.access_level)
  if (form.value.tags.length > 0) {
    formData.append('tags', form.value.tags.join(','))
  }

  try {
    const res = await fetch('/api/blog/import', {
      method: 'POST',
      headers: authHeaders({}),
      body: formData,
    })
    const result = await res.json()
    if (result.code === 'ok') {
      Message.success('导入成功，文章等待审核')
      form.value.title = result.data.title || ''
      form.value.content = result.data.content || ''
      form.value.tags = (result.data.tags || []).map(t => t.name)
    } else {
      Message.error(result.message || '导入失败')
    }
  } catch {
    Message.error('导入失败，网络错误')
  }
  // 重置 input 以便重复选择同一文件
  event.target.value = ''
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
    if (form.value.tags) body.tags = form.value.tags
    if (form.value.access_level) body.access_level = form.value.access_level

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
  justify-content: space-between;
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
