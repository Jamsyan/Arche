import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import ArcoVue from '@arco-design/web-vue'
import ArcoVueIcon from '@arco-design/web-vue/es/icon'
import '@arco-design/web-vue/dist/arco.css'
import router from './router/index.js'
import './styles/tokens.css'

// 全局覆盖 Arco 设计令牌：深棕红 + 青蓝配色（基于 Logo 色系）
const themeStyle = document.createElement('style')
themeStyle.textContent = `
  :root {
    /* 主色：深棕红（Logo 主色调） */
    --primary: #5C3D2E;
    --primary-light: #8B5A3C;
    --primary-dark: #3D2520;
    --primary-light-1: #F5EDE9;
    --primary-light-2: #E8D5CC;
    --primary-light-3: #D4B8A8;
    --primary-light-4: #B89580;

    /* 辅色：青蓝（Logo 点缀色） */
    --secondary: #5BA0B5;
    --secondary-light: #8BC5D4;
    --secondary-dark: #3D7A8C;

    /* 主色变量兼容 Arco */
    --color-primary: #5C3D2E;
    --color-primary-light-1: #F5EDE9;
    --color-primary-light-2: #E8D5CC;
    --color-primary-light-3: #D4B8A8;
    --color-primary-light-4: #B89580;
    --color-primary-dark-1: #3D2520;
    --color-primary-dark-2: #2E1A15;

    /* 文字色：温暖深灰 */
    --color-text-1: #2C2420;
    --color-text-2: #5A4F48;
    --color-text-3: #8A7F75;
    --color-text-4: #B5A99D;

    /* 边框：暖灰 */
    --color-border: var(--color-border-1);
    --color-border-1: #E8E2DC;
    --color-border-2: #D5CCC4;
    --color-border-3: #BEB4AA;

    /* 填充色 */
    --color-fill-1: #FAF8F6;
    --color-fill-2: #F2EDE8;
    --color-fill-3: #E8E0D8;
    --color-fill-4: #DCD2C8;

    /* 背景 */
    --color-bg-1: #FFFFFF;
    --color-bg-2: #FAF8F6;
    --color-bg-3: #F2EDE8;
    --color-bg-4: #E8E0D8;

    /* 标签徽章专用色 */
    --tag-bg: #F2EDE8;
    --tag-text: #5A4F48;
    --tag-border: #E0D6CC;
    --tag-hover: #E8DCD2;
    --primary-light: #E8D5CC;

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
  /* 主按钮：深棕红 */
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
    color: var(--primary) !important;
  }
`
document.head.appendChild(themeStyle)

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(ArcoVue)
app.use(ArcoVueIcon)
app.use(router)
app.mount('#app')
