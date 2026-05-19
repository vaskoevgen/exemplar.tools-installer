const PACT_KEY = "PACT:d97abb:project_scaffold";

import type { ProjectManifest, DependencyEntry, RequiredDependencies } from './types';
import { ScaffoldFilePath } from './types';

/**
 * Returns the canonical ProjectManifest for the exemplar-tools-doc project.
 * Pure function — always returns the same manifest regardless of filesystem state.
 */
export function getProjectManifest(): ProjectManifest {
  console.log(`[${PACT_KEY}] getProjectManifest: returning canonical manifest`);
  return {
    projectRoot: 'exemplar-tools-doc',
    files: Object.values(ScaffoldFilePath),
    projectName: 'exemplar-tools-doc',
    devServerPort: 4000,
  };
}

/**
 * Returns the complete list of pinned npm dependencies and devDependencies.
 * Pure function — deterministic output.
 */
export function getRequiredDependencies(): RequiredDependencies {
  console.log(`[${PACT_KEY}] getRequiredDependencies: returning pinned dependencies`);

  const dependencies: DependencyEntry[] = [
    { packageName: 'react', versionRange: '^18.3.0', isDev: false },
    { packageName: 'react-dom', versionRange: '^18.3.0', isDev: false },
    { packageName: 'react-router-dom', versionRange: '^6.23.0', isDev: false },
  ];

  const devDependencies: DependencyEntry[] = [
    { packageName: 'vite', versionRange: '^5.4.0', isDev: true },
    { packageName: '@vitejs/plugin-react', versionRange: '^4.3.0', isDev: true },
    { packageName: 'tailwindcss', versionRange: '^3.4.0', isDev: true },
    { packageName: 'vitest', versionRange: '^2.0.0', isDev: true },
    { packageName: '@testing-library/react', versionRange: '^16.0.0', isDev: true },
    { packageName: '@testing-library/jest-dom', versionRange: '^6.0.0', isDev: true },
    { packageName: 'jsdom', versionRange: '^24.0.0', isDev: true },
    { packageName: 'prism-react-renderer', versionRange: '^2.3.0', isDev: true },
    { packageName: 'autoprefixer', versionRange: '^10.4.0', isDev: true },
    { packageName: 'postcss', versionRange: '^8.4.0', isDev: true },
    { packageName: 'typescript', versionRange: '^5.5.0', isDev: true },
    { packageName: '@types/react', versionRange: '^18.3.0', isDev: true },
    { packageName: '@types/react-dom', versionRange: '^18.3.0', isDev: true },
  ];

  return { dependencies, devDependencies };
}
