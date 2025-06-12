// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 7070,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080', //  <-- 修改这里
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '') // 如果需要
      }
    }
  }
})