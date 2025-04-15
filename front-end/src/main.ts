import './assets/main.scss'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createYmaps } from 'vue-yandex-maps'
import App from './App.vue'
import router from './router'

const app = createApp(App)

const yamaps = createYmaps({
  apikey: 'REDACTED',
})

app.use(createPinia())
app.use(router)
app.use(yamaps)

app.mount('#app')

export { router }
