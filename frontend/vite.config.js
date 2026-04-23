import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 测试模式下处理静态资源引用，避免 jsdom 报错
const testAssetPlugin = () => ({
  name: 'test-asset-mock',
  enforce: 'pre',
  transform(code, id) {
    if (id.endsWith('.vue') && process.env.VITEST) {
      return code.replace(/src="\/logo\.png"/g, 'src="data:image/png;base64,iVBORw0KGgo="')
    }
    return null
  },
})

export default defineConfig({
  plugins: [testAssetPlugin(), vue()],
  test: {
    environment: 'jsdom',
    globalSetup: ['./tests/setup.js'],
    setupFiles: ['./tests/setup.js'],
    singleFork: true,
  },
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
