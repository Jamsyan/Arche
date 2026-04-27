<script setup lang="ts">
import { ref, h } from 'vue'
import { NCard, NButton, NTag, NPopconfirm, NSpace, useMessage } from 'naive-ui'
import { AddOutline } from '@/icons'
import ProTable from '@/components/ProTable.vue'
import {
  type AdminUser,
  createAdminUserApi,
  disableUserApi,
  enableUserApi,
  getUsersApi
} from '@/services/api'
import type { Paginated } from '@/services/api'

const message = useMessage()

interface UserRow {
  key: string
  id: string
  username: string
  nickname: string
  role: string
  createdAt: string
  status: string
}

const tableData = ref<UserRow[]>([])

const columns = [
  {
    title: '用户ID',
    key: 'id',
    width: 120
  },
  {
    title: '用户名',
    key: 'username',
    ellipsis: true
  },
  {
    title: '昵称',
    key: 'nickname',
    ellipsis: true
  },
  {
    title: '角色',
    key: 'role',
    width: 120,
    render: (row: { role: string }) => {
      return h(
        NTag,
        {
          type: row.role === 'admin' ? 'error' : row.role === 'user' ? 'primary' : 'default'
        },
        {
          default: () =>
            row.role === 'admin' ? '管理员' : row.role === 'user' ? '普通用户' : '访客'
        }
      )
    }
  },
  {
    title: '注册时间',
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
          type: row.status === '活跃' ? 'success' : 'error'
        },
        { default: () => row.status }
      )
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 240,
    render: (row: UserRow) => {
      return h(NSpace, { size: 'small' }, [
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
          NButton,
          {
            size: 'small',
            type: row.status === '活跃' ? 'warning' : 'success',
            quaternary: true,
            onClick: () => handleToggleStatus(row)
          },
          {
            default: () => (row.status === '活跃' ? '禁用' : '启用')
          }
        ),
        h(
          NPopconfirm,
          {
            title: '确认删除',
            content: `确定要删除用户"${row.username}"吗？`,
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

const toUserRow = (item: AdminUser): UserRow => ({
  key: item.id,
  id: item.id,
  username: item.username,
  nickname: item.nickname || item.username,
  role: item.role || 'user',
  createdAt: item.created_at ? item.created_at.slice(0, 10) : '-',
  status: item.is_active === false ? '禁用' : '活跃'
})

const fetchUsers = async (params: {
  page: number
  pageSize: number
}): Promise<Paginated<UserRow>> => {
  const res = await getUsersApi({
    page: params.page,
    page_size: params.pageSize
  })

  const list = (res.list || []).map(toUserRow)
  tableData.value = list
  return {
    total: res.total,
    page: res.page,
    page_size: res.page_size,
    list
  }
}

const handleCreate = () => {
  createAdminUserApi({
    email: `user${Date.now()}@example.com`,
    username: `user${Date.now().toString().slice(-6)}`,
    password: 'Passw0rd!123',
    level: 1
  })
    .then(() => {
      message.success('已创建演示用户')
    })
    .catch(() => {
      message.error('创建用户失败')
    })
}

const handleEdit = (row: UserRow) => {
  message.info(`编辑用户: ${row.username}`)
}

const handleToggleStatus = async (row: UserRow) => {
  try {
    if (row.status === '活跃') {
      await disableUserApi(row.id)
      row.status = '禁用'
      message.success('用户已禁用')
    } else {
      await enableUserApi(row.id)
      row.status = '活跃'
      message.success('用户已启用')
    }
  } catch {
    message.error('更新用户状态失败')
  }
}

const handleDelete = (row: UserRow) => {
  const index = tableData.value.findIndex((item) => item.key === row.key)
  if (index > -1) {
    tableData.value.splice(index, 1)
    message.success('删除成功')
  }
}
</script>

<template>
  <div class="users-page">
    <NCard class="users-card">
      <template #header>
        <div class="page-header">
          <h2>用户管理</h2>
          <NButton type="primary" @click="handleCreate">
            <template #icon>
              <AddOutline />
            </template>
            新建用户
          </NButton>
        </div>
      </template>

      <ProTable :columns="columns" :data="tableData" :request="fetchUsers" row-key="key" />
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
