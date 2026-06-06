<template>
  <div class="console-dashboard">
    <div class="page-header">
      <h1 class="page-title">控制台</h1>
      <p class="page-desc">总览站点核心数据</p>
    </div>

    <!-- 指标卡片 -->
    <div class="metric-grid">
      <div v-for="m in metrics" :key="m.label" class="metric-card">
        <div class="metric-icon" :class="m.colorClass">
          <NIcon size="22"><component :is="m.icon" /></NIcon>
        </div>
        <div class="metric-body">
          <span class="metric-value">{{ m.value }}</span>
          <span class="metric-label">{{ m.label }}</span>
          <span class="metric-change" :class="m.changeDir">{{ m.change }}</span>
        </div>
      </div>
    </div>

    <!-- 增长趋势图 -->
    <div class="chart-section">
      <div class="chart-header">
        <h2 class="section-title">内容增长趋势</h2>
        <div class="chart-tabs">
          <button
            :class="['chart-tab', { active: chartRange === '7d' }]"
            @click="chartRange = '7d'"
          >
            近7天
          </button>
          <button
            :class="['chart-tab', { active: chartRange === '30d' }]"
            @click="chartRange = '30d'"
          >
            近30天
          </button>
        </div>
      </div>
      <div class="chart-body">
        <svg viewBox="0 0 600 200" class="trend-chart">
          <!-- 网格线 -->
          <line
            v-for="i in 4"
            :key="'g' + i"
            x1="40"
            :y1="i * 40"
            x2="580"
            :y2="i * 40"
            stroke="var(--border-color)"
            stroke-width="0.5"
          />
          <!-- Y轴标签 -->
          <text
            v-for="(label, i) in yLabels"
            :key="'yl' + i"
            x="35"
            :y="200 - i * 40 + 4"
            text-anchor="end"
            class="chart-label"
          >
            {{ label }}
          </text>
          <!-- 折线 -->
          <path
            :d="chartPath"
            fill="none"
            stroke="var(--primary-color)"
            stroke-width="2.5"
            stroke-linejoin="round"
            stroke-linecap="round"
          />
          <!-- 数据点 -->
          <circle
            v-for="(pt, i) in chartPoints"
            :key="'pt' + i"
            :cx="pt.x"
            :cy="pt.y"
            r="3.5"
            fill="var(--primary-color)"
            stroke="#fff"
            stroke-width="1.5"
          />
          <!-- X轴标签 -->
          <text
            v-for="(label, i) in chartXLabels"
            :key="'xl' + i"
            :x="chartXPositions[i]"
            y="192"
            text-anchor="middle"
            class="chart-label"
          >
            {{ label }}
          </text>
        </svg>
      </div>
    </div>

    <!-- 系统状态 + 增长率 -->
    <div class="bottom-section">
      <div class="system-panel">
        <h2 class="section-title">系统状态</h2>
        <div v-for="sys in systemMetrics" :key="sys.label" class="sys-row">
          <span class="sys-label">{{ sys.label }}</span>
          <div class="sys-bar-track">
            <div
              class="sys-bar-fill"
              :style="{ width: sys.percent + '%', background: sys.color }"
            ></div>
          </div>
          <span class="sys-percent">{{ sys.percent }}%</span>
        </div>
      </div>
      <div class="growth-panel">
        <h2 class="section-title">增长率对比</h2>
        <div v-for="g in growthRates" :key="g.label" class="growth-row">
          <span class="growth-label">{{ g.label }}</span>
          <span class="growth-value" :class="g.dir">{{ g.value }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { NIcon } from 'naive-ui'
import { PulseOutline, DocumentTextOutline, PeopleOutline, ServerOutline } from '@vicons/ionicons5'

// ── 指标卡片 ──
const metrics = [
  {
    label: '网站留存',
    value: '76.3%',
    change: '+2.1% 较昨日',
    changeDir: 'up',
    icon: PulseOutline,
    colorClass: 'icon-warm'
  },
  {
    label: '帖子总量',
    value: '12,456',
    change: '+89 今日新增',
    changeDir: 'up',
    icon: DocumentTextOutline,
    colorClass: 'icon-blue'
  },
  {
    label: '当前在线',
    value: '23',
    change: '峰值 156',
    changeDir: 'up',
    icon: PeopleOutline,
    colorClass: 'icon-green'
  },
  {
    label: 'API 请求',
    value: '1,234/min',
    change: '12.4k 今日总计',
    changeDir: 'up',
    icon: ServerOutline,
    colorClass: 'icon-purple'
  }
]

// ── 折线图 ──
const chartRange = ref<'7d' | '30d'>('7d')

const chartData7d = [120, 135, 110, 150, 165, 145, 189]
const chartData30d = [
  120, 135, 110, 150, 165, 145, 189, 200, 180, 210, 195, 220, 240, 225, 250, 235, 260, 245, 270,
  255, 280, 265, 290, 275, 300, 285, 310, 295, 320, 305
]
const chartLabels7d = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const chartData = computed(() => (chartRange.value === '7d' ? chartData7d : chartData30d))
const chartLabels = computed(() =>
  chartRange.value === '7d' ? chartLabels7d : Array.from({ length: 30 }, (_, i) => `${i + 1}日`)
)

const padding = { top: 10, bottom: 25, left: 45, right: 10 }
const chartW = 600
const chartH = 200

const yMax = computed(() => Math.max(...chartData.value) * 1.2)
const yLabels = computed(() => {
  const step = Math.ceil(yMax.value / 4 / 10) * 10
  return [0, step, step * 2, step * 3, step * 4].reverse()
})

const chartPoints = computed(() =>
  chartData.value.map((v, i) => ({
    x:
      padding.left +
      (i / Math.max(chartData.value.length - 1, 1)) * (chartW - padding.left - padding.right),
    y: chartH - padding.bottom - (v / yMax.value) * (chartH - padding.top - padding.bottom)
  }))
)

const chartPath = computed(() => {
  if (chartPoints.value.length === 0) return ''
  return chartPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
})

const chartXPositions = computed(() => chartPoints.value.map((p) => p.x))

const chartXLabels = computed(() => chartLabels.value)

// ── 系统状态 ──
const systemMetrics = [
  { label: 'CPU', percent: 73, color: '#9a5a2f' },
  { label: '内存', percent: 45, color: '#4f7a57' },
  { label: '磁盘', percent: 67, color: '#1890ff' },
  { label: 'OSS', percent: 58, color: '#b98529' }
]

// ── 增长率对比 ──
const growthRates = [
  { label: '较昨日', value: '+2.1%', dir: 'up' },
  { label: '较上周', value: '+8.7%', dir: 'up' },
  { label: '较上月', value: '+15.3%', dir: 'up' }
]
</script>

<style scoped>
.console-dashboard {
  max-width: 100%;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 2px;
  color: var(--text-primary);
}

.page-desc {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0;
}

/* ── 指标卡片 ── */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.metric-card {
  display: flex;
  gap: 14px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  align-items: center;
}

.metric-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-warm {
  background: rgba(154, 90, 47, 0.1);
  color: var(--primary-color);
}
.icon-blue {
  background: rgba(24, 144, 255, 0.1);
  color: #1890ff;
}
.icon-green {
  background: rgba(79, 122, 87, 0.1);
  color: var(--success-color);
}
.icon-purple {
  background: rgba(114, 46, 209, 0.1);
  color: #722ed1;
}

.metric-body {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.metric-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.metric-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.metric-change {
  font-size: 11px;
  font-weight: 500;
}

.metric-change.up {
  color: var(--success-color);
}
.metric-change.down {
  color: var(--error-color);
}

/* ── 图表区域 ── */
.chart-section {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-tabs {
  display: flex;
  gap: 4px;
}

.chart-tab {
  padding: 4px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-tertiary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.chart-tab.active {
  background: var(--primary-light-color);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.chart-tab:hover:not(.active) {
  background: var(--surface-strong-color);
}

.chart-body {
  width: 100%;
}

.trend-chart {
  width: 100%;
  height: auto;
  display: block;
}

.chart-label {
  font-size: 10px;
  fill: var(--text-tertiary);
  font-family: inherit;
}

/* ── 底部双栏 ── */
.bottom-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.system-panel,
.growth-panel {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
}

/* 系统状态 */
.sys-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
}

.sys-label {
  width: 40px;
  font-size: 13px;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.sys-bar-track {
  flex: 1;
  height: 8px;
  background: var(--bg-color);
  border-radius: 4px;
  overflow: hidden;
}

.sys-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.sys-percent {
  width: 36px;
  font-size: 12px;
  color: var(--text-secondary);
  text-align: right;
  flex-shrink: 0;
}

/* 增长率 */
.growth-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--divider-color);
}

.growth-row:last-child {
  border-bottom: none;
}

.growth-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.growth-value {
  font-size: 15px;
  font-weight: 600;
}

.growth-value.up {
  color: var(--success-color);
}
.growth-value.down {
  color: var(--error-color);
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .bottom-section {
    grid-template-columns: 1fr;
  }

  .metric-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
