<script setup lang="ts">
import { ref, h } from 'vue'
import { NCard, NTable, NPagination, NButton, NTag, NPopconfirm, NSpace, useMessage } from 'naive-ui'
import { AddOutline, CreateOutline, TrashOutline, BanOutline, CheckmarkCircleOutline } from '@vicons/ionicons5'

const message = useMessage()
const page = ref(1)
const pageSize = ref(10)

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
      return h(NTag, {
        type: row.role === 'admin' ? 'error' : row.role === 'user' ? 'primary' : 'default'
      }, {
        default: () => row.role === 'admin' ? '管理员' : row.role === 'user' ? '普通用户' : '访客'
      })
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
      return h(NTag, {
        type: row.status === '活跃' ? 'success' : 'error'
      }, { default: () => row.status })
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 240,
    render: (row: { key: string; username: string; status: string }) => {
      return h(NSpace, { size: 'small' }, [
        h(NButton, {
          size: 'small',
          type: 'primary',
          quaternary: true,
          onClick: () => handleEdit(row)
        }, { default: () => '编辑' }),
        h(NButton, {
          size: 'small',
          type: row.status === '活跃' ? 'warning' : 'success',
          quaternary: true,
          onClick: () => handleToggleStatus(row)
        }, {
          default: () => row.status === '活跃' ? '禁用' : '启用'
        }),
        h(NPopconfirm, {
          title: '确认删除',
          content: `确定要删除用户"${row.username}"吗？`,
          positiveText: '确认',
          negativeText: '取消',
          onPositiveClick: () => handleDelete(row)
        }, {
          trigger: () => h(NButton, {
            size: 'small',
            type: 'error',
            quaternary: true
          }, { default: () => '删除' })
        })
      ])
    }
  }
]

const data = ref([
  {
    key: '1',
    id: '1',
    username: 'user',
    nickname: '普通用户',
    role: 'user',
    createdAt: '2026-04-25',
    status: '活跃'
  },
  {
    key: '2',
    id: '2',
    username: 'admin',
    nickname: '管理员',
    role: 'admin',
    createdAt: '2026-03-01',
    status: '活跃'
  },
  {
    key: '3',
    id: '3',
    username: 'guest',
    nickname: '访客',
    role: 'guest',
    createdAt: '2026-04-26',
    status: '禁用'
  }
])

const handleCreate = () => {
  message.info('新建用户功能开发中')
}

const handleEdit = (row: any) => {
  message.info(`编辑用户: ${row.username}`)
}

const handleToggleStatus = (row: any) => {
  row.status = row.status === '活跃' ? '禁用' : '活跃'
  message.success(`用户已${row.status === '活跃' ? '启用' : '禁用'}`)
}

const handleDelete = (row: any) => {
  const index = data.value.findIndex(item => item.key === row.key)
  if (index > -1) {
    data.value.splice(index, 1)
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

      <NTable
        :columns="columns"
        :data="data"
        row-key="key"
        :pagination="false"
        single-line
      />

      <div class="pagination-section">
        <NPagination
          v-model:page="page"
          v-model:page-size="pageSize"
          :page-count="1"
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
