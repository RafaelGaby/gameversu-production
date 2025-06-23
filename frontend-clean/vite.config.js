import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path' // Importe o módulo 'path' do Node.js

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Adicione este bloco para resolver o atalho '@'
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})