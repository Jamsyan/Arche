<template>
  <div class="config-management">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.push('/admin')" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <icon-settings class="header-icon" />
        <h1 class="page-title">配置管理</h1>
      </div>
      <a-space>
        <a-button type="outline" size="small" @click="reloadAll" :loading="reloading">
          <template #icon><icon-refresh /></template>
          重新加载
        </a-button>
        <a-tag color="red" size="small">P0 权限</a-tag>
      </a-space>
    </div>

    <!-- 分组 Tab -->
    <a-tabs v-model:activeKey="activeGroup" type="card" class="config-tabs">
      <a-tab-pane v-for="group in groupTabs" :key="group.key" :title="group.label">
        <div v-if="loading" class="empty-state">加载中...</div>
        <div v-else-if="groupFields[group.key].length === 0" class="empty-state">
          暂无配置项
        </div>
        <a-form v-else :model="getFormData(group.key)" layout="vertical" class="config-form">
          <a-form-item
            v-for="field in groupFields[group.key]"
            :key="field.key"
            :label="field.key"
          >
            <template v-if="field.description" #extra>
              <span class="field-desc">{{ field.description }}</span>
            </template>
            <a-input-password
              v-if="field.is_sensitive"
              v-model="formState[field.key]"
              placeholder="留空将清空值"
              allow-clear
            />
            <a-input
              v-else
              v-model="formState[field.key]"
              :placeholder="field.description || field.key"
            />
          </a-form-item>
          <div class="form-actions">
            <a-button type="primary" @click="saveGroup(group.key)" :loading="saving">
              保存 {{ group.label }}
            </a-button>
          </div>
        </a-form>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { IconArrowLeft, IconSettings, IconRefresh } from '@arco-design/web-vue/es/icon'
import { useAuth } from '../../router/auth.js'

const router = useRouter()
const { authHeaders } = useAuth()

const loading = ref(false)
const saving = ref(false)
const reloading = ref(false)
const activeGroup = ref('minio')
const allEntries = ref([])
const formState = ref({})

const GROUP_LABELS = {
  minio: 'MinIO',
  oss: '阿里云 OSS',
  cloud: '云训练',
  github: 'GitHub',
  crawler: '爬虫',
  logging: '日志',
  system: '系统',
  deploy: '部署',
  general: '通用',
}

const groupTabs = computed(() => {
  const groups = [...new Set(allEntries.value.map(e => e.group))]
  return groups.map(g => ({ key: g, label: GROUP_LABELS[g] || g }))
})

const groupFields = computed(() => {
  const result = {}
  for (const entry of allEntries.value) {
    if (!result[entry.group]) result[entry.group] = []
    result[entry.group].push(entry)
  }
  return result
})

function getFormData(groupKey) {
  const fields = groupFields.value[groupKey] || []
  const data = {}
  for (const f of fields) {
    data[f.key] = formState.value[f.key] ?? ''
  }
  return data
}

async function fetchConfigs() {
  loading.value = true
  try {
    const res = await fetch('/api/admin/config', { headers: authHeaders() })
    const result = await res.json()
    if (result.code === 'ok') {
      allEntries.value = result.data
      // 初始化表单状态（非敏感字段用真实值，敏感字段留空供编辑）
      formState.value = {}
      for (const entry of result.data) {
        formState.value[entry.key] = entry.is_sensitive ? '' : entry.value
      }
    } else {
      Message.error(result.message || '获取配置失败')
    }
  } catch {
    Message.error('网络错误')
  } finally {
    loading.value = false
  }
}

async function saveGroup(groupKey) {
  saving.value = true
  try {
    const fields = groupFields.value[groupKey] || []
    let success = 0
    for (const field of fields) {
      const value = formState.value[field.key] ?? ''
      const res = await fetch(`/api/admin/config/${encodeURIComponent(field.key)}`, {
        method: 'PUT',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ value }),
      })
      const result = await res.json()
      if (result.code === 'ok') {
        success++
      }
    }
    if (success === fields.length) {
      Message.success(`${GROUP_LABELS[groupKey] || groupKey} 配置已保存`)
    } else {
      Message.warning(`部分保存成功 (${success}/${fields.length})`)
    }
    await fetchConfigs()
  } catch {
    Message.error('网络错误')
  } finally {
    saving.value = false
  }
}

async function reloadAll() {
  reloading.value = true
  try {
    const res = await fetch('/api/admin/config/reload', {
      method: 'POST',
      headers: authHeaders(),
    })
    const result = await res.json()
    if (result.code === 'ok') {
      Message.success('缓存已清除，下次请求时生效')
      await fetchConfigs()
    }
  } catch {
    Message.error('网络错误')
  } finally {
    reloading.value = false
  }
}

onMounted(() => { fetchConfigs() })
</script>

<style scoped>
.config-management { max-width: 900px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.header-icon { width: 24px; height: 24px; color: var(--color-text-2); }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }

.config-tabs { margin-top: 8px; }
.config-form { max-width: 640px; }
.field-desc { color: var(--color-text-4); font-size: 12px; }
.form-actions { margin-top: 16px; }
.empty-state { text-align: center; padding: 48px 0; color: var(--color-text-4); }
</style>
