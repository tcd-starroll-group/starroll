import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: true, // 监听所有地址
    port: 5174 ,
    // 允许所有主机访问（包括 ngrok 域名）
    allowedHosts: [
      '.ngrok-free.app',
      '.ngrok-free.dev',
      '.ngrok.io',
      'localhost'
    ],
    // 或者使用通配符允许所有（开发环境）
    // allowedHosts: ['*']
  }
});

