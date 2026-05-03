<script setup lang="ts">
import { h, ref } from 'vue'
import { NButton, NInput, NSelect, NSpace, useMessage } from 'naive-ui'
import ProTable from '@/components/ProTable.vue'
import {
  getBlogPostsApi,
  approvePostApi,
  rejectPostApi,
  deletePostApi,
  type BlogPost
} from '@/services/api'

const message = useMessage()
const q = ref('')
const status = ref('')

const statusOptions = [
  { label: '全部状态', value: '' },
  { label: '待审核', value: 'pending' },
  { label: '已发布', value: 'published' },
  { label: '已驳回', value: 'rejected' }
]

const columns = [
  { title: '标题', key: 'title' },
  { title: '作者', key: 'author_username' },
  { title: '状态', key: 'status' },
  { title: '创建时间', key: 'created_at' },
  {
    title: '操作',
    key: 'actions',
    render: (row: BlogPost) =>
      h(NSpace, {}, () => [
        h(
          NButton,
          { size: 'small', type: 'success', onClick: () => doApprove(row.id) },
          { default: () => '通过' }
        ),
        h(
          NButton,
          { size: 'small', type: 'warning', onClick: () => doReject(row.id) },
          { default: () => '驳回' }
        ),
        h(
          NButton,
          { size: 'small', type: 'error', onClick: () => doDelete(row.id) },
          { default: () => '删除' }
        )
      ])
  }
]

const request = ({ page, pageSize }: { page: number; pageSize: number }) =>
  getBlogPostsApi({
    page,
    page_size: pageSize,
    ...(q.value ? { q: q.value } : {}),
    ...(status.value ? { status: status.value } : {})
  })

const doApprove = async (id: string) => {
  await approvePostApi(id)
  message.success('已通过')
}
const doReject = async (id: string) => {
  await rejectPostApi(id)
  message.success('已驳回')
}
const doDelete = async (id: string) => {
  await deletePostApi(id)
  message.success('已删除')
}
</script>

<template>
  <div>
    <NSpace style="margin-bottom: 12px">
      <NInput v-model:value="q" placeholder="搜索标题/正文" clearable />
      <NSelect v-model:value="status" :options="statusOptions" style="width: 180px" />
    </NSpace>
    <ProTable row-key="id" :columns="columns" :request="request" />
  </div>
</template>
