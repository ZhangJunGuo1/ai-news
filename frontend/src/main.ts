import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus, { ElMessage } from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/styles/themes.css'
import './assets/styles/global.css'
import { initTheme } from './utils/theme'

initTheme()

const app = createApp(App)
app.use(router)
app.use(ElementPlus)

// 配置全局 $message 方法
app.config.globalProperties.$message = ElMessage

app.mount('#app')