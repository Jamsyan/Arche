/**
 * 图表类型转换 composable
 * 根据数据类型推荐可用图表
 */

// 支持的图表类型
export const ChartTypes = {
  NUMBER: 'number',      // 数字卡片
  LINE: 'line',         // 折线图
  BAR: 'bar',           // 柱状图
  AREA: 'area',         // 面积图
  TABLE: 'table'        // 表格
}

// 数据类型到图表类型的映射
const DATA_TYPE_CHART_MAP = {
  numeric: [ChartTypes.NUMBER, ChartTypes.LINE, ChartTypes.BAR, ChartTypes.AREA],
  time_series: [ChartTypes.LINE, ChartTypes.BAR, ChartTypes.AREA, ChartTypes.NUMBER],
  list: [ChartTypes.TABLE, ChartTypes.NUMBER],
  status: [ChartTypes.NUMBER, ChartTypes.TABLE],
  percentage: [ChartTypes.NUMBER, ChartTypes.LINE, ChartTypes.BAR, ChartTypes.AREA]
}

// 图表类型中文名
const ChartTypeNames = {
  [ChartTypes.NUMBER]: '数字卡片',
  [ChartTypes.LINE]: '折线图',
  [ChartTypes.BAR]: '柱状图',
  [ChartTypes.AREA]: '面积图',
  [ChartTypes.TABLE]: '表格'
}

export function useChartInterop() {
  // 根据组件元信息获取支持的图表类型
  function getCompatibleCharts(componentMeta) {
    const dataType = componentMeta.dataType || 'numeric'
    return DATA_TYPE_CHART_MAP[dataType] || [ChartTypes.NUMBER]
  }

  // 获取图表类型名称
  function getChartTypeName(chartType) {
    return ChartTypeNames[chartType] || chartType
  }

  // 获取默认图表类型
  function getDefaultChartType(componentMeta) {
    const compatible = getCompatibleCharts(componentMeta)
    return componentMeta.defaultChart || compatible[0]
  }

  // 检测数据适合的图表类型
  function detectChartType(data) {
    if (!data) return ChartTypes.NUMBER

    // 单个数字
    if (typeof data === 'number') {
      return ChartTypes.NUMBER
    }

    // 数组
    if (Array.isArray(data)) {
      if (data.length === 0) return ChartTypes.NUMBER

      const first = data[0]

      // 时间序列数组
      if (typeof first === 'object' && first.timestamp) {
        return ChartTypes.LINE
      }

      // 普通数值数组
      if (typeof first === 'number') {
        return data.length > 1 ? ChartTypes.LINE : ChartTypes.NUMBER
      }

      // 对象数组
      if (typeof first === 'object') {
        const keys = Object.keys(first)
        // 有数值字段 → 折线图
        if (keys.some(k => typeof first[k] === 'number')) {
          return ChartTypes.LINE
        }
        // 只有文本 → 表格
        return ChartTypes.TABLE
      }
    }

    // 对象
    if (typeof data === 'object') {
      const values = Object.values(data)
      if (values.every(v => typeof v === 'number')) {
        return ChartTypes.BAR
      }
    }

    return ChartTypes.NUMBER
  }

  // 渲染图表（根据类型）
  function renderChart(chartType, data, options = {}) {
    switch (chartType) {
      case ChartTypes.NUMBER:
        return renderNumber(data, options)
      case ChartTypes.LINE:
        return renderLine(data, options)
      case ChartTypes.BAR:
        return renderBar(data, options)
      case ChartTypes.AREA:
        return renderArea(data, options)
      case ChartTypes.TABLE:
        return renderTable(data, options)
      default:
        return renderNumber(data, options)
    }
  }

  // 渲染数字
  function renderNumber(data, options = {}) {
    const { prefix = '', suffix = '', decimals = 0 } = options

    let value = data
    if (typeof data === 'object') {
      value = data.value ?? data.count ?? data.total ?? 0
    }

    const formatted = Number(value).toFixed(decimals)
    return {
      display: `${prefix}${formatted}${suffix}`,
      value: Number(value)
    }
  }

  // 渲染折线图数据
  function renderLine(data, options = {}) {
    if (!Array.isArray(data)) return { labels: [], values: [] }

    const labels = []
    const values = []

    data.forEach(item => {
      if (typeof item === 'number') {
        values.push(item)
        labels.push('')
      } else if (typeof item === 'object') {
        values.push(item.value ?? item.y ?? 0)
        labels.push(item.label ?? item.x ?? item.timestamp ?? '')
      }
    })

    return { labels, values }
  }

  // 渲染柱状图数据
  function renderBar(data, options = {}) {
    if (typeof data === 'object' && !Array.isArray(data)) {
      return {
        labels: Object.keys(data),
        values: Object.values(data).map(v => Number(v))
      }
    }
    return renderLine(data, options)
  }

  // 渲染面积图数据（同折线）
  function renderArea(data, options = {}) {
    return renderLine(data, options)
  }

  // 渲染表格数据
  function renderTable(data, options = {}) {
    const { columns = null } = options

    if (!Array.isArray(data)) {
      return { columns: [], rows: [] }
    }

    if (data.length === 0) {
      return { columns: [], rows: [] }
    }

    const first = data[0]
    const cols = columns || Object.keys(first).filter(k => !k.startsWith('_'))

    return {
      columns: cols,
      rows: data.map(item => cols.map(col => item[col]))
    }
  }

  return {
    ChartTypes,
    getCompatibleCharts,
    getChartTypeName,
    getDefaultChartType,
    detectChartType,
    renderChart,
    renderNumber,
    renderLine,
    renderBar,
    renderArea,
    renderTable
  }
}
