const PACT_KEY = "PACT:d97abb:project_scaffold";

import type { DependencyEntry } from './types';

export function buildPackageJson(
  projectName: string,
  dependencies: DependencyEntry[],
  devDependencies: DependencyEntry[],
): string {
  const deps: Record<string, string> = {};
  for (const d of dependencies) {
    deps[d.packageName] = d.versionRange;
  }
  const devDeps: Record<string, string> = {};
  for (const d of devDependencies) {
    devDeps[d.packageName] = d.versionRange;
  }

  const pkg = {
    name: projectName,
    private: true,
    version: '0.0.0',
    type: 'module',
    scripts: {
      dev: 'vite',
      build: 'tsc && vite build',
      preview: 'vite preview',
      test: 'vitest run',
    },
    dependencies: deps,
    devDependencies: devDeps,
  };

  return JSON.stringify(pkg, null, 2) + '\n';
}

export function buildTsconfigJson(): string {
  return `{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
`;
}

export function buildTsconfigNodeJson(): string {
  return `{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
`;
}

export function buildViteConfigTs(): string {
  return `import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 4000,
  },
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
  },
});
`;
}

export function buildTailwindConfigTs(): string {
  return `import type { Config } from 'tailwindcss';

export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config;
`;
}

export function buildPostcssConfigMjs(): string {
  return `import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';

export default {
  plugins: {
    tailwindcss,
    autoprefixer,
  },
};
`;
}

export function buildVercelJson(): string {
  const config = {
    rewrites: [
      { source: '/(.*)', destination: '/index.html' },
    ],
  };
  return JSON.stringify(config, null, 2) + '\n';
}

export function buildIndexHtml(): string {
  return `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>exemplar.tools</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
`;
}

export function buildVitestSetupTs(): string {
  return `import '@testing-library/jest-dom';
`;
}

export function buildMainTsx(): string {
  return `import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
`;
}

export function buildIndexCss(): string {
  return `@tailwind base;
@tailwind components;
@tailwind utilities;
`;
}

export function buildAppTsx(): string {
  return `import React from 'react';

export function App() {
  return (
    <div className="min-h-screen bg-white">
      <h1>exemplar.tools Documentation</h1>
    </div>
  );
}

export default App;
`;
}
