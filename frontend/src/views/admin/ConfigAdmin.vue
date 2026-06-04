<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { NButton, NInput, NModal, NPopconfirm, NSpace, NCheckbox, useMessage } from 'naive-ui'
import ProTable from '@/components/ProTable.vue'
import {
  getConfigListApi,
  updateConfigItemApi,
  createConfigItemApi,
  deleteConfigItemApi,
  getConfigGroupsApi,
  reloadConfigApi,
  type ConfigItem,
} from '@/services/api'

const message = useMessage()
const configs = ref<ConfigItem[]>([])
const groups = ref<string[]>([])
const activeGroup = ref<string>('')
const loading = ref(false)

// 编辑
const editModal = ref(false)
const editKey = ref('')
const editValue = ref('')

// 新建
const createModal = ref(false)
const createForm = ref({ key: '', value: '', group: 'general', description: '', is_sensitive: false })

const columns = [
  { title: 'Key', key: 'key', width: 180 },
  { title: '值', key: 'value', ellipsis: true },
  { title: '分组', key: 'group', width: 90 },
  { title: '描述', key: 'description', ellipsis: true },
  {
    title: '敏感',
    key: 'is_sensitive',
    width: 60,
    render: (row: ConfigItem) => (row.is_sensitive ? '是' : '否'),
  },
  {
    title: '操作',
    key: 'actions',
    width: 140,
    render: (row: ConfigItem) =>
      h(NSpace, { size: 'small' }, [
        h(NButton, {
          size: 'tiny',
          type: 'primary',
          quaternary: true,
          onClick: () => openEdit(row),
        }, { default: () => '编辑' }),
        h(NPopconfirm, {
          title: '确认删除',
          content: `确定要删除配置"${row.key}"吗？`,
          positiveText: '确认',
          negativeText: '取消',
          onPositiveClick: () => handleDelete(row.key),
        }, {
          trigger: () => h(NButton, { size: 'tiny', type: 'error', quaternary: true }, { default: () => '删除' }),
        }),
      ]),
  },
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

const handleCreate = async () => {
  try {
    const f = createForm.value
    await createConfigItemApi(
      { key: f.key, value: f.value, group: f.group, description: f.description, is_sensitive: f.is_sensitive },
      { silent: true },
    )
    message.success('已创建')
    createModal.value = false
    createForm.value = { key: '', value: '', group: 'general', description: '', is_sensitive: false }
    await fetchData()
  } catch {
    message.error('创建失败')
  }
}

const handleDelete = async (key: string) => {
  try {
    await deleteConfigItemApi(key, { silent: true })
    message.success('已删除')
    await fetchData()
  } catch {
    message.error('删除失败')
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
  fetchData()
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = activeGroup.value ? { group: activeGroup.value } : undefined
    const [list, grps] = await Promise.all([
      getConfigListApi(params, { silent: true, skipAuthLogout: true }),
      getConfigGroupsApi({ silent: true, skipAuthLogout: true }),
    ])
    configs.value = list || []
    groups.value = grps || []
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
      <NSpace size="small">
        <NButton size="small" type="primary" @click="createModal = true">新建</NButton>
        <NButton size="small" @click="handleReload">刷新缓存</NButton>
      </NSpace>
    </div>

    <div class="filter-bar">
      <NButton
        size="tiny"
        quaternary
        :type="!activeGroup ? 'primary' : 'default'"
        @click="filterByGroup('')"
      >全部</NButton>
      <NButton
        v-for="g in groups"
        :key="g"
        size="tiny"
        quaternary
        :type="activeGroup === g ? 'primary' : 'default'"
        @click="filterByGroup(g)"
      >{{ g }}</NButton>
    </div>

    <div class="section-card table-card">
      <ProTable :columns="columns" :data="configs" row-key="key" :loading="loading" />
    </div>

    <!-- 编辑弹窗 -->
    <NModal
      v-model:show="editModal"
      title="编辑配置"
      :mask-closable="false"
      preset="card"
      style="width: 500px"
    >
      <div class="form">
        <div class="field-row">
          <label>Key</label>
          <code>{{ editKey }}</code>
        </div>
        <div class="field-row">
          <label>值</label>
          <NInput v-model:value="editValue" type="textarea" :rows="3" class="themed-input" />
        </div>
        <div class="form-actions">
          <NButton @click="editModal = false">取消</NButton>
          <NButton type="primary" @click="handleSave">保存</NButton>
        </div>
      </div>
    </NModal>

    <!-- 新建弹窗 -->
    <NModal
      v-model:show="createModal"
      title="新建配置项"
      :mask-closable="false"
      preset="card"
      style="width: 500px"
    >
      <div class="form">
        <div class="field-row">
          <label>Key *</label>
          <NInput v-model:value="createForm.key" placeholder="配置键名" class="themed-input" />
        </div>
        <div class="field-row">
          <label>值 *</label>
          <NInput v-model:value="createForm.value" type="textarea" :rows="3" placeholder="配置值" class="themed-input" />
        </div>
        <div class="field-row">
          <label>分组</label>
          <NInput v-model:value="createForm.group" placeholder="general" class="themed-input" />
        </div>
        <div class="field-row">
          <label>描述</label>
          <NInput v-model:value="createForm.description" placeholder="选填" class="themed-input" />
        </div>
        <div class="field-row">
          <NCheckbox v-model:checked="createForm.is_sensitive">敏感字段（值会用 *** 掩码显示）</NCheckbox>
        </div>
        <div class="form-actions">
          <NButton @click="createModal = false">取消</NButton>
          <NButton type="primary" @click="handleCreate">创建</NButton>
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
.form {
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
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
