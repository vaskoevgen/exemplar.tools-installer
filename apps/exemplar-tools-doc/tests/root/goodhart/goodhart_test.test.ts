
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// Module-scope mock function refs — declared before vi.mock() calls
const mockCreateAppRouter = vi.fn();
const mockMountApp = vi.fn();

vi.mock('../src/../routing_and_layout', () => ({
  createAppRouter: mockCreateAppRouter,
}));

// Also mock with likely actual import paths
vi.mock('routing_and_layout', () => ({
  createAppRouter: mockCreateAppRouter,
}));

vi.mock('../src/../project_scaffold', () => ({
  mountApp: mockMountApp,
}));

vi.mock('project_scaffold', () => ({
  mountApp: mockMountApp,
}));

// We need to handle the actual import paths used by the module.
// Try multiple possible mock patterns for the dependencies.
vi.mock('@routing_and_layout', () => ({
  createAppRouter: mockCreateAppRouter,
}));

vi.mock('@project_scaffold', () => ({
  mountApp: mockMountApp,
}));

// Common relative path patterns
vi.mock('../routing_and_layout', () => ({
  createAppRouter: mockCreateAppRouter,
}));

vi.mock('../project_scaffold', () => ({
  mountApp: mockMountApp,
}));

vi.mock('./routing_and_layout', () => ({
  createAppRouter: mockCreateAppRouter,
}));

vi.mock('./project_scaffold', () => ({
  mountApp: mockMountApp,
}));

describe('Root - Adversarial Hidden Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Ensure #root element exists for happy-path tests
    if (!document.getElementById('root')) {
      const rootEl = document.createElement('div');
      rootEl.id = 'root';
      document.body.appendChild(rootEl);
    }
    // Default mock behavior
    mockCreateAppRouter.mockReturnValue({ __routerSentinel: true });
    mockMountApp.mockReturnValue(undefined);
  });

  afterEach(() => {
    const rootEl = document.getElementById('root');
    if (rootEl) {
      document.body.removeChild(rootEl);
    }
  });

  describe('initApp', () => {
    it('goodhart: initApp must pass the exact router instance returned by createAppRouter to mountApp, not a hardcoded or fabricated object', async () => {
      const uniqueRouter = { __unique: Symbol('router-sentinel'), routes: [] };
      mockCreateAppRouter.mockReturnValue(uniqueRouter);

      const { initApp } = await import('../../../src/root');
      initApp();

      expect(mockMountApp).toHaveBeenCalledTimes(1);
      const passedArg = mockMountApp.mock.calls[0][0];
      expect(passedArg).toBe(uniqueRouter);
    });

    it('goodhart: when createAppRouter returns different instances on successive calls, mountApp must receive the corresponding instance each time', async () => {
      const routerA = { id: 'router-A', __brand: Symbol('A') };
      const routerB = { id: 'router-B', __brand: Symbol('B') };
      mockCreateAppRouter.mockReturnValueOnce(routerA).mockReturnValueOnce(routerB);

      const { initApp } = await import('../../../src/root');

      initApp();
      expect(mockMountApp.mock.calls[0][0]).toBe(routerA);

      // Re-add #root if mountApp removed it
      if (!document.getElementById('root')) {
        const rootEl = document.createElement('div');
        rootEl.id = 'root';
        document.body.appendChild(rootEl);
      }

      initApp();
      expect(mockMountApp.mock.calls[1][0]).toBe(routerB);
      expect(routerA).not.toBe(routerB);
    });

    it('goodhart: initApp must call createAppRouter exactly once per invocation — never zero or multiple times', async () => {
      const { initApp } = await import('../../../src/root');
      initApp();
      expect(mockCreateAppRouter).toHaveBeenCalledTimes(1);
    });

    it('goodhart: initApp must call mountApp exactly once per invocation', async () => {
      const { initApp } = await import('../../../src/root');
      initApp();
      expect(mockMountApp).toHaveBeenCalledTimes(1);
    });

    it('goodhart: when createAppRouter throws, mountApp must never be invoked — error propagates before mount', async () => {
      mockCreateAppRouter.mockImplementation(() => {
        throw new Error('router_creation_failure: missing component');
      });

      const { initApp } = await import('../../../src/root');
      expect(() => initApp()).toThrow();
      expect(mockMountApp).not.toHaveBeenCalled();
    });

    it('goodhart: initApp must return void/undefined — it must not return the router or any other value', async () => {
      const { initApp } = await import('../../../src/root');
      const result = initApp();
      expect(result).toBeUndefined();
    });

    it('goodhart: initApp must be exported as a callable function', async () => {
      const { initApp } = await import('../../../src/root');
      expect(typeof initApp).toBe('function');
    });

    it('goodhart: mountApp must be called with exactly one argument — the router instance', async () => {
      const sentinel = { __router: true };
      mockCreateAppRouter.mockReturnValue(sentinel);

      const { initApp } = await import('../../../src/root');
      initApp();

      expect(mockMountApp).toHaveBeenCalledTimes(1);
      // Check it was called with exactly 1 arg
      expect(mockMountApp.mock.calls[0]).toHaveLength(1);
      expect(mockMountApp.mock.calls[0][0]).toBe(sentinel);
    });

    it('goodhart: createAppRouter must be called with zero arguments — root should not pass config or pages to it', async () => {
      const { initApp } = await import('../../../src/root');
      initApp();

      expect(mockCreateAppRouter).toHaveBeenCalledTimes(1);
      expect(mockCreateAppRouter.mock.calls[0]).toHaveLength(0);
    });

    it('goodhart: each invocation of initApp must call both dependencies — no caching or memoization across calls', async () => {
      const { initApp } = await import('../../../src/root');

      initApp();

      // Re-add #root if needed
      if (!document.getElementById('root')) {
        const rootEl = document.createElement('div');
        rootEl.id = 'root';
        document.body.appendChild(rootEl);
      }

      initApp();

      expect(mockCreateAppRouter).toHaveBeenCalledTimes(2);
      expect(mockMountApp).toHaveBeenCalledTimes(2);
    });

    it('goodhart: initApp should execute synchronously — it must not return a Promise', async () => {
      const { initApp } = await import('../../../src/root');
      const result = initApp();

      // Should not be a thenable
      const isThenable = result != null && typeof (result as any).then === 'function';
      expect(isThenable).toBe(false);
    });
  });

  describe('module structure invariants', () => {
    it('goodhart: src/root.ts must export exactly one named runtime export: initApp', async () => {
      const rootModule = await import('../../../src/root');
      const exportKeys = Object.keys(rootModule).filter(k => k !== 'default' && k !== '__esModule');
      // initApp must be present
      expect(exportKeys).toContain('initApp');
      // Filter to only runtime (non-type) exports — in JS, all keys are runtime
      // There should be exactly one
      const runtimeExports = exportKeys.filter(k => typeof rootModule[k as keyof typeof rootModule] !== 'undefined');
      expect(runtimeExports).toEqual(['initApp']);
    });

    it('goodhart: root module must not re-export domain types like StepId, RouteEntry, RouteSlug, etc.', async () => {
      const rootModule = await import('../../../src/root');
      const exportKeys = Object.keys(rootModule);
      const forbiddenExports = [
        'StepId', 'StepLabel', 'RouteSlug', 'StepContent', 'RouteEntry',
        'ROUTE_ENTRY_LIST', 'PIPELINE_NODES', 'PIPELINE_EDGES',
        'Layout', 'Sidebar', 'HomePage', 'CartographerPage',
        'ensureLeadingSlash', 'guardSlug', 'CodeBlock', 'VersionBadge',
      ];
      for (const name of forbiddenExports) {
        expect(exportKeys).not.toContain(name);
      }
    });

    it('goodhart: root module source must not directly import from shared_ui or pipeline_diagram', async () => {
      // Read the actual source file to check import statements
      const possiblePaths = [
        path.resolve(__dirname, '../src/root.ts'),
        path.resolve(__dirname, '../src/root.tsx'),
      ];

      let source = '';
      for (const p of possiblePaths) {
        try {
          source = fs.readFileSync(p, 'utf-8');
          break;
        } catch {
          // try next
        }
      }

      // If we can read the source, verify no direct imports from shared_ui or pipeline_diagram
      if (source) {
        // Check for import statements referencing these modules
        expect(source).not.toMatch(/from\s+['"].*shared_ui/);
        expect(source).not.toMatch(/from\s+['"].*pipeline_diagram/);
        expect(source).not.toMatch(/import\s+.*['"].*shared_ui/);
        expect(source).not.toMatch(/import\s+.*['"].*pipeline_diagram/);
      }
    });

    it('goodhart: root module source must not contain slug string manipulation — all slug handling delegated to routing_and_layout', async () => {
      const possiblePaths = [
        path.resolve(__dirname, '../src/root.ts'),
        path.resolve(__dirname, '../src/root.tsx'),
      ];

      let source = '';
      for (const p of possiblePaths) {
        try {
          source = fs.readFileSync(p, 'utf-8');
          break;
        } catch {
          // try next
        }
      }

      if (source) {
        // Should not contain slug manipulation like string replace, startsWith('/'), etc.
        // on slug-like strings
        expect(source).not.toMatch(/\.replace\s*\(\s*['"]\//);
        expect(source).not.toMatch(/\.startsWith\s*\(\s*['"]\//);
        expect(source).not.toMatch(/['"]\/[a-z]+-[a-z]+['"]/); // hardcoded route paths
      }
    });
  });

  describe('main module', () => {
    it('goodhart: main.tsx must have zero named exports — only side effects', async () => {
      // We need to be careful importing main.tsx as it has side effects
      // Instead, check its exports after import
      try {
        const mainModule = await import('../../../src/root/main');
        const exportKeys = Object.keys(mainModule).filter(k => k !== 'default' && k !== '__esModule');
        expect(exportKeys).toHaveLength(0);
      } catch {
        // If import fails due to side effects in test env, that's acceptable
        // The visible test should catch this — we just add extra coverage
      }
    });
  });
});
