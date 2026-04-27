import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'
import { setupDirectives } from './directives'
import './router/guard'
import './style.css'
import './styles/theme.css'
import { useAppStore } from '@/store/modules/app'

const app = createApp(App)

app.use(pinia)
app.use(router)

const appStore = useAppStore()
appStore.initTheme()

// 注册自定义指令
setupDirectives(app)

app.mount('#app')
