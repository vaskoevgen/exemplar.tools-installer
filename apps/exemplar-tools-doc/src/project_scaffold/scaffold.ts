import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import { ScaffoldFilePath } from './types';
import type {
  ProjectManifest,
  DependencyEntry,
  RequiredDependencies,
  ScaffoldResult,
  ScaffoldOptions,
  ScaffoldValidationResult,
} from './types';
import {
  DIRECTORY_NOT_FOUND,
  FILE_ALREADY_EXISTS,
  WRITE_PERMISSION_DENIED,
  INVALID_OUTPUT_DIR,
} from './errors';

const PACT_KEY = "PACT:d97abb:project_scaffold";

const ALL_FILE_PATHS: string[] = Object.values(ScaffoldFilePath);

// ── Pure functions ──────────────────────────────────────────

export function getProjectManifest(): ProjectManifest {
  console.log(PACT_KEY, 'getProjectManifest', 'invoked');
  return {
    projectRoot: 'exemplar-tools-doc',
    files: [...ALL_FILE_PATHS],
    projectName: 'exemplar-tools-doc',
    devServerPort: 4000,
  };
}

export function getRequiredDependencies(): RequiredDependencies {
  console.log(PACT_KEY, 'getRequiredDependencies', 'invoked');

  const dependencies: DependencyEntry[] = [
    { packageName: 'react', versionRange: '^18.3.0', isDev: false },
    { packageName: 'react-dom', versionRange: '^18.3.0', isDev: false },
    { packageName: 'react-router-dom', versionRange: '^6.23.0', isDev: false },
  ];

  const devDependencies: DependencyEntry[] = [
    { packageName: 'vite', versionRange: '^5.4.0', isDev: true },
    { packageName: '@vitejs/plugin-react', versionRange: '^4.3.0', isDev: true },
    { packageName: 'tailwindcss', versionRange: '^3.4.0', isDev: true },
    { packageName: 'vitest', versionRange: '^2.0.0', isDev: true },
    { packageName: '@testing-library/react', versionRange: '^16.0.0', isDev: true },
    { packageName: '@testing-library/jest-dom', versionRange: '^6.0.0', isDev: true },
    { packageName: 'jsdom', versionRange: '^24.0.0', isDev: true },
    { packageName: 'prism-react-renderer', versionRange: '^2.3.0', isDev: true },
    { packageName: 'autoprefixer', versionRange: '^10.4.0', isDev: true },
    { packageName: 'postcss', versionRange: '^8.4.0', isDev: true },
    { packageName: 'typescript', versionRange: '^5.5.0', isDev: true },
    { packageName: '@types/react', versionRange: '^18.3.0', isDev: true },
    { packageName: '@types/react-dom', versionRange: '^18.3.0', isDev: true },
  ];

  return { dependencies, devDependencies };
}

// ── File content builders ───────────────────────────────────

function buildPackageJson(): string {
  const { dependencies, devDependencies } = getRequiredDependencies();

  const deps: Record<string, string> = {};
  for (const d of dependencies) {
    deps[d.packageName] = d.versionRange;
  }

  const devDeps: Record<string, string> = {};
  for (const d of devDependencies) {
    devDeps[d.packageName] = d.versionRange;
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
      test: 'vitest run',
    },
    dependencies: deps,
    devDependencies: devDeps,
  };

  return JSON.stringify(pkg, null, 2) + '\n';
}

function buildTsconfigJson(): string {
  const config = {
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
  return JSON.stringify(config, null, 2) + '\n';
}

function buildTsconfigNodeJson(): string {
  const config = {
    compilerOptions: {
      composite: true,
      skipLibCheck: true,
      module: 'ESNext',
      moduleResolution: 'bundler',
      allowSyntheticDefaultImports: true,
    },
    include: ['vite.config.ts'],
  };
  return JSON.stringify(config, null, 2) + '\n';
}

function buildViteConfigTs(): string {
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

function buildTailwindConfigTs(): string {
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

function buildPostcssConfigMjs(): string {
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

function buildVercelJson(): string {
  const config = {
    rewrites: [
      { source: '/(.*)', destination: '/index.html' },
    ],
  };
  return JSON.stringify(config, null, 2) + '\n';
}

function buildIndexHtml(): string {
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

function buildVitestSetupTs(): string {
  return `import '@testing-library/jest-dom';
`;
}

function buildMainTsx(): string {
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

function buildIndexCss(): string {
  return `@tailwind base;
@tailwind components;
@tailwind utilities;
`;
}

function buildAppTsx(): string {
  return `import React from 'react';

export function App(): React.ReactElement {
  return (
    <div className="min-h-screen bg-white">
      <h1>exemplar.tools Documentation</h1>
    </div>
  );
}

export default App;
`;
}

// ── File content map ────────────────────────────────────────

function buildFileContents(): Record<string, string> {
  return {
    [ScaffoldFilePath['package.json']]: buildPackageJson(),
    [ScaffoldFilePath['tsconfig.json']]: buildTsconfigJson(),
    [ScaffoldFilePath['tsconfig.node.json']]: buildTsconfigNodeJson(),
    [ScaffoldFilePath['vite.config.ts']]: buildViteConfigTs(),
    [ScaffoldFilePath['tailwind.config.ts']]: buildTailwindConfigTs(),
    [ScaffoldFilePath['postcss.config.mjs']]: buildPostcssConfigMjs(),
    [ScaffoldFilePath['vercel.json']]: buildVercelJson(),
    [ScaffoldFilePath['index.html']]: buildIndexHtml(),
    [ScaffoldFilePath['vitest.setup.ts']]: buildVitestSetupTs(),
    [ScaffoldFilePath['src/main.tsx']]: buildMainTsx(),
    [ScaffoldFilePath['src/index.css']]: buildIndexCss(),
    [ScaffoldFilePath['src/App.tsx']]: buildAppTsx(),
  };
}

// ── generateScaffold ────────────────────────────────────────

export async function generateScaffold(
  options: ScaffoldOptions,
): Promise<ScaffoldResult> {
  console.log(PACT_KEY, 'generateScaffold', 'start', { outputDir: options.outputDir, overwrite: options.overwrite });

  const { outputDir, overwrite = false } = options;

  // Validate outputDir
  if (!outputDir || outputDir.trim().length === 0) {
    throw new INVALID_OUTPUT_DIR(outputDir);
  }
  if (outputDir.includes('\0')) {
    throw new INVALID_OUTPUT_DIR(outputDir);
  }

  // Check parent directory exists
  const resolvedDir = path.resolve(outputDir);
  const parentDir = path.dirname(resolvedDir);

  try {
    const parentStat = await fs.stat(parentDir);
    if (!parentStat.isDirectory()) {
      throw new DIRECTORY_NOT_FOUND(resolvedDir);
    }
  } catch (err: unknown) {
    if (err instanceof DIRECTORY_NOT_FOUND) throw err;
    if (err instanceof Error && 'code' in err && (err as NodeJS.ErrnoException).code === 'ENOENT') {
      throw new DIRECTORY_NOT_FOUND(resolvedDir);
    }
    throw err;
  }

  // Create output directory if needed
  await fs.mkdir(resolvedDir, { recursive: true });

  // Check for existing files if overwrite is false
  if (!overwrite) {
    const existing: string[] = [];
    for (const fp of ALL_FILE_PATHS) {
      const fullPath = path.join(resolvedDir, fp);
      try {
        await fs.access(fullPath);
        existing.push(fp);
      } catch {
        // File does not exist, which is fine
      }
    }
    if (existing.length > 0) {
      throw new FILE_ALREADY_EXISTS(existing);
    }
  }

  // Create src/ subdirectory
  const srcDir = path.join(resolvedDir, 'src');
  await fs.mkdir(srcDir, { recursive: true });

  // Build and write all files
  const fileContents = buildFileContents();
  let filesWritten = 0;

  for (const fp of ALL_FILE_PATHS) {
    const fullPath = path.join(resolvedDir, fp);
    const dir = path.dirname(fullPath);
    await fs.mkdir(dir, { recursive: true });

    try {
      await fs.writeFile(fullPath, fileContents[fp], 'utf-8');
      filesWritten++;
    } catch (err: unknown) {
      if (err instanceof Error && 'code' in err && (err as NodeJS.ErrnoException).code === 'EACCES') {
        throw new WRITE_PERMISSION_DENIED(fullPath);
      }
      throw err;
    }
  }

  const manifest: ProjectManifest = {
    projectRoot: resolvedDir,
    files: [...ALL_FILE_PATHS],
    projectName: 'exemplar-tools-doc',
    devServerPort: 4000,
  };

  const result: ScaffoldResult = {
    manifest,
    filesWritten,
    hasJsFiles: false,
    hasPyFiles: false,
  };

  console.log(PACT_KEY, 'generateScaffold', 'complete', { filesWritten });
  return result;
}

// ── validateScaffold ────────────────────────────────────────

export async function validateScaffold(
  projectRoot: string,
): Promise<ScaffoldValidationResult> {
  console.log(PACT_KEY, 'validateScaffold', 'start', { projectRoot });

  const resolvedRoot = path.resolve(projectRoot);

  // Check directory exists
  try {
    const stat = await fs.stat(resolvedRoot);
    if (!stat.isDirectory()) {
      throw new DIRECTORY_NOT_FOUND(resolvedRoot);
    }
  } catch (err: unknown) {
    if (err instanceof DIRECTORY_NOT_FOUND) throw err;
    if (err instanceof Error && 'code' in err && (err as NodeJS.ErrnoException).code === 'ENOENT') {
      throw new DIRECTORY_NOT_FOUND(resolvedRoot);
    }
    throw err;
  }

  const checks: Array<{ check: string; passed: boolean; message?: string }> = [];

  // Check all 12 files exist
  let allFilesExist = true;
  for (const fp of ALL_FILE_PATHS) {
    const fullPath = path.join(resolvedRoot, fp);
    try {
      const stat = await fs.stat(fullPath);
      if (stat.isFile()) {
        checks.push({ check: `file_exists:${fp}`, passed: true });
      } else {
        checks.push({ check: `file_exists:${fp}`, passed: false, message: `${fp} is not a regular file` });
        allFilesExist = false;
      }
    } catch {
      checks.push({ check: `file_exists:${fp}`, passed: false, message: `${fp} does not exist` });
      allFilesExist = false;
    }
  }

  // If not all files exist, skip content checks
  if (!allFilesExist) {
    console.log(PACT_KEY, 'validateScaffold', 'complete', { isValid: false });
    return { isValid: false, checks };
  }

  // Validate package.json
  try {
    const pkgContent = await fs.readFile(path.join(resolvedRoot, 'package.json'), 'utf-8');
    const pkg = JSON.parse(pkgContent) as Record<string, unknown>;
    const hasTypeModule = pkg.type === 'module';
    checks.push({ check: 'package_json_type_module', passed: hasTypeModule });

    // Check all required deps
    const requiredDeps = getRequiredDependencies();
    const pkgDeps = (pkg.dependencies ?? {}) as Record<string, string>;
    const pkgDevDeps = (pkg.devDependencies ?? {}) as Record<string, string>;

    for (const d of requiredDeps.dependencies) {
      const found = pkgDeps[d.packageName] === d.versionRange;
      checks.push({ check: `dep:${d.packageName}`, passed: found });
    }
    for (const d of requiredDeps.devDependencies) {
      const found = pkgDevDeps[d.packageName] === d.versionRange;
      checks.push({ check: `devDep:${d.packageName}`, passed: found });
    }
  } catch (err: unknown) {
    checks.push({ check: 'package_json_valid', passed: false, message: String(err) });
  }

  // Validate vite.config.ts
  try {
    const viteContent = await fs.readFile(path.join(resolvedRoot, 'vite.config.ts'), 'utf-8');
    checks.push({ check: 'vite_port_4000', passed: viteContent.includes('4000') });
    checks.push({ check: 'vite_jsdom', passed: viteContent.includes('jsdom') });
    checks.push({ check: 'vite_globals', passed: viteContent.includes('globals: true') });
    checks.push({ check: 'vite_setup_files', passed: viteContent.includes('./vitest.setup.ts') });
  } catch (err: unknown) {
    checks.push({ check: 'vite_config_valid', passed: false, message: String(err) });
  }

  // Validate vitest.setup.ts
  try {
    const setupContent = await fs.readFile(path.join(resolvedRoot, 'vitest.setup.ts'), 'utf-8');
    checks.push({ check: 'vitest_setup_jest_dom', passed: setupContent.includes('@testing-library/jest-dom') });
  } catch (err: unknown) {
    checks.push({ check: 'vitest_setup_valid', passed: false, message: String(err) });
  }

  // Validate vercel.json
  try {
    const vercelContent = await fs.readFile(path.join(resolvedRoot, 'vercel.json'), 'utf-8');
    const vercel = JSON.parse(vercelContent) as { rewrites?: Array<{ source: string; destination: string }> };
    const validRewrites =
      Array.isArray(vercel.rewrites) &&
      vercel.rewrites.length === 1 &&
      vercel.rewrites[0].source === '/(.*)' &&
      vercel.rewrites[0].destination === '/index.html';
    checks.push({ check: 'vercel_rewrite', passed: validRewrites });
  } catch (err: unknown) {
    checks.push({ check: 'vercel_json_valid', passed: false, message: String(err) });
  }

  // Check no .js or .py files
  const allFiles = await listFilesRecursive(resolvedRoot);
  const hasJs = allFiles.some((f) => f.endsWith('.js'));
  const hasPy = allFiles.some((f) => f.endsWith('.py'));
  checks.push({ check: 'no_js_files', passed: !hasJs });
  checks.push({ check: 'no_py_files', passed: !hasPy });

  const isValid = checks.every((c) => c.passed);
  console.log(PACT_KEY, 'validateScaffold', 'complete', { isValid });
  return { isValid, checks };
}

async function listFilesRecursive(dir: string): Promise<string[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const results: string[] = [];
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...(await listFilesRecursive(fullPath)));
    } else {
      results.push(fullPath);
    }
  }
  return results;
}
