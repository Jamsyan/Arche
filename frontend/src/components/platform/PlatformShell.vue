<template>
  <div class="platform-shell">
    <header class="platform-header">
      <h1 class="logo">Veil</h1>
      <nav class="platform-nav">
        <router-link to="/platform">仪表盘</router-link>
        <router-link v-if="userLevel <= 3" to="/editor">编辑器</router-link>
        <router-link v-if="userLevel <= 2" to="/upload">上传</router-link>
        <router-link v-if="userLevel <= 1" to="/github">GitHub</router-link>
        <router-link v-if="userLevel <= 1" to="/storage">存储</router-link>
        <router-link v-if="userLevel <= 1" to="/moderation">审核</router-link>
        <router-link v-if="userLevel <= 0" to="/admin">管理</router-link>
        <router-link v-if="userLevel <= 0" to="/ops/crawler">爬虫</router-link>
        <router-link v-if="userLevel <= 0" to="/ops/cloud">云训练</router-link>
      </nav>
      <span class="level-badge">P{{ userLevel }}</span>
      <button class="logout-btn" @click="$emit('logout')">退出</button>
    </header>
    <main class="platform-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
const props = defineProps({
  userLevel: { type: Number, default: 5 },
})
defineEmits(['logout'])
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
  gap: 1.5rem;
  padding: 0.8rem 2rem;
  background: #1a1a2e;
  color: #eee;
}
.logo {
  margin: 0;
  font-size: 1.3rem;
  color: #fff;
}
.platform-nav {
  display: flex;
  gap: 1rem;
  flex: 1;
}
.platform-nav a {
  color: #ccc;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}
.platform-nav a:hover,
.platform-nav a.router-link-active {
  color: #fff;
}
.level-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  background: #16213e;
  font-size: 0.8rem;
  color: #aaa;
}
.logout-btn {
  padding: 0.3rem 0.8rem;
  border: 1px solid #444;
  border-radius: 4px;
  background: transparent;
  color: #ccc;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}
.logout-btn:hover {
  border-color: #d32f2f;
  color: #d32f2f;
}
.platform-main {
  flex: 1;
  padding: 2rem;
}
</style>
