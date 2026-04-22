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
      <a-button type="primary" size="small">
        <template #icon><icon-plus /></template>
        添加资产
      </a-button>
    </div>

    <div class="status-row">
      <div class="status-card">
        <div class="status-num">{{ stats.total }}</div>
        <div class="status-label">总资产</div>
      </div>
      <div class="status-card">
        <div class="status-num">{{ stats.active }}</div>
        <div class="status-label">在线</div>
      </div>
      <div class="status-card s-fail">
        <div class="status-num">{{ stats.offline }}</div>
        <div class="status-label">离线</div>
      </div>
    </div>

    <div class="asset-list">
      <div v-if="assets.length === 0" class="empty-state">
        <icon-apps class="empty-icon" />
        <p>暂无资产记录</p>
        <a-button type="primary" size="small">添加第一个资产</a-button>
      </div>
      <a-table v-else :data="assets" :columns="columns" row-key="id" :bordered="false" class="asset-table" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { IconApps, IconPlus, IconArrowLeft } from '@arco-design/web-vue/es/icon'

const stats = ref({ total: 0, active: 0, offline: 0 })
const assets = ref([])
const columns = [
  { title: '名称', dataIndex: 'name' },
  { title: '类型', dataIndex: 'type' },
  { title: '状态', slotName: 'status' },
  { title: '更新时间', dataIndex: 'updated_at' },
]
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
.status-card.s-fail .status-num { color: #cf222e; }
.status-label { font-size: 12px; color: var(--color-text-4); margin-top: 4px; }
.asset-list { display: flex; flex-direction: column; gap: 12px; }
.asset-table {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  overflow: hidden;
}
.empty-state {
  text-align: center; padding: 48px 24px; color: var(--color-text-4);
  background: rgba(255,255,255,0.5); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px dashed var(--color-border-2); border-radius: var(--border-radius-large);
}
.empty-icon { width: 48px; height: 48px; color: var(--color-border-2); margin-bottom: 12px; }
.empty-state p { margin: 8px 0 16px; font-size: 14px; }
</style>
