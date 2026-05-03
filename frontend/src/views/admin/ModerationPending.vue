<script setup lang="ts">
import { h, ref } from 'vue'
import { NButton, NDrawer, NDrawerContent, NSpace, useMessage } from 'naive-ui'
import ProTable from '@/components/ProTable.vue'
import {
  approvePostApi,
  rejectPostApi,
  batchApproveApi,
  batchRejectApi,
  getModerationPendingApi,
  getPostByIdApi,
  type BlogPost
} from '@/services/api'

const message = useMessage()
const currentIds = ref<string[]>([])
const previewOpen = ref(false)
const previewPost = ref<BlogPost | null>(null)

const columns = [
  { title: '标题', key: 'title' },
  { title: '作者', key: 'author_username' },
  { title: '提交时间', key: 'created_at' },
  {
    title: '操作',
    key: 'actions',
    render: (row: BlogPost) =>
      h(NSpace, {}, () => [
        h(
          NButton,
          { size: 'small', type: 'success', onClick: () => singleApprove(row.id) },
          { default: () => '通过' }
        ),
        h(
          NButton,
          { size: 'small', type: 'warning', onClick: () => singleReject(row.id) },
          { default: () => '驳回' }
        ),
        h(NButton, { size: 'small', onClick: () => openPreview(row.id) }, { default: () => '预览' })
      ])
  }
]

const fetchPending = async ({ page, pageSize }: { page: number; pageSize: number }) => {
  const res = await getModerationPendingApi({ page, page_size: pageSize })
  currentIds.value = (res.list || []).map((item) => item.id)
  return { ...res, list: res.list || [] }
}

const singleApprove = async (postId: string) => {
  await approvePostApi(postId)
  message.success('已通过')
}
const singleReject = async (postId: string) => {
  await rejectPostApi(postId)
  message.success('已驳回')
}

const batchApprove = async () => {
  if (!currentIds.value.length) return
  await batchApproveApi({ post_ids: currentIds.value })
  message.success('批量通过成功')
}
const batchReject = async () => {
  if (!currentIds.value.length) return
  await batchRejectApi({ post_ids: currentIds.value })
  message.success('批量驳回成功')
}

const openPreview = async (postId: string) => {
  previewPost.value = await getPostByIdApi(postId)
  previewOpen.value = true
}
</script>

<template>
  <div>
    <NSpace style="margin-bottom: 12px">
      <NButton type="success" @click="batchApprove">批量通过</NButton>
      <NButton type="warning" @click="batchReject">批量驳回</NButton>
    </NSpace>
    <ProTable row-key="id" :columns="columns" :request="fetchPending" />

    <NDrawer v-model:show="previewOpen" :width="560">
      <NDrawerContent title="帖子预览">
        <h3>{{ previewPost?.title }}</h3>
        <pre>{{ previewPost?.content }}</pre>
      </NDrawerContent>
    </NDrawer>
  </div>
</template>
