<script setup lang="ts">
import { ref, h } from 'vue'
import {
  NCard,
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
import ProTable from '@/components/ProTable.vue'
import {
  getAssetStatsApi,
  getConfigGroupsApi,
  getPluginLikeListApi,
  getSystemSummaryApi,
  type Paginated,
  type PluginSummary
} from '@/services/api'

const message = useMessage()
const showInfoModal = ref(false)
const currentPlugin = ref<PluginSummary | null>(null)
const tableData = ref<PluginSummary[]>([])

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
    render: (row: PluginSummary) => {
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

const fetchPlugins = async (params: {
  page: number
  pageSize: number
}): Promise<Paginated<PluginSummary>> => {
  const [assets, summary, groups] = await Promise.all([
    getPluginLikeListApi({
      page: params.page,
      page_size: params.pageSize
    }),
    getSystemSummaryApi({ silent: true }),
    getConfigGroupsApi({ silent: true })
  ])
  const list = (assets.list || []).map((item) => ({
    ...item,
    status: item.status || '已启用'
  }))
  tableData.value = list
  message.info(
    `系统摘要已同步（CPU: ${(summary.cpu_usage || 0).toFixed(1)}%，配置分组: ${groups.length}）`
  )
  return {
    total: assets.total,
    page: assets.page,
    page_size: assets.page_size,
    list
  }
}

const handleInstall = () => {
  getAssetStatsApi({ silent: true })
    .then((stats) => {
      message.success(`资产总数：${stats.total}`)
    })
    .catch(() => {
      message.error('获取资产统计失败')
    })
}

const handleViewInfo = (row: PluginSummary) => {
  currentPlugin.value = row
  showInfoModal.value = true
}

const handleConfig = (row: PluginSummary) => {
  message.info(`配置插件: ${row.name}`)
}

const handleToggleStatus = (row: PluginSummary) => {
  if (row.status === '开发中') {
    message.warning('开发中插件无法启用')
    return
  }
  row.status = row.status === '已启用' ? '已禁用' : '已启用'
  message.success(`插件已${row.status === '已启用' ? '启用' : '禁用'}`)
}

const handleUninstall = (row: PluginSummary) => {
  const index = tableData.value.findIndex((item) => item.id === row.id)
  if (index > -1) {
    tableData.value.splice(index, 1)
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

      <ProTable :columns="columns" :data="tableData" :request="fetchPlugins" row-key="id" />
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
</style>
