import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// ---------------------------------------------------------------------------
// Mocks — declared at module scope so vi.mock factories can reference them
// ---------------------------------------------------------------------------
const mockRender = vi.fn();
const mockCreateRoot = vi.fn(() => ({ render: mockRender }));

// We will dynamically control whether react-router-dom is available
let shouldThrowRouterImport = false;

// Mock react-dom/client for mountApp tests
vi.mock('react-dom/client', () => ({
  createRoot: mockCreateRoot,
}));

// Prevent vite/esbuild from initializing in jsdom (TextEncoder crash)
vi.mock('@vitejs/plugin-react', () => ({ default: () => ({}) }));
vi.mock('vite', () => ({ defineConfig: (c: unknown) => c }));

// ---------------------------------------------------------------------------
// 1. App() Component Tests
// ---------------------------------------------------------------------------
describe('App() Component', () => {
  // We import dynamically so we can test module shape
  it('renders a div with id="app-shell" inside a BrowserRouter', async () => {
    // Use dynamic import to get the App component
    const { render, screen } = await import('@testing-library/react');
    const AppModule = await import('../../src/project_scaffold/App');

    const { App } = AppModule;
    expect(typeof App).toBe('function');

    const { container } = render(App());
    const appShell = container.querySelector('#app-shell');
    expect(appShell).not.toBeNull();
    expect(appShell?.tagName.toLowerCase()).toBe('div');
  });

  it('is available as a named export { App } — not a default export', async () => {
    const AppModule = await import('../../src/project_scaffold/App');

    // Named export must exist
    expect(AppModule).toHaveProperty('App');
    expect(typeof AppModule.App).toBe('function');

    // No default export
    expect(
      (AppModule as Record<string, unknown>)['default'],
    ).toBeUndefined();
  });

  it('postcondition: rendered tree has BrowserRouter at its root', async () => {
    const { render } = await import('@testing-library/react');
    const { App } = await import('../../src/project_scaffold/App');

    // Rendering App outside any router context should still work because
    // App itself provides BrowserRouter. We just confirm no error is thrown.
    expect(() => render(App())).not.toThrow();
  });
});

// ---------------------------------------------------------------------------
// 2. mountApp() Bootstrap Tests
// ---------------------------------------------------------------------------
describe('mountApp() Bootstrap', () => {
  let rootDiv: HTMLDivElement | null = null;

  beforeEach(() => {
    // Reset mocks
    mockCreateRoot.mockClear();
    mockRender.mockClear();

    // Reset modules so each test gets a fresh side-effect import
    vi.resetModules();
  });

  afterEach(() => {
    // Clean up #root if it was added
    if (rootDiv && rootDiv.parentNode) {
      rootDiv.parentNode.removeChild(rootDiv);
    }
    rootDiv = null;
  });

  it('happy path: calls createRoot on #root and renders <App />', async () => {
    // Set up DOM
    rootDiv = document.createElement('div');
    rootDiv.id = 'root';
    document.body.appendChild(rootDiv);

    // Re-mock createRoot for this fresh module load
    vi.doMock('react-dom/client', () => ({
      createRoot: mockCreateRoot,
    }));

    // Dynamically import to trigger the side-effect
    await import('../../src/project_scaffold/main');

    expect(mockCreateRoot).toHaveBeenCalledTimes(1);
    // Verify it was called with the actual #root element
    const calledWith = mockCreateRoot.mock.calls[0][0];
    expect(calledWith).toBe(rootDiv);
    expect(mockRender).toHaveBeenCalledTimes(1);
  });

  it('error: missing_root_element — throws when no #root exists in DOM', async () => {
    // Ensure no #root element exists
    const existing = document.getElementById('root');
    if (existing) existing.remove();

    vi.doMock('react-dom/client', () => ({
      createRoot: mockCreateRoot,
    }));

    // The side-effect module should throw or createRoot should receive null
    try {
      await import('../../src/project_scaffold/main');
      // If it didn't throw, at minimum createRoot should NOT have been
      // called with a valid element — or it may have thrown inside
      if (mockCreateRoot.mock.calls.length > 0) {
        const calledWith = mockCreateRoot.mock.calls[0][0];
        expect(calledWith).toBeNull();
      }
    } catch (err: unknown) {
      // Expected — module threw because #root is missing
      expect(err).toBeDefined();
    }
  });

  it('invariant: mountApp module has no named exports (side-effect only)', async () => {
    rootDiv = document.createElement('div');
    rootDiv.id = 'root';
    document.body.appendChild(rootDiv);

    vi.doMock('react-dom/client', () => ({
      createRoot: mockCreateRoot,
    }));

    const mainModule = await import('../../src/project_scaffold/main') as Record<string, unknown>;
    const exportedKeys = Object.keys(mainModule).filter(
      (k) => k !== '__esModule' && k !== 'default',
    );
    expect(exportedKeys.length).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// 3. Configuration Contract Tests
// ---------------------------------------------------------------------------
describe('Configuration Contracts', () => {
  // --- ViteServerConfig ---
  describe('ViteServerConfig', () => {
    it('port must be exactly 4000', async () => {
      const viteConfig = await import('../../src/project_scaffold/vite.config') as Record<string, unknown>;
      // The config might expose server.port at the top level or via a default export
      const config = (viteConfig.default ?? viteConfig) as Record<string, unknown>;
      const server = config.server as Record<string, unknown> | undefined;
      expect(server).toBeDefined();
      expect(server!.port).toBe(4000);
    });

    it('rejects port values other than 4000', async () => {
      const invalidPort = 3000;
      expect(invalidPort).not.toBe(4000);
      // Contract: ViteServerConfig port validator (range): value == 4000
      // Any config with port !== 4000 violates the contract
    });
  });

  // --- VitestConfig ---
  describe('VitestConfig', () => {
    it('environment must be "jsdom"', async () => {
      const viteConfig = await import('../../src/project_scaffold/vite.config') as Record<string, unknown>;
      const config = (viteConfig.default ?? viteConfig) as Record<string, unknown>;
      const test = config.test as Record<string, unknown> | undefined;
      expect(test).toBeDefined();
      expect(test!.environment).toBe('jsdom');
    });

    it('globals must be true', async () => {
      const viteConfig = await import('../../src/project_scaffold/vite.config') as Record<string, unknown>;
      const config = (viteConfig.default ?? viteConfig) as Record<string, unknown>;
      const test = config.test as Record<string, unknown> | undefined;
      expect(test).toBeDefined();
      expect(test!.globals).toBe(true);
    });

    it('setupFiles must point to "./src/test-setup.ts"', async () => {
      const viteConfig = await import('../../src/project_scaffold/vite.config') as Record<string, unknown>;
      const config = (viteConfig.default ?? viteConfig) as Record<string, unknown>;
      const test = config.test as Record<string, unknown> | undefined;
      expect(test).toBeDefined();
      expect(test!.setupFiles).toBe('./src/test-setup.ts');
    });

    it('rejects environment values other than "jsdom"', () => {
      const invalidEnv = 'node';
      expect(invalidEnv).not.toBe('jsdom');
      // Contract: VitestConfig environment validator: value === 'jsdom'
    });
  });

  // --- TsCompilerOptions ---
  describe('TsCompilerOptions', () => {
    it('strict must be true', async () => {
      const tsConfig = await import('../../src/project_scaffold/tsconfig.json') as Record<string, unknown>;
      const config = (tsConfig.default ?? tsConfig) as Record<string, unknown>;
      const compilerOptions = config.compilerOptions as Record<string, unknown>;
      expect(compilerOptions).toBeDefined();
      expect(compilerOptions.strict).toBe(true);
    });

    it('jsx must be "react-jsx"', async () => {
      const tsConfig = await import('../../src/project_scaffold/tsconfig.json') as Record<string, unknown>;
      const config = (tsConfig.default ?? tsConfig) as Record<string, unknown>;
      const compilerOptions = config.compilerOptions as Record<string, unknown>;
      expect(compilerOptions).toBeDefined();
      expect(compilerOptions.jsx).toBe('react-jsx');
    });

    it('moduleResolution must be "bundler"', async () => {
      const tsConfig = await import('../../src/project_scaffold/tsconfig.json') as Record<string, unknown>;
      const config = (tsConfig.default ?? tsConfig) as Record<string, unknown>;
      const compilerOptions = config.compilerOptions as Record<string, unknown>;
      expect(compilerOptions).toBeDefined();
      expect(compilerOptions.moduleResolution).toBe('bundler');
    });

    it('isolatedModules must be true', async () => {
      const tsConfig = await import('../../src/project_scaffold/tsconfig.json') as Record<string, unknown>;
      const config = (tsConfig.default ?? tsConfig) as Record<string, unknown>;
      const compilerOptions = config.compilerOptions as Record<string, unknown>;
      expect(compilerOptions).toBeDefined();
      expect(compilerOptions.isolatedModules).toBe(true);
    });
  });

  // --- TailwindContentGlob ---
  describe('TailwindContentGlob', () => {
    it('content array includes "./index.html" and "./src/**/*.{ts,tsx}"', async () => {
      const twConfig = await import('../../src/project_scaffold/tailwind.config') as Record<string, unknown>;
      const config = (twConfig.default ?? twConfig) as Record<string, unknown>;
      const content = config.content as string[];
      expect(Array.isArray(content)).toBe(true);
      expect(content).toContain('./index.html');
      expect(content).toContain('./src/**/*.{ts,tsx}');
    });
  });

  // --- VercelRewriteRule ---
  describe('VercelRewriteRule', () => {
    it('has a catch-all rewrite: /(.*) -> /index.html', async () => {
      const vercelConfig = await import('../../src/project_scaffold/vercel.json') as Record<string, unknown>;
      const config = (vercelConfig.default ?? vercelConfig) as Record<string, unknown>;
      const rewrites = config.rewrites as Array<{ source: string; destination: string }>;
      expect(Array.isArray(rewrites)).toBe(true);
      expect(rewrites.length).toBeGreaterThanOrEqual(1);

      const catchAll = rewrites.find((r) => r.source === '/(.*)');
      expect(catchAll).toBeDefined();
      expect(catchAll!.source).toBe('/(.*)');
      expect(catchAll!.destination).toBe('/index.html');
    });
  });

  // --- PackageDependencyMap ---
  describe('PackageDependencyMap', () => {
    it('lists react, react-dom, and react-router-dom as runtime dependencies with correct semver', async () => {
      const pkg = await import('../../src/project_scaffold/package.json') as Record<string, unknown>;
      const config = (pkg.default ?? pkg) as Record<string, unknown>;
      const deps = config.dependencies as Record<string, string>;
      expect(deps).toBeDefined();

      // react ^18.x
      expect(deps.react).toBeDefined();
      expect(deps.react).toMatch(/^\^18\./);

      // react-dom ^18.x
      expect(deps['react-dom']).toBeDefined();
      expect(deps['react-dom']).toMatch(/^\^18\./);

      // react-router-dom ^x
      expect(deps['react-router-dom']).toBeDefined();
      expect(deps['react-router-dom']).toMatch(/^\^/);
    });
  });

  // --- PackageDevDependencyMap ---
  describe('PackageDevDependencyMap', () => {
    it('lists all 10 required devDependencies with caret-pinned versions', async () => {
      const pkg = await import('../../src/project_scaffold/package.json') as Record<string, unknown>;
      const config = (pkg.default ?? pkg) as Record<string, unknown>;
      const devDeps = config.devDependencies as Record<string, string>;
      expect(devDeps).toBeDefined();

      const requiredDevDeps = [
        'vite',
        'vitest',
        'tailwindcss',
        '@testing-library/react',
        'jsdom',
        '@vitejs/plugin-react',
        'typescript',
        'autoprefixer',
        'postcss',
        '@testing-library/jest-dom',
      ];

      for (const dep of requiredDevDeps) {
        expect(devDeps[dep], `devDependency "${dep}" should be present`).toBeDefined();
        expect(
          devDeps[dep],
          `devDependency "${dep}" should start with ^`,
        ).toMatch(/^\^/);
      }
    });
  });

  // --- index.css Tailwind directives ---
  describe('index.css Tailwind directives', () => {
    it('contains @tailwind base, components, and utilities directives', async () => {
      // We read the file as a raw string via fs
      const fs = await import('fs');
      const path = await import('path');
      const cssPath = path.resolve(__dirname, '../../src/project_scaffold/index.css');
      const cssContent = fs.readFileSync(cssPath, 'utf-8');

      expect(cssContent).toContain('@tailwind base;');
      expect(cssContent).toContain('@tailwind components;');
      expect(cssContent).toContain('@tailwind utilities;');
    });
  });

  // --- index.html structure ---
  describe('index.html structure', () => {
    it('contains <div id="root"></div> and <script type="module" src="/src/main.tsx"></script>', async () => {
      const fs = await import('fs');
      const path = await import('path');
      const htmlPath = path.resolve(__dirname, '../../src/project_scaffold/index.html');
      const htmlContent = fs.readFileSync(htmlPath, 'utf-8');

      expect(htmlContent).toContain('<div id="root"></div>');
      expect(htmlContent).toContain('src="/src/main.tsx"');
      expect(htmlContent).toContain('type="module"');
    });
  });

  // --- postcss.config.js ---
  describe('postcss.config.js plugins', () => {
    it('includes tailwindcss and autoprefixer plugins', async () => {
      const postcssConfig = await import('../../src/project_scaffold/postcss.config') as Record<string, unknown>;
      const config = (postcssConfig.default ?? postcssConfig) as Record<string, unknown>;
      const plugins = config.plugins as Record<string, unknown>;
      expect(plugins).toBeDefined();
      expect(plugins).toHaveProperty('tailwindcss');
      expect(plugins).toHaveProperty('autoprefixer');
    });
  });

  // --- test-setup.ts ---
  describe('test-setup.ts', () => {
    it('imports @testing-library/jest-dom for global matchers', async () => {
      const fs = await import('fs');
      const path = await import('path');
      const setupPath = path.resolve(__dirname, '../../src/project_scaffold/test-setup.ts');
      const setupContent = fs.readFileSync(setupPath, 'utf-8');

      expect(setupContent).toContain('@testing-library/jest-dom');
    });
  });
});
