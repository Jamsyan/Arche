<template>
  <div class="widget">
    <div class="widget-label">网络 I/O</div>
    <div class="widget-row">
      <span class="label">发送</span>
      <span class="value">{{ formatBytes(netSent) }}</span>
    </div>
    <div class="widget-row">
      <span class="label">接收</span>
      <span class="value">{{ formatBytes(netRecv) }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { system } from '../../../api'

const netSent = ref(0)
const netRecv = ref(0)
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0, v = bytes
  while (v >= 1024 && i < units.length - 1) { v /= 1024; i++ }
  return `${v.toFixed(1)} ${units[i]}`
}

async function load() {
  try {
    const data = await system.summary()
    if (data) {
      netSent.value = data.net_sent || 0
      netRecv.value = data.net_recv || 0
    }
  } catch {}
}

onMounted(() => { load(); timer = setInterval(load, 10000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.widget { display: flex; flex-direction: column; gap: 6px; }
.widget-label { font-size: 11px; color: var(--color-text-4); text-transform: uppercase; }
.widget-row { display: flex; justify-content: space-between; font-size: 13px; }
.label { color: var(--color-text-4); }
.value { font-weight: 600; color: var(--color-text-2); }
</style>
