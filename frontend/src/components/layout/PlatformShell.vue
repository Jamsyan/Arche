<template>
  <div class="platform-shell">
    <TopStatusBar />

    <div class="platform-body">
      <Sidebar />

      <main class="platform-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import TopStatusBar from './TopStatusBar.vue'
import Sidebar from './Sidebar.vue'
import { onMounted } from 'vue'
import { useMonitorStore } from '../../stores/monitor.js'
import { usePluginRegistry } from '../../stores/pluginRegistry.js'

const monitorStore = useMonitorStore()
const pluginRegistry = usePluginRegistry()

onMounted(async () => {
  // 加载监控模板
  await monitorStore.loadTemplates()
  await monitorStore.ensureDefaultTemplate()
})
</script>

<style scoped>
.platform-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-fill-1);
}

.platform-body {
  flex: 1;
  display: flex;
}

.platform-main {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
