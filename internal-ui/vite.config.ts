import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/virtual-assistant/v1': {
        target: "http://localhost:8083",
        rewrite: path => path.replace(/^\/api\/virtual-assistant\/v1/, '/api/v1')
      }
    },
  },
})
