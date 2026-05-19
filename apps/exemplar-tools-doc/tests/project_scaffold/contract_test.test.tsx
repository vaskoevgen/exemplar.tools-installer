import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import * as os from 'node:os';
import {
  generateScaffold,
  getProjectManifest,
  getRequiredDependencies,
  validateScaffold,
} from '../../src/project_scaffold';

const SCAFFOLD_FILE_PATHS = [
  'package.json',
  'tsconfig.json',
  'tsconfig.node.json',
  'vite.config.ts',
  'tailwind.config.ts',
  'postcss.config.mjs',
  'vercel.json',
  'index.html',
  'vitest.setup.ts',
  'src/main.tsx',
  'src/index.css',
  'src/App.tsx',
] as const;

/** Recursively list all files relative to `dir`. */
async function listFiles(dir: string, base = dir): Promise<string[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const results: string[] = [];
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      results.push(...(await listFiles(full, base)));
    } else {
      results.push(path.relative(base, full));
    }
  }
  return results;
}

let tmpDir: string;

async function makeTmpDir(): Promise<string> {
  return fs.mkdtemp(path.join(os.tmpdir(), 'scaffold-test-'));
}

// ─────────────────────────────────────────────────────────────
// 1. getProjectManifest
// ─────────────────────────────────────────────────────────────
describe('getProjectManifest', () => {
  it('returns a ProjectManifest with all required fields and correct types', () => {
    const manifest = getProjectManifest();
    expect(typeof manifest.projectRoot).toBe('string');
    expect(Array.isArray(manifest.files)).toBe(true);
    expect(typeof manifest.projectName).toBe('string');
    expect(typeof manifest.devServerPort).toBe('number');
  });

  it('returns exactly 12 files matching all ScaffoldFilePath variants', () => {
    const manifest = getProjectManifest();
    expect(manifest.files).toHaveLength(12);
    for (const fp of SCAFFOLD_FILE_PATHS) {
      expect(manifest.files, `manifest.files should contain "${fp}"`).toContain(fp);
    }
  });

  it('returns projectName === "exemplar-tools-doc"', () => {
    const manifest = getProjectManifest();
    expect(manifest.projectName).toBe('exemplar-tools-doc');
  });

  it('returns devServerPort === 4000', () => {
    const manifest = getProjectManifest();
    expect(manifest.devServerPort).toBe(4000);
  });

  it('projectName matches ^[a-z][a-z0-9\\-]*$', () => {
    const manifest = getProjectManifest();
    expect(manifest.projectName).toMatch(/^[a-z][a-z0-9\-]*$/);
  });

  it('is pure — two sequential calls return deeply equal results', () => {
    const a = getProjectManifest();
    const b = getProjectManifest();
    expect(a).toEqual(b);
  });
});

// ─────────────────────────────────────────────────────────────
// 2. getRequiredDependencies
// ─────────────────────────────────────────────────────────────
describe('getRequiredDependencies', () => {
  it('returns dependencies and devDependencies arrays', () => {
    const deps = getRequiredDependencies();
    expect(Array.isArray(deps.dependencies)).toBe(true);
    expect(Array.isArray(deps.devDependencies)).toBe(true);
  });

  it('returns exactly 3 dependencies and 13 devDependencies', () => {
    const deps = getRequiredDependencies();
    expect(deps.dependencies).toHaveLength(3);
    expect(deps.devDependencies).toHaveLength(13);
  });

  it('dependencies contain react@^18.3, react-dom@^18.3, react-router-dom@^6.23', () => {
    const deps = getRequiredDependencies();
    const names = deps.dependencies.map((d: { packageName: string }) => d.packageName);
    expect(names).toContain('react');
    expect(names).toContain('react-dom');
    expect(names).toContain('react-router-dom');
    for (const d of deps.dependencies as Array<{ packageName: string; versionRange: string }>) {
      if (d.packageName === 'react') expect(d.versionRange).toMatch(/\^18\.3/);
      if (d.packageName === 'react-dom') expect(d.versionRange).toMatch(/\^18\.3/);
      if (d.packageName === 'react-router-dom') expect(d.versionRange).toMatch(/\^6\.23/);
    }
  });

  it('devDependencies contain all 13 required packages', () => {
    const deps = getRequiredDependencies();
    const names = deps.devDependencies.map((d: { packageName: string }) => d.packageName);
    const required = [
      'vite', '@vitejs/plugin-react', 'tailwindcss', 'vitest',
      '@testing-library/react', '@testing-library/jest-dom', 'jsdom',
      'prism-react-renderer', 'autoprefixer', 'postcss', 'typescript',
      '@types/react', '@types/react-dom',
    ];
    for (const pkg of required) {
      expect(names, `devDependencies should contain "${pkg}"`).toContain(pkg);
    }
  });

  it('each DependencyEntry has correct field types', () => {
    const deps = getRequiredDependencies();
    const all = [...deps.dependencies, ...deps.devDependencies] as Array<{
      packageName: string; versionRange: string; isDev: boolean;
    }>;
    for (const entry of all) {
      expect(typeof entry.packageName).toBe('string');
      expect(typeof entry.versionRange).toBe('string');
      expect(typeof entry.isDev).toBe('boolean');
    }
  });

  it('isDev is false for dependencies and true for devDependencies', () => {
    const deps = getRequiredDependencies();
    for (const d of deps.dependencies as Array<{ isDev: boolean }>) {
      expect(d.isDev, 'dependency entry should have isDev === false').toBe(false);
    }
    for (const d of deps.devDependencies as Array<{ isDev: boolean }>) {
      expect(d.isDev, 'devDependency entry should have isDev === true').toBe(true);
    }
  });

  it('every packageName matches the valid regex', () => {
    const deps = getRequiredDependencies();
    const all = [...deps.dependencies, ...deps.devDependencies] as Array<{ packageName: string }>;
    const re = /^@?[a-z][a-z0-9\-]*(\/[a-z][a-z0-9\-]*)*$/;
    for (const e of all) {
      expect(e.packageName, `"${e.packageName}" should match packageName regex`).toMatch(re);
    }
  });

  it('every versionRange matches the valid regex', () => {
    const deps = getRequiredDependencies();
    const all = [...deps.dependencies, ...deps.devDependencies] as Array<{ versionRange: string }>;
    const re = /^[\^~>=<\d\|\s\.\-\*]+.*$/;
    for (const e of all) {
      expect(e.versionRange, `"${e.versionRange}" should match versionRange regex`).toMatch(re);
    }
  });

  it('no duplicate packageNames', () => {
    const deps = getRequiredDependencies();
    const all = [...deps.dependencies, ...deps.devDependencies] as Array<{ packageName: string }>;
    const names = all.map((e) => e.packageName);
    expect(new Set(names).size, 'all packageNames should be unique').toBe(names.length);
  });

  it('no dependency uses "latest" or bare "*" as version range', () => {
    const deps = getRequiredDependencies();
    const all = [...deps.dependencies, ...deps.devDependencies] as Array<{ versionRange: string }>;
    for (const e of all) {
      expect(e.versionRange).not.toBe('latest');
      expect(e.versionRange).not.toBe('*');
    }
  });

  it('is pure — two sequential calls return deeply equal results', () => {
    const a = getRequiredDependencies();
    const b = getRequiredDependencies();
    expect(a).toEqual(b);
  });
});

// ─────────────────────────────────────────────────────────────
// 3. generateScaffold
// ─────────────────────────────────────────────────────────────
describe('generateScaffold', () => {
  beforeEach(async () => {
    tmpDir = await makeTmpDir();
  });
  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('happy path: writes all 12 files and returns correct ScaffoldResult', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    const result = await generateScaffold({ outputDir, overwrite: false });

    expect(result.filesWritten, 'filesWritten should be 12').toBe(12);
    expect(result.hasJsFiles, 'hasJsFiles should be false').toBe(false);
    expect(result.hasPyFiles, 'hasPyFiles should be false').toBe(false);
    expect(result.manifest).toBeDefined();

    for (const fp of SCAFFOLD_FILE_PATHS) {
      const fullPath = path.join(outputDir, fp);
      const stat = await fs.stat(fullPath);
      expect(stat.isFile(), `${fp} should exist as a file`).toBe(true);
    }
  });

  it('overwrite=false with existing files throws file_already_exists', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    // First generation
    await generateScaffold({ outputDir, overwrite: true });
    // Second generation with overwrite=false
    await expect(
      generateScaffold({ outputDir, overwrite: false })
    ).rejects.toThrow(/file_already_exists|FILE_ALREADY_EXISTS|already exist/i);
  });

  it('overwrite=true succeeds even when files already exist', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: true });
    const result = await generateScaffold({ outputDir, overwrite: true });
    expect(result.filesWritten).toBe(12);
  });

  it('throws directory_not_found when parent directory does not exist', async () => {
    const outputDir = path.join(tmpDir, 'nonexistent', 'deep', 'project');
    await expect(
      generateScaffold({ outputDir, overwrite: false })
    ).rejects.toThrow(/directory_not_found|DIRECTORY_NOT_FOUND|not found|does not exist/i);
  });

  it('throws invalid_output_dir when outputDir is empty string', async () => {
    await expect(
      generateScaffold({ outputDir: '', overwrite: false })
    ).rejects.toThrow(/invalid_output_dir|INVALID_OUTPUT_DIR|invalid.*output/i);
  });

  it('throws invalid_output_dir when outputDir contains null bytes', async () => {
    await expect(
      generateScaffold({ outputDir: '/tmp/foo\0bar', overwrite: false })
    ).rejects.toThrow(/invalid_output_dir|INVALID_OUTPUT_DIR|invalid|null/i);
  });

  it('no .js files exist in output directory tree after generation', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const files = await listFiles(outputDir);
    const jsFiles = files.filter((f) => f.endsWith('.js'));
    expect(jsFiles, 'no .js files should exist').toEqual([]);
  });

  it('no .py files exist in output directory tree after generation', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const files = await listFiles(outputDir);
    const pyFiles = files.filter((f) => f.endsWith('.py'));
    expect(pyFiles, 'no .py files should exist').toEqual([]);
  });

  it('package.json has "type": "module"', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const pkg = JSON.parse(await fs.readFile(path.join(outputDir, 'package.json'), 'utf-8'));
    expect(pkg.type).toBe('module');
  });

  it('vite.config.ts configures server.port = 4000', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const content = await fs.readFile(path.join(outputDir, 'vite.config.ts'), 'utf-8');
    expect(content).toMatch(/4000/);
  });

  it('vitest.setup.ts contains import "@testing-library/jest-dom"', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const content = await fs.readFile(path.join(outputDir, 'vitest.setup.ts'), 'utf-8');
    expect(content).toMatch(/@testing-library\/jest-dom/);
  });

  it('vercel.json has exactly one rewrite with correct source and destination', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const vercel = JSON.parse(await fs.readFile(path.join(outputDir, 'vercel.json'), 'utf-8'));
    expect(vercel.rewrites).toHaveLength(1);
    expect(vercel.rewrites[0].source).toBe('/(.*)');
    expect(vercel.rewrites[0].destination).toBe('/index.html');
  });

  it('index.html has div#root and module script for main.tsx', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const html = await fs.readFile(path.join(outputDir, 'index.html'), 'utf-8');
    expect(html).toMatch(/<div id="root"><\/div>/);
    expect(html).toMatch(/<script type="module" src="\/src\/main\.tsx"><\/script>/);
  });

  it('src/main.tsx imports React, ReactDOM, App, and index.css', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const content = await fs.readFile(path.join(outputDir, 'src/main.tsx'), 'utf-8');
    expect(content, 'main.tsx should import React').toMatch(/import\s+React/);
    expect(content, 'main.tsx should import ReactDOM').toMatch(/ReactDOM|react-dom/);
    expect(content, 'main.tsx should import App').toMatch(/import.*App/);
    expect(content, 'main.tsx should import index.css').toMatch(/index\.css/);
  });

  it('src/index.css contains @tailwind base, components, utilities', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const content = await fs.readFile(path.join(outputDir, 'src/index.css'), 'utf-8');
    expect(content).toMatch(/@tailwind base/);
    expect(content).toMatch(/@tailwind components/);
    expect(content).toMatch(/@tailwind utilities/);
  });

  it('src/App.tsx has both named export and default export', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const content = await fs.readFile(path.join(outputDir, 'src/App.tsx'), 'utf-8');
    expect(content, 'App.tsx should have a named export').toMatch(/export\s+(function|const)\s+App/);
    expect(content, 'App.tsx should have a default export').toMatch(/export default/);
  });

  it('postcss.config.mjs uses ESM export default, not CommonJS module.exports', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const content = await fs.readFile(path.join(outputDir, 'postcss.config.mjs'), 'utf-8');
    expect(content).toMatch(/export default/);
    expect(content).not.toMatch(/module\.exports/);
  });

  it('postcss.config.mjs references tailwindcss and autoprefixer plugins', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const content = await fs.readFile(path.join(outputDir, 'postcss.config.mjs'), 'utf-8');
    expect(content).toMatch(/tailwindcss/);
    expect(content).toMatch(/autoprefixer/);
  });

  it('tailwind.config.ts content array includes ./index.html and ./src/**/*.{ts,tsx}', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const content = await fs.readFile(path.join(outputDir, 'tailwind.config.ts'), 'utf-8');
    expect(content).toMatch(/\.\/index\.html/);
    expect(content).toMatch(/\.\/src\/\*\*\/\*\.\{ts,tsx\}/);
  });
});

// ─────────────────────────────────────────────────────────────
// 4. validateScaffold
// ─────────────────────────────────────────────────────────────
describe('validateScaffold', () => {
  beforeEach(async () => {
    tmpDir = await makeTmpDir();
  });
  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('returns valid result after successful generateScaffold', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    const result = await validateScaffold(outputDir);
    expect(result.isValid, 'scaffold should validate as valid after generation').toBe(true);
  });

  it('throws directory_not_found for non-existent directory', async () => {
    const nonexistent = path.join(tmpDir, 'does-not-exist');
    await expect(
      validateScaffold(nonexistent)
    ).rejects.toThrow(/directory_not_found|DIRECTORY_NOT_FOUND|not found|does not exist/i);
  });

  it('reports invalid when a scaffold file is deleted', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });
    await generateScaffold({ outputDir, overwrite: false });
    // Delete one file
    await fs.unlink(path.join(outputDir, 'vercel.json'));
    const result = await validateScaffold(outputDir);
    expect(result.isValid, 'scaffold should be invalid when a file is missing').toBe(false);
  });

  it('reports invalid for an empty directory', async () => {
    const emptyDir = path.join(tmpDir, 'empty');
    await fs.mkdir(emptyDir, { recursive: true });
    const result = await validateScaffold(emptyDir);
    expect(result.isValid, 'empty directory should not validate').toBe(false);
  });
});

// ─────────────────────────────────────────────────────────────
// 5. Integration: scaffold round-trip
// ─────────────────────────────────────────────────────────────
describe('integration: scaffold round-trip', () => {
  beforeEach(async () => {
    tmpDir = await makeTmpDir();
  });
  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true, force: true });
  });

  it('generate → validate → inspect config files structurally', async () => {
    const outputDir = path.join(tmpDir, 'project');
    await fs.mkdir(outputDir, { recursive: true });

    // Generate
    const scaffoldResult = await generateScaffold({ outputDir, overwrite: false });
    expect(scaffoldResult.filesWritten).toBe(12);

    // Validate
    const validationResult = await validateScaffold(outputDir);
    expect(validationResult.isValid, 'round-trip validation should pass').toBe(true);

    // Structurally inspect vercel.json
    const vercel = JSON.parse(await fs.readFile(path.join(outputDir, 'vercel.json'), 'utf-8'));
    expect(vercel.rewrites).toHaveLength(1);
    expect(vercel.rewrites[0]).toEqual({ source: '/(.*)', destination: '/index.html' });

    // Structurally inspect package.json
    const pkg = JSON.parse(await fs.readFile(path.join(outputDir, 'package.json'), 'utf-8'));
    expect(pkg.type).toBe('module');

    // Verify all required deps are in package.json
    const requiredDeps = getRequiredDependencies();
    for (const dep of requiredDeps.dependencies as Array<{ packageName: string; versionRange: string }>) {
      expect(
        pkg.dependencies?.[dep.packageName],
        `package.json dependencies should include ${dep.packageName}`
      ).toBeDefined();
      expect(pkg.dependencies[dep.packageName]).toBe(dep.versionRange);
    }
    for (const dep of requiredDeps.devDependencies as Array<{ packageName: string; versionRange: string }>) {
      expect(
        pkg.devDependencies?.[dep.packageName],
        `package.json devDependencies should include ${dep.packageName}`
      ).toBeDefined();
      expect(pkg.devDependencies[dep.packageName]).toBe(dep.versionRange);
    }

    // Verify manifest consistency
    const manifest = getProjectManifest();
    expect(scaffoldResult.manifest.files).toEqual(expect.arrayContaining(manifest.files));
    expect(scaffoldResult.manifest.files).toHaveLength(12);
  });
});
