// === Project Scaffold & Configuration (project_scaffold) v1 ===
// Initialize the exemplar-tools-doc/ project directory with all configuration files for a Vite + React + TypeScript documentation website. Produces exactly 12 deterministic files at known paths: package.json, tsconfig.json, tsconfig.node.json, vite.config.ts, tailwind.config.ts, postcss.config.mjs, vercel.json, index.html, vitest.setup.ts, src/main.tsx, src/index.css, src/App.tsx. PostCSS uses standalone postcss.config.mjs (ESM, no .js). Vitest configured inside vite.config.ts with jsdom environment, globals: true, setupFiles. Dev server port 4000. Path alias @/ → src/. All dependencies pinned to compatible ranges. No .py or .js source files emitted.

// Module invariants:
//   - Exactly 12 files are produced, no more, no fewer — paths enumerated in ScaffoldFilePath
//   - No file with a .js extension is ever produced (postcss uses .mjs, all others use .ts/.tsx)
//   - No file with a .py extension is ever produced
//   - package.json always has "type": "module"
//   - All dependency version ranges are pinned to the specified caret ranges and never use latest or *
//   - vite.config.ts server.port is always 4000
//   - vitest.setup.ts always contains the import '@testing-library/jest-dom' statement
//   - vercel.json always contains exactly one rewrite rule: { source: '/(.*)', destination: '/index.html' }
//   - src/main.tsx always imports React from 'react' as the first import
//   - src/App.tsx always has both a named export and a default export
//   - postcss.config.mjs is ESM (export default) not CommonJS (module.exports)
//   - getProjectManifest and getRequiredDependencies are pure functions with deterministic output

/** Literal string union of every file path produced by the scaffold, relative to project root. Downstream components depend on these exact paths. */
export type ScaffoldFilePath = "package.json" | "tsconfig.json" | "tsconfig.node.json" | "vite.config.ts" | "tailwind.config.ts" | "postcss.config.mjs" | "vercel.json" | "index.html" | "vitest.setup.ts" | "src/main.tsx" | "src/index.css" | "src/App.tsx";

/** Manifest enumerating all produced file paths and project metadata. Named export from the scaffold module, enabling downstream components to assert scaffold completeness. */
export interface ProjectManifest {
  projectRoot: string;  // required, Absolute path to the exemplar-tools-doc/ project directory.
  files: unknown[];  // required, length(length == 12), Ordered array of all 12 file paths (ScaffoldFilePath values) relative to projectRoot.
  projectName: string;  // required, regex(^[a-z][a-z0-9\-]*$), The npm package name: 'exemplar-tools-doc'.
  devServerPort: number;  // required, range(value == 4000), Vite dev server port, must be 4000.
}

/** A single npm dependency with its pinned semver range. */
export interface DependencyEntry {
  packageName: string;  // required, regex(^@?[a-z][a-z0-9\-]*(\/?[a-z][a-z0-9\-]*)*$), npm package name, e.g. 'react'.
  versionRange: string;  // required, regex(^[\^~>=<\d\|\s\.\-\*]+.*$), Semver range string, e.g. '^18.3'.
  isDev: boolean;  // required, True if this belongs in devDependencies, false for dependencies.
}

/** Complete set of pinned dependencies the scaffold must declare in package.json. */
export interface RequiredDependencies {
  dependencies: unknown[];  // required, Runtime dependencies: react@^18.3, react-dom@^18.3, react-router-dom@^6.23.
  devDependencies: unknown[];  // required, Dev dependencies: vite@^5.4, @vitejs/plugin-react@^4.3, tailwindcss@^3.4, vitest@^2.0, @testing-library/react@^16, @testing-library/jest-dom@^6, jsdom@^24, prism-react-renderer@^2.3, autoprefixer@^10.4, postcss@^8.4, typescript@^5.5, @types/react@^18.3, @types/react-dom@^18.3.
}

/** A single Vercel rewrite rule for SPA routing. */
export interface VercelRewriteRule {
  source: string;  // required, custom(value === '/(.*)'), Source path pattern.
  destination: string;  // required, custom(value === '/index.html'), Destination path.
}

/** Structure of vercel.json with SPA rewrite rules. */
export interface VercelConfig {
  rewrites: unknown[];  // required, length(length == 1), Array of VercelRewriteRule. Must contain exactly one rule for SPA routing.
}

/** Key properties that must be present in vite.config.ts. */
export interface ViteConfig {
  serverPort: number;  // required, range(value == 4000), Dev server port, must be 4000.
  testEnvironment: string;  // required, custom(value === 'jsdom'), Vitest environment, must be 'jsdom'.
  testGlobals: boolean;  // required, Vitest globals flag, must be true.
  testSetupFiles: unknown[];  // required, custom(value.includes('./vitest.setup.ts')), Vitest setupFiles array, must include './vitest.setup.ts'.
  resolveAlias: string;  // required, Path alias '@' mapped to './src' directory using import.meta.dirname.
  pluginReact: boolean;  // required, Must include @vitejs/plugin-react.
}

/** Result of scaffold generation, including manifest and validation status. */
export interface ScaffoldResult {
  manifest: ProjectManifest;  // required, The complete project manifest with all file paths.
  filesWritten: number;  // required, range(value == 12), Number of files successfully written. Must equal 12.
  hasJsFiles: boolean;  // required, custom(value === false), Must be false — no .js files in output.
  hasPyFiles: boolean;  // required, custom(value === false), Must be false — no .py files in output.
}

/** Options controlling scaffold generation behavior. */
export interface ScaffoldOptions {
  outputDir: string;  // required, length(length >= 1), Absolute or relative path to the target project directory (exemplar-tools-doc/).
  overwrite?: boolean;  // optional, default: false, If true, overwrite existing files. If false, fail if any target file already exists.
}

/** Discriminated error types for scaffold generation failures. */
export type ScaffoldError = "DIRECTORY_NOT_FOUND" | "FILE_ALREADY_EXISTS" | "WRITE_PERMISSION_DENIED" | "INVALID_OUTPUT_DIR";

/** Auto-stubbed type — referenced but not defined in contract 'project_scaffold' */
export interface ScaffoldValidationResult {
}

/**
 * Generate all 12 project configuration files at the specified output directory. Writes package.json, tsconfig.json, tsconfig.node.json, vite.config.ts, tailwind.config.ts, postcss.config.mjs, vercel.json, index.html, vitest.setup.ts, src/main.tsx, src/index.css, and src/App.tsx. Creates the src/ subdirectory if it does not exist. Returns a ScaffoldResult confirming all files were written and no forbidden file types exist.
 *
 * @precondition options.outputDir is a valid filesystem path
 * @precondition If options.overwrite is false, none of the 12 target files may already exist
 * @precondition Parent directory of options.outputDir must exist and be writable
 * @postcondition Exactly 12 files exist at the paths enumerated in ScaffoldFilePath
 * @postcondition package.json contains all entries from RequiredDependencies with pinned version ranges
 * @postcondition package.json has "type": "module"
 * @postcondition vite.config.ts configures server.port = 4000
 * @postcondition vite.config.ts configures test.environment = 'jsdom', test.globals = true, test.setupFiles = ['./vitest.setup.ts']
 * @postcondition vite.config.ts includes @vitejs/plugin-react plugin
 * @postcondition vite.config.ts configures resolve.alias '@' to src/ using import.meta.dirname
 * @postcondition vitest.setup.ts contains import '@testing-library/jest-dom'
 * @postcondition vercel.json contains exactly one rewrite: { source: '/(.*)', destination: '/index.html' }
 * @postcondition tailwind.config.ts content array includes './index.html' and './src/**/*.{ts,tsx}'
 * @postcondition postcss.config.mjs exports tailwindcss and autoprefixer plugins
 * @postcondition index.html has a <div id="root"></div> mount point and <script type="module" src="/src/main.tsx"></script>
 * @postcondition src/main.tsx imports React, ReactDOM, App, and index.css, renders <App /> into #root
 * @postcondition src/index.css contains @tailwind base, @tailwind components, @tailwind utilities directives
 * @postcondition src/App.tsx exports both named and default export per operating procedures
 * @postcondition No files with .js or .py extensions exist in the output directory tree
 * @postcondition result.filesWritten === 12
 * @postcondition result.hasJsFiles === false
 * @postcondition result.hasPyFiles === false
 * @throws directory_not_found (DIRECTORY_NOT_FOUND) - The parent directory of options.outputDir does not exist on the filesystem.
 *   path: The resolved outputDir path that was not found
 * @throws file_already_exists (FILE_ALREADY_EXISTS) - options.overwrite is false and at least one of the 12 target files already exists.
 *   existingFiles: JSON array of file paths that already exist
 * @throws write_permission_denied (WRITE_PERMISSION_DENIED) - The process does not have write permissions to the output directory or src/ subdirectory.
 *   path: The path where permission was denied
 * @throws invalid_output_dir (INVALID_OUTPUT_DIR) - options.outputDir is empty, contains null bytes, or is otherwise not a valid filesystem path.
 *   outputDir: The invalid outputDir value provided
 * @sideEffects none
 * @idempotent no
 */
export async function generateScaffold(
  options: ScaffoldOptions,
): Promise<ScaffoldResult>;

/**
 * Returns the canonical ProjectManifest for the exemplar-tools-doc project. Pure function that always returns the same manifest regardless of filesystem state. Used by downstream components to discover expected file paths without performing I/O.
 *
 * @postcondition Returned manifest.files has exactly 12 entries matching all ScaffoldFilePath variants
 * @postcondition Returned manifest.projectName === 'exemplar-tools-doc'
 * @postcondition Returned manifest.devServerPort === 4000
 * @sideEffects none
 * @idempotent yes
 */
export function getProjectManifest(): ProjectManifest;

/**
 * Returns the complete list of pinned npm dependencies and devDependencies that package.json must declare. Pure function enabling downstream validation without filesystem access.
 *
 * @postcondition dependencies contains exactly 3 entries: react@^18.3, react-dom@^18.3, react-router-dom@^6.23
 * @postcondition devDependencies contains exactly 13 entries with pinned ranges: vite@^5.4, @vitejs/plugin-react@^4.3, tailwindcss@^3.4, vitest@^2.0, @testing-library/react@^16, @testing-library/jest-dom@^6, jsdom@^24, prism-react-renderer@^2.3, autoprefixer@^10.4, postcss@^8.4, typescript@^5.5, @types/react@^18.3, @types/react-dom@^18.3
 * @sideEffects none
 * @idempotent yes
 */
export function getRequiredDependencies(): RequiredDependencies;

/**
 * Validates an existing project directory against the scaffold contract. Checks that all 12 files exist, package.json contains all required dependencies, vite.config.ts has correct port and vitest settings, vitest.setup.ts imports jest-dom, vercel.json has the SPA rewrite, and no .js or .py files exist anywhere in the output tree.
 *
 * @precondition projectRoot exists and is a readable directory
 * @postcondition Result enumerates all validation checks with pass/fail status
 * @postcondition Result.isValid is true only if all checks pass
 * @throws directory_not_found (DIRECTORY_NOT_FOUND) - projectRoot does not exist or is not a directory.
 *   path: The projectRoot path that was not found
 * @sideEffects none
 * @idempotent yes
 */
export async function validateScaffold(
  projectRoot: string,  // length(length >= 1)
): Promise<ScaffoldValidationResult>;

// -- REQUIRED EXPORTS -----------------------------------------------
// Your implementation module MUST export ALL of these names
// with EXACTLY these spellings. Tests import them by name.
// exports: ['ScaffoldFilePath', 'ProjectManifest', 'DependencyEntry', 'RequiredDependencies', 'VercelRewriteRule', 'VercelConfig', 'ViteConfig', 'ScaffoldResult', 'ScaffoldOptions', 'ScaffoldError', 'ScaffoldValidationResult', 'generateScaffold', 'DIRECTORY_NOT_FOUND', 'FILE_ALREADY_EXISTS', 'WRITE_PERMISSION_DENIED', 'INVALID_OUTPUT_DIR', 'getProjectManifest', 'getRequiredDependencies', 'validateScaffold']
