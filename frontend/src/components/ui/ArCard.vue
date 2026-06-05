<script setup lang="ts">
import { computed } from 'vue'

type CardPadding = 'none' | 'sm' | 'md' | 'lg'
type CardVariant = 'solid' | 'glass'

const props = withDefaults(
  defineProps<{
    padding?: CardPadding
    hoverable?: boolean
    bordered?: boolean
    variant?: CardVariant
  }>(),
  {
    padding: 'md',
    hoverable: false,
    bordered: true,
    variant: 'solid'
  }
)

const classes = computed(() => [
  'ar-card',
  `ar-card--${props.variant}`,
  `ar-card--padding-${props.padding}`,
  {
    'ar-card--hoverable': props.hoverable,
    'ar-card--bordered': props.bordered,
    'ar-card--unbordered': !props.bordered
  }
])
</script>

<template>
  <div :class="classes">
    <div v-if="$slots.header" class="ar-card__header">
      <slot name="header" />
    </div>
    <div v-if="$slots.default" class="ar-card__body">
      <slot />
    </div>
    <div v-if="$slots.footer" class="ar-card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<style scoped>
.ar-card {
  border-radius: var(--radius-lg);
  transition:
    box-shadow var(--transition-normal),
    transform var(--transition-normal),
    border-color var(--transition-normal);
  font-family: var(--font-sans);
}

/* ── variant: solid ── */
.ar-card--solid {
  background: var(--surface-color);
  box-shadow: var(--shadow-sm);
}

.ar-card--solid.ar-card--bordered {
  border: 1px solid var(--border-color);
}

/* ── variant: glass ── */
.ar-card--glass {
  border: 1px solid rgba(26, 24, 23, 0.08);
}

.ar-card--glass.ar-card--bordered {
  border: 1px solid rgba(26, 24, 23, 0.08);
}

.ar-card--glass.ar-card--unbordered {
  border: none;
}

/* 使用 .glass-surface 类时，确保 border-radius 一致 */
.ar-card--glass {
  background: rgba(245, 240, 232, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

/* ── hoverable ── */
.ar-card--hoverable {
  cursor: pointer;
}

.ar-card--hoverable:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* ── padding ── */
.ar-card--padding-none > .ar-card__body,
.ar-card--padding-none > .ar-card__header,
.ar-card--padding-none > .ar-card__footer {
  padding: 0;
}

.ar-card--padding-sm > .ar-card__body,
.ar-card--padding-sm > .ar-card__header,
.ar-card--padding-sm > .ar-card__footer {
  padding: var(--spacing-md);
}

.ar-card--padding-md > .ar-card__body,
.ar-card--padding-md > .ar-card__header,
.ar-card--padding-md > .ar-card__footer {
  padding: var(--spacing-lg);
}

.ar-card--padding-lg > .ar-card__body,
.ar-card--padding-lg > .ar-card__header,
.ar-card--padding-lg > .ar-card__footer {
  padding: var(--spacing-xl);
}

/* ── header / footer divider ── */
.ar-card__header {
  border-bottom: 1px solid var(--border-color);
}

.ar-card__footer {
  border-top: 1px solid var(--border-color);
}
</style>
