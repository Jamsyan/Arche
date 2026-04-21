<template>
  <div class="platform-shell">
    <header class="platform-header">
      <h1>Veil</h1>
      <nav class="platform-nav">
        <component :is="navItem" v-for="(navItem, i) in navItems" :key="i" />
      </nav>
      <span class="role-badge">{{ role }}</span>
    </header>
    <main class="platform-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { defineAsyncComponent } from 'vue'
import { loadComponent } from '../../router/component-registry.js'

const props = defineProps({ role: { type: String, required: true } })

// Dynamically create nav items based on role
const navItems = []
const adminLoader = loadComponent(props.role, 'AdminPanel')
if (adminLoader) {
  navItems.push(defineAsyncComponent(adminLoader))
}
</script>

<style scoped>
.platform-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.platform-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 2rem;
  background: #1a1a2e;
  color: #eee;
}
.platform-main {
  flex: 1;
  padding: 2rem;
}
.role-badge {
  margin-left: auto;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  background: #16213e;
  font-size: 0.85rem;
}
</style>
