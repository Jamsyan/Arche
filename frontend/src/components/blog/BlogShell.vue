<template>
  <div class="blog-shell">
    <header class="blog-header">
      <h1>Veil Blog</h1>
      <nav>
        <router-link to="/">首页</router-link>
        <router-link to="/login" class="login-link">登录</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.blog-shell {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}
.blog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}
.blog-header h1 {
  margin: 0;
  font-size: 1.4rem;
  color: #1a1a2e;
}
.blog-header nav {
  display: flex;
  gap: 1rem;
  align-items: center;
}
.blog-header nav a {
  color: #444;
  text-decoration: none;
  font-size: 0.9rem;
}
.blog-header nav a:hover {
  color: #1a1a2e;
}
.login-link {
  color: #1a1a2e !important;
  font-weight: 500;
}
</style>
