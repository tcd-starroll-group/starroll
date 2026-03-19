import { fileURLToPath, URL } from 'node:url'
import { readFileSync } from 'fs'
import { join } from 'path'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 80,
    // 建议把 localhost 也加进去，方便你本地通过 http://localhost 访问测试
    allowedHosts: ['starroll.ie', 'localhost', '127.0.0.1'], 
    proxy: {
      '/api': {
        // 👇 将这里改成你本地的 FastAPI 服务地址
        target: 'http://127.0.0.1:8000', 
        changeOrigin: true,            
        secure: false,                 
      }
    }
  },
})