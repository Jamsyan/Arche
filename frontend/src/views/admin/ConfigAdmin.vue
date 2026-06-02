<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { NButton, NInput, NModal, useMessage } from 'naive-ui'
import ProTable from '@/components/ProTable.vue'
import {
  getConfigListApi,
  updateConfigItemApi,
  getConfigGroupsApi,
  reloadConfigApi,
  type ConfigItem
} from '@/services/api'

const message = useMessage()
const configs = ref<ConfigItem[]>([])
const groups = ref<string[]>([])
const activeGroup = ref<string>('')
const loading = ref(false)

const editModal = ref(false)
const editKey = ref('')
const editValue = ref('')

const filteredConfigs = ref<ConfigItem[]>([])

const columns = [
  { title: 'Key', key: 'key', width: 200 },
  { title: '值', key: 'value', ellipsis: true },
  { title: '分组', key: 'group', width: 100 },
  { title: '描述', key: 'description', ellipsis: true },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row: ConfigItem) =>
      h(
        NButton,
        {
          size: 'tiny',
          type: 'primary',
          quaternary: true,
          onClick: () => openEdit(row)
        },
        { default: () => '编辑' }
      )
  }
]

const openEdit = (item: ConfigItem) => {
  editKey.value = item.key
  editValue.value = item.value
  editModal.value = true
}

const handleSave = async () => {
  try {
    await updateConfigItemApi(editKey.value, editValue.value, { silent: true })
    message.success('已更新')
    editModal.value = false
    await fetchData()
  } catch {
    message.error('更新失败')
  }
}

const handleReload = async () => {
  try {
    await reloadConfigApi({ silent: true })
    message.success('缓存已刷新')
  } catch {
    message.error('刷新失败')
  }
}

const filterByGroup = (group: string) => {
  activeGroup.value = group
  filteredConfigs.value = group ? configs.value.filter((c) => c.group === group) : configs.value
}

const fetchData = async () => {
  loading.value = true
  try {
    const [list, grps] = await Promise.all([
      getConfigListApi(undefined, { silent: true, skipAuthLogout: true }),
      getConfigGroupsApi({ silent: true, skipAuthLogout: true })
    ])
    configs.value = list || []
    groups.value = grps || []
    filterByGroup(activeGroup.value)
  } catch {
    // 静默
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="config-admin-page">
    <div class="page-heading">
      <h2>配置管理</h2>
      <NButton size="small" @click="handleReload">刷新缓存</NButton>
    </div>

    <div class="filter-bar">
      <NButton
        size="tiny"
        quaternary
        :type="!activeGroup ? 'primary' : 'default'"
        @click="filterByGroup('')"
        >全部</NButton
      >
      <NButton
        v-for="g in groups"
        :key="g"
        size="tiny"
        quaternary
        :type="activeGroup === g ? 'primary' : 'default'"
        @click="filterByGroup(g)"
        >{{ g }}</NButton
      >
    </div>

    <div class="section-card table-card">
      <ProTable :columns="columns" :data="filteredConfigs" row-key="key" />
    </div>

    <NModal
      v-model:show="editModal"
      title="编辑配置"
      :mask-closable="false"
      preset="card"
      style="width: 500px"
    >
      <div class="edit-form">
        <div class="field-row">
          <label>Key</label>
          <code>{{ editKey }}</code>
        </div>
        <div class="field-row">
          <label>值</label>
          <NInput v-model:value="editValue" type="textarea" :rows="3" class="themed-input" />
        </div>
        <div class="edit-actions">
          <NButton @click="editModal = false">取消</NButton>
          <NButton type="primary" @click="handleSave">保存</NButton>
        </div>
      </div>
    </NModal>
  </div>
</template>

<style scoped>
.config-admin-page {
  max-width: 100%;
}
.page-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.page-heading h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}
.filter-bar {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.section-card {
  background: rgba(255, 248, 236, 0.72);
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-md);
  backdrop-filter: blur(4px);
}
.table-card {
  padding: 16px;
}
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.field-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.field-row label {
  font-size: 13px;
  color: var(--text-secondary);
}
.field-row code {
  font-size: 13px;
  color: var(--text-primary);
  background: rgba(130, 95, 65, 0.06);
  padding: 4px 8px;
  border-radius: 4px;
}
.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
