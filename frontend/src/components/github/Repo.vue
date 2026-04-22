<template>
  <div class="ops-page">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.push('/platform')" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <icon-github class="header-icon" />
        <h1 class="page-title">GitHub 代理</h1>
      </div>
      <a-space>
        <a-input-search
          v-model="searchQuery"
          placeholder="搜索仓库 / 用户..."
          size="small"
          style="width: 220px"
          @search="doSearch"
        />
        <a-button type="primary" size="small" @click="showAddRepoModal = true">
          <template #icon><icon-plus /></template>
          添加仓库
        </a-button>
      </a-space>
    </div>

    <!-- 统计概览 -->
    <div class="status-row">
      <div class="status-card">
        <div class="status-num">{{ stats.repos }}</div>
        <div class="status-label">追踪仓库</div>
      </div>
      <div class="status-card">
        <div class="status-num">{{ stats.stars }}</div>
        <div class="status-label">总 Star</div>
      </div>
      <div class="status-card">
        <div class="status-num">{{ stats.tasks }}</div>
        <div class="status-label">活跃任务</div>
      </div>
      <div class="status-card">
        <div class="status-num">{{ stats.langs }}</div>
        <div class="status-label">语言</div>
      </div>
    </div>

    <!-- 活跃任务 -->
    <div class="section-header">
      <icon-sync class="section-icon spin" />
      <span>活跃任务</span>
    </div>

    <div v-if="activeTasks.length === 0" class="empty-hint">暂无活跃任务</div>
    <div v-else class="task-row">
      <div v-for="task in activeTasks" :key="task.id" class="task-item">
        <div class="task-left">
          <a-tag :color="taskActionColor(task.action)" size="small">{{ task.actionLabel }}</a-tag>
          <span class="task-repo">{{ task.repo }}</span>
        </div>
        <div class="task-right">
          <a-progress :percent="task.progress" size="small" style="width: 100px" />
          <span class="task-status">{{ task.statusLabel }}</span>
        </div>
      </div>
    </div>

    <!-- 仓库列表 -->
    <div class="section-header">
      <icon-apps class="section-icon" />
      <span>追踪仓库</span>
    </div>

    <div v-if="repos.length === 0" class="empty-state">
      <icon-github class="empty-icon" />
      <p>暂无追踪的仓库</p>
      <a-button type="primary" size="small" @click="showAddRepoModal = true">添加第一个仓库</a-button>
    </div>
    <div v-else class="repo-grid">
      <div v-for="repo in repos" :key="repo.full_name" class="repo-card">
        <div class="repo-top">
          <a-avatar :style="{ backgroundColor: '#1f2328', width: 32, height: 32, fontSize: 14 }">
            <icon-github />
          </a-avatar>
          <div class="repo-info">
            <div class="repo-name">{{ repo.name }}</div>
            <div class="repo-full">{{ repo.full_name }}</div>
          </div>
        </div>
        <div class="repo-desc">{{ repo.description || '暂无描述' }}</div>
        <div class="repo-meta">
          <span class="meta-item">
            <icon-star /> {{ repo.stars }}
          </span>
          <span class="meta-item">
            <icon-language /> {{ repo.lang }}
          </span>
          <span class="meta-item">
            <icon-calendar /> {{ repo.updated }}
          </span>
        </div>
        <div class="repo-actions">
          <a-button type="text" size="mini" @click="syncRepo(repo)">
            <template #icon><icon-refresh /></template>
            同步
          </a-button>
          <a-button type="text" size="mini" @click="crawlRepo(repo)">
            <template #icon><icon-download /></template>
            抓取
          </a-button>
          <a-button type="text" size="mini" status="danger" @click="removeRepo(repo)">
            <template #icon><icon-delete /></template>
          </a-button>
        </div>
      </div>
    </div>

    <!-- 添加仓库弹窗 -->
    <a-modal v-model:visible="showAddRepoModal" title="添加 GitHub 仓库" @ok="addRepo">
      <a-form :model="newRepo" layout="vertical">
        <a-form-item label="仓库地址" field="url">
          <a-input v-model="newRepo.url" placeholder="https://github.com/owner/repo" />
        </a-form-item>
        <a-form-item label="同步频率" field="sync">
          <a-select v-model="newRepo.sync">
            <a-option value="manual">手动同步</a-option>
            <a-option value="daily">每天</a-option>
            <a-option value="weekly">每周</a-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  IconGithub, IconPlus, IconStar, IconLanguage, IconCalendar,
  IconRefresh, IconDownload, IconDelete, IconApps, IconArrowLeft,
  IconSync,
} from '@arco-design/web-vue/es/icon'

const searchQuery = ref('')
const showAddRepoModal = ref(false)

const newRepo = ref({ url: '', sync: 'daily' })

const stats = ref({ repos: 0, stars: 0, tasks: 0, langs: 0 })

const repos = ref([])
const activeTasks = ref([])

const TASK_ACTIONS = {
  sync: { label: '同步', color: 'blue' },
  crawl: { label: '抓取', color: 'green' },
  mirror: { label: '镜像', color: 'orange' },
}

function taskActionColor(action) { return TASK_ACTIONS[action]?.color ?? 'gray' }

function doSearch() {
  if (!searchQuery.value.trim()) return
  Message.info(`搜索: ${searchQuery.value}`)
}

function syncRepo(repo) {
  Message.info(`正在同步: ${repo.full_name}`)
}

function crawlRepo(repo) {
  Message.info(`正在抓取: ${repo.full_name}`)
}

function removeRepo(repo) {
  Message.info(`移除仓库: ${repo.full_name}`)
}

function addRepo() {
  if (!newRepo.value.url) {
    Message.warning('请输入仓库地址')
    return
  }
  Message.success(`仓库添加成功`)
  showAddRepoModal.value = false
  newRepo.value = { url: '', sync: 'daily' }
}
</script>

<style scoped>
.ops-page { max-width: 1100px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.header-icon { width: 24px; height: 24px; color: var(--color-text-1); }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }

.status-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
.status-card {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  padding: 16px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.status-card .status-num { font-size: 28px; font-weight: 700; color: var(--color-text-1); line-height: 1; }
.status-label { font-size: 12px; color: var(--color-text-4); margin-top: 4px; }

.section-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600; color: var(--color-text-2);
  margin-bottom: 12px; margin-top: 24px;
}
.section-icon { width: 16px; height: 16px; color: var(--color-text-4); }
.spin { animation: spin 1.5s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.empty-hint {
  text-align: center; padding: 24px; color: var(--color-text-4);
  background: rgba(255,255,255,0.5); border: 1px dashed var(--color-border-2);
  border-radius: var(--border-radius-large); margin-bottom: 16px;
}

.task-row { display: flex; flex-direction: column; gap: 8px; }
.task-item {
  display: flex; justify-content: space-between; align-items: center;
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-medium);
  padding: 10px 16px;
}
.task-left { display: flex; align-items: center; gap: 8px; }
.task-repo { font-size: 13px; font-weight: 500; }
.task-right { display: flex; align-items: center; gap: 12px; }
.task-status { font-size: 12px; color: var(--color-text-3); white-space: nowrap; }

.repo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px; }
.repo-card {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.repo-top { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.repo-info { flex: 1; overflow: hidden; }
.repo-name { font-size: 15px; font-weight: 600; color: var(--color-text-1); }
.repo-full { font-size: 12px; color: var(--color-text-4); }
.repo-desc { font-size: 13px; color: var(--color-text-3); margin-bottom: 12px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.repo-meta { display: flex; gap: 16px; margin-bottom: 12px; }
.meta-item { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: var(--color-text-4); }
.meta-item .arco-icon { width: 12px; height: 12px; }
.repo-actions { display: flex; gap: 4px; border-top: 1px solid var(--color-border-1); padding-top: 8px; }

.empty-state {
  text-align: center; padding: 48px 24px; color: var(--color-text-4);
  background: rgba(255,255,255,0.5); backdrop-filter: blur(12px);
  border: 1px dashed var(--color-border-2); border-radius: var(--border-radius-large);
}
.empty-icon { width: 48px; height: 48px; color: var(--color-border-2); margin-bottom: 12px; }
.empty-state p { margin: 8px 0 16px; font-size: 14px; }
</style>
