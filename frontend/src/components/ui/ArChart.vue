<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(
  defineProps<{
    /** ECharts option */
    option?: Record<string, unknown>
    /** 是否不渲染（用于异步加载） */
    lazy?: boolean
    /** 容器高度 */
    height?: number | string
  }>(),
  {
    option: () => ({}),
    lazy: false,
    height: 300
  }
)

const chartRef = ref<HTMLDivElement>()
let instance: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

function initChart() {
  if (!chartRef.value || props.lazy) return
  instance?.dispose()
  instance = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  instance.setOption(props.option)
  // ResizeObserver 代替 window.resize
  resizeObserver = new ResizeObserver(() => {
    instance?.resize()
  })
  resizeObserver.observe(chartRef.value)
}

function updateChart() {
  if (!instance) return
  instance.setOption(props.option, { notMerge: false })
}

onMounted(initChart)

watch(() => props.option, updateChart, { deep: true })

onUnmounted(() => {
  resizeObserver?.disconnect()
  instance?.dispose()
  instance = null
})
</script>

<template>
  <div ref="chartRef" class="ar-chart" :style="{ height: typeof height === 'number' ? height + 'px' : height }" />
</template>

<style scoped>
.ar-chart {
  width: 100%;
  min-height: 100px;
}
</style>
