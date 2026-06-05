<template>
  <BaseLayout layout-mode="guest" :sidebar-items="[]" :show-footer="true">
    <template v-if="isConsoleRoute">
      <ConsoleShell><slot /></ConsoleShell>
    </template>
    <template v-else>
      <slot />
    </template>
  </BaseLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BaseLayout from './BaseLayout.vue'
import ConsoleShell from '@/components/ConsoleShell.vue'

const route = useRoute()
const isConsoleRoute = computed(() => route.meta?.console === true)
</script>
