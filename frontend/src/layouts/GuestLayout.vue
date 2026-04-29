<template>
  <div class="guest-layout">
    <header class="guest-header glass">
      <div class="header-content">
        <SiteLogo size="md" />
        <div class="center-zone">
          <nav class="nav-menu">
            <RouterLink to="/" class="nav-item">首页</RouterLink>
            <RouterLink to="/explore" class="nav-item">探索</RouterLink>
            <RouterLink to="/about" class="nav-item">关于</RouterLink>
          </nav>
          <div class="search-wrap">
            <NIcon class="search-leading-icon" size="17" aria-hidden="true">
              <SearchOutline />
            </NIcon>
            <input
              v-model.trim="searchKeyword"
              class="search-input"
              type="search"
              placeholder="搜索"
              @keydown.enter="goSearch"
            >
          </div>
        </div>
        <div class="action-area">
          <RouterLink v-if="isLoggedIn" to="/creator" class="nav-item">创作</RouterLink>
          <RouterLink v-if="isLoggedIn" to="/profile" class="avatar-link">{{
            userInitial
          }}</RouterLink>
          <template v-else>
            <RouterLink to="/register" class="nav-item">加入我们</RouterLink>
            <RouterLink to="/login" class="nav-item login-btn">登录</RouterLink>
          </template>
        </div>
      </div>
    </header>
    <main class="guest-main">
      <div class="container">
        <slot />
      </div>
    </main>
    <footer class="guest-footer glass">
      <div class="container footer-content">
        <section class="footer-brand">
          <SiteLogo size="sm" />
          <p class="brand-note">记录风华正茂的时光日志，连接真实表达与开放共创。</p>
        </section>
        <section>
          <h4>站点导航</h4>
          <div class="footer-links">
            <RouterLink to="/">首页</RouterLink>
            <RouterLink to="/explore">探索</RouterLink>
            <RouterLink to="/about">关于</RouterLink>
          </div>
        </section>
        <section>
          <h4>联系与条款</h4>
          <div class="footer-links">
            <a href="mailto:hello@jinnianzhi.local">联系我</a>
            <RouterLink to="/about">社媒与介绍</RouterLink>
            <a href="#" @click.prevent>隐私与条款</a>
          </div>
        </section>
      </div>
      <div class="container footer-bottom">
        <p>© {{ currentYear }} 锦年志 · 时光日志</p>
        <p class="record-line">
          <a
            class="record-link"
            href="https://beian.miit.gov.cn/"
            target="_blank"
            rel="noopener noreferrer"
          >
            <NIcon size="14" aria-hidden="true"><DocumentTextOutline /></NIcon>
            苏ICP备2026004054号-1
          </a>
        </p>
        <p class="record-line">
          <a
            class="record-link police-link"
            href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=32068202000798"
            target="_blank"
            rel="noopener noreferrer"
          >
            <img
              class="police-logo-img"
              src="https://www.beian.gov.cn/img/new/gongan.png"
              alt=""
              aria-hidden="true"
            >
            苏公网安备32068202000798号
          </a>
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NIcon } from 'naive-ui'
import { DocumentTextOutline, SearchOutline } from '@vicons/ionicons5'
import SiteLogo from '@/components/SiteLogo.vue'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const userStore = useUserStore()
const searchKeyword = ref('')

const currentYear = new Date().getFullYear()
const isLoggedIn = computed(() => Boolean(userStore.token))
const userInitial = computed(
  () => (userStore.userInfo?.nickname || userStore.userInfo?.username || '我')[0]
)

const goSearch = () => {
  router.push({
    path: '/explore',
    query: {
      q: searchKeyword.value || undefined
    }
  })
}
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
  background: rgba(255, 250, 241, 0.82);
  overflow-x: auto;
}

.header-content {
  width: 100%;
  height: 53px;
  padding: 0 var(--spacing-md);
  min-width: 1080px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
  white-space: nowrap;
}

.nav-menu {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
  margin-left: clamp(24px, 4vw, 72px);
}

.center-zone {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-width: 0;
  margin-left: 12px;
}

.action-area {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.search-input {
  width: 250px;
  height: 40px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-color);
  background: rgba(255, 250, 241, 0.92);
  padding: 0 14px 0 38px;
  color: var(--text-primary);
  outline: none;
  font-size: 13px;
  transition:
    border-color 0.3s ease,
    box-shadow 0.3s ease,
    background 0.3s ease,
    transform 0.3s ease;
}

.search-input:focus {
  border-color: var(--primary-color);
  box-shadow:
    0 0 0 3px var(--primary-light-color),
    0 8px 20px rgba(111, 63, 34, 0.16);
  background: rgba(255, 250, 241, 0.98);
  transform: translateY(-1px);
}

.search-wrap {
  position: relative;
}

.search-leading-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
  transition: color 0.25s ease;
  z-index: 1;
}

.search-wrap::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: var(--radius-full);
  background: radial-gradient(circle at 20% 50%, rgba(154, 90, 47, 0.2), transparent 65%);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.search-wrap:focus-within .search-leading-icon {
  color: var(--primary-color);
}

.search-wrap:focus-within::after {
  opacity: 1;
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
  border-radius: var(--radius-full);
  padding: 8px 14px;
}

.login-btn:hover {
  background: var(--primary-hover-color);
  color: white;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.avatar-link {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: var(--text-primary);
  font-size: 13px;
  background: rgba(255, 250, 241, 0.88);
}

.avatar-link:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.guest-main {
  flex: 1;
  padding: var(--spacing-xl) 0;
}

.guest-footer {
  background: rgba(255, 250, 241, 0.76);
  border-top: var(--glass-border);
  padding: var(--spacing-xl) 0 var(--spacing-lg);
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: auto;
}

.footer-content {
  display: grid;
  grid-template-columns: 1.3fr 1fr 1fr;
  gap: var(--spacing-lg);
}

.footer-content h3,
.footer-content h4 {
  margin: 0 0 8px;
  color: var(--text-primary);
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.footer-content p {
  margin: 0;
}

.brand-note {
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-tertiary);
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-links a {
  color: var(--text-secondary);
  text-decoration: none;
}

.footer-links a:hover {
  color: var(--primary-color);
}

.footer-bottom {
  margin-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
  padding-top: var(--spacing-md);
}

.footer-bottom p {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 12px;
}

.record-line {
  margin-top: 4px;
}

.record-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-tertiary);
  text-decoration: none;
}

.record-link:hover {
  color: var(--primary-color);
  text-decoration: underline;
}

.police-link {
  font-weight: 500;
}

.police-logo-img {
  width: 14px;
  height: 14px;
  object-fit: contain;
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
}
</style>
