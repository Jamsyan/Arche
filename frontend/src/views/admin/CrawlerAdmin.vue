<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NButton, NTag, useMessage } from 'naive-ui'
import ProTable from '@/components/ProTable.vue'
import {
  getCrawlerStatusApi,
  startCrawlerApi,
  stopCrawlerApi,
  getCrawlerRecordsApi,
  getCrawlerSeedsApi,
  addCrawlerSeedApi,
  type CrawlerStatus
} from '@/services/api'

const message = useMessage()
const status = ref<CrawlerStatus>({ running: false })
const seeds = ref<string[]>([])
const loading = ref(false)
const newSeed = ref('')

const columns = [
  { title: 'URL', key: 'url', ellipsis: true },
  { title: '状态', key: 'status', width: 100 },
  { title: '时间', key: 'created_at', width: 160 }
]

const toggleCrawler = async () => {
  try {
    if (status.value.running) {
      await stopCrawlerApi({ silent: true })
      status.value.running = false
      message.success('爬虫已停止')
    } else {
      await startCrawlerApi({ silent: true })
      status.value.running = true
      message.success('爬虫已启动')
    }
  } catch {
    message.error('操作失败')
  }
}

const addSeed = async () => {
  if (!newSeed.value.trim()) return
  try {
    await addCrawlerSeedApi(newSeed.value, { silent: true })
    seeds.value.push(newSeed.value)
    newSeed.value = ''
    message.success('种子已添加')
  } catch {
    message.error('添加失败')
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const [statusRes, seedsRes] = await Promise.all([
      getCrawlerStatusApi({ silent: true, skipAuthLogout: true }),
      getCrawlerSeedsApi({ silent: true, skipAuthLogout: true })
    ])
    status.value = statusRes
    seeds.value = seedsRes || []
  } catch {
    // 静默
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="crawler-admin-page">
    <div class="page-heading">
      <h2>爬虫管理</h2>
      <div class="status-bar">
        <NTag :type="status.running ? 'success' : 'default'" size="small" :bordered="false">
          {{ status.running ? '运行中' : '已停止' }}
        </NTag>
        <NButton size="small" :type="status.running ? 'warning' : 'primary'" @click="toggleCrawler">
          {{ status.running ? '停止' : '启动' }}
        </NButton>
      </div>
    </div>

    <div class="section-card seeds-card">
      <h3 class="section-title">种子管理</h3>
      <div class="seed-input">
        <input
          v-model="newSeed"
          class="seed-field"
          placeholder="输入种子 URL……"
          @keydown.enter="addSeed"
        />
        <NButton size="small" type="primary" @click="addSeed">添加</NButton>
      </div>
      <div v-if="seeds.length > 0" class="seed-list">
        <span v-for="s in seeds" :key="s" class="seed-tag">{{ s }}</span>
      </div>
      <div v-else class="empty-hint">暂无种子</div>
    </div>

    <div class="section-card table-card">
      <h3 class="section-title">抓取记录</h3>
      <ProTable
        :columns="columns"
        :request="
          (p) =>
            getCrawlerRecordsApi(
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
.crawler-admin-page {
  max-width: 100%;
}
.page-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-heading h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}
.status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-card {
  background: rgba(255, 248, 236, 0.72);
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-md);
  backdrop-filter: blur(4px);
}
.seeds-card {
  padding: 16px;
  margin-bottom: 16px;
}
.table-card {
  padding: 16px;
}
.section-title {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
.seed-input {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.seed-field {
  flex: 1;
  height: 32px;
  border: 1px solid rgba(130, 95, 65, 0.14);
  border-radius: var(--radius-sm);
  background: rgba(255, 248, 236, 0.52);
  padding: 0 10px;
  font-size: 13px;
  color: var(--text-primary);
  outline: none;
}
.seed-field:focus {
  border-color: var(--primary-color);
}
.seed-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.seed-tag {
  font-size: 12px;
  background: rgba(130, 95, 65, 0.08);
  color: var(--text-secondary);
  padding: 3px 8px;
  border-radius: 4px;
}
.empty-hint {
  font-size: 13px;
  color: var(--text-tertiary);
  text-align: center;
  padding: 12px 0;
}
</style>
