import { fileURLToPath, URL } from 'node:url'
// ... (其他 import 保持不变)

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      // 如果你之前修复了 gen 的路径，这里应该还有 '@gen': ...
    },
  },
  server: {
    host: '0.0.0.0',
    port: 80,
    allowedHosts: ['starroll.ie'],
    
    // === 新增以下 proxy 配置 ===
    proxy: {
      '/api': {
        target: 'https://starroll.ie', // 你的线上后端地址
        changeOrigin: true,            // 允许跨域
        secure: false,                 // 如果线上环境 HTTPS 证书有问题，设为 false 忽略验证
      }
    }
    // ========================
    
    // https: {
    //   key: readFileSync(join(__dirname, './cert/privkey.pem')),
    //   cert: readFileSync(join(__dirname, './cert/fullchain.pem')),
    // },
  },
})