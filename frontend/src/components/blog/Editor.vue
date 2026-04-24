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

    <div class="editor-layout">
      <!-- 左侧：标签列表 -->
      <aside class="editor-sidebar tags-panel">
        <div class="panel-header">
          <icon-bookmark class="panel-icon" />
          <span>标签</span>
          <a-button type="text" size="mini" @click="showTagInput = !showTagInput" class="add-tag-btn">
            <template #icon><icon-plus /></template>
          </a-button>
        </div>

        <!-- 新建标签输入 -->
        <div v-if="showTagInput" class="tag-input-wrapper">
          <a-input v-model="newTagName" placeholder="新标签名" size="small" @pressEnter="createTag" />
          <a-button type="primary" size="mini" @click="createTag" :disabled="!newTagName.trim()">创建</a-button>
        </div>

        <!-- 标签列表（徽章网格） -->
        <div class="tags-grid">
          <a-tag
            v-for="tag in allTags"
            :key="tag.id"
            :color="isSelectedTag(tag) ? 'var(--primary)' : 'var(--tag-bg)'"
            :class="['tag-badge', { selected: isSelectedTag(tag) }]"
            @click="toggleTag(tag)"
          >
            {{ tag.name }}
          </a-tag>
        </div>
      </aside>

      <!-- 中间：核心编辑区 -->
      <main class="editor-main">
        <a-form :model="form" layout="vertical" @submit="handleSubmit">
          <a-form-item label="标题" field="title" :rules="[{ required: true, message: '请输入标题' }]">
            <a-input
              v-model="form.title"
              placeholder="请输入文章标题"
              :max-length="256"
              show-word-limit
              class="title-input"
            />
          </a-form-item>

          <a-form-item label="内容" field="content" :rules="[{ required: true, message: '请输入内容' }]">
            <a-textarea
              v-model="form.content"
              placeholder="使用 Markdown 格式编写内容..."
              :auto-size="{ minRows: 16, maxRows: 40 }"
              class="content-textarea"
            />
          </a-form-item>
        </a-form>

        <a-alert v-if="!isAuthenticated" type="warning" style="margin-top: 16px">
          请先登录后再发布文章
        </a-alert>
      </main>

      <!-- 右侧：发布设置 -->
      <aside class="editor-sidebar settings-panel">
        <div class="panel-header">
          <icon-settings class="panel-icon" />
          <span>发布设置</span>
        </div>

        <div class="settings-content">
          <div class="setting-item">
            <label class="setting-label">阅读权限</label>
            <a-select v-model="form.access_level" placeholder="选择可见权限等级" size="small">
              <a-option
                v-for="opt in availableAccessLevels"
                :key="opt.value"
                :value="opt.value"
                :label="opt.label"
              />
            </a-select>
          </div>

          <div class="selected-tags">
            <label class="setting-label">已选标签</label>
            <div class="selected-tags-list">
              <a-tag
                v-for="tag in form.tags"
                :key="tag.id || tag"
                closable
                @close="removeTag(tag)"
                class="selected-tag-badge"
              >
                {{ tag.name || tag }}
              </a-tag>
              <span v-if="form.tags.length === 0" class="no-tags-hint">点击左侧标签添加</span>
            </div>
          </div>

          <div class="action-buttons">
            <a-button type="primary" html-type="submit" :loading="submitting" size="large" class="publish-btn" @click="handleSubmit">
              {{ isEdit ? '更新文章' : '发布文章' }}
            </a-button>
            <a-space style="margin-top: 12px;">
              <a-button @click="resetForm" size="small">重置</a-button>
              <a-button @click="showPreview" size="small">预览</a-button>
            </a-space>
          </div>
        </div>
      </aside>
    </div>

    <!-- 预览弹窗 -->
    <a-modal
      v-model:visible="previewVisible"
      title="文章预览"
      :width="800"
      :footer="null"
    >
      <div class="preview-content">
        <h1 class="preview-title">{{ form.title || '无标题' }}</h1>
        <div class="preview-meta">
          <a-space>
            <a-tag v-for="tag in form.tags" :key="tag.id || tag" size="small" color="var(--primary-light)">
              {{ tag.name || tag }}
            </a-tag>
          </a-space>
          <a-tag :color="getAccessLevelColor(form.access_level)">
            {{ form.access_level }}
          </a-tag>
        </div>
        <a-divider />
        <div class="markdown-body" v-html="renderedPreview" />
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../../router/auth.js'
import { blog } from '../../api'
import { Message } from '@arco-design/web-vue'
import MarkdownIt from 'markdown-it'
import { IconArrowLeft, IconUpload, IconBookmark, IconPlus, IconSettings } from '@arco-design/web-vue/es/icon'

const router = useRouter()
const route = useRoute()
const { isAuthenticated, level } = useAuth()

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
const previewVisible = ref(false)

// 标签相关
const allTags = ref([
  { id: 1, name: '生活' },
  { id: 2, name: '娱乐' },
  { id: 3, name: '吐槽' },
  { id: 4, name: '科技' },
  { id: 5, name: 'AI' },
  { id: 6, name: '编程' },
  { id: 7, name: '美食' },
  { id: 8, name: '旅行' },
  { id: 9, name: '读书' },
  { id: 10, name: '健身' },
])
const showTagInput = ref(false)
const newTagName = ref('')

// 加载全站标签
async function loadAllTags() {
  try {
    const data = await blog.listTags()
    if (data) {
      allTags.value = data
    }
  } catch {
    // 使用默认标签
  }
}

function toggleTag(tag) {
  const idx = form.value.tags.findIndex(t => (t.id || t) === tag.id || t === tag.name)
  if (idx >= 0) {
    form.value.tags.splice(idx, 1)
  } else {
    form.value.tags.push(tag)
  }
}

function isSelectedTag(tag) {
  return form.value.tags.some(t => (t.id || t) === tag.id || t === tag.name)
}

function removeTag(tag) {
  const idx = form.value.tags.findIndex(t => (t.id || t) === tag.id || t === tag.name)
  if (idx >= 0) {
    form.value.tags.splice(idx, 1)
  }
}

async function createTag() {
  const name = newTagName.value.trim()
  if (!name) return

  try {
    const data = await blog.createTag({ name })
    allTags.value.push(data)
    form.value.tags.push(data)
    newTagName.value = ''
    showTagInput.value = false
    Message.success('标签创建成功')
  } catch (err) {
    Message.error(err.message || '创建标签失败')
  }
}

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

const renderedPreview = computed(() => {
  if (!form.value.content) return '<p style="color: #999;">内容为空</p>'
  return md.render(form.value.content)
})

function showPreview() {
  previewVisible.value = true
}

function getAccessLevelColor(level) {
  const colors = {
    'A0': 'red',
    'A1': 'orange',
    'A2': 'gold',
    'A3': 'lime',
    'A4': 'green',
    'A5': 'arcoblue',
  }
  return colors[level] || 'arcoblue'
}

// 根据用户等级计算可选的权限等级
const availableAccessLevels = computed(() => {
  const lvl = level.value ?? 5
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
  await loadAllTags()
  if (route.params.id) {
    isEdit.value = true
    await loadPostContent()
  }
})

async function loadPostContent() {
  loadingEdit.value = true
  try {
    const data = await blog.getPostById(route.params.id)
    form.value.title = data.title || ''
    form.value.content = data.content || ''
    form.value.tags = data.tags || []
    form.value.access_level = data.access_level || 'A5'
  } catch (err) {
    Message.error(err.message || '加载文章内容失败')
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
    formData.append('tags', form.value.tags.map(t => t.name || t).join(','))
  }

  try {
    const result = await blog.importPost(formData)
    if (result.code === 'ok') {
      Message.success('导入成功，文章等待审核')
      form.value.title = result.data.title || ''
      form.value.content = result.data.content || ''
      form.value.tags = result.data.tags || []
    } else {
      Message.error(result.message || '导入失败')
    }
  } catch {
    Message.error('导入失败，网络错误')
  }
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
    const body = {
      title: form.value.title,
      content: form.value.content,
      tags: form.value.tags.map(t => t.name || t),
      access_level: form.value.access_level,
    }

    if (isEdit.value) {
      await blog.updatePost(route.params.id, body)
      Message.success('更新成功，文章重新进入审核')
    } else {
      await blog.createPost(body)
      Message.success('发布成功，文章等待审核')
    }
    router.push('/monitor')
  } catch (err) {
    Message.error(err.message || '操作失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.post-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
  margin: 16px;
  background: var(--color-bg-1);
  border-radius: var(--border-radius-large);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border-1);
  flex-shrink: 0;
}
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.page-title { margin: 0; font-size: 18px; font-weight: 600; color: var(--color-text-1); }

/* 三栏布局 */
.editor-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 200px 1fr 220px;
  gap: 12px;
  padding: 16px;
  min-height: 0;
  overflow: hidden;
}

/* 侧边栏通用样式 */
.editor-sidebar {
  background: var(--color-bg-2);
  border-radius: var(--border-radius-medium);
  padding: 12px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--color-border-1);
  font-weight: 600;
  color: var(--color-text-1);
  font-size: 14px;
}

.panel-icon {
  font-size: 16px;
  color: var(--primary);
}

.add-tag-btn {
  margin-left: auto;
  padding: 4px 8px;
  color: var(--color-text-3);
}
.add-tag-btn:hover {
  color: var(--primary);
}

/* 标签面板 */
.tags-panel {
  overflow-y: auto;
}

.tag-input-wrapper {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.tags-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 徽章样式标签 */
.tag-badge {
  cursor: pointer;
  padding: 6px 14px;
  border-radius: 20px;
  background: var(--color-bg-1);
  color: var(--color-text-2);
  border: 1px solid var(--color-border-1);
  transition: all 0.2s ease;
  font-size: 13px;
  width: 100%;
  text-align: center;
}

.tag-badge:hover {
  background: var(--primary-light-1);
  border-color: var(--primary-light-3);
  color: var(--primary);
}

.tag-badge.selected {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
  box-shadow: 0 2px 8px rgba(92, 61, 46, 0.3);
}

/* 中间编辑区 */
.editor-main {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow-y: auto;
  background: var(--color-bg-2);
  border-radius: var(--border-radius-medium);
  padding: 16px;
}

.title-input :deep(.arco-input-wrapper) {
  background: var(--color-bg-1);
}

.content-textarea :deep(.arco-textarea) {
  background: var(--color-bg-1);
  min-height: 400px;
}

.post-editor :deep(.arco-form-item-label) {
  font-weight: 500;
  font-size: 13px;
}

/* 右侧设置面板 */
.settings-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.settings-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.setting-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.selected-tags {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.selected-tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  min-height: 28px;
}

.selected-tag-badge {
  background: var(--primary-light-1);
  color: var(--primary);
  border: none;
  border-radius: 16px;
  padding: 2px 8px;
  font-size: 12px;
}

.no-tags-hint {
  font-size: 12px;
  color: var(--color-text-4);
  font-style: italic;
}

.action-buttons {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-1);
}

.publish-btn {
  width: 100%;
  background: var(--primary) !important;
  border-color: var(--primary) !important;
  font-weight: 600;
  letter-spacing: 1px;
}

/* 预览 */
.preview-content { max-height: 60vh; overflow-y: auto; }
.preview-title { font-size: 24px; font-weight: 600; margin-bottom: 12px; }
.preview-meta { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
</style>
