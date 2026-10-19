import { defineConfig } from 'vite'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    // Keep the current React + Tailwind setup aligned with the existing frontend code.
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      // Alias @ to the src directory for shared imports.
      '@': path.resolve(__dirname, './src'),
    },
  },

  // File types that can be imported as raw assets in this project.
  assetsInclude: ['**/*.svg', '**/*.csv'],
})
