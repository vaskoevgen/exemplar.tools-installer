import { defineConfig } from 'vitest/config';
import React from 'react';

export default defineConfig({
  plugins: [],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['@testing-library/jest-dom/vitest'],
    include: ['tests/**/*.test.ts', 'tests/**/*.test.tsx', 'src/**/*.test.ts', 'src/**/*.test.tsx'],
  },
  resolve: {
    alias: {
      '@': new URL('./src', import.meta.url).pathname,
      'app_routing': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/app_routing',
      '../app_routing': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/app_routing',
      'page_components': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/page_components',
      '../page_components': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/page_components',
      'project_scaffold': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/project_scaffold',
      '../project_scaffold': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/project_scaffold',
      'root': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/root',
      '../root': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/root',
      'shared_components': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/shared_components',
      '../shared_components': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/shared_components',
    },
  },
});
