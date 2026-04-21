import { createApp } from 'vue'
import App from './App.vue'
import ArcoVue from '@arco-design/web-vue'
import '@arco-design/web-vue/dist/arco.css'
import router from './router/index.js'

// 全局覆盖 Arco 设计令牌：低饱和配色 + 大圆角 + 舒适间距
const themeStyle = document.createElement('style')
themeStyle.textContent = `
  :root {
    /* 主色：低饱和灰蓝，不要高饱和纯蓝 */
    --color-primary: #5b7fa4;
    --color-primary-light-1: #e8eef4;
    --color-primary-light-2: #d1dfe9;
    --color-primary-light-3: #b9cddd;
    --color-primary-light-4: #a2bccf;
    --color-primary-dark-1: #4a6a8a;
    --color-primary-dark-2: #395670;

    /* 文字色：不用纯黑，用暖灰 */
    --color-text-1: #2c3e50;
    --color-text-2: #5a6c7d;
    --color-text-3: #8899a6;
    --color-text-4: #aab8c2;

    /* 边框：更柔和 */
    --color-border-1: #e1e8ed;
    --color-border-2: #c9d4dc;
    --color-border-3: #b0bec5;

    /* 填充色 */
    --color-fill-1: #f7f9fb;
    --color-fill-2: #eef2f5;
    --color-fill-3: #e3e9ee;
    --color-fill-4: #d5dde4;

    /* 背景 */
    --color-bg-1: #ffffff;
    --color-bg-2: #f7f9fb;
    --color-bg-3: #eef2f5;
    --color-bg-4: #e3e9ee;

    /* 圆角：更大更柔和 */
    --border-radius-none: 0;
    --border-radius-small: 8px;
    --border-radius-medium: 12px;
    --border-radius-large: 16px;
    --border-radius-huge: 20px;
    --border-radius-circle: 50%;
  }

  /* 全局字体 */
  * {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "PingFang SC",
      "Hiragino Sans GB", "Microsoft YaHei", Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  body {
    margin: 0;
    background: var(--color-fill-1);
    color: var(--color-text-1);
  }

  /* Arco 组件全局覆盖 */
  .arco-card {
    border-radius: var(--border-radius-large) !important;
  }
  .arco-btn {
    border-radius: var(--border-radius-medium) !important;
  }
  .arco-input-wrapper,
  .arco-textarea-wrapper {
    border-radius: var(--border-radius-medium) !important;
  }
  .arco-tag {
    border-radius: var(--border-radius-small) !important;
  }
  .arco-alert {
    border-radius: var(--border-radius-medium) !important;
  }
  .arco-menu {
    border-radius: var(--border-radius-medium) !important;
  }
  .arco-radio-button {
    border-radius: var(--border-radius-small) !important;
  }
  .arco-list-bordered {
    border-radius: var(--border-radius-large) !important;
    overflow: hidden;
  }
  .arco-table {
    border-radius: var(--border-radius-large) !important;
  }
  .arco-page-header {
    padding-left: 0 !important;
    padding-right: 0 !important;
  }
  /* 去掉 Arco 默认的主按钮高饱和蓝渐变 */
  .arco-btn-primary {
    background: var(--color-primary) !important;
    border-color: var(--color-primary) !important;
  }
  .arco-btn-primary:hover {
    background: var(--color-primary-dark-1) !important;
    border-color: var(--color-primary-dark-1) !important;
  }
  /* 链接颜色 */
  a {
    color: var(--color-primary) !important;
  }
`
document.head.appendChild(themeStyle)

const app = createApp(App)
app.use(ArcoVue)
app.use(router)
app.mount('#app')
