<template>
  <div class="cloud-repos">
    <!-- 统计卡片 -->
    <div class="status-row">
      <div class="status-card">
        <div class="status-num">{{ stats.total ?? 0 }}</div>
        <div class="status-label">总仓库数</div>
      </div>
      <div class="status-card s-github">
        <div class="status-num">{{ stats.byPlatform?.github ?? 0 }}</div>
        <div class="status-label">GitHub</div>
      </div>
      <div class="status-card s-gitee">
        <div class="status-num">{{ stats.byPlatform?.gitee ?? 0 }}</div>
        <div class="status-label">Gitee</div>
      </div>
      <div class="status-card s-other">
        <div class="status-num">{{ stats.byPlatform?.other ?? 0 }}</div>
        <div class="status-label">其他平台</div>
      </div>
    </div>

    <!-- 仓库列表 -->
    <a-table
      :data="repos"
      :columns="repoColumns"
      row-key="id"
      :bordered="false"
      :pagination="pagination"
      class="repo-table"
      @page-change="onPageChange"
    >
      <template #name="{ record }">
        <div class="repo-item">
          <icon-github class="repo-icon" />
          <div class="repo-info">
            <span class="repo-name">{{ record.name }}</span>
            <a-link :href="record.git_url" target="_blank" class="repo-url">{{ record.git_url }}</a-link>
          </div>
        </div>
      </template>
      <template #branch="{ record }">
        <a-tag size="small" color="gray">{{ record.git_branch }}</a-tag>
      </template>
      <template #auth="{ record }">
        <a-tag v-if="record.git_token" size="small" color="green">已配置 Token</a-tag>
        <span v-else class="no-auth">公开</span>
      </template>
      <template #created_at="{ record }">
        <span class="time-text">{{ formatTime(record.created_at) }}</span>
      </template>
      <template #actions="{ record }">
        <a-space size="small">
          <a-button size="mini" @click="syncRepo(record)">
            <template #icon><icon-sync /></template>
            同步
          </a-button>
          <a-button size="mini" @click="editRepo(record)">
            <template #icon><icon-edit /></template>
            编辑
          </a-button>
          <a-popconfirm
            content="确定要删除这个代码仓库吗？删除后不可恢复。"
            @ok="deleteRepo(record)"
          >
            <a-button size="mini" status="danger">
              <template #icon><icon-delete /></template>
              删除
            </a-button>
          </a-popconfirm>
        </a-space>
      </template>
    </a-table>

    <!-- 添加/编辑仓库弹窗 -->
    <a-modal v-model:visible="showAddModal" :title="isEdit ? '编辑代码仓库' : '添加代码仓库'" @ok="saveRepo" width="600">
      <a-form :model="repoForm" layout="vertical">
        <a-form-item label="仓库名称" field="name" :rules="[{ required: true, message: '请输入仓库名称' }]">
          <a-input v-model="repoForm.name" placeholder="例如：BERT 中文预训练" />
        </a-form-item>

        <a-form-item label="Git 仓库 URL" field="git_url" :rules="[{ required: true, message: '请输入仓库 URL' }]">
          <a-input v-model="repoForm.git_url" placeholder="https://github.com/user/repo.git" />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="分支" :rules="[{ required: true, message: '请输入分支名称' }]">
              <a-input v-model="repoForm.git_branch" placeholder="main" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="Git 访问 Token（私有仓库必填）">
          <a-input-password v-model="repoForm.git_token" placeholder="ghp_xxxxxxx，留空表示公开仓库" />
          <div class="form-hint">
            Token 会被加密存储，仅用于拉取代码，不会用于其他用途
          </div>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 同步确认弹窗 -->
    <a-modal v-model:visible="showSyncModal" title="同步代码仓库" @ok="confirmSync" okText="开始同步">
      <p>确定要同步仓库 <strong>{{ syncingRepo?.name }}</strong> 到本地吗？</p>
      <p class="hint">同步会拉取最新版本的代码，覆盖现有内容。</p>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { cloud } from '../../api'
import {
  IconPlus, IconRefresh, IconGithub, IconSync,
  IconEdit, IconDelete,
} from '@arco-design/web-vue/es/icon'
const refreshing = ref(false)
const showAddModal = ref(false)
const showSyncModal = ref(false)
const isEdit = ref(false)
const repos = ref([])
const syncingRepo = ref(null)
const stats = ref({ total: 0, byPlatform: {} })
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const pagination = { showTotal: true, pageSize: 20 }

const repoColumns = [
  { title: '名称/地址', slotName: 'name', width: 400 },
  { title: '分支', slotName: 'branch', width: 100 },
  { title: '认证状态', slotName: 'auth', width: 120 },
  { title: '添加时间', slotName: 'created_at', width: 180 },
  { title: '操作', slotName: 'actions', width: 240, fixed: 'right' },
]

const repoForm = ref({
  id: undefined,
  name: '',
  git_url: '',
  git_branch: 'main',
  git_token: '',
})

// 工具函数
function formatTime(timeStr) {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 提取平台信息
function getPlatform(url) {
  if (!url) return 'other'
  if (url.includes('github.com')) return 'github'
  if (url.includes('gitee.com')) return 'gitee'
  return 'other'
}

async function fetchRepos() {
  refreshing.value = true
  try {
    const data = await cloud.listRepos({ page: page.value, page_size: pageSize.value })
    repos.value = data?.items || []
    total.value = data?.total || 0
    pagination.total = total.value

    // 统计平台
    const byPlatform = { github: 0, gitee: 0, other: 0 }
    repos.value.forEach(repo => {
      const platform = getPlatform(repo.git_url)
      byPlatform[platform] = (byPlatform[platform] || 0) + 1
    })
    stats.value = {
      total: total.value,
      byPlatform,
    }
  } catch (err) {
    Message.error(err.message || '加载代码仓库失败')
  } finally {
    refreshing.value = false
  }
}

function onPageChange(p) {
  page.value = p
  fetchRepos()
}

function editRepo(repo) {
  isEdit.value = true
  repoForm.value = {
    id: repo.id,
    name: repo.name,
    git_url: repo.git_url,
    git_branch: repo.git_branch,
    git_token: repo.git_token || '', // Token 会被加密，这里可能返回空，需要用户重新输入或者保留原有值
  }
  showAddModal.value = true
}

async function saveRepo() {
  if (!repoForm.value.name?.trim()) { Message.warning('请输入仓库名称'); return }
  if (!repoForm.value.git_url?.trim()) { Message.warning('请输入 Git 仓库 URL'); return }
  if (!repoForm.value.git_branch?.trim()) { Message.warning('请输入分支名称'); return }

  try {
    const body = {
      name: repoForm.value.name,
      git_url: repoForm.value.git_url,
      git_branch: repoForm.value.git_branch,
    }

    // 只有当用户输入了新的 Token 时才发送
    if (repoForm.value.git_token?.trim()) {
      body.git_token = repoForm.value.git_token.trim()
    }

    if (isEdit.value) {
      await cloud.updateRepo(repoForm.value.id, body)
    } else {
      await cloud.createRepo(body)
    }
    Message.success(isEdit.value ? '仓库更新成功' : '仓库添加成功')
    showAddModal.value = false
    repoForm.value = { id: undefined, name: '', git_url: '', git_branch: 'main', git_token: '' }
    isEdit.value = false
    await fetchRepos()
  } catch (err) {
    Message.error(err.message || '保存失败')
  }
}

function syncRepo(repo) {
  syncingRepo.value = repo
  showSyncModal.value = true
}

async function confirmSync() {
  if (!syncingRepo.value) return

  try {
    await cloud.syncRepo(syncingRepo.value.id)
    Message.success('同步任务已提交，将在后台拉取最新代码')
    showSyncModal.value = false
    syncingRepo.value = null
  } catch (err) {
    Message.error(err.message || '网络错误')
  }
}

async function deleteRepo(repo) {
  try {
    await cloud.deleteRepo(repo.id)
    Message.success('代码仓库已删除')
    await fetchRepos()
  } catch (err) {
    Message.error(err.message || '网络错误')
  }
}

onMounted(() => {
  fetchRepos()
})
</script>

<style scoped>
.cloud-repos {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
}

/* 统计卡片行 */
.status-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.status-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
  transition: all 0.2s ease;
}

.status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.status-card .status-num {
  font-size: 32px;
  font-weight: 700;
  color: #1d2129;
  line-height: 1;
  margin-bottom: 8px;
}

.status-card.s-github .status-num { color: #165dff; }
.status-card.s-gitee .status-num { color: #f53f3f; }
.status-card.s-other .status-num { color: #722ed1; }

.status-label {
  font-size: 13px;
  color: #86909c;
}

/* 仓库表格 */
.repo-table {
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.7);
}

.repo-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.repo-icon {
  font-size: 24px;
  color: #f53f3f;
  flex-shrink: 0;
}

.repo-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.repo-name {
  font-weight: 500;
  color: #1d2129;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.repo-url {
  font-size: 12px;
  color: #165dff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-auth {
  font-size: 13px;
  color: #86909c;
}

.time-text {
  font-size: 13px;
  color: #4e5969;
}

.form-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #86909c;
}

.hint {
  color: #86909c;
  font-size: 13px;
}
</style>
