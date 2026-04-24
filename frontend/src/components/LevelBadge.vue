<template>
  <span class="level-badge" :style="badgeStyle">
    <span class="level-label">{{ label }}</span>
  </span>
</template>

<script setup>
const LEVELS = {
  0: { label: 'P0', gradient: 'linear-gradient(135deg, #1a7f37, #2ea043)', shadow: '#e8b311' },
  1: { label: 'P1', gradient: 'linear-gradient(135deg, #8250df, #a371f7)', shadow: '#8250df' },
  2: { label: 'P2', gradient: 'linear-gradient(135deg, #0969da, #54aeff)', shadow: '#2e10f1' },
  3: { label: 'P3', gradient: 'linear-gradient(135deg, #9a6700, #d4a72c)', shadow: '#297caa' },
  4: { label: 'P4', gradient: 'linear-gradient(135deg, #6e7781, #8b949e)', shadow: '#6e7781' },
  5: { label: 'P5', gradient: 'linear-gradient(135deg, #e1e4e8, #f6f8fa)', shadow: '#c9d1d9' },
}

const props = defineProps({ level: { type: Number, default: 5 } })
const info = LEVELS[props.level] ?? LEVELS[5]
const label = info.label
const badgeStyle = {
  background: info.gradient,
  boxShadow: `0 2px 6px ${info.shadow}40, inset 0 1px 0 rgba(255,255,255,0.2)`,
}
</script>

<style scoped>
.level-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 10px;
  font-size: 12px;
  font-weight: 700;
  line-height: 20px;
  border-radius: 12px;
  white-space: nowrap;
  border: 1px solid rgba(255, 255, 255, 0.3);
  letter-spacing: 0.5px;
  position: relative;
  overflow: hidden;
}
.level-label {
  position: relative;
  z-index: 1;
}
/* 光泽效果 */
.level-badge::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 50%;
  background: linear-gradient(180deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0) 100%);
  border-radius: 12px 12px 0 0;
  pointer-events: none;
}
</style>
