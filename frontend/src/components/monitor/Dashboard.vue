<template>
  <div class="monitor-dashboard">
    <!-- 顶部工具栏 -->
    <div class="dashboard-toolbar">
      <div class="toolbar-left">
        <a-dropdown @select="handleTemplateSelect">
          <a-button type="text">
            {{ activeTemplateName }}
            <icon-down />
          </a-button>
          <template #content>
            <a-doption v-for="t in templates" :key="t.id" :value="t.id">
              {{ t.name }}
            </a-doption>
            <a-divider />
            <a-doption value="new" @click="showNewTemplateModal = true">
              <icon-plus /> 新建模板
            </a-doption>
          </template>
        </a-dropdown>
      </div>

      <div class="toolbar-right">
        <a-button type="text" @click="showAddComponentModal = true">
          <icon-plus /> 添加组件
        </a-button>
        <a-button type="text" @click="saveLayout">
          <icon-save /> 保存
        </a-button>
      </div>
    </div>

    <!-- 拖拽布局 -->
    <div class="dashboard-grid">
      <grid-layout
        v-model:layout="layout"
        :col-num="12"
        :row-height="80"
        :is-draggable="true"
        :is-resizable="true"
        :vertical-compact="true"
        :use-css-transforms="true"
        @layout-updated="onLayoutUpdated"
      >
        <grid-item
          v-for="item in layout"
          :key="item.i"
          :x="item.x"
          :y="item.y"
          :w="item.w"
          :h="item.h"
          :i="item.i"
          :min-w="2"
          :min-h="2"
        >
          <component-card
            :component-id="item.componentId"
            :title="item.title"
            :chart-type="item.chartType"
            @remove="removeComponent(item.i)"
            @change-chart="handleChartChange(item.i, $event)"
          />
        </grid-item>
      </grid-layout>
    </div>

    <!-- 新建模板弹窗 -->
    <a-modal v-model:visible="showNewTemplateModal" title="新建监控模板" @ok="createTemplate" @cancel="showNewTemplateModal = false">
      <a-input v-model="newTemplateName" placeholder="模板名称" />
    </a-modal>

    <!-- 添加组件弹窗 -->
    <a-modal v-model:visible="showAddComponentModal" title="添加组件" width="600" :footer="false">
      <div class="component-picker">
        <div
          v-for="comp in availableComponents"
          :key="comp.id"
          class="component-item"
          @click="addComponent(comp)"
        >
          <component :is="getIcon(comp.icon)" class="component-icon" />
          <div class="component-info">
            <div class="component-name">{{ comp.name }}</div>
            <div class="component-desc">{{ comp.description || comp.dataType }}</div>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { GridLayout, GridItem } from 'vue-grid-layout'
import { Message } from '@arco-design/web-vue'
import {
  IconDown,
  IconPlus,
  IconSave,
  IconHome,
  IconEdit,
  IconFolder,
  IconTool,
  IconApps,
  IconRefresh
} from '@arco-design/web-vue/es/icon'
import ComponentCard from './ComponentCard.vue'
import { useMonitorStore } from '../../stores/monitor.js'
import { usePluginRegistry } from '../../stores/pluginRegistry.js'

const monitorStore = useMonitorStore()
const pluginRegistry = usePluginRegistry()

// 模板
const templates = computed(() => monitorStore.templates)
const activeTemplateName = computed(() => {
  const t = templates.value.find(t => t.id === monitorStore.activeTemplateId)
  return t?.name || '选择模板'
})

// 布局数据
const layout = ref([])

// UI 状态
const showNewTemplateModal = ref(false)
const showAddComponentModal = ref(false)
const newTemplateName = ref('')

// 可用组件
const availableComponents = computed(() => pluginRegistry.atomicComponents)

// 处理模板选择
async function handleTemplateSelect(id) {
  if (id === 'new') {
    showNewTemplateModal.value = true
  } else {
    await monitorStore.activateTemplate(id)
    syncLayout()
  }
}

// 创建模板
async function createTemplate() {
  if (!newTemplateName.value.trim()) {
    Message.warning('请输入模板名称')
    return
  }

  const template = await monitorStore.createTemplate(newTemplateName.value)
  if (template) {
    await monitorStore.activateTemplate(template.id)
    layout.value = []
    Message.success('模板已创建')
  }

  showNewTemplateModal.value = false
  newTemplateName.value = ''
}

// 添加组件
function addComponent(comp) {
  const newItem = {
    i: crypto.randomUUID(),
    x: 0,
    y: Infinity,  // 放在最下面
    w: 4,
    h: 3,
    componentId: comp.id,
    title: comp.name,
    chartType: comp.defaultChart || 'number'
  }

  layout.value.push(newItem)
  monitorStore.addComponent({
    componentId: comp.id,
    title: comp.name,
    chartType: comp.defaultChart || 'number',
    position: { x: newItem.x, y: newItem.y, w: newItem.w, h: newItem.h }
  })

  showAddComponentModal.value = false
  Message.success('组件已添加')
}

// 移除组件
function removeComponent(id) {
  layout.value = layout.value.filter(item => item.i !== id)
  const comp = layout.value.find(item => item.i === id)
  if (comp) {
    monitorStore.removeComponent(comp.id)
  }
}

// 处理图表类型变更
function handleChartChange(id, chartType) {
  const item = layout.value.find(i => i.i === id)
  if (item) {
    item.chartType = chartType
    const storeComp = monitorStore.components.find(c => c.id === item.id)
    if (storeComp) {
      monitorStore.changeChartType(storeComp.id, chartType)
    }
  }
}

// 布局更新
function onLayoutUpdated(newLayout) {
  layout.value = newLayout
}

// 保存布局
async function saveLayout() {
  await monitorStore.saveTemplate()
  Message.success('布局已保存')
}

// 同步布局
function syncLayout() {
  layout.value = monitorStore.components.map((comp, idx) => ({
    i: comp.id || `comp-${idx}`,
    x: comp.position?.x || 0,
    y: comp.position?.y || idx * 3,
    w: comp.position?.w || 4,
    h: comp.position?.h || 3,
    componentId: comp.componentId,
    title: comp.title,
    chartType: comp.chartType
  }))
}

// 图标映射
const iconMap = {
  home: IconHome,
  edit: IconEdit,
  folder: IconFolder,
  tool: IconTool,
  apps: IconApps,
  refresh: IconRefresh
}

function getIcon(name) {
  return iconMap[name] || IconApps
}

onMounted(() => {
  syncLayout()
})
</script>

<style scoped>
.monitor-dashboard {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.dashboard-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 16px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 8px;
}

.dashboard-grid {
  flex: 1;
  overflow: auto;
}

/* vue-grid-layout 样式 */
:deep(.vue-grid-layout) {
  background: transparent;
}

:deep(.vue-grid-item) {
  transition: transform 0.2s ease;
}

:deep(.vue-grid-item.vue-grid-placeholder) {
  background: var(--color-primary-light-2);
  border-radius: 8px;
  opacity: 0.5;
}

:deep(.vue-resizable-handle) {
  width: 20px;
  height: 20px;
  bottom: 0;
  right: 0;
  cursor: se-resize;
  background: transparent;
}

/* 组件选择器 */
.component-picker {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.component-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.component-item:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-light-1);
}

.component-icon {
  width: 32px;
  height: 32px;
  color: var(--color-primary);
}

.component-info {
  flex: 1;
}

.component-name {
  font-weight: 500;
  color: var(--color-text-1);
}

.component-desc {
  font-size: 12px;
  color: var(--color-text-3);
}
</style>
