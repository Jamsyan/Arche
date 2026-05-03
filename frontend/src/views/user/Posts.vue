<script setup lang="ts">
import { ref, h } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NButton, NTag, NPopconfirm, useMessage } from 'naive-ui'
import { AddOutline } from '@/icons'
import ProTable from '@/components/ProTable.vue'
import { deletePostApi, getMyPostsApi, type BlogPost, type Paginated } from '@/services/api'

const message = useMessage()
const router = useRouter()
const tableData = ref<PostRow[]>([])

interface PostRow {
  key: string
  id: string
  title: string
  createdAt: string
  status: string
}
const columns = [
  {
    title: '标题',
    key: 'title',
    ellipsis: true
  },
  {
    title: '发布时间',
    key: 'createdAt',
    width: 160
  },
  {
    title: '状态',
    key: 'status',
    width: 120,
    render: (row: { status: string }) => {
      return h(
        NTag,
        {
          type: row.status === '已发布' ? 'success' : 'warning'
        },
        { default: () => row.status }
      )
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (row: PostRow) => {
      return h('div', { style: { display: 'flex', gap: '8px' } }, [
        h(
          NButton,
          {
            size: 'small',
            type: 'primary',
            quaternary: true,
            onClick: () => handleEdit(row)
          },
          { default: () => '编辑' }
        ),
        h(
          NPopconfirm,
          {
            title: '确认删除',
            content: `确定要删除文章"${row.title}"吗？`,
            positiveText: '确认',
            negativeText: '取消',
            onPositiveClick: () => handleDelete(row)
          },
          {
            trigger: () =>
              h(
                NButton,
                {
                  size: 'small',
                  type: 'error',
                  quaternary: true
                },
                { default: () => '删除' }
              )
          }
        )
      ])
    }
  }
]

const toPostRow = (item: BlogPost): PostRow => ({
  key: item.id,
  id: item.id,
  title: item.title,
  createdAt: item.created_at ? item.created_at.slice(0, 10) : '-',
  status: item.status || '草稿'
})

const fetchPosts = async (params: {
  page: number
  pageSize: number
}): Promise<Paginated<PostRow>> => {
  const res = await getMyPostsApi({
    page: params.page,
    page_size: params.pageSize
  })
  const list = (res.list || []).map(toPostRow)
  tableData.value = list
  return {
    total: res.total,
    page: res.page,
    page_size: res.page_size,
    list
  }
}

const handleCreate = () => {
  router.push('/posts/new')
}

const handleEdit = (row: PostRow) => {
  router.push(`/posts/${row.id}/edit`)
}

const handleDelete = async (row: PostRow) => {
  try {
    await deletePostApi(row.id)
    const index = tableData.value.findIndex((item) => item.key === row.key)
    if (index > -1) {
      tableData.value.splice(index, 1)
    }
    message.success('删除成功')
  } catch {
    message.error('删除文章失败')
  }
}
</script>

<template>
  <div class="posts-page">
    <NCard class="posts-card">
      <template #header>
        <div class="page-header">
          <h2>我的文章</h2>
          <NButton type="primary" @click="handleCreate">
            <template #icon>
              <AddOutline />
            </template>
            新建文章
          </NButton>
        </div>
      </template>

      <ProTable :columns="columns" :data="tableData" :request="fetchPosts" row-key="key" />
    </NCard>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}
</style>
