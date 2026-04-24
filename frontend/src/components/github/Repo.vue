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
        <a-button type="text" size="small" @click="clearCache">
          <template #icon><icon-refresh /></template>
        </a-button>
      </a-space>
    </div>

    <!-- 搜索结果显示 -->
    <div v-if="searchResults.length > 0" class="status-row">
      <div class="status-card">
        <div class="status-num">{{ searchResults.length }}</div>
        <div class="status-label">搜索结果</div>
      </div>
      <div class="status-card">
        <div class="status-num">{{ searchResults.reduce((s, r) => s + (r.stargazers_count || 0), 0) }}</div>
        <div class="status-label">总 Star</div>
      </div>
      <div class="status-card">
        <div class="status-num">{{ new Set(searchResults.map(r => r.language).filter(Boolean)).size }}</div>
        <div class="status-label">语言</div>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-if="searchResults.length > 0" class="section-header">
      <icon-search class="section-icon" />
      <span>搜索结果</span>
    </div>

    <div v-if="searchResults.length > 0" class="repo-grid">
      <div v-for="repo in searchResults" :key="repo.id" class="repo-card">
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
            <icon-star /> {{ repo.stargazers_count || 0 }}
          </span>
          <span class="meta-item" v-if="repo.language">
            <icon-language /> {{ repo.language }}
          </span>
          <span class="meta-item">
            <icon-calendar /> {{ formatDate(repo.updated_at) }}
          </span>
        </div>
        <div class="repo-actions">
          <a-button type="text" size="mini" @click="openRepo(repo.html_url)">
            <template #icon><icon-link /></template>
            打开
          </a-button>
        </div>
      </div>
    </div>

    <a-empty v-else-if="hasSearched" description="未找到匹配的仓库" />

    <!-- 使用说明 -->
    <div v-if="!hasSearched" class="guide-card">
      <icon-bulb class="guide-icon" />
      <h3 class="guide-title">使用说明</h3>
      <p class="guide-text">通过代理访问 GitHub API，搜索仓库、查看项目信息。</p>
      <p class="guide-text">在上方搜索框输入关键词搜索仓库或用户。</p>
      <div class="guide-examples">
        <a-button type="text" size="mini" @click="quickSearch('vue')">Vue</a-button>
        <a-button type="text" size="mini" @click="quickSearch('python')">Python</a-button>
        <a-button type="text" size="mini" @click="quickSearch('llm')">LLM</a-button>
        <a-button type="text" size="mini" @click="quickSearch('rust')">Rust</a-button>
      </div>
    </div>

    <!-- 缓存状态 -->
    <div class="cache-status">
      <a-tag v-if="lastCacheHit" color="green">缓存命中</a-tag>
      <a-tag v-else color="gray">未使用缓存</a-tag>
      <span class="cache-hint">请求通过代理转发，自动缓存响应结果</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  IconGithub, IconSearch, IconStar, IconLanguage, IconCalendar,
  IconArrowLeft, IconRefresh, IconBulb, IconLink,
} from '@arco-design/web-vue/es/icon'
import { github } from '../../api'

const searchQuery = ref('')
const searchResults = ref([])
const hasSearched = ref(false)
const lastCacheHit = ref(false)

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
}

function openRepo(url) {
  window.open(url, '_blank')
}

async function doSearch() {
  if (!searchQuery.value.trim()) return
  hasSearched.value = true
  searchResults.value = []

  try {
    // 通过代理搜索 GitHub API
    const data = await github.searchRepos({ q: searchQuery.value, per_page: 30 })

    if (Array.isArray(data.items)) {
      searchResults.value = data.items
      lastCacheHit.value = false // 搜索结果通常不缓存
    } else if (Array.isArray(data)) {
      searchResults.value = data
    } else {
      Message.error('搜索失败：响应格式异常')
    }
  } catch (err) {
    Message.error(err.message || '搜索失败：网络错误')
  }
}

function quickSearch(term) {
  searchQuery.value = term
  doSearch()
}

async function clearCache() {
  try {
    await github.clearCache()
    Message.success('缓存已清理')
  } catch (err) {
    Message.error(err.message || '清理失败')
  }
}

onMounted(() => {
  // 页面加载，无需额外操作
})
</script>

<style scoped>
.ops-page { max-width: 1100px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.header-icon { width: 24px; height: 24px; color: var(--color-text-1); }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }

.status-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }
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

.guide-card {
  text-align: center; padding: 48px 24px;
  background: rgba(255,255,255,0.5); border: 1px dashed var(--color-border-2);
  border-radius: var(--border-radius-large);
}
.guide-icon { width: 48px; height: 48px; color: var(--color-border-2); margin-bottom: 12px; }
.guide-title { margin: 8px 0 16px; font-size: 16px; font-weight: 600; color: var(--color-text-1); }
.guide-text { margin: 4px 0; font-size: 14px; color: var(--color-text-3); }
.guide-examples { display: flex; gap: 8px; justify-content: center; margin-top: 16px; }

.cache-status { display: flex; align-items: center; gap: 8px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--color-border-1); }
.cache-hint { font-size: 12px; color: var(--color-text-4); }
</style>
