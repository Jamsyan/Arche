<template>
  <div class="speed-limit-config">
    <!-- 全局限速 -->
    <a-card :bordered="false" title="全局限速" class="glass-card">
      <a-space direction="vertical" :size="16" style="width: 100%">
        <div class="rate-row">
          <span class="rate-label">当前限速</span>
          <a-input-number
            v-model="globalRateMB"
            :min="0.1"
            :max="100"
            :step="0.5"
            :precision="1"
            style="width: 160px"
          >
            <template #suffix>MB/s</template>
          </a-input-number>
          <a-button type="primary" size="small" @click="saveGlobalRate" :loading="saving">
            保存
          </a-button>
        </div>
        <div class="rate-visual">
          <div class="rate-bar" :style="{ width: barWidth + '%' }"></div>
        </div>
      </a-space>
    </a-card>

    <!-- 用户倍率 -->
    <a-card :bordered="false" title="用户限速倍率" style="margin-top: 16px" class="glass-card">
      <a-table
        :data="userRates"
        :columns="rateColumns"
        row-key="user_id"
        :pagination="{ showTotal: true, pageSize: 20 }"
        :loading="loading"
      >
        <template #user="{ record }">
          <span class="user-cell">{{ shortId(record.user_id) }}</span>
        </template>
        <template #multiplier="{ record }">
          <a-input-number
            v-model="record.speed_multiplier"
            :min="0.1"
            :max="10"
            :step="0.1"
            size="small"
            style="width: 100px"
            @change="saveUserRate(record)"
          />
          <span class="hint-text">x</span>
        </template>
        <template #effective="{ record }">
          {{ (globalRateMB * record.speed_multiplier).toFixed(1) }} MB/s
        </template>
      </a-table>

      <a-empty v-if="!loading && userRates.length === 0" description="暂无用户倍率数据" />
    </a-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useAuth } from '../../router/auth.js'

const { authHeaders } = useAuth()
const globalRateMB = ref(10)
const saving = ref(false)
const userRates = ref([])
const loading = ref(false)

const barWidth = computed(() => Math.min(100, (globalRateMB.value / 100) * 100))

const rateColumns = [
  { title: '用户', slotName: 'user', width: 220 },
  { title: '倍率', slotName: 'multiplier', width: 150 },
  { title: '等效限速', slotName: 'effective', width: 150 },
]

function shortId(id) {
  return id ? `${id.slice(0, 8)}...${id.slice(-4)}` : '-'
}

async function loadGlobalRate() {
  try {
    const res = await fetch('/api/oss/admin/rate-limit', { headers: authHeaders() })
    const data = await res.json()
    if (data.code === 'ok') {
      globalRateMB.value = data.data.global_rate_mb
    }
  } catch { /* 使用默认值 */ }
}

async function saveGlobalRate() {
  saving.value = true
  try {
    const rateBytes = Math.round(globalRateMB.value * 1024 * 1024)
    const res = await fetch('/api/oss/admin/rate-limit', {
      method: 'PUT',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ global_rate_bytes: rateBytes }),
    })
    const data = await res.json()
    if (data.code === 'ok') {
      Message.success('全局限速更新成功')
    } else {
      Message.error(data.message)
    }
  } catch {
    Message.error('网络错误')
  } finally {
    saving.value = false
  }
}

async function loadUserRates() {
  loading.value = true
  try {
    const res = await fetch('/api/oss/admin/quotas?limit=200', { headers: authHeaders() })
    const data = await res.json()
    if (data.code === 'ok') userRates.value = data.data.items || []
  } catch {
    Message.error('加载用户倍率失败')
  } finally {
    loading.value = false
  }
}

async function saveUserRate(record) {
  try {
    const res = await fetch(`/api/oss/admin/rate-limit/users/${record.user_id}`, {
      method: 'PUT',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ speed_multiplier: record.speed_multiplier }),
    })
    const data = await res.json()
    if (data.code === 'ok') {
      Message.success(`${shortId(record.user_id)} 倍率已更新为 ${record.speed_multiplier}x`)
    }
  } catch {
    Message.error('保存失败')
  }
}

onMounted(() => {
  loadGlobalRate()
  loadUserRates()
})
</script>

<style scoped>
.glass-card {
  background: rgba(255,255,255,0.75) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(0,0,0,0.06) !important;
  border-radius: var(--border-radius-large) !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03) !important;
}
.rate-row { display: flex; align-items: center; gap: 12px; }
.rate-label { font-weight: 600; color: var(--color-text-2); }
.rate-visual { height: 8px; background: var(--color-fill-2); border-radius: 4px; overflow: hidden; }
.rate-bar { height: 100%; background: var(--color-primary); border-radius: 4px; transition: width 0.3s; }
.user-cell { font-family: monospace; font-size: 13px; }
.hint-text { color: var(--color-text-4); margin-left: 4px; }
</style>
