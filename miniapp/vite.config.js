import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/xion-trade-miniapp/',
  server: {
    host: '0.0.0.0',
    port: 3000,
    cors: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
