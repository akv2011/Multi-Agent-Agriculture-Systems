import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load environment variables based on mode (development/production)
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [react()],
    // Define default environment variables to be available in the client
    define: {
      // Ensure environment variables are strings
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL || 'http://localhost:8000'),
      'import.meta.env.VITE_WEBSOCKET_URL': JSON.stringify(env.VITE_WEBSOCKET_URL || 'ws://localhost:8765'),
      'import.meta.env.VITE_ENABLE_SATELLITE_VISUALIZATION': JSON.stringify(env.VITE_ENABLE_SATELLITE_VISUALIZATION || false),
      'import.meta.env.VITE_ENABLE_MULTILINGUAL_SUPPORT': JSON.stringify(env.VITE_ENABLE_MULTILINGUAL_SUPPORT || false),
      'import.meta.env.VITE_ANALYTICS_KEY': JSON.stringify(env.VITE_ANALYTICS_KEY || ''),
    },
  }
})
