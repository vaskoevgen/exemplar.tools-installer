const PACT_KEY = "PACT:d97abb:project_scaffold";

export { App } from './App';
export { mountApp } from './mountApp';
export type {
  ViteServerConfig,
  VitestConfig,
  TsCompilerOptions,
  VercelRewriteRule,
  PackageDependencyMap,
  PackageDevDependencyMap,
} from './types';
export { ModuleNotFoundError, DOMException, ImportError } from './errors';
