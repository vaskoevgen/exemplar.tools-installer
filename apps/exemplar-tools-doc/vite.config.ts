import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      app_routing: resolve(__dirname, 'src/app_routing'),
      page_components: resolve(__dirname, 'src/page_components'),
      project_scaffold: resolve(__dirname, 'src/project_scaffold'),
      root: resolve(__dirname, 'src/root'),
      shared_components: resolve(__dirname, 'src/shared_components'),
    },
  },
  server: { port: 4000 },
});
