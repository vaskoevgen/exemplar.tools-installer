const PACT_KEY = "PACT:d97abb:project_scaffold";

import { getRequiredDependencies } from './dependencies';

export function generatePackageJson(): string {
  const deps = getRequiredDependencies();
  const dependencies: Record<string, string> = {};
  for (const d of deps.dependencies) {
    dependencies[d.packageName] = d.versionRange;
  }
  const devDependencies: Record<string, string> = {};
  for (const d of deps.devDependencies) {
    devDependencies[d.packageName] = d.versionRange;
  }
  const pkg = {
    name: 'exemplar-tools-doc',
    private: true,
    version: '0.0.0',
    type: 'module',
    scripts: {
      dev: 'vite',
      build: 'tsc && vite build',
      preview: 'vite preview',
      test: 'vitest',
    },
    dependencies,
    devDependencies,
  };
  return JSON.stringify(pkg, null, 2) + '\n';
}

export function generateTsconfigJson(): string {
  const tsconfig = {
    compilerOptions: {
      target: 'ES2020',
      useDefineForClassFields: true,
      lib: ['ES2020', 'DOM', 'DOM.Iterable'],
      module: 'ESNext',
      skipLibCheck: true,
      moduleResolution: 'bundler',
      allowImportingTsExtensions: true,
      resolveJsonModule: true,
      isolatedModules: true,
      noEmit: true,
      jsx: 'react-jsx',
      strict: true,
      noUnusedLocals: true,
      noUnusedParameters: true,
      noFallthroughCasesInSwitch: true,
      baseUrl: '.',
      paths: {
        '@/*': ['./src/*'],
      },
    },
    include: ['src'],
    references: [{ path: './tsconfig.node.json' }],
  };
  return JSON.stringify(tsconfig, null, 2) + '\n';
}

export function generateTsconfigNodeJson(): string {
  const tsconfig = {
    compilerOptions: {
      composite: true,
      skipLibCheck: true,
      module: 'ESNext',
      moduleResolution: 'bundler',
      allowSyntheticDefaultImports: true,
    },
    include: ['vite.config.ts'],
  };
  return JSON.stringify(tsconfig, null, 2) + '\n';
}

export function generateViteConfigTs(): string {
  return `import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    port: 4000,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
  },
});
`;
}

export function generateTailwindConfigTs(): string {
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

export function generatePostcssConfigMjs(): string {
  return `import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';

export default {
  plugins: [
    tailwindcss,
    autoprefixer,
  ],
};
`;
}

export function generateVercelJson(): string {
  const config = {
    rewrites: [
      { source: '/(.*)', destination: '/index.html' },
    ],
  };
  return JSON.stringify(config, null, 2) + '\n';
}

export function generateIndexHtml(): string {
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

export function generateVitestSetupTs(): string {
  return `import '@testing-library/jest-dom';
`;
}

export function generateMainTsx(): string {
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

export function generateIndexCss(): string {
  return `@tailwind base;
@tailwind components;
@tailwind utilities;
`;
}

export function generateAppTsx(): string {
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
