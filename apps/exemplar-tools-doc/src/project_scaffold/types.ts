const PACT_KEY = "PACT:d97abb:project_scaffold";

export const ScaffoldFilePath = {
  'package.json': 'package.json',
  'tsconfig.json': 'tsconfig.json',
  'tsconfig.node.json': 'tsconfig.node.json',
  'vite.config.ts': 'vite.config.ts',
  'tailwind.config.ts': 'tailwind.config.ts',
  'postcss.config.mjs': 'postcss.config.mjs',
  'vercel.json': 'vercel.json',
  'index.html': 'index.html',
  'vitest.setup.ts': 'vitest.setup.ts',
  'src/main.tsx': 'src/main.tsx',
  'src/index.css': 'src/index.css',
  'src/App.tsx': 'src/App.tsx',
} as const;

export type ScaffoldFilePathValue = (typeof ScaffoldFilePath)[keyof typeof ScaffoldFilePath];

export interface ProjectManifest {
  projectRoot: string;
  files: string[];
  projectName: string;
  devServerPort: number;
}

export interface DependencyEntry {
  packageName: string;
  versionRange: string;
  isDev: boolean;
}

export interface RequiredDependencies {
  dependencies: DependencyEntry[];
  devDependencies: DependencyEntry[];
}

export interface VercelRewriteRule {
  source: string;
  destination: string;
}

export interface VercelConfig {
  rewrites: VercelRewriteRule[];
}

export interface ViteConfig {
  serverPort: number;
  testEnvironment: string;
  testGlobals: boolean;
  testSetupFiles: string[];
  resolveAlias: string;
  pluginReact: boolean;
}

export interface ScaffoldResult {
  manifest: ProjectManifest;
  filesWritten: number;
  hasJsFiles: boolean;
  hasPyFiles: boolean;
}

export interface ScaffoldOptions {
  outputDir: string;
  overwrite?: boolean;
}

export interface ScaffoldValidationResult {
  isValid: boolean;
  checks: Array<{ check: string; passed: boolean; message?: string }>;
}
