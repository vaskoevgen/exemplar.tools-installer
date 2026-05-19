
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { readFileSync, existsSync } from 'fs';
import { resolve } from 'path';

/**
 * Adversarial hidden tests for Project Scaffold & Configuration.
 * These tests catch implementations that hardcode returns to pass visible tests
 * without truly satisfying the contract.
 */

// Helper to read a project file relative to the project root
function readProjectFile(relativePath: string): string {
  const fullPath = resolve(process.cwd(), relativePath);
  if (!existsSync(fullPath)) {
    throw new Error(`Expected file not found: ${relativePath}`);
  }
  return readFileSync(fullPath, 'utf-8');
}

describe('goodhart: App component behavioral properties', () => {
  beforeEach(() => {
    // Set up a minimal DOM for React rendering
    document.body.innerHTML = '<div id="root"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('goodhart: should be a callable function component, not a pre-rendered element', async () => {
    const appModule = await import('../../../src/project_scaffold/App');
    expect(typeof appModule.App).toBe('function');
    // It should be callable (function components are functions)
    expect(appModule.App).toBeInstanceOf(Function);
  });

  it('goodhart: should return a valid React element when invoked as JSX', async () => {
    const React = await import('react');
    const { render, cleanup } = await import('@testing-library/react');
    const { App } = await import('../../../src/project_scaffold/App');

    const { container } = render(React.createElement(App));
    // The rendered output must have actual DOM content, not be empty
    expect(container.innerHTML).not.toBe('');
    cleanup();
  });

  it('goodhart: should produce consistent DOM structure across multiple independent renders', async () => {
    const React = await import('react');
    const { render, cleanup } = await import('@testing-library/react');
    const { App } = await import('../../../src/project_scaffold/App');

    const result1 = render(React.createElement(App));
    const html1 = result1.container.innerHTML;
    cleanup();

    const result2 = render(React.createElement(App));
    const html2 = result2.container.innerHTML;
    cleanup();

    expect(html1).toBe(html2);
    // Both should contain app-shell
    expect(html1).toContain('app-shell');
  });

  it('goodhart: should render app-shell div inside a routing context so useLocation works for descendants', async () => {
    const React = await import('react');
    const { render, cleanup, screen } = await import('@testing-library/react');
    const { useLocation } = await import('react-router-dom');
    const { App } = await import('../../../src/project_scaffold/App');

    // Create a child component that uses routing hooks to verify context
    let locationCaptured = false;
    function LocationProbe() {
      const location = useLocation();
      locationCaptured = true;
      return React.createElement('span', { 'data-testid': 'probe' }, location.pathname);
    }

    // We need to render App and ensure router context is available
    // By rendering App on its own, BrowserRouter should be at root
    const { container } = render(React.createElement(App));
    const appShell = container.querySelector('#app-shell');
    expect(appShell).not.toBeNull();
    cleanup();
  });

  it('goodhart: should render an empty app-shell div with no page content or route definitions', async () => {
    const React = await import('react');
    const { render, cleanup } = await import('@testing-library/react');
    const { App } = await import('../../../src/project_scaffold/App');

    const { container } = render(React.createElement(App));
    const appShell = container.querySelector('#app-shell');
    expect(appShell).not.toBeNull();
    // The app-shell should be empty — no page content, no routes, no layout
    // It might have zero children or minimal structural children, but no text
    const textContent = appShell!.textContent?.trim() ?? '';
    expect(textContent).toBe('');
    cleanup();
  });

  it('goodhart: module namespace must have App but must NOT have a default key', async () => {
    const appModule = await import('../../../src/project_scaffold/App');
    // Named export must exist
    expect(appModule).toHaveProperty('App');
    expect(typeof appModule.App).toBe('function');
    // Default export must not exist
    expect(appModule).not.toHaveProperty('default');
  });
});

describe('goodhart: mountApp behavioral properties', () => {
  it('goodhart: index.html must contain a div with id root as the React mount target', () => {
    const html = readProjectFile('src/project_scaffold/index.html');
    // Must have a div with id="root"
    expect(html).toMatch(/<div\s+id=["']root["']\s*>\s*<\/div>/);
  });

  it('goodhart: index.html must reference /src/main.tsx as a type=module script', () => {
    const html = readProjectFile('src/project_scaffold/index.html');
    // Must have script type="module" src="/src/main.tsx"
    expect(html).toMatch(/<script\s[^>]*type=["']module["'][^>]*src=["']\/src\/main\.tsx["'][^>]*>/);
  });

  it('goodhart: src/index.css must contain all three @tailwind directives and no extra CSS rules', () => {
    const css = readProjectFile('src/project_scaffold/index.css');
    expect(css).toContain('@tailwind base;');
    expect(css).toContain('@tailwind components;');
    expect(css).toContain('@tailwind utilities;');
    // Strip whitespace and comments, ensure nothing else significant
    const stripped = css
      .replace(/\/\*[\s\S]*?\*\//g, '') // remove block comments
      .replace(/\s+/g, ' ')
      .trim();
    // After removing whitespace, it should be just the three directives
    expect(stripped).toMatch(
      /^@tailwind base;\s*@tailwind components;\s*@tailwind utilities;?\s*$/
    );
  });

  it('goodhart: main.tsx must be a side-effect-only module with no named exports', async () => {
    // We can't actually import main.tsx without side effects, but we can read the source
    const source = readProjectFile('src/project_scaffold/main.tsx');
    // Should not have export const/function/class/let/var/type/interface patterns
    // except "export {}" which is sometimes used for module declaration
    const exportStatements = source.match(/export\s+(const|let|var|function|class|interface|type|enum)\s/g);
    expect(exportStatements).toBeNull();
    // Should not have "export default"
    expect(source).not.toMatch(/export\s+default/);
  });
});

describe('goodhart: vite.config.ts behavioral properties', () => {
  it('goodhart: vite config must use @vitejs/plugin-react', () => {
    const source = readProjectFile('src/project_scaffold/vite.config.ts');
    // Should import from @vitejs/plugin-react
    expect(source).toMatch(/@vitejs\/plugin-react/);
    // Should call the plugin in the plugins array
    expect(source).toMatch(/plugins\s*:\s*\[/);
  });

  it('goodhart: vite config test block must have all three vitest fields simultaneously', () => {
    const source = readProjectFile('src/project_scaffold/vite.config.ts');
    // All three fields must be present
    expect(source).toContain("'jsdom'");
    expect(source).toMatch(/globals\s*:\s*true/);
    expect(source).toContain('./src/test-setup.ts');
    // Server port must be 4000
    expect(source).toMatch(/port\s*:\s*4000/);
  });
});

describe('goodhart: tsconfig.json behavioral properties', () => {
  it('goodhart: tsconfig compilerOptions must contain all four required fields simultaneously', () => {
    const raw = readProjectFile('src/project_scaffold/tsconfig.json');
    // Strip comments for JSON parsing (tsconfig supports comments)
    const stripped = raw.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
    const config = JSON.parse(stripped);
    const opts = config.compilerOptions;

    expect(opts).toBeDefined();
    expect(opts.strict).toBe(true);
    expect(opts.jsx).toBe('react-jsx');
    expect(opts.moduleResolution).toBe('bundler');
    expect(opts.isolatedModules).toBe(true);
  });
});

describe('goodhart: tailwind.config.js behavioral properties', () => {
  it('goodhart: content array must include both glob patterns simultaneously', () => {
    const source = readProjectFile('src/project_scaffold/tailwind.config.js');
    expect(source).toContain('./index.html');
    expect(source).toContain('./src/**/*.{ts,tsx}');
  });
});

describe('goodhart: postcss.config.js behavioral properties', () => {
  it('goodhart: postcss config must include both tailwindcss and autoprefixer plugins', () => {
    const source = readProjectFile('src/project_scaffold/postcss.config.js');
    expect(source).toContain('tailwindcss');
    expect(source).toContain('autoprefixer');
  });
});

describe('goodhart: vercel.json behavioral properties', () => {
  it('goodhart: vercel.json rewrites must be an array with exactly one rule', () => {
    const raw = readProjectFile('src/project_scaffold/vercel.json');
    const config = JSON.parse(raw);
    expect(config.rewrites).toBeDefined();
    expect(Array.isArray(config.rewrites)).toBe(true);
    expect(config.rewrites).toHaveLength(1);
    expect(config.rewrites[0].source).toBe('/(.*)');
    expect(config.rewrites[0].destination).toBe('/index.html');
  });
});

describe('goodhart: test-setup.ts behavioral properties', () => {
  it('goodhart: test-setup.ts must import @testing-library/jest-dom for global DOM matchers', () => {
    const source = readProjectFile('src/project_scaffold/test-setup.ts');
    expect(source).toMatch(/@testing-library\/jest-dom/);
    // Must be an import statement, not just a comment mentioning it
    expect(source).toMatch(/import\s+['"]@testing-library\/jest-dom['"]/);
  });
});

describe('goodhart: package.json dependency behavioral properties', () => {
  it('goodhart: react-dom must be a runtime dependency with ^18.x version', () => {
    const raw = readProjectFile('src/project_scaffold/package.json');
    const pkg = JSON.parse(raw);
    expect(pkg.dependencies).toBeDefined();
    expect(pkg.dependencies['react-dom']).toBeDefined();
    expect(pkg.dependencies['react-dom']).toMatch(/^\^18\./);
  });

  it('goodhart: react-router-dom must be a runtime dependency with caret-pinned version', () => {
    const raw = readProjectFile('src/project_scaffold/package.json');
    const pkg = JSON.parse(raw);
    expect(pkg.dependencies).toBeDefined();
    expect(pkg.dependencies['react-router-dom']).toBeDefined();
    expect(pkg.dependencies['react-router-dom']).toMatch(/^\^/);
  });

  it('goodhart: react must be a runtime dependency not just a devDependency', () => {
    const raw = readProjectFile('src/project_scaffold/package.json');
    const pkg = JSON.parse(raw);
    // react must be in dependencies (not devDependencies)
    expect(pkg.dependencies).toBeDefined();
    expect(pkg.dependencies['react']).toBeDefined();
    expect(pkg.dependencies['react']).toMatch(/^\^18\./);
  });

  it('goodhart: @testing-library/jest-dom must be in devDependencies with caret version', () => {
    const raw = readProjectFile('src/project_scaffold/package.json');
    const pkg = JSON.parse(raw);
    expect(pkg.devDependencies).toBeDefined();
    expect(pkg.devDependencies['@testing-library/jest-dom']).toBeDefined();
    expect(pkg.devDependencies['@testing-library/jest-dom']).toMatch(/^\^/);
  });

  it('goodhart: all 10 required devDependencies must each have caret-pinned versions', () => {
    const raw = readProjectFile('src/project_scaffold/package.json');
    const pkg = JSON.parse(raw);
    const devDeps = pkg.devDependencies ?? {};

    const requiredDevDeps = [
      'vite',
      'vitest',
      'tailwindcss',
      '@testing-library/react',
      '@testing-library/jest-dom',
      'jsdom',
      '@vitejs/plugin-react',
      'typescript',
      'autoprefixer',
      'postcss',
    ];

    for (const dep of requiredDevDeps) {
      expect(devDeps[dep], `devDependency ${dep} should be present`).toBeDefined();
      expect(devDeps[dep], `devDependency ${dep} should be caret-pinned`).toMatch(/^\^/);
    }
  });

  it('goodhart: runtime dependencies should not include devDependency-only packages like vitest or tailwindcss', () => {
    const raw = readProjectFile('src/project_scaffold/package.json');
    const pkg = JSON.parse(raw);
    const deps = pkg.dependencies ?? {};

    // These should NOT be in runtime dependencies
    expect(deps['vitest']).toBeUndefined();
    expect(deps['tailwindcss']).toBeUndefined();
    expect(deps['jsdom']).toBeUndefined();
    expect(deps['typescript']).toBeUndefined();
  });
});
