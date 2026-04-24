/**
 * 监控大屏状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMonitorStore = defineStore('monitor', () => {
  // 当前激活的模板 ID
  const activeTemplateId = ref(null)

  // 模板列表
  const templates = ref([])

  // 组件实例列表（当前模板的组件）
  const components = ref([])

  // 全局右键菜单状态
  const contextMenu = ref({
    visible: false,
    x: 0,
    y: 0,
    pageComponents: []  // 当前页面可捡起的组件
  })

  // 加载模板列表
  async function loadTemplates() {
    try {
      const res = await fetch('/api/monitor/templates')
      if (res.ok) {
        templates.value = await res.json()
      }
    } catch (e) {
      console.warn('Failed to load monitor templates:', e)
    }
  }

  // 创建新模板
  async function createTemplate(name) {
    try {
      const res = await fetch('/api/monitor/templates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      })
      if (res.ok) {
        const template = await res.json()
        templates.value.push(template)
        return template
      }
    } catch (e) {
      console.error('Failed to create template:', e)
    }
    return null
  }

  // 删除模板
  async function deleteTemplate(id) {
    try {
      const res = await fetch(`/api/monitor/templates/${id}`, {
        method: 'DELETE'
      })
      if (res.ok) {
        templates.value = templates.value.filter(t => t.id !== id)
        if (activeTemplateId.value === id) {
          activeTemplateId.value = templates.value[0]?.id ?? null
        }
      }
    } catch (e) {
      console.error('Failed to delete template:', e)
    }
  }

  // 激活模板
  async function activateTemplate(id) {
    try {
      const res = await fetch(`/api/monitor/templates/${id}`)
      if (res.ok) {
        const template = await res.json()
        activeTemplateId.value = id
        components.value = template.components || []
      }
    } catch (e) {
      console.error('Failed to activate template:', e)
    }
  }

  // 添加组件到当前大屏
  async function addComponent(componentInstance) {
    const newComponent = {
      ...componentInstance,
      id: crypto.randomUUID()
    }
    components.value.push(newComponent)

    // 保存到后端
    if (activeTemplateId.value) {
      await saveTemplate()
    }
  }

  // 移除组件
  async function removeComponent(componentId) {
    components.value = components.value.filter(c => c.id !== componentId)
    if (activeTemplateId.value) {
      await saveTemplate()
    }
  }

  // 更新组件位置/大小
  function updateComponentPosition(componentId, layout) {
    const comp = components.value.find(c => c.id === componentId)
    if (comp) {
      comp.position = layout
    }
  }

  // 切换图表类型
  async function changeChartType(componentId, chartType) {
    const comp = components.value.find(c => c.id === componentId)
    if (comp) {
      comp.chartType = chartType
      if (activeTemplateId.value) {
        await saveTemplate()
      }
    }
  }

  // 保存当前模板到后端
  async function saveTemplate() {
    if (!activeTemplateId.value) return

    try {
      await fetch(`/api/monitor/templates/${activeTemplateId.value}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          components: components.value
        })
      })
    } catch (e) {
      console.error('Failed to save template:', e)
    }
  }

  // 显示右键菜单
  function showContextMenu(x, y, pageComponents) {
    contextMenu.value = {
      visible: true,
      x,
      y,
      pageComponents
    }
  }

  // 隐藏右键菜单
  function hideContextMenu() {
    contextMenu.value.visible = false
  }

  // 自动创建默认模板（首次访问时）
  async function ensureDefaultTemplate() {
    if (templates.value.length === 0) {
      const template = await createTemplate('默认监控')
      if (template) {
        await activateTemplate(template.id)
      }
    } else if (!activeTemplateId.value) {
      await activateTemplate(templates.value[0].id)
    }
  }

  return {
    activeTemplateId,
    templates,
    components,
    contextMenu,
    loadTemplates,
    createTemplate,
    deleteTemplate,
    activateTemplate,
    addComponent,
    removeComponent,
    updateComponentPosition,
    changeChartType,
    saveTemplate,
    showContextMenu,
    hideContextMenu,
    ensureDefaultTemplate
  }
})
