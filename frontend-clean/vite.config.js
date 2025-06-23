import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url' // Forma moderna de lidar com caminhos

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Esta é a forma mais robusta e moderna de definir o atalho
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})