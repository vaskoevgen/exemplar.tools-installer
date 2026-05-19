const PACT_KEY = "PACT:d97abb:project_scaffold";
console.debug(PACT_KEY, "module:config loaded");

export interface ViteServerConfig {
  port: number;
}

export interface VitestConfig {
  environment: string;
  globals: boolean;
  setupFiles: string;
}

export interface TsCompilerOptions {
  strict: boolean;
  jsx: string;
  moduleResolution: string;
  isolatedModules: boolean;
}

export interface VercelRewriteRule {
  source: string;
  destination: string;
}

export interface PackageDependencyMap {
  react: string;
  react_dom: string;
  react_router_dom: string;
}

export interface PackageDevDependencyMap {
  vite: string;
  vitest: string;
  tailwindcss: string;
  testing_library_react: string;
  jsdom: string;
  vitejs_plugin_react: string;
  typescript: string;
  autoprefixer: string;
  postcss: string;
  testing_library_jest_dom: string;
}
