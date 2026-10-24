/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Components
import App from './App.vue'
import { createApp } from 'vue'
import { registerPlugins } from '@/plugins'
import router from './router' 

const app = createApp(App)
registerPlugins(app)
app.use(router).mount('#app')

