<template>
  <BaseLayout layout-mode="guest" :sidebar-items="[]" :show-footer="true">
    <slot />
  </BaseLayout>
</template>

<script setup lang="ts">
import BaseLayout from './BaseLayout.vue'
</script>
