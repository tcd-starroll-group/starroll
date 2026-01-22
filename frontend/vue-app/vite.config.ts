import { fileURLToPath, URL } from 'node:url'
import { readFileSync } from 'fs'
import { join } from 'path'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 443,
    allowedHosts: ['starroll.ie'],
    https: {
      key: readFileSync(join(__dirname, './cert/privkey.pem')),
      cert: readFileSync(join(__dirname, './cert/fullchain.pem')),
    },
  },
})
