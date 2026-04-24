<template>
  <div class="component-card" @contextmenu.prevent="showContextMenu">
    <!-- 卡片头部 -->
    <div class="card-header">
      <span class="card-title">{{ title }}</span>
      <div class="card-actions">
        <!-- 图表类型切换 -->
        <a-dropdown trigger="click" @select="handleChartChange">
          <a-button type="text" size="mini" title="切换图表">
            <icon-swap />
          </a-button>
          <template #content>
            <a-doption
              v-for="ct in compatibleCharts"
              :key="ct"
              :value="ct"
              :class="{ active: ct === chartType }"
            >
              {{ getChartTypeName(ct) }}
            </a-doption>
          </template>
        </a-dropdown>

        <!-- 移除 -->
        <a-button type="text" size="mini" @click="$emit('remove')" title="移除">
          <icon-close />
        </a-button>
      </div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-content">
      <!-- 数字卡片 -->
      <div v-if="chartType === 'number'" class="number-display">
        <span class="number-value">{{ displayData.value }}</span>
        <span v-if="displayData.suffix" class="number-suffix">{{ displayData.suffix }}</span>
      </div>

      <!-- 折线图 -->
      <div v-else-if="chartType === 'line'" class="chart-container">
        <uplot
          ref="chartRef"
          :options="lineOptions"
          :data="chartData"
        />
      </div>

      <!-- 柱状图 -->
      <div v-else-if="chartType === 'bar'" class="chart-container">
        <uplot
          ref="chartRef"
          :options="barOptions"
          :data="chartData"
        />
      </div>

      <!-- 表格 -->
      <div v-else-if="chartType === 'table'" class="table-container">
        <table>
          <thead>
            <tr>
              <th v-for="col in tableData.columns" :key="col">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in tableData.rows" :key="idx">
              <td v-for="(cell, cidx) in row" :key="cidx">{{ cell }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-overlay">
        <a-spin size="24" />
      </div>
    </div>

    <!-- 卡片底部：刷新控制 -->
    <div class="card-footer">
      <div class="refresh-info">
        <span class="refresh-label">刷新:</span>
        <a-input-number
          v-model="refreshInterval"
          :min="5"
          :max="300"
          size="mini"
          hide-button
          style="width: 60px"
          @change="handleIntervalChange"
        />
        <span class="refresh-unit">秒</span>
      </div>
      <a-button type="text" size="mini" @click="handleRefresh" :loading="isLoading">
        <icon-refresh :class="{ spinning: isLoading }" />
      </a-button>
    </div>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenuVisible"
      class="context-menu"
      :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }"
      @click.stop
    >
      <div class="context-menu-item" @click="handleAddToDashboard">
        <icon-plus /> 添加到监控大屏
      </div>
      <div class="context-menu-item" @click="handleConvertChart">
        <icon-swap /> 转换图表
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import uPlot from 'uplot'
import 'uplot/dist/uPlot.min.css'
import {
  IconClose,
  IconSwap,
  IconRefresh,
  IconPlus
} from '@arco-design/web-vue/es/icon'
import { useMonitorStore } from '../../stores/monitor.js'
import { usePluginRegistry } from '../../stores/pluginRegistry.js'
import { useMonitorPolling } from '../../composables/useMonitorPolling.js'
import { useChartInterop } from '../../composables/useChartInterop.js'

const props = defineProps({
  componentId: { type: String, required: true },
  title: { type: String, default: '' },
  chartType: { type: String, default: 'number' }
})

const emit = defineEmits(['remove', 'change-chart'])

const monitorStore = useMonitorStore()
const pluginRegistry = usePluginRegistry()
const { ChartTypes, getCompatibleCharts, getChartTypeName, renderChart, renderNumber, renderLine, renderBar, renderTable } = useChartInterop()

// 组件元信息
const componentMeta = computed(() =>
  pluginRegistry.atomicComponents.find(c => c.id === props.componentId)
)

// 支持的图表类型
const compatibleCharts = computed(() =>
  getCompatibleCharts(componentMeta.value || {})
)

// 右键菜单
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)

function showContextMenu(e) {
  contextMenuVisible.value = true
  contextMenuX.value = e.offsetX
  contextMenuY.value = e.offsetY

  document.addEventListener('click', hideContextMenu, { once: true })
}

function hideContextMenu() {
  contextMenuVisible.value = false
}

function handleAddToDashboard() {
  monitorStore.addComponent({
    componentId: props.componentId,
    title: props.title,
    chartType: props.chartType
  })
  hideContextMenu()
}

function handleConvertChart() {
  // 切换到下一个支持的图表类型
  const charts = compatibleCharts.value
  const currentIdx = charts.indexOf(props.chartType)
  const nextIdx = (currentIdx + 1) % charts.length
  emit('change-chart', charts[nextIdx])
  hideContextMenu()
}

// 轮询
const refreshInterval = ref(30)
const { isPolling, isLoading, lastData, startPolling, stopPolling, refresh } = useMonitorPolling({
  dataSource: componentMeta.value?.dataSource || '/api/monitor/default',
  onData: (data) => {
    // 数据更新时会自动触发视图更新
  }
})

// 显示数据
const displayData = computed(() => {
  if (!lastData.value) return { value: '--', suffix: '' }
  return renderNumber(lastData.value, {
    suffix: componentMeta.value?.suffix || ''
  })
})

// 图表数据
const chartData = computed(() => {
  if (!lastData.value) return [[], []]
  const data = Array.isArray(lastData.value) ? lastData.value : [lastData.value]
  return renderLine(data)
})

// 图表配置
const chartRef = ref(null)

const lineOptions = computed(() => ({
  width: 400,
  height: 150,
  scales: {
    x: { time: true },
    y: { auto: true }
  },
  axes: [
    { stroke: '#999', grid: { stroke: 'rgba(0,0,0,0.05)' } },
    { stroke: '#999', grid: { stroke: 'rgba(0,0,0,0.05)' } }
  ],
  series: [
    {},
    { stroke: '#165dff', width: 2, fill: 'rgba(22,93,255,0.1)' }
  ]
}))

const barOptions = computed(() => ({
  width: 400,
  height: 150,
  scales: {
    x: { time: false },
    y: { auto: true }
  },
  axes: [
    { stroke: '#999', grid: { stroke: 'rgba(0,0,0,0.05)' } },
    { stroke: '#999', grid: { stroke: 'rgba(0,0,0,0.05)' } }
  ],
  series: [
    {},
    { fill: '#165dff', stroke: '#165dff' }
  ]
}))

// 表格数据
const tableData = computed(() => {
  if (!lastData.value) return { columns: [], rows: [] }
  return renderTable(lastData.value)
})

// 处理图表类型变更
function handleChartChange(chartType) {
  emit('change-chart', chartType)
}

// 处理刷新间隔变更
function handleIntervalChange(interval) {
  refreshInterval.value = interval
  if (isPolling.value) {
    startPolling(interval)
  }
}

// 手动刷新
function handleRefresh() {
  refresh()
}

// 监听组件元信息变化，更新轮询源
watch(() => componentMeta.value?.dataSource, (newSource) => {
  if (newSource && isPolling.value) {
    startPolling(refreshInterval.value)
  }
})

onMounted(() => {
  if (componentMeta.value?.dataSource) {
    startPolling(refreshInterval.value)
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.component-card {
  height: 100%;
  background: #fff;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-fill-1);
}

.card-title {
  font-weight: 500;
  font-size: 13px;
  color: var(--color-text-1);
}

.card-actions {
  display: flex;
  gap: 4px;
}

.card-content {
  flex: 1;
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.number-display {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.number-value {
  font-size: 32px;
  font-weight: 600;
  color: var(--color-text-1);
  font-variant-numeric: tabular-nums;
}

.number-suffix {
  font-size: 14px;
  color: var(--color-text-3);
}

.chart-container {
  width: 100%;
  height: 100%;
}

.table-container {
  width: 100%;
  overflow: auto;
}

.table-container table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.table-container th,
.table-container td {
  padding: 6px 8px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.table-container th {
  font-weight: 500;
  background: var(--color-fill-1);
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  border-top: 1px solid var(--color-border);
  background: var(--color-fill-1);
}

.refresh-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--color-text-3);
}

.refresh-unit {
  color: var(--color-text-4);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.context-menu {
  position: absolute;
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 4px 0;
  z-index: 1000;
  min-width: 160px;
}

.context-menu-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.context-menu-item:hover {
  background: var(--color-fill-1);
}
</style>
