import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import * as path from 'path'
import basicSsl from '@vitejs/plugin-basic-ssl'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), basicSsl()],
  server: {
    proxy: {
        '/api': 'http://localhost:8080',
        '/github': 'http://localhost:8080'
    },
    https: true
  },
  resolve: {
    alias: [
        {
            find: '@src',
            replacement: path.resolve(__dirname, 'src/')
        },
        {
            find: '@assets',
            replacement: path.resolve(__dirname, 'src/assets')
        },
        {
            find: '@components',
            replacement: path.resolve(__dirname, 'src/components')
        },
         {
            find: '@layouts',
            replacement: path.resolve(__dirname, 'src/layouts')
        },
        {
            find: '@pages',
            replacement: path.resolve(__dirname, 'src/pages')
        },
        {
            find: '@routes',
            replacement: path.resolve(__dirname, 'src/routes')
        },
        {
            find: '@theme',
            replacement: path.resolve(__dirname, 'src/theme')
        }
    ]
  }
})
