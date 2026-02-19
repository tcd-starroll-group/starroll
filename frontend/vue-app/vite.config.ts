import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

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
    proxy: {
      // 当你代码里请求以 /api 开头的地址时
      '/api': {
        target: 'http://localhost:8000', // 这里填你后端真实的运行地址
        changeOrigin: true,              // 允许跨域
        rewrite: (path) => path.replace(/^\/api/, ''), // 去掉 /api 前缀（如果后端路由没有）
        secure: false, // 若后端是自签名 https 可启用
      }
    }
  }
})