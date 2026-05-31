<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NInput, NButton, NSelect, NTag, NDivider, useMessage, NIcon, NPopover } from 'naive-ui'
import { EyeOutline, SaveOutline, SendOutline, InformationCircleOutline } from '@vicons/ionicons5'
import ConsoleShell from '@/components/ConsoleShell.vue'
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
  access_level: 'A5'
})
const tagOptions = ref<{ label: string; value: string }[]>([])
const lastSaved = ref<string | null>(null)

const accessLevelOptions = [
  { label: '所有人可见', value: 'A5' },
  { label: '社区成员可见', value: 'A3' },
  { label: '仅核心成员可见', value: 'A1' },
  { label: '仅管理员可见', value: 'A0' }
]

const accessLevelDescriptions: Record<string, { summary: string; detail: string }> = {
  A5: {
    summary: '默认权限，所有访客均可浏览',
    detail: '文章对所有用户可见，包括未登录访客。适合公开发布的内容。'
  },
  A3: {
    summary: 'P3 等级及以上的用户可浏览',
    detail: '仅向权限等级 P3 及以上的用户开放。适合面向有一定贡献的社区成员的内容。'
  },
  A1: {
    summary: 'P1 等级及以上的用户可浏览',
    detail: '仅向权限等级 P1 及以上的核心成员开放。适合敏感或内部内容。'
  },
  A0: {
    summary: '仅 P0 超级管理员可浏览',
    detail: '最高权限限制，仅超级管理员可查看。适合系统级内容。'
  }
}

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
    label: `${tag.name}（${tag.count || 0}）`,
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
        access_level: form.value.access_level
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
  <ConsoleShell>
    <div class="post-editor-page">
      <div class="page-heading">
        <h2>{{ mode === 'edit' ? '编辑文章' : '创作新文章' }}</h2>
      </div>
      <div class="editor-shell">
        <div class="editor-main">
          <div class="section-card editor-card">
            <div class="editor-header">
              <div class="header-right">
                <span class="word-count">{{ wordCount }} 字</span>
                <NButton quaternary size="small" @click="showPreview = !showPreview">
                  <template #icon
                    ><NIcon><EyeOutline /></NIcon
                  ></template>
                  {{ showPreview ? '编辑' : '预览' }}
                </NButton>
              </div>
            </div>

            <div v-show="!showPreview" class="edit-area">
              <div class="title-section">
                <NInput
                  v-model:value="form.title"
                  placeholder="输入文章标题……"
                  size="large"
                  :maxlength="120"
                  class="themed-input title-input"
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
                  class="themed-input content-input"
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
                    >{{ tag }}</NTag
                  >
                </div>
                <NDivider />
                <div class="preview-body">{{ form.content }}</div>
              </div>
              <div v-else class="preview-empty">
                <p>暂无内容可预览</p>
              </div>
            </div>
          </div>
        </div>

        <aside class="editor-sidebar">
          <div class="section-card sidebar-card">
            <div class="sidebar-section-title">发布设置</div>
            <div class="sidebar-section">
              <div class="field-row">
                <label class="field-label">可见范围</label>
                <NPopover trigger="hover" placement="left" :width="260">
                  <template #trigger>
                    <NIcon size="16" class="help-icon"><InformationCircleOutline /></NIcon>
                  </template>
                  <div class="help-content">
                    <p class="help-title">关于可见范围</p>
                    <p class="help-intro">
                      权限等级越低（A→0），可见范围越小；你的等级决定了你能设置的最高权限。
                    </p>
                    <div v-for="opt in accessLevelOptions" :key="opt.value" class="help-item">
                      <strong>{{ opt.label }}</strong>
                      <p class="help-summary">{{ accessLevelDescriptions[opt.value].summary }}</p>
                      <p class="help-detail">{{ accessLevelDescriptions[opt.value].detail }}</p>
                    </div>
                    <p class="help-note">发布后仍可在文章管理中修改可见范围。</p>
                  </div>
                </NPopover>
              </div>
              <NSelect
                v-model:value="form.access_level"
                :options="accessLevelOptions"
                size="small"
                class="themed-select"
              />
            </div>
            <div class="sidebar-section">
              <label class="field-label">标签</label>
              <NSelect
                v-model:value="form.tags"
                multiple
                filterable
                tag
                :options="tagOptions"
                placeholder="搜索或输入新标签"
                size="small"
                class="themed-select"
              />
            </div>
          </div>

          <div class="section-card sidebar-card">
            <div class="sidebar-section-title">操作</div>
            <div class="sidebar-actions">
              <NButton
                type="primary"
                block
                :loading="submitting"
                :disabled="!canSubmit"
                @click="submit"
              >
                <template #icon
                  ><NIcon><SendOutline /></NIcon
                ></template>
                {{ mode === 'edit' ? '保存修改' : '提交审核' }}
              </NButton>
              <NButton block @click="saveDraft">
                <template #icon
                  ><NIcon><SaveOutline /></NIcon
                ></template>
                保存草稿
              </NButton>
              <div class="draft-info" v-if="lastSaved">
                <span class="draft-time">草稿已存 {{ lastSaved }}</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </ConsoleShell>
</template>

<style scoped>
.post-editor-page {
  max-width: 100%;
}

.page-heading {
  margin-bottom: 16px;
}

.page-heading h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.editor-shell {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 16px;
  align-items: start;
}

.editor-card {
  padding: 20px;
}

.section-card {
  background: rgba(255, 248, 236, 0.72);
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-md);
  backdrop-filter: blur(4px);
}

.editor-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
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

.title-section {
  position: relative;
  padding-top: 4px;
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
  padding: 16px;
}

.sidebar-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(130, 95, 65, 0.1);
}

.sidebar-section {
  margin-bottom: 16px;
}

.sidebar-section:last-child {
  margin-bottom: 0;
}

.field-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.field-label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
}

.help-icon {
  color: var(--text-tertiary);
  cursor: pointer;
  transition: color 0.2s;
}

.help-icon:hover {
  color: var(--primary-color);
}

.help-content {
  font-size: 13px;
  line-height: 1.6;
}

.help-title {
  font-weight: 600;
  margin: 0 0 8px;
  font-size: 14px;
}

.help-item {
  margin-bottom: 8px;
}

.help-item:last-child {
  margin-bottom: 0;
}

.help-item p {
  margin: 2px 0 0;
  color: var(--text-tertiary);
}

.help-note {
  margin: 8px 0 0;
  color: var(--text-tertiary);
  font-size: 12px;
  border-top: 1px solid rgba(130, 95, 65, 0.1);
  padding-top: 6px;
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

/* ── 主题覆盖：输入框/下拉框 ── */
.themed-input {
  --n-color: rgba(255, 248, 236, 0.52) !important;
}

.themed-input :deep(.n-input__border) {
  border-color: rgba(130, 95, 65, 0.14) !important;
}

.themed-input :deep(.n-input__state-border) {
  border-color: rgba(154, 90, 47, 0.3) !important;
}

.themed-select {
  --n-color: rgba(255, 248, 236, 0.52) !important;
}

.themed-select :deep(.n-base-selection__border) {
  border-color: rgba(130, 95, 65, 0.14) !important;
}

.themed-select :deep(.n-base-selection__state-border) {
  border-color: rgba(154, 90, 47, 0.3) !important;
}

.help-intro {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0 0 10px;
  line-height: 1.5;
}

.help-summary {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.help-detail {
  margin: 2px 0 0;
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
