// === Project Scaffold & Configuration (project_scaffold) v1 ===
// Bootstraps the exemplar-tools-doc project: package.json with all dependencies (react, react-dom, react-router-dom, vite, tailwindcss, vitest, @testing-library/react, jsdom), vite.config.ts (port 4000), tsconfig.json (strict mode), tailwind.config.js, postcss.config.js, index.html entry point, vercel.json with SPA rewrites, and the main App.tsx shell that sets up BrowserRouter. All config files only — no page content. Named exports only per SOP for application source files. Config files are tool-mandated and exempt from the named-export SOP.

// Module invariants:
//   - All application source files (.ts, .tsx) use TypeScript strict mode as enforced by tsconfig.json strict: true.
//   - All application source files use named exports only — no default exports. Config files (package.json, vite.config.ts, tailwind.config.js, postcss.config.js, vercel.json) are exempt from this rule as they are tool-mandated.
//   - Vite dev server always listens on port 4000.
//   - Vitest uses jsdom environment with globals enabled and setupFiles pointing to src/test-setup.ts.
//   - tsconfig.json uses jsx: 'react-jsx', moduleResolution: 'bundler', and isolatedModules: true.
//   - tailwind.config.js content array includes './index.html' and './src/**/*.{ts,tsx}'.
//   - postcss.config.js includes tailwindcss and autoprefixer plugins.
//   - index.html contains <div id='root'></div> and <script type='module' src='/src/main.tsx'></script>.
//   - vercel.json contains a single rewrite rule: { source: '/(.*)', destination: '/index.html' } for SPA client-side routing.
//   - src/index.css contains exactly: @tailwind base; @tailwind components; @tailwind utilities;
//   - src/test-setup.ts imports '@testing-library/jest-dom' to register custom DOM matchers globally.
//   - package.json lists react, react-dom, and react-router-dom as runtime dependencies (caret-pinned to their major versions).
//   - package.json lists vite, vitest, tailwindcss, @testing-library/react, @testing-library/jest-dom, jsdom, @vitejs/plugin-react, typescript, autoprefixer, and postcss as devDependencies (all caret-pinned).
//   - The App component renders a BrowserRouter at its root with a child div having id='app-shell'.
//   - No page content, route definitions, or layout components are defined by this scaffold — those are the responsibility of downstream components.

/** Opaque React.ReactElement returned by function components. Represents a rendered React virtual DOM tree. */
export type ReactElementNode = unknown;

/** Shape of the Vite dev server configuration block in vite.config.ts. */
export interface ViteServerConfig {
  port: number;  // required, range(value == 4000), Dev server listen port. Must be 4000 per SOP.
}

/** Shape of the vitest test configuration block embedded in vite.config.ts. */
export interface VitestConfig {
  environment: string;  // required, custom(value === 'jsdom'), Test environment. Must be 'jsdom' for React component testing.
  globals: boolean;  // required, custom(value === true), When true, vitest globals (describe, it, expect) are available without imports.
  setupFiles: string;  // required, custom(value === './src/test-setup.ts'), Path to the test setup file that imports @testing-library/jest-dom.
}

/** Key tsconfig.json compilerOptions that the scaffold guarantees. */
export interface TsCompilerOptions {
  strict: boolean;  // required, custom(value === true), TypeScript strict mode flag.
  jsx: string;  // required, custom(value === 'react-jsx'), JSX transform mode.
  moduleResolution: string;  // required, custom(value === 'bundler'), Module resolution strategy.
  isolatedModules: boolean;  // required, custom(value === true), Ensures each file can be transpiled independently.
}

/** A glob pattern string used in tailwind.config.js content array to specify which files to scan for class usage. */
export type TailwindContentGlob = unknown;

/** A single Vercel rewrite rule for SPA client-side routing support. */
export interface VercelRewriteRule {
  source: string;  // required, custom(value === '/(.*)'), URL pattern to match. For SPA catch-all this is '/(.*)'.
  destination: string;  // required, custom(value === '/index.html'), Target to rewrite to. For SPA this is '/index.html'.
}

/** Required npm dependencies with caret-pinned semver versions. */
export interface PackageDependencyMap {
  react: string;  // required, regex(^\^18\.), React 18.x runtime.
  react_dom: string;  // required, regex(^\^18\.), React DOM 18.x renderer.
  react_router_dom: string;  // required, regex(^\^), React Router DOM for client-side routing.
}

/** Required npm devDependencies with caret-pinned semver versions. */
export interface PackageDevDependencyMap {
  vite: string;  // required, regex(^\^), Vite build tool.
  vitest: string;  // required, regex(^\^), Vitest test runner.
  tailwindcss: string;  // required, regex(^\^), Tailwind CSS utility framework.
  testing_library_react: string;  // required, regex(^\^), @testing-library/react for component tests.
  jsdom: string;  // required, regex(^\^), jsdom environment for vitest.
  vitejs_plugin_react: string;  // required, regex(^\^), @vitejs/plugin-react for JSX/Fast Refresh support.
  typescript: string;  // required, regex(^\^), TypeScript compiler.
  autoprefixer: string;  // required, regex(^\^), PostCSS autoprefixer plugin.
  postcss: string;  // required, regex(^\^), PostCSS processor.
  testing_library_jest_dom: string;  // required, regex(^\^), @testing-library/jest-dom for custom DOM matchers.
}

/**
 * Root React function component. Renders a BrowserRouter wrapping a container div with id='app-shell'. Children and routes are injected by the downstream routing_and_layout component. Exported as a named export from src/App.tsx. Must NOT be a default export.
 *
 * @precondition React 18 runtime is available in the module scope.
 * @precondition react-router-dom BrowserRouter is importable.
 * @postcondition Returns a React element tree with BrowserRouter at the root.
 * @postcondition The rendered DOM contains a div with id='app-shell' inside the BrowserRouter.
 * @postcondition The component is available as a named export: `import { App } from './App'`.
 * @postcondition No default export exists on the module.
 * @throws missing_react_router (ModuleNotFoundError) - react-router-dom is not installed or importable.
 *   module: react-router-dom
 * @sideEffects none
 * @idempotent yes
 */
export function App(): ReactElementNode;

/**
 * Side-effect entry point in src/main.tsx. Imports { App } from './App', imports './index.css' for Tailwind styles, calls createRoot on the DOM element with id='root', and renders <App />. This module has no named exports — it executes on import as the Vite entry point referenced by index.html.
 *
 * @precondition DOM element with id='root' exists in index.html.
 * @precondition react-dom/client createRoot is importable.
 * @precondition src/App.tsx exports { App } as a named export.
 * @precondition src/index.css contains valid Tailwind @tailwind directives.
 * @postcondition React application is mounted into the #root DOM element.
 * @postcondition Tailwind base/components/utilities styles are injected into the document.
 * @postcondition No named exports exist on this module — it is a side-effect-only entry point.
 * @throws missing_root_element (DOMException) - No DOM element with id='root' found in the document.
 *   selector: #root
 * @throws app_import_failure (ImportError) - Named export { App } not found in ./App module.
 *   module: ./App
 *   export: App
 * @sideEffects Mounts React tree to DOM #root element, Imports CSS side-effect module
 * @idempotent no
 */
export function mountApp(): null;

// -- REQUIRED EXPORTS -----------------------------------------------
// Your implementation module MUST export ALL of these names
// with EXACTLY these spellings. Tests import them by name.
// exports: ['ViteServerConfig', 'VitestConfig', 'TsCompilerOptions', 'VercelRewriteRule', 'PackageDependencyMap', 'PackageDevDependencyMap', 'App', 'ModuleNotFoundError', 'mountApp', 'DOMException', 'ImportError']
