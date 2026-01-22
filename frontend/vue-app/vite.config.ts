import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: true, // 允许外部访问
    allowedHosts: [
      '.ngrok.io',           // 允许所有 ngrok.io 子域名
      '.ngrok-free.app',     // 允许所有 ngrok-free.app 子域名
      '.ngrok-free.dev',     // 允许所有 ngrok-free.dev 子域名
    ],
  },
})
