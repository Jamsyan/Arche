<template>
  <div class="guest-layout">
    <!-- 博客公开布局 - 对外展示就是个人博客 -->
    <header class="guest-header glass">
      <div class="container header-content">
        <div class="logo">
          <h2>Arche</h2>
          <span class="logo-desc">个人博客</span>
        </div>
        <nav class="nav-menu">
          <RouterLink to="/" class="nav-item"> 首页 </RouterLink>
          <RouterLink to="/blog" class="nav-item"> 文章 </RouterLink>
          <RouterLink to="/about" class="nav-item"> 关于 </RouterLink>
          <RouterLink to="/login" class="nav-item login-btn"> 登录 </RouterLink>
        </nav>
      </div>
    </header>
    <main class="guest-main">
      <div class="container">
        <slot />
        <!-- 页面内容在这里 -->
      </div>
    </main>
    <footer class="guest-footer glass">
      <div class="container">
        <p>© 2025 Arche | 个人博客平台</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
// 公开页面布局，对外展示为个人博客
</script>

<style scoped>
.guest-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: var(--text-primary);
}

.guest-header {
  border-bottom: var(--glass-border);
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.5);
}

.header-content {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.logo h2 {
  margin: 0;
  font-weight: 700;
  font-size: 20px;
  background: var(--bg-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-desc {
  font-size: 13px;
  color: var(--text-tertiary);
  padding-left: var(--spacing-sm);
  border-left: 1px solid var(--border-color);
}

.nav-menu {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.nav-item {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
  font-size: 14px;
}

.nav-item:hover,
.nav-item.router-link-active {
  background: var(--primary-light-color);
  color: var(--primary-color);
}

.login-btn {
  background: var(--primary-color);
  color: white;
  margin-left: var(--spacing-sm);
}

.login-btn:hover {
  background: var(--primary-hover-color);
  color: white;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.guest-main {
  flex: 1;
  padding: var(--spacing-xl) 0;
}

.guest-footer {
  background: rgba(255, 255, 255, 0.4);
  border-top: var(--glass-border);
  padding: var(--spacing-lg) 0;
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: auto;
}

.guest-footer p {
  margin: 0;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .logo-desc {
    display: none;
  }

  .nav-menu {
    gap: var(--spacing-xs);
  }

  .nav-item {
    padding: 6px 12px;
    font-size: 13px;
  }
}
</style>
