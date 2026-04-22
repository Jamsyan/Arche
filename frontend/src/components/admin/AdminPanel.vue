<template>
  <div class="admin-panel">
    <div class="page-header">
      <div class="header-left">
        <a-button type="text" size="mini" @click="$router.push('/platform')" class="back-btn">
          <template #icon><icon-arrow-left /></template>
        </a-button>
        <icon-lock class="header-icon" />
        <h1 class="page-title">管理员面板</h1>
      </div>
      <a-tag color="red" size="small">P0 权限</a-tag>
    </div>

    <!-- 系统监控 -->
    <div class="section-header">
      <icon-dashboard class="section-icon" />
      <span>系统监控</span>
    </div>

    <div class="monitor-grid">
      <!-- CPU -->
      <div class="monitor-card">
        <div class="monitor-label">CPU 使用率</div>
        <div class="monitor-value">{{ sysInfo.cpu }}%</div>
        <a-progress :percent="sysInfo.cpu" size="small" :stroke-width="6" />
      </div>
      <!-- 内存 -->
      <div class="monitor-card">
        <div class="monitor-label">内存</div>
        <div class="monitor-value">{{ sysInfo.memoryUsed }} / {{ sysInfo.memoryTotal }} GB</div>
        <a-progress :percent="sysInfo.memoryPercent" size="small" :stroke-width="6" />
      </div>
      <!-- 磁盘 -->
      <div class="monitor-card">
        <div class="monitor-label">磁盘</div>
        <div class="monitor-value">{{ sysInfo.diskUsed }} / {{ sysInfo.diskTotal }} GB</div>
        <a-progress :percent="sysInfo.diskPercent" size="small" :stroke-width="6" />
      </div>
      <!-- 带宽 -->
      <div class="monitor-card">
        <div class="monitor-label">带宽</div>
        <div class="monitor-value">{{ sysInfo.bandwidth }}</div>
        <div class="monitor-sub">↑ {{ sysInfo.bandwidthUp }} / ↓ {{ sysInfo.bandwidthDown }}</div>
      </div>
      <!-- 在线用户 -->
      <div class="monitor-card">
        <div class="monitor-label">在线用户</div>
        <div class="monitor-value">{{ sysInfo.onlineUsers }}</div>
        <div class="monitor-sub">今日活跃 {{ sysInfo.todayActive }}</div>
      </div>
      <!-- 请求数 -->
      <div class="monitor-card">
        <div class="monitor-label">请求数</div>
        <div class="monitor-value">{{ sysInfo.requests }}</div>
        <div class="monitor-sub">QPS: {{ sysInfo.qps }}</div>
      </div>
    </div>

    <!-- 服务状态 -->
    <div class="section-header">
      <icon-desktop class="section-icon" />
      <span>服务状态</span>
    </div>

    <a-table
      :data="services"
      :columns="serviceColumns"
      row-key="id"
      :bordered="false"
      :pagination="false"
      class="service-table"
    >
      <template #status="{ record }">
        <a-tag :color="record.running ? 'green' : 'red'">
          {{ record.running ? '运行中' : '已停止' }}
        </a-tag>
      </template>
      <template #actions="{ record }">
        <a-space size="small">
          <a-button
            v-if="!record.running"
            type="text" size="mini"
            @click="toggleService(record, true)"
          >启动</a-button>
          <a-button
            v-else
            type="text" size="mini" status="danger"
            @click="toggleService(record, false)"
          >停止</a-button>
          <a-button type="text" size="mini" @click="restartService(record)">重启</a-button>
        </a-space>
      </template>
    </a-table>

    <!-- 插件管理 -->
    <div class="section-header">
      <icon-apps class="section-icon" />
      <span>插件管理</span>
    </div>

    <a-table
      :data="plugins"
      :columns="pluginColumns"
      row-key="id"
      :bordered="false"
      :pagination="false"
      class="plugin-table"
    >
      <template #name="{ record }">
        <div class="plugin-name-cell">
          <span class="plugin-name">{{ record.name }}</span>
          <a-tag v-if="record.builtin" color="gray" size="mini">内置</a-tag>
        </div>
      </template>
      <template #status="{ record }">
        <a-tag :color="record.active ? 'green' : 'red'">
          {{ record.active ? '已激活' : '未激活' }}
        </a-tag>
      </template>
      <template #actions="{ record }">
        <a-space size="small">
          <a-button
            v-if="!record.active"
            type="text" size="mini"
            @click="togglePlugin(record, true)"
          >启用</a-button>
          <a-button
            v-else
            type="text" size="mini" status="warning"
            @click="togglePlugin(record, false)"
          >停用</a-button>
          <a-button type="text" size="mini" @click="configurePlugin(record)">配置</a-button>
        </a-space>
      </template>
    </a-table>

    <!-- 快捷操作 -->
    <div class="section-header">
      <icon-bulb class="section-icon" />
      <span>快捷操作</span>
    </div>

    <div class="quick-actions">
      <a-button type="outline" @click="$router.push('/admin/users')">
        <template #icon><icon-user /></template>
        用户管理
      </a-button>
      <a-button type="outline" @click="showSystemSettings = true">
        <template #icon><icon-settings /></template>
        系统设置
      </a-button>
      <a-button type="outline" status="warning" @click="clearCache">
        <template #icon><icon-delete /></template>
        清理缓存
      </a-button>
      <a-button type="outline" status="danger" @click="emergencyMode">
        <template #icon><icon-lock /></template>
        紧急模式
      </a-button>
    </div>

    <!-- 系统设置弹窗 -->
    <a-modal v-model:visible="showSystemSettings" title="系统设置" width="560">
      <a-form layout="vertical">
        <a-form-item label="站点名称">
          <a-input v-model="settings.siteName" />
        </a-form-item>
        <a-form-item label="维护模式">
          <a-switch v-model="settings.maintenance" />
        </a-form-item>
        <a-form-item label="新用户默认等级">
          <a-select v-model="settings.defaultLevel">
            <a-option :value="5">P5 - 访客</a-option>
            <a-option :value="4">P4 - 注册用户</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="最大上传文件 (MB)">
          <a-input-number v-model="settings.maxUpload" :min="1" />
        </a-form-item>
      </a-form>
      <template #footer>
        <a-button @click="showSystemSettings = false">取消</a-button>
        <a-button type="primary" @click="saveSettings">保存</a-button>
      </template>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import {
  IconLock, IconArrowLeft, IconDashboard, IconDesktop,
  IconApps, IconBulb, IconUser, IconSettings, IconDelete,
} from '@arco-design/web-vue/es/icon'

const showSystemSettings = ref(false)

const sysInfo = reactive({
  cpu: 23,
  memoryUsed: 4.2,
  memoryTotal: 16,
  memoryPercent: 26,
  diskUsed: 120,
  diskTotal: 500,
  diskPercent: 24,
  bandwidth: '12.5 MB/s',
  bandwidthUp: '3.2 MB/s',
  bandwidthDown: '9.3 MB/s',
  onlineUsers: 7,
  todayActive: 42,
  requests: 18453,
  qps: 12.3,
})

const services = ref([
  { id: 1, name: 'Web 服务', pid: 1234, port: 8000, running: true, uptime: '3d 14h' },
  { id: 2, name: '任务队列', pid: 1235, port: 6379, running: true, uptime: '3d 14h' },
  { id: 3, name: '爬虫引擎', pid: 1236, port: 9001, running: true, uptime: '1d 6h' },
  { id: 4, name: '训练调度器', pid: 1237, port: 9002, running: false, uptime: '—' },
  { id: 5, name: '静态文件服务', pid: 1238, port: 8080, running: true, uptime: '3d 14h' },
])

const plugins = ref([
  { id: 1, name: 'auth', version: '1.0.0', active: true, builtin: true, description: '用户认证' },
  { id: 2, name: 'blog', version: '1.0.0', active: true, builtin: true, description: '博客系统' },
  { id: 3, name: 'oss', version: '0.1.0', active: false, builtin: false, description: '对象存储' },
  { id: 4, name: 'crawler', version: '0.5.0', active: true, builtin: false, description: '爬虫引擎' },
  { id: 5, name: 'training', version: '0.2.0', active: false, builtin: false, description: '云训练' },
  { id: 6, name: 'moderation', version: '0.1.0', active: true, builtin: false, description: '内容审核' },
])

const settings = reactive({
  siteName: 'Veil',
  maintenance: false,
  defaultLevel: 4,
  maxUpload: 100,
})

const serviceColumns = [
  { title: '服务名称', dataIndex: 'name', width: 160 },
  { title: 'PID', dataIndex: 'pid', width: 80 },
  { title: '端口', dataIndex: 'port', width: 80 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '运行时间', dataIndex: 'uptime', width: 120 },
  { title: '操作', slotName: 'actions', width: 140 },
]

const pluginColumns = [
  { title: '插件', slotName: 'name', width: 160 },
  { title: '版本', dataIndex: 'version', width: 90 },
  { title: '描述', dataIndex: 'description', ellipsis: true, tooltip: true },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'actions', width: 140 },
]

function toggleService(service, start) {
  service.running = start
  Message.success(`${start ? '已启动' : '已停止'}: ${service.name}`)
}

function restartService(service) {
  Message.info(`重启服务: ${service.name}`)
}

function togglePlugin(plugin, activate) {
  plugin.active = activate
  Message.success(`${activate ? '已启用' : '已停用'}插件: ${plugin.name}`)
}

function configurePlugin(plugin) {
  Message.info(`配置插件: ${plugin.name}`)
}

function clearCache() {
  Modal.confirm({
    title: '确认清理缓存',
    content: '清理后将导致缓存文件全部失效，确认继续？',
    onOk: () => Message.success('缓存已清理'),
  })
}

function emergencyMode() {
  Modal.confirm({
    title: '紧急模式',
    content: '紧急模式将限制非管理员访问，仅保留核心功能。确认启用？',
    buttonProps: { status: 'danger' },
    onOk: () => Message.warning('紧急模式已启用'),
  })
}

function saveSettings() {
  Message.success('设置已保存')
  showSystemSettings.value = false
}
</script>

<style scoped>
.admin-panel { max-width: 1100px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.back-btn { padding: 2px; color: var(--color-text-3); }
.back-btn:hover { color: var(--color-text-1); }
.header-left { display: flex; align-items: center; gap: 10px; }
.header-icon { width: 24px; height: 24px; color: #cf222e; }
.page-title { margin: 0; font-size: 20px; font-weight: 600; color: var(--color-text-1); }

.section-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600; color: var(--color-text-2);
  margin-bottom: 12px; margin-top: 28px;
}
.section-header:first-child { margin-top: 0; }
.section-icon { width: 16px; height: 16px; color: var(--color-text-4); }

.monitor-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.monitor-card {
  background: rgba(255,255,255,0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: var(--border-radius-large);
  padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.monitor-label { font-size: 12px; color: var(--color-text-4); margin-bottom: 4px; }
.monitor-value { font-size: 22px; font-weight: 700; color: var(--color-text-1); margin-bottom: 8px; }
.monitor-sub { font-size: 12px; color: var(--color-text-4); margin-top: 4px; }

.service-table, .plugin-table { border-radius: var(--border-radius-large); overflow: hidden; }
.service-table :deep(.arco-table), .plugin-table :deep(.arco-table) { border-radius: var(--border-radius-large); }
.plugin-name-cell { display: flex; align-items: center; gap: 8px; }
.plugin-name { font-weight: 500; }

.quick-actions { display: flex; flex-wrap: wrap; gap: 12px; }
.quick-actions .arco-btn { min-width: 140px; justify-content: center; }
</style>
