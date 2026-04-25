import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'
import { setupDirectives } from './directives'
import './router/guard'
import './style.css'
import './styles/theme.css'

const app = createApp(App)

app.use(pinia)
app.use(router)

// 注册自定义指令
setupDirectives(app)

app.mount('#app')
