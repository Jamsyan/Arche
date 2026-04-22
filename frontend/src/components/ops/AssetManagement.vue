<template>
  <div class="ops-page">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.push('/platform')" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <icon-apps class="header-icon" />
        <h1 class="page-title">资产管理</h1>
      </div>
      <a-space>
        <a-input-search v-model="searchKeyword" placeholder="搜索资产..." size="small" style="width: 200px" @search="doSearch" />
        <a-button type="text" size="small" @click="fetchAssets" :loading="refreshing">
          <template #icon><icon-refresh /></template>
        </a-button>
      </a-space>
    </div>

    <!-- 统计概览 -->
    <div class="status-row">
      <div class="status-card">
        <div class="status-num">{{ assetStats.total ?? 0 }}</div>
        <div class="status-label">总资产</div>
      </div>
      <div class="status-card">
        <div class="status-num">{{ assetStats.byType?.model ?? 0 }}</div>
        <div class="status-label">模型</div>
      </div>
      <div class="status-card">
        <div class="status-num">{{ assetStats.byType?.dataset ?? 0 }}</div>
        <div class="status-label">数据集</div>
      </div>
    </div>

    <!-- 资产列表 -->
    <a-table
      :data="assets"
      :columns="columns"
      row-key="id"
      :bordered="false"
      :pagination="pagination"
      :loading="loading"
      class="asset-table"
      @page-change="onPageChange"
    >
      <template #name="{ record }">
        <span class="asset-name">{{ record.name || record.asset_name }}</span>
      </template>
      <template #asset_type="{ record }">
        <a-tag :color="assetTypeColor(record.asset_type || record.type)">
          {{ record.asset_type || record.type || '—' }}
        </a-tag>
      </template>
      <template #status="{ record }">
        <a-tag :color="record.status === 'active' ? 'green' : 'gray'">
          {{ record.status === 'active' ? '可用' : (record.status || '—') }}
        </a-tag>
      </template>
      <template #created_at="{ record }">
        {{ record.created_at ? new Date(record.created_at).toLocaleString('zh-CN') : '-' }}
      </template>
    </a-table>

    <a-empty v-if="!loading && assets.length === 0" description="暂无资产" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useAuth } from '../../router/auth.js'
import { IconApps, IconArrowLeft, IconRefresh } from '@arco-design/web-vue/es/icon'

const { authHeaders } = useAuth()
const loading = ref(true)
const refreshing = ref(false)
const assets = ref([])
const assetStats = ref({ total: 0, byType: {} })
const searchKeyword = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const pagination = { showTotal: true, pageSize: 20 }

const columns = [
  { title: '名称', slotName: 'name', width: 240 },
  { title: '类型', slotName: 'asset_type', width: 100 },
  { title: '状态', slotName: 'status', width: 80 },
  { title: '创建时间', slotName: 'created_at', width: 180 },
]

const ASSET_TYPE_COLORS = {
  model: 'blue', dataset: 'green', checkpoint: 'orange', config: 'purple', other: 'gray',
}

function assetTypeColor(type) { return ASSET_TYPE_COLORS[type] ?? 'gray' }

async function fetchAssets() {
  loading.value = true
  try {
    const [listRes, statsRes] = await Promise.all([
      fetch(`/api/assets?page=${page.value}&page_size=${pageSize.value}`, { headers: authHeaders() }),
      fetch('/api/assets/stats', { headers: authHeaders() }),
    ])
    const listData = await listRes.json()
    const statsData = await statsRes.json()
    if (listData.code === 'ok') {
      assets.value = listData.data.items || []
      total.value = listData.data.total || 0
      pagination.total = total.value
    }
    if (statsData.code === 'ok') {
      assetStats.value = statsData.data
    }
  } catch {
    Message.error('加载资产失败')
  } finally {
    loading.value = false
  }
}

async function doSearch() {
  if (!searchKeyword.value.trim()) { fetchAssets(); return }
  loading.value = true
  try {
    const res = await fetch(`/api/assets/search?keyword=${encodeURIComponent(searchKeyword.value)}`, {
      headers: authHeaders(),
    })
    const result = await res.json()
    if (result.code === 'ok') {
      assets.value = result.data.items || []
      total.value = result.data.total || 0
      pagination.total = total.value
    } else {
      Message.error(result.message || '搜索失败')
    }
  } catch {
    Message.error('网络错误')
  } finally {
    loading.value = false
  }
}

function onPageChange(p) {
  page.value = p
  fetchAssets()
}

onMounted(() => { fetchAssets() })
</script>

<style scoped>
.ops-page { max-width: 800px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.header-icon { width: 24px; height: 24px; color: var(--color-primary); }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }
.status-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }
.status-card {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  padding: 16px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.status-card .status-num { font-size: 28px; font-weight: 700; color: var(--color-text-1); line-height: 1; }
.status-label { font-size: 12px; color: var(--color-text-4); margin-top: 4px; }
.asset-table {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  box-shadow: 0 1px 4px rgba(0,0,0,0.03); overflow: hidden;
}
.asset-name { font-weight: 500; }
</style>
