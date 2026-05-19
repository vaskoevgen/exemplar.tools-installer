const PACT_KEY = "PACT:d97abb:project_scaffold";

import * as fs from 'node:fs/promises';
import * as path from 'node:path';

import type { ScaffoldValidationResult } from './types';
import { ScaffoldFilePath, DIRECTORY_NOT_FOUND } from './types';

/**
 * Recursively list all files relative to `dir`.
 */
async function listFilesRecursive(dir: string, base: string = dir): Promise<string[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const results: string[] = [];
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      results.push(...(await listFilesRecursive(full, base)));
    } else {
      results.push(path.relative(base, full));
    }
  }
  return results;
}

/**
 * Validates an existing project directory against the scaffold contract.
 */
export async function validateScaffold(projectRoot: string): Promise<ScaffoldValidationResult> {
  console.log(`[${PACT_KEY}] validateScaffold: start`, { projectRoot });

  if (!projectRoot || projectRoot.length === 0) {
    throw new DIRECTORY_NOT_FOUND(projectRoot);
  }

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

  const checks: Array<{ name: string; passed: boolean; message?: string }> = [];
  const allPaths = Object.values(ScaffoldFilePath);

  // Check all 12 files exist
  let allFilesExist = true;
  for (const relPath of allPaths) {
    const fullPath = path.join(resolvedRoot, relPath);
    try {
      const stat = await fs.stat(fullPath);
      if (stat.isFile()) {
        checks.push({ name: `file_exists:${relPath}`, passed: true });
      } else {
        checks.push({ name: `file_exists:${relPath}`, passed: false, message: `${relPath} is not a file` });
        allFilesExist = false;
      }
    } catch {
      checks.push({ name: `file_exists:${relPath}`, passed: false, message: `${relPath} does not exist` });
      allFilesExist = false;
    }
  }

  // If not all files exist, skip content checks
  if (!allFilesExist) {
    console.log(`[${PACT_KEY}] validateScaffold: invalid — missing files`);
    return { isValid: false, checks };
  }

  // Check package.json
  try {
    const pkgContent = await fs.readFile(path.join(resolvedRoot, 'package.json'), 'utf-8');
    const pkg = JSON.parse(pkgContent);
    const hasTypeModule = pkg.type === 'module';
    checks.push({
      name: 'package_json_type_module',
      passed: hasTypeModule,
      message: hasTypeModule ? undefined : 'package.json missing type: module',
    });
  } catch (err: unknown) {
    checks.push({ name: 'package_json_type_module', passed: false, message: 'Failed to read/parse package.json' });
  }

  // Check vite.config.ts for port 4000
  try {
    const viteContent = await fs.readFile(path.join(resolvedRoot, 'vite.config.ts'), 'utf-8');
    const hasPort = viteContent.includes('4000');
    checks.push({
      name: 'vite_port_4000',
      passed: hasPort,
      message: hasPort ? undefined : 'vite.config.ts does not configure port 4000',
    });
  } catch {
    checks.push({ name: 'vite_port_4000', passed: false, message: 'Failed to read vite.config.ts' });
  }

  // Check vitest.setup.ts for jest-dom import
  try {
    const setupContent = await fs.readFile(path.join(resolvedRoot, 'vitest.setup.ts'), 'utf-8');
    const hasJestDom = setupContent.includes('@testing-library/jest-dom');
    checks.push({
      name: 'vitest_setup_jest_dom',
      passed: hasJestDom,
      message: hasJestDom ? undefined : 'vitest.setup.ts missing jest-dom import',
    });
  } catch {
    checks.push({ name: 'vitest_setup_jest_dom', passed: false, message: 'Failed to read vitest.setup.ts' });
  }

  // Check vercel.json rewrites
  try {
    const vercelContent = await fs.readFile(path.join(resolvedRoot, 'vercel.json'), 'utf-8');
    const vercel = JSON.parse(vercelContent);
    const hasRewrite = Array.isArray(vercel.rewrites) &&
      vercel.rewrites.length === 1 &&
      vercel.rewrites[0].source === '/(.*)' &&
      vercel.rewrites[0].destination === '/index.html';
    checks.push({
      name: 'vercel_spa_rewrite',
      passed: hasRewrite,
      message: hasRewrite ? undefined : 'vercel.json missing correct SPA rewrite',
    });
  } catch {
    checks.push({ name: 'vercel_spa_rewrite', passed: false, message: 'Failed to read/parse vercel.json' });
  }

  // Check no .js or .py files
  try {
    const allFiles = await listFilesRecursive(resolvedRoot);
    const jsFiles = allFiles.filter((f) => f.endsWith('.js'));
    const pyFiles = allFiles.filter((f) => f.endsWith('.py'));
    checks.push({
      name: 'no_js_files',
      passed: jsFiles.length === 0,
      message: jsFiles.length === 0 ? undefined : `Found .js files: ${jsFiles.join(', ')}`,
    });
    checks.push({
      name: 'no_py_files',
      passed: pyFiles.length === 0,
      message: pyFiles.length === 0 ? undefined : `Found .py files: ${pyFiles.join(', ')}`,
    });
  } catch {
    checks.push({ name: 'no_js_files', passed: false, message: 'Failed to list files' });
    checks.push({ name: 'no_py_files', passed: false, message: 'Failed to list files' });
  }

  const isValid = checks.every((c) => c.passed);
  console.log(`[${PACT_KEY}] validateScaffold: complete`, { isValid });
  return { isValid, checks };
}
