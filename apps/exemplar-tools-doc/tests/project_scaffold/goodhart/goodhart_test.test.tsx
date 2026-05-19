import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';
import {
  generateScaffold,
  getProjectManifest,
  getRequiredDependencies,
  validateScaffold,
} from '../../../src/project_scaffold';

function makeTempDir(suffix: string): string {
  return fs.mkdtempSync(path.join(os.tmpdir(), `goodhart-${suffix}-`));
}

function cleanDir(dir: string) {
  try {
    fs.rmSync(dir, { recursive: true, force: true });
  } catch {
    // ignore
  }
}

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

describe('goodhart: getProjectManifest', () => {
  it('goodhart: should contain every specific ScaffoldFilePath variant as an exact string in the files array', () => {
    const manifest = getProjectManifest();
    for (const fp of SCAFFOLD_FILE_PATHS) {
      expect(manifest.files).toContain(fp);
    }
  });

  it('goodhart: should not contain any file paths outside the ScaffoldFilePath enum', () => {
    const manifest = getProjectManifest();
    const allowed = new Set<string>(SCAFFOLD_FILE_PATHS);
    for (const f of manifest.files) {
      expect(allowed.has(f)).toBe(true);
    }
  });

  it('goodhart: should have a non-empty projectRoot string', () => {
    const manifest = getProjectManifest();
    expect(typeof manifest.projectRoot).toBe('string');
    expect(manifest.projectRoot.length).toBeGreaterThan(0);
  });

  it('goodhart: should return independent objects so mutations do not affect future calls', () => {
    const m1 = getProjectManifest();
    // mutate the returned object
    (m1 as any).projectName = 'hacked';
    (m1 as any).files.push('evil.js');
    (m1 as any).devServerPort = 9999;

    const m2 = getProjectManifest();
    expect(m2.projectName).toBe('exemplar-tools-doc');
    expect(m2.files).toHaveLength(12);
    expect(m2.devServerPort).toBe(4000);
  });
});

describe('goodhart: getRequiredDependencies', () => {
  it('goodhart: should pin each dependency to its exact specified caret range', () => {
    const deps = getRequiredDependencies();
    const allEntries = [...deps.dependencies, ...deps.devDependencies];
    const lookup = new Map(allEntries.map((e: any) => [e.packageName, e.versionRange]));

    // Production deps
    expect(lookup.get('react')).toMatch(/^\^18\.3/);
    expect(lookup.get('react-dom')).toMatch(/^\^18\.3/);
    expect(lookup.get('react-router-dom')).toMatch(/^\^6\.23/);

    // Dev deps — check every one
    expect(lookup.get('vite')).toMatch(/^\^5\.4/);
    expect(lookup.get('@vitejs/plugin-react')).toMatch(/^\^4\.3/);
    expect(lookup.get('tailwindcss')).toMatch(/^\^3\.4/);
    expect(lookup.get('vitest')).toMatch(/^\^2\.0/);
    expect(lookup.get('@testing-library/react')).toMatch(/^\^16/);
    expect(lookup.get('@testing-library/jest-dom')).toMatch(/^\^6/);
    expect(lookup.get('jsdom')).toMatch(/^\^24/);
    expect(lookup.get('prism-react-renderer')).toMatch(/^\^2\.3/);
    expect(lookup.get('autoprefixer')).toMatch(/^\^10\.4/);
    expect(lookup.get('postcss')).toMatch(/^\^8\.4/);
    expect(lookup.get('typescript')).toMatch(/^\^5\.5/);
    expect(lookup.get('@types/react')).toMatch(/^\^18\.3/);
    expect(lookup.get('@types/react-dom')).toMatch(/^\^18\.3/);
  });

  it('goodhart: should contain only the 3 specified packages in dependencies — no extras', () => {
    const deps = getRequiredDependencies();
    const names = deps.dependencies.map((d: any) => d.packageName).sort();
    expect(names).toEqual(['react', 'react-dom', 'react-router-dom'].sort());
  });

  it('goodhart: should contain only the 13 specified packages in devDependencies — no extras', () => {
    const deps = getRequiredDependencies();
    const names = new Set(deps.devDependencies.map((d: any) => d.packageName));
    const expected = new Set([
      'vite', '@vitejs/plugin-react', 'tailwindcss', 'vitest',
      '@testing-library/react', '@testing-library/jest-dom', 'jsdom',
      'prism-react-renderer', 'autoprefixer', 'postcss', 'typescript',
      '@types/react', '@types/react-dom',
    ]);
    expect(names).toEqual(expected);
  });

  it('goodhart: should return independent objects so mutations do not affect future calls', () => {
    const d1 = getRequiredDependencies();
    d1.dependencies.push({ packageName: 'evil', versionRange: '^1.0', isDev: false } as any);
    d1.devDependencies.length = 0;

    const d2 = getRequiredDependencies();
    expect(d2.dependencies).toHaveLength(3);
    expect(d2.devDependencies).toHaveLength(13);
  });
});

describe('goodhart: generateScaffold file contents', () => {
  let outputDir: string;

  beforeEach(() => {
    outputDir = makeTempDir('scaffold');
  });

  afterEach(() => {
    cleanDir(outputDir);
  });

  it('goodhart: should create the src/ subdirectory within the output directory', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const srcDir = path.join(outputDir, 'src');
    expect(fs.existsSync(srcDir)).toBe(true);
    expect(fs.statSync(srcDir).isDirectory()).toBe(true);
  });

  it('goodhart: should write all 12 files with non-empty content — no zero-byte placeholders', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    for (const fp of SCAFFOLD_FILE_PATHS) {
      const fullPath = path.join(outputDir, fp);
      expect(fs.existsSync(fullPath)).toBe(true);
      const content = fs.readFileSync(fullPath, 'utf-8');
      expect(content.trim().length).toBeGreaterThan(0);
    }
  });

  it('goodhart: should produce a valid parseable package.json with dependencies and devDependencies objects', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const raw = fs.readFileSync(path.join(outputDir, 'package.json'), 'utf-8');
    const pkg = JSON.parse(raw);
    expect(typeof pkg).toBe('object');
    expect(pkg).toHaveProperty('dependencies');
    expect(pkg).toHaveProperty('devDependencies');
    expect(typeof pkg.dependencies).toBe('object');
    expect(typeof pkg.devDependencies).toBe('object');
  });

  it('goodhart: should include all required dependency version ranges in the generated package.json', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const raw = fs.readFileSync(path.join(outputDir, 'package.json'), 'utf-8');
    const pkg = JSON.parse(raw);

    // Check all production deps
    expect(pkg.dependencies['react']).toMatch(/^\^18\.3/);
    expect(pkg.dependencies['react-dom']).toMatch(/^\^18\.3/);
    expect(pkg.dependencies['react-router-dom']).toMatch(/^\^6\.23/);

    // Check all dev deps
    expect(pkg.devDependencies['vite']).toMatch(/^\^5\.4/);
    expect(pkg.devDependencies['@vitejs/plugin-react']).toMatch(/^\^4\.3/);
    expect(pkg.devDependencies['tailwindcss']).toMatch(/^\^3\.4/);
    expect(pkg.devDependencies['vitest']).toMatch(/^\^2\.0/);
    expect(pkg.devDependencies['@testing-library/react']).toMatch(/^\^16/);
    expect(pkg.devDependencies['@testing-library/jest-dom']).toMatch(/^\^6/);
    expect(pkg.devDependencies['jsdom']).toMatch(/^\^24/);
    expect(pkg.devDependencies['prism-react-renderer']).toMatch(/^\^2\.3/);
    expect(pkg.devDependencies['autoprefixer']).toMatch(/^\^10\.4/);
    expect(pkg.devDependencies['postcss']).toMatch(/^\^8\.4/);
    expect(pkg.devDependencies['typescript']).toMatch(/^\^5\.5/);
    expect(pkg.devDependencies['@types/react']).toMatch(/^\^18\.3/);
    expect(pkg.devDependencies['@types/react-dom']).toMatch(/^\^18\.3/);
  });

  it('goodhart: should produce a package.json with name matching the project manifest name', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const raw = fs.readFileSync(path.join(outputDir, 'package.json'), 'utf-8');
    const pkg = JSON.parse(raw);
    expect(pkg.name).toBe('exemplar-tools-doc');
  });

  it('goodhart: should produce a valid parseable vercel.json with correct structural shape', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const raw = fs.readFileSync(path.join(outputDir, 'vercel.json'), 'utf-8');
    const vercel = JSON.parse(raw);
    expect(vercel).toHaveProperty('rewrites');
    expect(Array.isArray(vercel.rewrites)).toBe(true);
    expect(vercel.rewrites).toHaveLength(1);
    expect(vercel.rewrites[0].source).toBe('/(.*)');
    expect(vercel.rewrites[0].destination).toBe('/index.html');
  });

  it('goodhart: should configure test.globals = true in vite.config.ts', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const content = fs.readFileSync(path.join(outputDir, 'vite.config.ts'), 'utf-8');
    // Must contain globals: true (with flexible whitespace)
    expect(content).toMatch(/globals\s*:\s*true/);
  });

  it('goodhart: should configure test.setupFiles referencing vitest.setup.ts in vite.config.ts', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const content = fs.readFileSync(path.join(outputDir, 'vite.config.ts'), 'utf-8');
    expect(content).toMatch(/setupFiles/);
    expect(content).toMatch(/vitest\.setup\.ts/);
  });

  it('goodhart: should configure resolve.alias with @ mapped to src using import.meta.dirname', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const content = fs.readFileSync(path.join(outputDir, 'vite.config.ts'), 'utf-8');
    expect(content).toMatch(/@/);
    expect(content).toMatch(/resolve/);
    expect(content).toMatch(/alias/);
    expect(content).toMatch(/import\.meta\.dirname/);
  });

  it('goodhart: should import and use @vitejs/plugin-react in vite.config.ts', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const content = fs.readFileSync(path.join(outputDir, 'vite.config.ts'), 'utf-8');
    expect(content).toMatch(/@vitejs\/plugin-react/);
    expect(content).toMatch(/plugins/);
    // The react plugin should be invoked: react()
    expect(content).toMatch(/react\s*\(/);
  });

  it('goodhart: should configure test.environment specifically as jsdom, not happy-dom', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const content = fs.readFileSync(path.join(outputDir, 'vite.config.ts'), 'utf-8');
    expect(content).toMatch(/environment\s*:\s*['"]jsdom['"]/);
    expect(content).not.toMatch(/happy-dom/);
  });

  it('goodhart: should export both tailwindcss and autoprefixer plugins from postcss.config.mjs', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const content = fs.readFileSync(path.join(outputDir, 'postcss.config.mjs'), 'utf-8');
    expect(content).toMatch(/tailwindcss/);
    expect(content).toMatch(/autoprefixer/);
  });

  it('goodhart: should render App into #root in src/main.tsx using createRoot', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const content = fs.readFileSync(path.join(outputDir, 'src', 'main.tsx'), 'utf-8');
    expect(content).toMatch(/getElementById\s*\(\s*['"]root['"]\s*\)/);
    expect(content).toMatch(/createRoot/);
    expect(content).toMatch(/<App\s*\/?>/);
  });

  it('goodhart: should have React from react as the first import in src/main.tsx', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const content = fs.readFileSync(path.join(outputDir, 'src', 'main.tsx'), 'utf-8');
    const lines = content.split('\n').filter(l => l.trim().length > 0);
    const firstImportLine = lines.find(l => l.trim().startsWith('import'));
    expect(firstImportLine).toBeDefined();
    expect(firstImportLine).toMatch(/import\s+React\s+from\s+['"]react['"]/);
  });

  it('goodhart: should have a named export called App specifically in src/App.tsx', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const content = fs.readFileSync(path.join(outputDir, 'src', 'App.tsx'), 'utf-8');
    // Must have "export function App" or "export const App"
    expect(content).toMatch(/export\s+(function|const)\s+App\b/);
    // Must also have a default export
    expect(content).toMatch(/export\s+default\b/);
  });

  it('goodhart: should produce valid parseable tsconfig.json with compilerOptions', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const raw = fs.readFileSync(path.join(outputDir, 'tsconfig.json'), 'utf-8');
    const parsed = JSON.parse(raw);
    expect(parsed).toHaveProperty('compilerOptions');
  });

  it('goodhart: should produce valid parseable tsconfig.node.json with compilerOptions', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const raw = fs.readFileSync(path.join(outputDir, 'tsconfig.node.json'), 'utf-8');
    const parsed = JSON.parse(raw);
    expect(parsed).toHaveProperty('compilerOptions');
  });

  it('goodhart: should produce a proper HTML document in index.html, not just tag fragments', async () => {
    await generateScaffold({ outputDir, overwrite: false });
    const content = fs.readFileSync(path.join(outputDir, 'index.html'), 'utf-8');
    expect(content).toMatch(/<!DOCTYPE\s+html>/i);
    expect(content).toMatch(/<html/i);
    expect(content).toMatch(/<head/i);
    expect(content).toMatch(/<body/i);
  });

  it('goodhart: should return a ScaffoldResult with manifest matching canonical values', async () => {
    const result = await generateScaffold({ outputDir, overwrite: false });
    expect(result.manifest.files).toHaveLength(12);
    expect(result.manifest.projectName).toBe('exemplar-tools-doc');
    expect(result.manifest.devServerPort).toBe(4000);
    expect(result.filesWritten).toBe(12);
    expect(result.hasJsFiles).toBe(false);
    expect(result.hasPyFiles).toBe(false);
  });
});

describe('goodhart: generateScaffold with different output directories', () => {
  it('goodhart: should work with an arbitrary temp directory path, not just a hardcoded one', async () => {
    const dir1 = makeTempDir('alt-a');
    const dir2 = makeTempDir('alt-b');
    try {
      const r1 = await generateScaffold({ outputDir: dir1, overwrite: false });
      const r2 = await generateScaffold({ outputDir: dir2, overwrite: false });
      expect(r1.filesWritten).toBe(12);
      expect(r2.filesWritten).toBe(12);
      // Both should have all files
      for (const fp of SCAFFOLD_FILE_PATHS) {
        expect(fs.existsSync(path.join(dir1, fp))).toBe(true);
        expect(fs.existsSync(path.join(dir2, fp))).toBe(true);
      }
    } finally {
      cleanDir(dir1);
      cleanDir(dir2);
    }
  });

  it('goodhart: should actually replace file content when overwrite=true, not skip existing files', async () => {
    const dir = makeTempDir('overwrite');
    try {
      // Write a garbage package.json first
      fs.writeFileSync(path.join(dir, 'package.json'), '{"garbage": true}');
      await generateScaffold({ outputDir: dir, overwrite: true });
      const raw = fs.readFileSync(path.join(dir, 'package.json'), 'utf-8');
      const pkg = JSON.parse(raw);
      // Should have the real content, not garbage
      expect(pkg).toHaveProperty('type', 'module');
      expect(pkg).toHaveProperty('dependencies');
      expect(pkg.dependencies).toHaveProperty('react');
      expect(pkg).not.toHaveProperty('garbage');
    } finally {
      cleanDir(dir);
    }
  });
});

describe('goodhart: generateScaffold error handling', () => {
  it('goodhart: should reject whitespace-only outputDir as invalid', async () => {
    await expect(
      generateScaffold({ outputDir: '   ', overwrite: false })
    ).rejects.toThrow(/invalid.output.dir/i);
  });
});

describe('goodhart: validateScaffold edge cases', () => {
  let outputDir: string;

  beforeEach(() => {
    outputDir = makeTempDir('validate');
  });

  afterEach(() => {
    cleanDir(outputDir);
  });

  it('goodhart: should detect invalid scaffold when package.json has missing dependencies', async () => {
    // Generate a valid scaffold first, then corrupt package.json
    await generateScaffold({ outputDir, overwrite: false });
    // Overwrite package.json with minimal invalid content
    fs.writeFileSync(
      path.join(outputDir, 'package.json'),
      JSON.stringify({ type: 'module', dependencies: {}, devDependencies: {} })
    );
    const result = await validateScaffold(outputDir);
    expect(result.isValid).toBe(false);
  });
});
