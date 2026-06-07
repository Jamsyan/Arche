<script setup lang="ts">
import { computed, useSlots } from 'vue'

type DividerType = 'solid' | 'dashed' | 'ink'

const props = withDefaults(
  defineProps<{
    type?: DividerType
    withText?: boolean
  }>(),
  {
    type: 'solid',
    withText: false
  }
)

const slots = useSlots()

const classes = computed(() => [
  'ar-divider',
  `ar-divider--${props.type}`,
  {
    'ar-divider--with-text': props.withText && !!slots.default
  }
])
</script>

<template>
  <div :class="classes" role="separator" :aria-orientation="withText ? undefined : 'horizontal'">
    <span v-if="withText && $slots.default" class="ar-divider__text">
      <slot />
    </span>
  </div>
</template>

<style scoped>
.ar-divider {
  display: flex;
  align-items: center;
  width: 100%;
  margin: var(--spacing-lg) 0;
}

/* ── solid ── */
.ar-divider--solid {
  border-top: 1px solid var(--divider-color);
}

/* ── dashed ── */
.ar-divider--dashed {
  border-top: 1px dashed var(--divider-color);
}

/* ── ink ── */
.ar-divider--ink {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--text-tertiary), transparent);
}

/* ── with text ── */
.ar-divider--with-text {
  border-top: none;
  gap: var(--spacing-md);
}

.ar-divider--with-text::before,
.ar-divider--with-text::after {
  content: '';
  flex: 1;
  height: 1px;
}

.ar-divider--solid.ar-divider--with-text::before,
.ar-divider--solid.ar-divider--with-text::after {
  border-top: 1px solid var(--divider-color);
}

.ar-divider--dashed.ar-divider--with-text::before,
.ar-divider--dashed.ar-divider--with-text::after {
  border-top: 1px dashed var(--divider-color);
}

.ar-divider--ink.ar-divider--with-text::before,
.ar-divider--ink.ar-divider--with-text::after {
  background: linear-gradient(90deg, transparent, var(--text-tertiary), transparent);
}

.ar-divider--ink.ar-divider--with-text::before {
  background: linear-gradient(90deg, transparent, var(--text-tertiary));
}

.ar-divider--ink.ar-divider--with-text::after {
  background: linear-gradient(90deg, var(--text-tertiary), transparent);
}

.ar-divider__text {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  padding: 0 var(--spacing-sm);
  font-family: var(--font-sans);
}
</style>
