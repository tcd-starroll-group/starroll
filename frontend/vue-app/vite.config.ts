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
  // --- 新增开发服务器配置 ---
  server: {
    proxy: {
      // 当你代码里请求以 /api 开头的地址时
      '/api': {
        target: 'http://10.6.50.69:8000', // 这里填你后端真实的运行地址
        changeOrigin: true,              // 允许跨域
        rewrite: (path) => path.replace(/^\/api/, '') // 发给后端时去掉 /api 前缀
      }
    }
  }
})