import { fileURLToPath, URL } from 'node:url'
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
    allowedHosts: ['starroll.ie'],
    
    proxy: {
      '/api': {
        target: 'https://starroll.ie', 
        changeOrigin: true,       
        secure: false,      
      }
    }
    // ========================
    
    // https: {
    //   key: readFileSync(join(__dirname, './cert/privkey.pem')),
    //   cert: readFileSync(join(__dirname, './cert/fullchain.pem')),
    // },
  },
})