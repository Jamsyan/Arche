import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
// 注册持久化插件
pinia.use(piniaPluginPersistedstate)

// 导出所有store
export * from './modules/user'
export * from './modules/app'
export * from './modules/permission'

export default pinia
