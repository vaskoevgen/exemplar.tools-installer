const PACT_KEY = "PACT:d97abb:project_scaffold";

import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import { ScaffoldFilePath } from './types';
import type { ScaffoldOptions, ScaffoldResult, ProjectManifest } from './types';
import { DIRECTORY_NOT_FOUND, FILE_ALREADY_EXISTS, INVALID_OUTPUT_DIR } from './errors';
import { getProjectManifest } from './manifest';
import {
  generatePackageJson,
  generateTsconfigJson,
  generateTsconfigNodeJson,
  generateViteConfigTs,
  generateTailwindConfigTs,
  generatePostcssConfigMjs,
  generateVercelJson,
  generateIndexHtml,
  generateVitestSetupTs,
  generateMainTsx,
  generateIndexCss,
  generateAppTsx,
} from './file-contents';

const FILE_GENERATORS: Record<string, () => string> = {
  [ScaffoldFilePath.PACKAGE_JSON]: generatePackageJson,
  [ScaffoldFilePath.TSCONFIG_JSON]: generateTsconfigJson,
  [ScaffoldFilePath.TSCONFIG_NODE_JSON]: generateTsconfigNodeJson,
  [ScaffoldFilePath.VITE_CONFIG_TS]: generateViteConfigTs,
  [ScaffoldFilePath.TAILWIND_CONFIG_TS]: generateTailwindConfigTs,
  [ScaffoldFilePath.POSTCSS_CONFIG_MJS]: generatePostcssConfigMjs,
  [ScaffoldFilePath.VERCEL_JSON]: generateVercelJson,
  [ScaffoldFilePath.INDEX_HTML]: generateIndexHtml,
  [ScaffoldFilePath.VITEST_SETUP_TS]: generateVitestSetupTs,
  [ScaffoldFilePath.SRC_MAIN_TSX]: generateMainTsx,
  [ScaffoldFilePath.SRC_INDEX_CSS]: generateIndexCss,
  [ScaffoldFilePath.SRC_APP_TSX]: generateAppTsx,
};

export async function generateScaffold(options: ScaffoldOptions): Promise<ScaffoldResult> {
  console.log(`[${PACT_KEY}] generateScaffold started`, { outputDir: options.outputDir });

  const { outputDir, overwrite = false } = options;

  // Validate outputDir
  if (!outputDir || outputDir.length === 0) {
    throw new INVALID_OUTPUT_DIR(outputDir);
  }
  if (outputDir.includes('\0')) {
    throw new INVALID_OUTPUT_DIR(outputDir);
  }

  // Resolve and check parent directory exists
  const resolvedDir = path.resolve(outputDir);
  const parentDir = path.dirname(resolvedDir);

  try {
    const parentStat = await fs.stat(parentDir);
    if (!parentStat.isDirectory()) {
      throw new DIRECTORY_NOT_FOUND(resolvedDir);
    }
  } catch (err: unknown) {
    if (err instanceof DIRECTORY_NOT_FOUND) throw err;
    if (err instanceof INVALID_OUTPUT_DIR) throw err;
    throw new DIRECTORY_NOT_FOUND(resolvedDir);
  }

  // Ensure the output directory itself exists
  await fs.mkdir(resolvedDir, { recursive: true });

  // Get the manifest to know which files to generate
  const manifest = getProjectManifest();
  const filePaths = manifest.files;

  // Check for existing files if overwrite is false
  if (!overwrite) {
    const existingFiles: string[] = [];
    for (const fp of filePaths) {
      const fullPath = path.join(resolvedDir, fp);
      try {
        await fs.stat(fullPath);
        existingFiles.push(fp);
      } catch {
        // File does not exist, which is expected
      }
    }
    if (existingFiles.length > 0) {
      throw new FILE_ALREADY_EXISTS(existingFiles);
    }
  }

  // Ensure src/ subdirectory exists
  const srcDir = path.join(resolvedDir, 'src');
  await fs.mkdir(srcDir, { recursive: true });

  // Write all files
  let filesWritten = 0;
  for (const fp of filePaths) {
    const fullPath = path.join(resolvedDir, fp);
    const generator = FILE_GENERATORS[fp];
    if (!generator) {
      throw new Error(`No generator found for file: ${fp}`);
    }
    const content = generator();
    await fs.writeFile(fullPath, content, 'utf-8');
    filesWritten++;
  }

  const resultManifest: ProjectManifest = {
    ...manifest,
    projectRoot: resolvedDir,
  };

  const result: ScaffoldResult = {
    manifest: resultManifest,
    filesWritten,
    hasJsFiles: false,
    hasPyFiles: false,
  };

  console.log(`[${PACT_KEY}] generateScaffold completed`, { filesWritten });
  return result;
}
