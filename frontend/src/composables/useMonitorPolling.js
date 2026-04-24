/**
 * 轮询逻辑 composable
 * 处理间隔验证、请求、本地插值
 */

import { ref, onUnmounted } from 'vue'

// 最小间隔（秒）
const MIN_INTERVAL = 10
// 最大间隔（秒）
const MAX_INTERVAL = 300
// 插值数据点数量
const INTERPOLATION_POINTS = 10

export function useMonitorPolling(options = {}) {
  const { onData, interval = 30 } = options

  const currentInterval = ref(interval)
  const isPolling = ref(false)
  const isLoading = ref(false)
  const lastData = ref(null)
  const dataHistory = ref([])  // 历史数据用于插值
  let timer = null
  let abortController = null

  // 验证并修正间隔
  function validateInterval(interval) {
    if (interval < MIN_INTERVAL) {
      console.warn(`Interval too low (${interval}s), forcing to ${MIN_INTERVAL}s`)
      return MIN_INTERVAL
    }
    if (interval > MAX_INTERVAL) {
      console.warn(`Interval too high (${interval}s), data may be stale`)
    }
    return interval
  }

  // 线性插值
  function interpolate(dataPoints, targetLength) {
    if (!dataPoints || dataPoints.length < 2) return dataPoints

    const result = []
    const step = (dataPoints.length - 1) / (targetLength - 1)

    for (let i = 0; i < targetLength; i++) {
      const idx = i * step
      const lower = Math.floor(idx)
      const upper = Math.ceil(idx)
      const fraction = idx - lower

      if (lower === upper || upper >= dataPoints.length) {
        result.push(dataPoints[Math.min(lower, dataPoints.length - 1)])
      } else {
        // 线性插值
        const lowerVal = dataPoints[lower]
        const upperVal = dataPoints[upper]
        result.push(lowerVal + (upperVal - lowerVal) * fraction)
      }
    }

    return result
  }

  // 执行轮询
  async function fetchData() {
    if (abortController) {
      abortController.abort()
    }
    abortController = new AbortController()

    isLoading.value = true

    try {
      const response = await fetch(options.dataSource, {
        signal: abortController.signal
      })

      if (!response.ok) throw new Error('Fetch failed')

      const data = await response.json()

      // 记录历史
      dataHistory.value.push({
        timestamp: Date.now(),
        data
      })

      // 只保留最近 INTERPOLATION_POINTS * 2 个历史点
      if (dataHistory.value.length > INTERPOLATION_POINTS * 2) {
        dataHistory.value.shift()
      }

      lastData.value = data

      // 调用回调
      if (onData) {
        onData(data, dataHistory.value)
      }
    } catch (e) {
      if (e.name !== 'AbortError') {
        console.error('Polling error:', e)
      }
    } finally {
      isLoading.value = false
    }
  }

  // 获取插值后的数据
  function getInterpolatedData(length = INTERPOLATION_POINTS) {
    return interpolate(
      dataHistory.value.map(h => h.data),
      length
    )
  }

  // 开始轮询
  function startPolling(interval = currentInterval.value) {
    stopPolling()

    currentInterval.value = validateInterval(interval)
    isPolling.value = true

    // 立即执行一次
    fetchData()

    // 设置定时器
    timer = setInterval(fetchData, currentInterval.value * 1000)
  }

  // 停止轮询
  function stopPolling() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    if (abortController) {
      abortController.abort()
      abortController = null
    }
    isPolling.value = false
  }

  // 手动刷新
  async function refresh() {
    await fetchData()
  }

  // 清理
  onUnmounted(() => {
    stopPolling()
  })

  return {
    currentInterval,
    isPolling,
    isLoading,
    lastData,
    dataHistory,
    startPolling,
    stopPolling,
    refresh,
    getInterpolatedData,
    validateInterval
  }
}
