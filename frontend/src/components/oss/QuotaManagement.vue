<template>
  <div class="quota-management">
    <a-table
      :data="quotas"
      :columns="quotaColumns"
      row-key="user_id"
      :pagination="{ showTotal: true, pageSize: 20 }"
      :loading="loading"
    >
      <template #user="{ record }">
        <span class="user-cell">{{ shortId(record.user_id) }}</span>
      </template>
      <template #quota="{ record }">
        {{ formatBytes(record.quota_bytes) }}
      </template>
      <template #used="{ record }">
        <div class="used-cell">
          <a-progress :percent="record.usage_percent" size="mini" :color="progressColor(record.usage_percent)" />
          <span class="used-text">{{ formatBytes(record.used_bytes) }}</span>
        </div>
      </template>
      <template #multiplier="{ record }">
        <a-tag :color="multiplierColor(record.speed_multiplier)" size="small">
          {{ record.speed_multiplier.toFixed(1) }}x
        </a-tag>
      </template>
      <template #actions="{ record }">
        <a-button type="text" size="mini" @click="editQuota(record)">编辑</a-button>
      </template>
    </a-table>

    <a-empty v-if="!loading && quotas.length === 0" description="暂无配额数据" />

    <!-- 编辑弹窗 -->
    <a-modal v-model:visible="showEditModal" title="编辑配额" @ok="saveQuota" width="480px">
      <a-form layout="vertical">
        <a-form-item label="用户">
          <span>{{ editForm.user_id }}</span>
        </a-form-item>
        <a-form-item label="配额上限">
          <a-input-number
            v-model="editForm.quota_gb"
            :min="0.1"
            :step="0.5"
            :precision="1"
            style="width: 100%"
          >
            <template #suffix>GB</template>
          </a-input-number>
        </a-form-item>
        <a-form-item label="限速倍率">
          <a-slider
            v-model="editForm.speed_multiplier"
            :min="0.1"
            :max="5.0"
            :step="0.1"
            :marks="{ 0.1: '0.1x', 1: '1x', 5: '5x' }"
          />
          <span class="slider-hint">当前 {{ editForm.speed_multiplier.toFixed(1) }}x</span>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { oss } from '../../api'

const quotas = ref([])
const loading = ref(false)
const showEditModal = ref(false)
const editForm = ref({ user_id: '', quota_gb: 1, speed_multiplier: 1.0 })

const quotaColumns = [
  { title: '用户', slotName: 'user', width: 220 },
  { title: '配额', slotName: 'quota', width: 120 },
  { title: '已用', slotName: 'used', width: 200 },
  { title: '限速倍率', slotName: 'multiplier', width: 100 },
  { title: '操作', slotName: 'actions', width: 80, fixed: 'right' },
]

function shortId(id) {
  return id ? `${id.slice(0, 8)}...${id.slice(-4)}` : '-'
}

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let v = bytes
  while (v >= 1024 && i < units.length - 1) { v /= 1024; i++ }
  return `${v.toFixed(1)} ${units[i]}`
}

function progressColor(pct) {
  if (pct >= 90) return 'var(--color-danger)'
  if (pct >= 70) return 'var(--color-warning)'
  return 'var(--color-success)'
}

function multiplierColor(m) {
  if (m > 1.5) return 'green'
  if (m < 0.5) return 'red'
  return 'blue'
}

async function loadQuotas() {
  loading.value = true
  try {
    const data = await oss.adminQuotas({ limit: 200 })
    if (data) quotas.value = data.items || []
  } catch (err) {
    Message.error(err.message || '加载配额失败')
  } finally {
    loading.value = false
  }
}

function editQuota(record) {
  editForm.value = {
    user_id: record.user_id,
    quota_gb: parseFloat((record.quota_bytes / 1024**3).toFixed(1)),
    speed_multiplier: record.speed_multiplier,
  }
  showEditModal.value = true
}

async function saveQuota() {
  const quotaBytes = Math.round(editForm.value.quota_gb * 1024**3)
  try {
    await oss.updateQuota(editForm.value.user_id, {
      quota_bytes: quotaBytes,
      speed_multiplier: editForm.value.speed_multiplier,
    })
    Message.success('配额更新成功')
    showEditModal.value = false
    await loadQuotas()
  } catch (err) {
    Message.error(err.message || '更新失败')
  }
}

onMounted(() => { loadQuotas() })
</script>

<style scoped>
.user-cell { font-family: monospace; font-size: 13px; }
.used-cell { display: flex; align-items: center; gap: 8px; }
.used-text { font-size: 12px; color: var(--color-text-3); white-space: nowrap; }
.slider-hint { font-size: 12px; color: var(--color-text-3); margin-top: 4px; display: block; }
</style>
