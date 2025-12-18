import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'
import './styles/index.css'

const app = createApp(App)

// Pinia State Management
const pinia = createPinia()
app.use(pinia)

// Vue Router
app.use(router)

// Element Plus with Chinese locale
app.use(ElementPlus, {
  locale: zhCn
})

// Mount app
app.mount('#app')
