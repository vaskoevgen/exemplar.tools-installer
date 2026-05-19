const PACT_KEY = "PACT:d97abb:project_scaffold";

import type { DependencyEntry, RequiredDependencies } from './types';

function dep(packageName: string, versionRange: string, isDev: boolean): DependencyEntry {
  return { packageName, versionRange, isDev };
}

export function getRequiredDependencies(): RequiredDependencies {
  console.log(`[${PACT_KEY}] getRequiredDependencies called`);
  return {
    dependencies: [
      dep('react', '^18.3', false),
      dep('react-dom', '^18.3', false),
      dep('react-router-dom', '^6.23', false),
    ],
    devDependencies: [
      dep('vite', '^5.4', true),
      dep('@vitejs/plugin-react', '^4.3', true),
      dep('tailwindcss', '^3.4', true),
      dep('vitest', '^2.0', true),
      dep('@testing-library/react', '^16', true),
      dep('@testing-library/jest-dom', '^6', true),
      dep('jsdom', '^24', true),
      dep('prism-react-renderer', '^2.3', true),
      dep('autoprefixer', '^10.4', true),
      dep('postcss', '^8.4', true),
      dep('typescript', '^5.5', true),
      dep('@types/react', '^18.3', true),
      dep('@types/react-dom', '^18.3', true),
    ],
  };
}
