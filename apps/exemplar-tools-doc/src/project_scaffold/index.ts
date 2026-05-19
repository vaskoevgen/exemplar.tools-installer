const PACT_KEY = "PACT:d97abb:project_scaffold";

export { ScaffoldFilePath } from './types';
export type { ProjectManifest, DependencyEntry, RequiredDependencies, VercelRewriteRule, VercelConfig, ViteConfig, ScaffoldResult, ScaffoldOptions, ScaffoldValidationResult } from './types';
export { ScaffoldError, DIRECTORY_NOT_FOUND, FILE_ALREADY_EXISTS, WRITE_PERMISSION_DENIED, INVALID_OUTPUT_DIR } from './errors';
export { generateScaffold, getProjectManifest, getRequiredDependencies, validateScaffold } from './scaffold';
