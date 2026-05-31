<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NInput, NButton, NSelect, NTag, NDivider, useMessage, NIcon } from 'naive-ui'
import { EyeOutline, SaveOutline, SendOutline, ArrowBackOutline } from '@vicons/ionicons5'
import {
  createPostApi,
  updatePostApi,
  getPostByIdApi,
  getBlogTagsApi,
  type BlogTag
} from '@/services/api'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const loading = ref(false)
const submitting = ref(false)
const showPreview = ref(false)
const mode = computed(() => (route.params.id ? 'edit' : 'create'))
const postId = computed(() => String(route.params.id || ''))

const form = ref({
  title: '',
  content: '',
  tags: [] as string[],
  access_level: 'A10'
})
const tagOptions = ref<{ label: string; value: string }[]>([])
const lastSaved = ref<string | null>(null)

const accessLevelOptions = [
  { label: '公开发布', value: 'A10' },
  { label: '登录可见', value: 'A5' },
  { label: '仅自己', value: 'A1' }
]

const wordCount = computed(() => {
  const text = form.value.content.trim()
  return text ? text.length : 0
})

const titleWordCount = computed(() => form.value.title.trim().length)

const canSubmit = computed(() => {
  return form.value.title.trim().length > 0 && form.value.content.trim().length > 0
})

const fetchTags = async () => {
  const res = await getBlogTagsApi({ page: 1, page_size: 100 }, { silent: true })
  tagOptions.value = (res.list || []).map((tag: BlogTag) => ({
    label: tag.name,
    value: tag.name
  }))
}

const fetchDetail = async () => {
  if (mode.value !== 'edit') return
  loading.value = true
  try {
    const detail = await getPostByIdApi(postId.value)
    form.value.title = detail.title
    form.value.content = detail.content
    form.value.tags = detail.tags || []
  } finally {
    loading.value = false
  }
}

const loadDraft = () => {
  const key = mode.value === 'edit' ? `post-draft-${postId.value}` : 'post-draft-new'
  const saved = localStorage.getItem(key)
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      if (parsed.title || parsed.content) {
        form.value.title = parsed.title || form.value.title
        form.value.content = parsed.content || form.value.content
        form.value.tags = parsed.tags || form.value.tags
        lastSaved.value = new Date().toLocaleTimeString()
        message.info('已恢复本地草稿')
      }
    } catch {
      localStorage.removeItem(key)
    }
  }
}

const saveDraft = () => {
  const key = mode.value === 'edit' ? `post-draft-${postId.value}` : 'post-draft-new'
  localStorage.setItem(key, JSON.stringify(form.value))
  lastSaved.value = new Date().toLocaleTimeString()
  message.success('草稿已保存')
}

const removeDraft = () => {
  const key = mode.value === 'edit' ? `post-draft-${postId.value}` : 'post-draft-new'
  localStorage.removeItem(key)
  lastSaved.value = null
}

const submit = async () => {
  if (!canSubmit.value) {
    message.warning('请输入标题和正文')
    return
  }
  submitting.value = true
  try {
    if (mode.value === 'edit') {
      await updatePostApi(postId.value, {
        title: form.value.title,
        content: form.value.content
      })
      removeDraft()
      message.success('保存成功')
    } else {
      await createPostApi({
        title: form.value.title,
        content: form.value.content,
        tags: form.value.tags,
        access_level: Number(form.value.access_level.slice(1))
      })
      removeDraft()
      message.success('发布成功，帖子已提交审核')
    }
    await router.push('/posts')
  } catch {
    message.error(mode.value === 'edit' ? '保存失败，请重试' : '发布失败，请重试')
  } finally {
    submitting.value = false
  }
}

const handleKeydown = (e: KeyboardEvent) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    saveDraft()
  }
}

onMounted(async () => {
  await fetchTags()
  await fetchDetail()
  loadDraft()
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="post-editor-page">
    <div class="editor-shell">
      <div class="editor-main">
        <NCard class="editor-card" :loading="loading">
          <template #header>
            <div class="editor-header">
              <div class="header-left">
                <NButton text @click="router.push('/posts')" class="back-btn">
                  <template #icon>
                    <NIcon><ArrowBackOutline /></NIcon>
                  </template>
                </NButton>
                <h2>{{ mode === 'edit' ? '编辑文章' : '创作新文章' }}</h2>
              </div>
              <div class="header-right">
                <span class="word-count">{{ wordCount }} 字</span>
                <NButton quaternary size="small" @click="showPreview = !showPreview">
                  <template #icon>
                    <NIcon><EyeOutline /></NIcon>
                  </template>
                  {{ showPreview ? '编辑' : '预览' }}
                </NButton>
              </div>
            </div>
          </template>

          <div class="editor-body">
            <div v-show="!showPreview" class="edit-area">
              <div class="title-section">
                <NInput
                  v-model:value="form.title"
                  placeholder="输入文章标题……"
                  size="large"
                  :maxlength="120"
                  class="title-input"
                  :input-props="{
                    style: 'font-size: 22px; font-weight: 600; border: none; padding: 12px 0;'
                  }"
                />
                <div class="title-counter">
                  <NTag size="tiny" :bordered="false">{{ titleWordCount }}/120</NTag>
                </div>
              </div>

              <NDivider style="margin: 0 0 16px" />

              <div class="content-section">
                <NInput
                  v-model:value="form.content"
                  type="textarea"
                  :autosize="{ minRows: 18, maxRows: 36 }"
                  placeholder="开始写下你的想法……"
                  class="content-input"
                />
              </div>
            </div>

            <div v-show="showPreview" class="preview-area">
              <div class="preview-content" v-if="form.content">
                <h1 class="preview-title">{{ form.title || '（无标题）' }}</h1>
                <div class="preview-meta">
                  <NTag
                    v-for="tag in form.tags"
                    :key="tag"
                    size="small"
                    :bordered="false"
                    class="preview-tag"
                  >
                    {{ tag }}
                  </NTag>
                </div>
                <NDivider />
                <div class="preview-body">{{ form.content }}</div>
              </div>
              <div v-else class="preview-empty">
                <p>暂无内容可预览</p>
              </div>
            </div>
          </div>
        </NCard>
      </div>

      <aside class="editor-sidebar">
        <NCard class="sidebar-card" size="small">
          <template #header><span class="sidebar-title">发布设置</span></template>
          <div class="sidebar-section">
            <label class="field-label">可见范围</label>
            <NSelect v-model:value="form.access_level" :options="accessLevelOptions" size="small" />
          </div>
          <div class="sidebar-section">
            <label class="field-label">标签</label>
            <NSelect
              v-model:value="form.tags"
              multiple
              filterable
              tag
              :options="tagOptions"
              placeholder="添加标签"
              size="small"
            />
          </div>
        </NCard>

        <NCard class="sidebar-card" size="small">
          <template #header><span class="sidebar-title">操作</span></template>
          <div class="sidebar-actions">
            <NButton
              type="primary"
              block
              :loading="submitting"
              :disabled="!canSubmit"
              @click="submit"
            >
              <template #icon>
                <NIcon><SendOutline /></NIcon>
              </template>
              {{ mode === 'edit' ? '保存修改' : '提交审核' }}
            </NButton>
            <NButton block @click="saveDraft">
              <template #icon>
                <NIcon><SaveOutline /></NIcon>
              </template>
              保存草稿
            </NButton>
            <div class="draft-info" v-if="lastSaved">
              <span class="draft-time">草稿已存 {{ lastSaved }}</span>
            </div>
          </div>
        </NCard>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.post-editor-page {
  max-width: 1120px;
  margin: 0 auto;
}

.editor-shell {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 16px;
  align-items: start;
}

.editor-card {
  --n-padding: 0;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.back-btn {
  color: var(--text-tertiary);
  transition: color 0.2s;
}

.back-btn:hover {
  color: var(--primary-color);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.word-count {
  font-size: 13px;
  color: var(--text-tertiary);
}

.editor-body {
  padding: 0 24px 24px;
}

.title-section {
  position: relative;
  padding-top: 8px;
}

.title-input :deep(.n-input__input) {
  font-size: 22px !important;
  font-weight: 600 !important;
}

.title-counter {
  position: absolute;
  right: 0;
  bottom: -4px;
}

.content-section {
  margin-top: 4px;
}

.content-input :deep(textarea) {
  font-size: 15px;
  line-height: 1.8;
  min-height: 420px;
}

.preview-area {
  min-height: 400px;
}

.preview-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px;
}

.preview-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.preview-tag {
  background: rgba(154, 90, 47, 0.1);
  color: var(--primary-color);
}

.preview-body {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
}

.preview-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: var(--text-tertiary);
}

.sidebar-card {
  margin-bottom: 16px;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
}

.sidebar-section {
  margin-bottom: 16px;
}

.sidebar-section:last-child {
  margin-bottom: 0;
}

.field-label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.sidebar-actions {
  display: grid;
  gap: 10px;
}

.draft-info {
  text-align: center;
}

.draft-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

@media (max-width: 860px) {
  .editor-shell {
    grid-template-columns: 1fr;
  }

  .editor-sidebar {
    order: -1;
  }
}
</style>
