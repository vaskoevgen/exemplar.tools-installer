const PACT_KEY = "PACT:d97abb:project_scaffold";

import type { ReactElement } from 'react';

export type ReactElementNode = ReactElement;

export type ViteServerConfig = {
  port: 4000;
};

export type VitestConfig = {
  environment: 'jsdom';
  globals: true;
  setupFiles: './src/test-setup.ts';
};

export type TsCompilerOptions = {
  strict: true;
  jsx: 'react-jsx';
  moduleResolution: 'bundler';
  isolatedModules: true;
};

export type TailwindContentGlob = string;

export type VercelRewriteRule = {
  source: string;
  destination: string;
};

export type PackageDependencyMap = {
  react: string;
  react_dom: string;
  react_router_dom: string;
};

export type PackageDevDependencyMap = {
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
};
