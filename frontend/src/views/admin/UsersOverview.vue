<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Component } from 'vue'
import { NIcon } from 'naive-ui'
import { PersonOutline, DocumentTextOutline } from '@vicons/ionicons5'

const router = useRouter()

interface StatItem {
  label: string
  value: string | number
}

interface CardItem {
  title: string
  icon: Component
  stats: StatItem[]
  to: string
  note?: string
  chartData?: number[]
}

const cards: CardItem[] = [
  {
    title: '用户列表',
    icon: PersonOutline,
    stats: [
      { label: '总用户', value: 128 },
      { label: '本月新增', value: 12 },
      { label: '在线', value: 5 }
    ],
    to: '/admin/users/list',
    desc: '查看和管理所有注册用户',
    chartData: [42, 48, 45, 53, 59, 55, 62, 68, 64, 71, 75, 78]
  },
  {
    title: '资产管理',
    icon: DocumentTextOutline,
    stats: [
      { value: '456', label: '帖子' },
      { value: '1,280', label: '评论' },
      { value: '2,345', label: '文件' }
    ],
    to: '/admin/users/assets',
    desc: '帖子/评论/静态文件统一管理'
  }
]

const navigate = (to: string) => {
  router.push(to)
}

const sparklinePath = (data: number[]): string => {
  if (!data || data.length === 0) return ''
  const w = 120,
    h = 30
  const max = Math.max(...data) * 1.2
  const min = Math.min(...data) * 0.8
  const range = max - min || 1
  return data
    .map((v, i) => {
      const x = (i / (data.length - 1)) * w
      const y = h - ((v - min) / range) * h
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
    })
    .join(' ')
}
</script>

<template>
  <div class="overview-page">
    <h1 class="page-title">{{ $route.meta.title }}</h1>
    <div class="card-grid card-grid--2x2">
      <div v-for="card in cards" :key="card.title" class="overview-card" @click="navigate(card.to)">
        <div class="card-header">
          <NIcon size="28" class="card-icon"><component :is="card.icon" /></NIcon>
          <span class="card-title">{{ card.title }}</span>
          <span v-if="card.note" class="card-note">{{ card.note }}</span>
        </div>
        <div class="card-desc" v-if="card.desc">{{ card.desc }}</div>
        <div class="card-stats">
          <div v-for="stat in card.stats" :key="stat.label" class="stat-item">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>
        <div class="card-sparkline-wrap" v-if="card.chartData">
          <svg class="card-sparkline" :viewBox="'0 0 120 30'">
            <path
              :d="sparklinePath(card.chartData!)"
              fill="none"
              stroke="var(--primary-color)"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>
        <div class="card-action">
          <span>进入管理</span>
          <span class="action-arrow">→</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overview-page {
  max-width: 100%;
}

.page-title {
  margin: 0 0 var(--spacing-lg);
  font-size: 22px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.card-grid {
  display: grid;
  gap: var(--spacing-md);
}

.card-grid--2x2 {
  grid-template-columns: repeat(2, 1fr);
}

.overview-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  backdrop-filter: blur(4px);
}

.overview-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.card-icon {
  color: var(--primary-color);
  flex-shrink: 0;
}

.card-title {
  font-size: 16px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.card-note {
  font-size: 11px;
  color: var(--text-tertiary);
  background: var(--surface-inset-color);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  margin-left: auto;
}

.card-desc {
  font-size: 12px;
  color: var(--text-tertiary);
  line-height: 1.4;
}

.card-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-sm);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: var(--spacing-sm) 0;
  background: var(--surface-inset-color);
  border-radius: var(--radius-sm);
}

.stat-value {
  font-size: 20px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.card-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--border-color);
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  color: var(--primary-color);
  transition: all var(--transition-fast);
}

.overview-card:hover .card-action {
  color: var(--primary-hover-color);
}

.action-arrow {
  font-size: 16px;
  transition: transform var(--transition-fast);
}

.overview-card:hover .action-arrow {
  transform: translateX(4px);
}

.card-sparkline-wrap {
  margin: 8px 0 4px;
  height: 40px;
}
.card-sparkline {
  width: 100%;
  height: 100%;
}

/* 响应式 */
@media (max-width: 768px) {
  .card-grid--2x2 {
    grid-template-columns: 1fr;
  }
}
</style>
