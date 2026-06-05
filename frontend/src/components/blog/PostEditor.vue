<script setup lang="ts">
import { ref, computed } from 'vue'
import ArInput from '@/components/ui/ArInput.vue'
import ArButton from '@/components/ui/ArButton.vue'
import ArTag from '@/components/ui/ArTag.vue'
import type { BlogPost, CreatePostPayload, UpdatePostPayload } from '@/services/api'

const props = withDefaults(
  defineProps<{
    post?: BlogPost | null
    loading?: boolean
  }>(),
  {
    post: null,
    loading: false
  }
)

const emit = defineEmits<{
  save: [payload: CreatePostPayload | UpdatePostPayload]
  cancel: []
}>()

const isEdit = computed(() => !!props.post)

const title = ref(props.post?.title || '')
const content = ref(props.post?.content || '')
const tagInput = ref('')
const tags = ref<string[]>(props.post?.tags || [])
const accessLevel = ref(props.post?.access_level || 'public')

const canSubmit = computed(() => title.value.trim().length > 0 && content.value.trim().length > 0)

function addTag() {
  const t = tagInput.value.trim()
  if (t && !tags.value.includes(t)) {
    tags.value.push(t)
  }
  tagInput.value = ''
}

function removeTag(tag: string) {
  tags.value = tags.value.filter((t) => t !== tag)
}

function handleTagKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    addTag()
  }
}

function handleSave() {
  if (!canSubmit.value) return
  const payload: CreatePostPayload | UpdatePostPayload = isEdit.value
    ? {
        title: title.value.trim(),
        content: content.value.trim()
      }
    : {
        title: title.value.trim(),
        content: content.value.trim(),
        tags: tags.value,
        access_level: accessLevel.value
      }
  emit('save', payload)
}

function handleCancel() {
  emit('cancel')
}
</script>

<template>
  <div class="post-editor">
    <!-- 标题 -->
    <div class="editor-field">
      <label class="field-label">标题</label>
      <ArInput
        v-model:value="title"
        placeholder="输入文章标题……"
        size="large"
        :maxlength="120"
        show-count
      />
    </div>

    <!-- 内容 -->
    <div class="editor-field">
      <label class="field-label">正文</label>
      <ArInput
        v-model:value="content"
        type="textarea"
        :rows="14"
        :autosize="{ minRows: 12, maxRows: 36 }"
        placeholder="开始写下你的想法……"
      />
    </div>

    <!-- 标签 -->
    <div class="editor-field">
      <label class="field-label">标签</label>
      <div class="tag-input-row">
        <ArInput
          v-model:value="tagInput"
          placeholder="输入标签后按 Enter 添加"
          size="small"
          @keydown="handleTagKeydown"
        />
        <ArButton size="sm" type="secondary" @click="addTag">添加</ArButton>
      </div>
      <div v-if="tags.length > 0" class="tag-list">
        <ArTag
          v-for="tag in tags"
          :key="tag"
          color="primary"
          size="sm"
          type="light"
          closable
          @close="removeTag(tag)"
        >
          {{ tag }}
        </ArTag>
      </div>
    </div>

    <!-- 访问级别（仅新建模式） -->
    <div v-if="!isEdit" class="editor-field">
      <label class="field-label">访问级别</label>
      <select v-model="accessLevel" class="field-select">
        <option value="public">公开</option>
        <option value="private">私密</option>
      </select>
    </div>

    <!-- 操作按钮 -->
    <div class="editor-actions">
      <ArButton type="ghost" @click="handleCancel">取消</ArButton>
      <ArButton type="primary" :loading="loading" :disabled="!canSubmit" @click="handleSave">
        {{ isEdit ? '保存修改' : '发布' }}
      </ArButton>
    </div>
  </div>
</template>

<style scoped>
.post-editor {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  font-family: var(--font-sans);
}

.editor-field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.field-label {
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.tag-input-row {
  display: flex;
  gap: var(--spacing-sm);
}

.tag-input-row .ar-input {
  flex: 1;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: var(--spacing-xs);
}

.field-select {
  width: 100%;
  max-width: 240px;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--surface-color);
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 14px;
  outline: none;
  cursor: pointer;
  transition: border-color var(--transition-fast);
  appearance: auto;
}

.field-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-light-color);
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-color);
}
</style>
