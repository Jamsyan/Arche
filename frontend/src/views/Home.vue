<template>
  <div class="home-page">
    <!-- 博客欢迎区域 -->
    <div class="hero-section card-glass">
      <div class="hero-content">
        <h1 class="hero-title">你好，我是 Arche</h1>
        <p class="hero-subtitle">
          一名热爱技术的开发者，在这里分享我的技术思考、项目经验和生活感悟。
        </p>
        <div class="hero-buttons">
          <NButton type="primary" size="large" @click="goToBlog"> 浏览文章 </NButton>
          <NButton size="large" @click="goToAbout"> 了解更多 </NButton>
        </div>
      </div>
    </div>

    <!-- 最新文章 -->
    <div class="latest-section">
      <div class="section-header">
        <h2 class="section-title">最新文章</h2>
        <NButton quaternary @click="goToBlog"> 查看全部 → </NButton>
      </div>
      <div class="articles-grid">
        <article
          v-for="post in latestPosts"
          :key="post.id"
          class="article-card card-glass glass-hover"
        >
          <div class="article-meta">
            <span class="article-date">{{ post.date }}</span>
            <NTag size="small" :type="post.tagType">
              {{ post.tag }}
            </NTag>
          </div>
          <h3 class="article-title">
            {{ post.title }}
          </h3>
          <p class="article-excerpt">
            {{ post.excerpt }}
          </p>
          <div class="article-footer">
            <span class="read-time">{{ post.readTime }} 分钟阅读</span>
            <NButton text size="small" @click="viewArticle(post)"> 阅读全文 → </NButton>
          </div>
        </article>
      </div>
    </div>

    <!-- 侧边信息 - 关于我 -->
    <div class="about-section card-glass">
      <div class="about-avatar">
        <!-- 这里可以放头像 -->
        <div class="avatar-placeholder">👨‍💻</div>
      </div>
      <h3 class="about-name">Arche</h3>
      <p class="about-bio">全栈开发者，热爱开源，喜欢探索新技术。</p>
      <div class="about-stats">
        <div class="stat-item">
          <span class="stat-number">{{ stats.articles }}</span>
          <span class="stat-label">文章</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ stats.projects }}</span>
          <span class="stat-label">项目</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ stats.tags }}</span>
          <span class="stat-label">标签</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NButton, NTag, useMessage } from 'naive-ui'
import { getBlogPostsApi } from '@/services/api'

const message = useMessage()

type PostTagType = 'primary' | 'success' | 'warning' | 'error' | 'default' | 'info'

interface LatestPost {
  id: number
  title: string
  excerpt: string
  date: string
  tag: string
  tagType: PostTagType
  readTime: number
}

// 模拟最新文章数据
const latestPosts = ref<LatestPost[]>([])

// 模拟统计数据
const stats = ref({
  articles: 42,
  projects: 15,
  tags: 28
})

const goToBlog = () => {
  message.info('博客页面开发中')
}

const goToAbout = () => {
  message.info('关于页面开发中')
}

const viewArticle = (post: any) => {
  message.info(`打开文章: ${post.title}`)
}

onMounted(async () => {
  try {
    const res = await getBlogPostsApi({
      page: 1,
      page_size: 3
    })
    latestPosts.value = (res.list || []).map((item, index) => ({
      id: Number(item.id || index + 1),
      title: item.title,
      excerpt: item.content?.slice(0, 70) || '暂无摘要',
      date: item.created_at ? item.created_at.slice(0, 10) : '-',
      tag: item.tags?.[0] || '通用',
      tagType: (['primary', 'success', 'warning'][index % 3] as PostTagType) || 'info',
      readTime: Math.max(3, Math.round((item.content?.length || 100) / 240))
    }))
  } catch {
    message.warning('加载最新文章失败，已展示占位内容')
    latestPosts.value = [
      {
        id: 1,
        title: '暂时无法拉取文章',
        excerpt: '请检查后端服务是否启动。',
        date: '-',
        tag: '系统',
        tagType: 'warning',
        readTime: 1
      }
    ]
  }
})
</script>

<style scoped>
.home-page {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--spacing-xl);
}

.hero-section {
  grid-column: 1 / -1;
  text-align: center;
  padding: var(--spacing-2xl);
}

.hero-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: var(--spacing-md);
  background: var(--bg-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 18px;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto var(--spacing-xl);
}

.hero-buttons {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  flex-wrap: wrap;
}

.latest-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.articles-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.article-card {
  padding: var(--spacing-lg);
  cursor: pointer;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.article-date {
  font-size: 13px;
  color: var(--text-tertiary);
}

.article-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
  line-height: 1.4;
}

.article-excerpt {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--spacing-md);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--divider-color);
}

.read-time {
  font-size: 13px;
  color: var(--text-tertiary);
}

.about-section {
  height: fit-content;
  text-align: center;
  padding: var(--spacing-xl);
}

.about-avatar {
  margin-bottom: var(--spacing-md);
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-full);
  background: var(--primary-light-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  margin: 0 auto;
}

.about-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.about-bio {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: var(--spacing-lg);
}

.about-stats {
  display: flex;
  justify-content: space-around;
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--divider-color);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.stat-number {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-color);
}

.stat-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .home-page {
    grid-template-columns: 1fr;
  }

  .about-section {
    order: -1;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .hero-section {
    padding: var(--spacing-xl);
  }
}
</style>
