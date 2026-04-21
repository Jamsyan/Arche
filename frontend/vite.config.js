import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        // Chunk splitting: separate vendor libs from app code
        manualChunks(id) {
          if (id.includes('node_modules')) return 'vendor'
          // Each component group gets its own chunk
          if (id.includes('/components/platform/')) return 'platform'
          if (id.includes('/components/admin/')) return 'admin'
          return null
        }
      }
    }
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
