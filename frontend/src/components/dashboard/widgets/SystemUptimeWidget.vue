<template>
  <div class="widget">
    <div class="widget-label">运行时长</div>
    <div class="widget-value">{{ uptime }}</div>
    <div class="widget-sub">{{ platform }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { system } from '../../../api'

const uptime = ref('—')
const platform = ref('')
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

async function load() {
  try {
    const data = await system.summary()
    if (data) {
      uptime.value = data.uptime || '—'
      platform.value = data.platform || ''
    }
  } catch {}
}

onMounted(() => { load(); timer = setInterval(load, 30000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.widget { display: flex; flex-direction: column; gap: 4px; }
.widget-label { font-size: 11px; color: var(--color-text-4); text-transform: uppercase; }
.widget-value { font-size: 20px; font-weight: 700; color: var(--color-text-1); }
.widget-sub { font-size: 11px; color: var(--color-text-4); }
</style>
