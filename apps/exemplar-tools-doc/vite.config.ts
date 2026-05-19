import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      shared_ui: resolve(__dirname, 'src/shared_ui'),
      page_content: resolve(__dirname, 'src/page_content'),
      pipeline_diagram: resolve(__dirname, 'src/pipeline_diagram'),
      routing_and_layout: resolve(__dirname, 'src/routing_and_layout'),
      project_scaffold: resolve(__dirname, 'src/project_scaffold'),
      root: resolve(__dirname, 'src/root'),
    },
  },
  server: {
    port: 4000,
  },
});
