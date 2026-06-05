<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NGrid, NGi } from 'naive-ui'
import ProTable from '@/components/ProTable.vue'
import { getAssetsApi, getAssetStatsApi, type AssetStats } from '@/services/api'

const stats = ref<AssetStats>({ total: 0, by_type: {} })

const columns = [
  { title: '名称', key: 'name', ellipsis: true },
  { title: '类型', key: 'asset_type', width: 120 },
  { title: '创建时间', key: 'created_at', width: 160 }
]

const typeEntries = ref<{ type: string; count: number; label: string }[]>([])

const typeLabelMap: Record<string, string> = {
  blog_post: '博客帖子',
  file: '文件',
  crawl_result: '爬取结果',
  training_job: '训练任务',
  dataset: '数据集',
  artifact: '构建产物',
  config: '配置',
  code_repo: '代码仓库',
  oss_file: 'OSS文件',
  monitor_template: '监控模板',
  training_instance: '训练实例'
}

const fetchData = async () => {
  try {
    const statsRes = await getAssetStatsApi({ silent: true, skipAuthLogout: true })
    stats.value = statsRes
    typeEntries.value = Object.entries(statsRes.by_type || {}).map(([type, value]) => ({
      type,
      count: typeof value === 'object' ? value.count : value,
      label: typeLabelMap[type] || type
    }))
  } catch {
    // 静默
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="asset-admin-page">
    <div class="page-heading">
      <h2>资产目录</h2>
    </div>

    <NGrid :cols="typeEntries.length + 1" :x-gap="12" :y-gap="12" class="stats-grid">
      <NGi>
        <div class="section-card stat-card">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">资产总数</div>
        </div>
      </NGi>
      <NGi v-for="entry in typeEntries" :key="entry.type">
        <div class="section-card stat-card">
          <div class="stat-value">{{ entry.count }}</div>
          <div class="stat-label">{{ entry.label }}</div>
        </div>
      </NGi>
    </NGrid>

    <div class="section-card table-card">
      <ProTable
        :columns="columns"
        :request="
          (p) =>
            getAssetsApi(
              { page: p.page, page_size: p.pageSize },
              { silent: true, skipAuthLogout: true }
            )
        "
        row-key="id"
      />
    </div>
  </div>
</template>

<style scoped>
.asset-admin-page {
  max-width: 100%;
}
.page-heading {
  margin-bottom: 16px;
}
.page-heading h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}
.stats-grid {
  margin-bottom: 16px;
}
.section-card {
  background: rgba(255, 248, 236, 0.72);
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-md);
  backdrop-filter: blur(4px);
}
.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  gap: 6px;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}
.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}
.table-card {
  padding: 16px;
}
</style>
