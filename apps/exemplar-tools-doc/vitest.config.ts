import { defineConfig } from 'vitest/config';
import React from 'react';

// Stub plugin: intercepts .svg (and .svg?react) imports using virtual
// module IDs (\0 prefix) so Vite never tries to resolve non-existent
// SVG files. React can render the stub without DOMException.
const SVG_PREFIX = '\x00svg:';
const svgReactStubPlugin = {
  name: 'svg-react-stub',
  resolveId(id: string) {
    if (id.includes('.svg')) return SVG_PREFIX + id;
  },
  load(id: string) {
    if (id.startsWith(SVG_PREFIX)) {
      return `import React from 'react'; export default function SvgStub(props) { return React.createElement('svg', props); }`;
    }
  },
};

export default defineConfig({
  plugins: [svgReactStubPlugin],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['@testing-library/jest-dom/vitest'],
    include: ['tests/**/*.test.ts', 'tests/**/*.test.tsx', 'src/**/*.test.ts', 'src/**/*.test.tsx'],
  },
  resolve: {
    alias: {
      '@': new URL('./src', import.meta.url).pathname,
      'page_content': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/page_content',
      '../page_content': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/page_content',
      'pipeline_diagram': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/pipeline_diagram',
      '../pipeline_diagram': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/pipeline_diagram',
      'project_scaffold': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/project_scaffold',
      '../project_scaffold': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/project_scaffold',
      'root': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/root',
      '../root': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/root',
      'routing_and_layout': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/routing_and_layout',
      '../routing_and_layout': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/routing_and_layout',
      'shared_ui': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/shared_ui',
      '../shared_ui': '/Users/yevhenvasko/source/exemplar.tools-installer/apps/exemplar-tools-doc/src/shared_ui',
    },
  },
});
