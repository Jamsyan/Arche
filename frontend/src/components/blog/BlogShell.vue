<template>
  <div class="blog-shell">
    <a-layout-header class="blog-header">
      <a-typography-title :heading="4" style="margin: 0">Veil</a-typography-title>
      <a-space>
        <router-link to="/">首页</router-link>
        <a-button type="primary" size="small" @click="$router.push('/login')">登录</a-button>
      </a-space>
    </a-layout-header>
    <main class="blog-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.blog-shell { min-height: 100vh; }
.blog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}
.blog-header a {
  color: var(--color-text-2);
  text-decoration: none;
  font-size: 14px;
}
.blog-header a:hover { color: rgb(var(--primary-6)); }
.blog-main {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}
</style>
