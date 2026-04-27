<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NInput, NButton, NSelect, NSpace, useMessage } from 'naive-ui'
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
const mode = computed(() => (route.params.id ? 'edit' : 'create'))
const postId = computed(() => String(route.params.id || ''))

const form = ref({
  title: '',
  content: '',
  tags: [] as string[]
})
const tagOptions = ref<{ label: string; value: string }[]>([])

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

const submit = async () => {
  submitting.value = true
  try {
    if (mode.value === 'edit') {
      await updatePostApi(postId.value, {
        title: form.value.title,
        content: form.value.content
      })
      message.success('保存成功，帖子已重新进入审核')
    } else {
      await createPostApi({
        title: form.value.title,
        content: form.value.content,
        tags: form.value.tags
      })
      message.success('创建成功，帖子已提交审核')
    }
    await router.push('/posts')
  } finally {
    submitting.value = false
  }
}

const saveDraft = () => {
  const key = mode.value === 'edit' ? `post-draft-${postId.value}` : 'post-draft-new'
  localStorage.setItem(key, JSON.stringify(form.value))
  message.success('草稿已保存到本地')
}

onMounted(async () => {
  await fetchTags()
  await fetchDetail()
})
</script>

<template>
  <NCard :title="mode === 'edit' ? '编辑文章' : '新建文章'" :loading="loading">
    <NSpace vertical :size="16">
      <NInput v-model:value="form.title" placeholder="请输入标题" />
      <NSelect
        v-model:value="form.tags"
        multiple
        filterable
        tag
        :options="tagOptions"
        placeholder="选择或输入标签"
      />
      <NInput
        v-model:value="form.content"
        type="textarea"
        :autosize="{ minRows: 14, maxRows: 22 }"
        placeholder="请输入正文（第一版为纯文本）"
      />
      <NSpace justify="end">
        <NButton @click="router.push('/posts')">取消</NButton>
        <NButton @click="saveDraft">保存草稿</NButton>
        <NButton type="primary" :loading="submitting" @click="submit">提交审核</NButton>
      </NSpace>
    </NSpace>
  </NCard>
</template>
