<script setup lang="ts">
import { ref, h } from 'vue'
import { NCard, NTable, NPagination, NButton, NTag, NPopconfirm, useMessage } from 'naive-ui'
import { AddOutline } from '@/icons'

const message = useMessage()
const page = ref(1)
const pageSize = ref(10)

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
    render: (row: { key: string; title: string }) => {
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

const data = ref([
  {
    key: '1',
    title: 'Arche 架构设计思考',
    createdAt: '2026-04-25',
    status: '已发布'
  },
  {
    key: '2',
    title: 'Vue 3 权限驱动架构实践',
    createdAt: '2026-04-24',
    status: '已发布'
  },
  {
    key: '3',
    title: '微内核 + 插件系统原理',
    createdAt: '2026-04-23',
    status: '草稿'
  }
])

const handleCreate = () => {
  message.info('新建文章功能开发中')
}

const handleEdit = (row: any) => {
  message.info(`编辑文章: ${row.title}`)
}

const handleDelete = (row: any) => {
  const index = data.value.findIndex((item) => item.key === row.key)
  if (index > -1) {
    data.value.splice(index, 1)
    message.success('删除成功')
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

      <NTable :columns="columns" :data="data" row-key="key" :pagination="false" single-line />

      <div class="pagination-section">
        <NPagination
          v-model:page="page"
          v-model:page-size="pageSize"
          :page-count="10"
          show-size-changer
          :page-sizes="[10, 20, 50]"
          show-quick-jumper
        />
      </div>
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

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-xl);
}
</style>
