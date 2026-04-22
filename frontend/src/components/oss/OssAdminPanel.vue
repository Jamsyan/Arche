<template>
  <div class="oss-admin-page">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.push('/admin')" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <icon-storage class="header-icon" />
        <h1 class="page-title">OSS 管理</h1>
      </div>
      <a-tag color="red" size="small">P0 权限</a-tag>
    </div>

    <a-tabs default-active-key="dashboard" type="rounded" class="oss-tabs">
      <a-tab-pane key="dashboard" title="统计大盘">
        <OssDashboard />
      </a-tab-pane>
      <a-tab-pane key="quota" title="配额管理">
        <QuotaManagement />
      </a-tab-pane>
      <a-tab-pane key="speed" title="限速配置">
        <SpeedLimitConfig />
      </a-tab-pane>
      <a-tab-pane key="files" title="文件管理">
        <FileManagement />
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup>
import { IconStorage, IconArrowLeft } from '@arco-design/web-vue/es/icon'
import OssDashboard from './OssDashboard.vue'
import QuotaManagement from './QuotaManagement.vue'
import SpeedLimitConfig from './SpeedLimitConfig.vue'
import FileManagement from './FileManagement.vue'
</script>

<style scoped>
.oss-admin-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 8px 0 32px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.header-icon { width: 24px; height: 24px; color: var(--color-primary); }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }

.oss-tabs :deep(.arco-tabs-nav) {
  background: rgba(255,255,255,0.5);
  backdrop-filter: blur(12px);
  border-radius: var(--border-radius-large);
  padding: 4px;
}
</style>
