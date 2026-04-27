<script setup lang="ts">
import { ref, h } from 'vue'
import {
  NCard,
  NTable,
  NPagination,
  NButton,
  NTag,
  NPopconfirm,
  NSpace,
  useMessage,
  NDescriptions,
  NDescriptionsItem,
  NModal
} from 'naive-ui'
import { AddOutline } from '@/icons'

const message = useMessage()
const page = ref(1)
const pageSize = ref(10)
const showInfoModal = ref(false)
const currentPlugin = ref<any>(null)

const columns = [
  {
    title: '插件名称',
    key: 'name',
    ellipsis: true
  },
  {
    title: '描述',
    key: 'description',
    ellipsis: true
  },
  {
    title: '作者',
    key: 'author',
    width: 120
  },
  {
    title: '版本',
    key: 'version',
    width: 100
  },
  {
    title: '状态',
    key: 'status',
    width: 120,
    render: (row: { status: string }) => {
      let type: 'success' | 'warning' | 'default' | 'error' = 'default'
      if (row.status === '已启用') type = 'success'
      else if (row.status === '已禁用') type = 'error'
      else if (row.status === '开发中') type = 'warning'
      return h(NTag, { type }, { default: () => row.status })
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 280,
    render: (row: any) => {
      return h(NSpace, { size: 'small' }, [
        h(
          NButton,
          {
            size: 'small',
            type: 'default',
            quaternary: true,
            onClick: () => handleViewInfo(row)
          },
          { default: () => '详情' }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'primary',
            quaternary: true,
            onClick: () => handleConfig(row)
          },
          { default: () => '配置' }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: row.status === '已启用' ? 'warning' : 'success',
            quaternary: true,
            onClick: () => handleToggleStatus(row)
          },
          {
            default: () => (row.status === '已启用' ? '禁用' : '启用')
          }
        ),
        h(
          NPopconfirm,
          {
            title: '确认卸载',
            content: `确定要卸载插件"${row.name}"吗？卸载后相关数据将被删除。`,
            positiveText: '确认',
            negativeText: '取消',
            onPositiveClick: () => handleUninstall(row)
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
                { default: () => '卸载' }
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
    name: 'Blog 博客',
    description: '提供博客文章管理、发布、展示功能',
    author: 'Arche',
    version: '1.0.0',
    status: '已启用'
  },
  {
    key: '2',
    name: 'GitHub Proxy',
    description: 'GitHub 代理服务，加速 GitHub 资源访问',
    author: 'Arche',
    version: '0.2.0',
    status: '已启用'
  },
  {
    key: '3',
    name: 'User System',
    description: '用户系统，提供用户注册、登录、权限管理功能',
    author: 'Arche',
    version: '0.1.0',
    status: '开发中'
  }
])

const handleInstall = () => {
  message.info('插件安装功能开发中')
}

const handleViewInfo = (row: any) => {
  currentPlugin.value = row
  showInfoModal.value = true
}

const handleConfig = (row: any) => {
  message.info(`配置插件: ${row.name}`)
}

const handleToggleStatus = (row: any) => {
  if (row.status === '开发中') {
    message.warning('开发中插件无法启用')
    return
  }
  row.status = row.status === '已启用' ? '已禁用' : '已启用'
  message.success(`插件已${row.status === '已启用' ? '启用' : '禁用'}`)
}

const handleUninstall = (row: any) => {
  const index = data.value.findIndex((item) => item.key === row.key)
  if (index > -1) {
    data.value.splice(index, 1)
    message.success('插件卸载成功')
  }
}
</script>

<template>
  <div class="plugins-page">
    <NCard class="plugins-card">
      <template #header>
        <div class="page-header">
          <h2>插件管理</h2>
          <NButton type="primary" @click="handleInstall">
            <template #icon>
              <AddOutline />
            </template>
            安装插件
          </NButton>
        </div>
      </template>

      <NTable :columns="columns" :data="data" row-key="key" :pagination="false" single-line />

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

    <NModal
      v-model:show="showInfoModal"
      title="插件详情"
      preset="dialog"
      :show-icon="false"
      positive-text="关闭"
      :show-negative-button="false"
      style="width: 600px"
    >
      <NDescriptions :column="1" bordered v-if="currentPlugin">
        <NDescriptionsItem label="插件名称">
          {{ currentPlugin.name }}
        </NDescriptionsItem>
        <NDescriptionsItem label="描述">
          {{ currentPlugin.description }}
        </NDescriptionsItem>
        <NDescriptionsItem label="作者">
          {{ currentPlugin.author }}
        </NDescriptionsItem>
        <NDescriptionsItem label="版本">
          {{ currentPlugin.version }}
        </NDescriptionsItem>
        <NDescriptionsItem label="状态">
          <NTag
            :type="
              currentPlugin.status === '已启用'
                ? 'success'
                : currentPlugin.status === '已禁用'
                  ? 'error'
                  : 'warning'
            "
          >
            {{ currentPlugin.status }}
          </NTag>
        </NDescriptionsItem>
      </NDescriptions>
    </NModal>
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
