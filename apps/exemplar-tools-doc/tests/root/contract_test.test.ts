import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// ─── Module-level mock fns — use vi.hoisted so they are available inside hoisted vi.mock() factories ───

const { mockCreateAppRouter, mockMountApp, mockInitApp } = vi.hoisted(() => ({
  mockCreateAppRouter: vi.fn(),
  mockMountApp: vi.fn(),
  mockInitApp: vi.fn(),
}));

// ─── vi.mock() factories ───

// Mock routing_and_layout
vi.mock('../../src/routing_and_layout', () => ({
  createAppRouter: mockCreateAppRouter,
  ensureLeadingSlash: vi.fn((s: string) => (s.startsWith('/') ? s : `/${s}`)),
  Sidebar: vi.fn(),
  Layout: vi.fn(),
  getNavLinkClassName: vi.fn(),
}));

// Mock project_scaffold
vi.mock('../../src/project_scaffold', () => ({
  mountApp: mockMountApp,
  App: vi.fn(),
}));

// Mock page_content — every named runtime export
vi.mock('../../src/page_content', () => ({
  StepPage: vi.fn(),
  HomePage: vi.fn(),
  CartographerPage: vi.fn(),
  ConstrainPage: vi.fn(),
  LedgerPage: vi.fn(),
  PactPage: vi.fn(),
  AdvocatePage: vi.fn(),
  ArbiterPage: vi.fn(),
  BatonPage: vi.fn(),
  SentinelPage: vi.fn(),
  ChroniclerPage: vi.fn(),
  StigmergyPage: vi.fn(),
  ApprenticePage: vi.fn(),
  KindexPage: vi.fn(),
  getStepContent: vi.fn(),
}));

// Mock pipeline_diagram
vi.mock('../../src/pipeline_diagram', () => ({
  PipelineDiagram: vi.fn(),
  guardSlug: vi.fn(),
  PIPELINE_NODES: vi.fn(() => []),
  PIPELINE_EDGES: vi.fn(() => []),
}));

// Mock shared_ui
vi.mock('../../src/shared_ui', () => ({
  CodeBlock: vi.fn(),
  VersionBadge: vi.fn(),
  YouTubeEmbed: vi.fn(),
  CalloutBox: vi.fn(),
  extractYouTubeVideoId: vi.fn(),
}));

// ─── Import the module under test ───
// Note: we import AFTER vi.mock() declarations (which are hoisted anyway)
import * as rootModule from '../../src/root';

// ─── Test Suite ───

describe('root – initApp()', () => {
  const callOrder: string[] = [];

  beforeEach(() => {
    // Set up the DOM with a #root element
    document.body.innerHTML = '<div id="root"></div>';

    // Reset call tracking
    callOrder.length = 0;

    // Set up mock implementations that track call order
    const fakeRouter = { routes: 'fake-router-instance' };
    mockCreateAppRouter.mockImplementation(() => {
      callOrder.push('createAppRouter');
      return fakeRouter;
    });
    mockMountApp.mockImplementation(() => {
      callOrder.push('mountApp');
    });
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('happy path: calls createAppRouter once then mountApp once, mounting the app into #root', () => {
    const { initApp } = rootModule;

    initApp();

    expect(mockCreateAppRouter).toHaveBeenCalledTimes(1);
    expect(mockMountApp).toHaveBeenCalledTimes(1);

    // Verify ordering: createAppRouter before mountApp
    expect(callOrder).toEqual(['createAppRouter', 'mountApp']);
  });

  it('invariant: createAppRouter is called strictly before mountApp', () => {
    const { initApp } = rootModule;

    initApp();

    const createIndex = callOrder.indexOf('createAppRouter');
    const mountIndex = callOrder.indexOf('mountApp');

    expect(createIndex).toBeGreaterThanOrEqual(0);
    expect(mountIndex).toBeGreaterThanOrEqual(0);
    expect(createIndex).toBeLessThan(mountIndex);
  });

  it('error: missing_root_element — propagates error when #root DOM element does not exist', () => {
    // Remove the #root element
    document.body.innerHTML = '';

    const { initApp } = rootModule;

    // mountApp should be configured to throw when root is missing
    mockMountApp.mockImplementation(() => {
      const el = document.getElementById('root');
      if (!el) {
        throw new Error('missing_root_element: DOM element with id="root" not found');
      }
    });

    expect(() => initApp()).toThrow();

    // createAppRouter should still have been called (it runs first)
    expect(mockCreateAppRouter).toHaveBeenCalledTimes(1);
  });

  it('error: router_creation_failure — propagates error when createAppRouter throws', () => {
    const routerError = new Error('router_creation_failure: Missing page component import');
    mockCreateAppRouter.mockImplementation(() => {
      throw routerError;
    });

    const { initApp } = rootModule;

    expect(() => initApp()).toThrow(routerError);

    // mountApp must NOT be called if createAppRouter fails
    expect(mockMountApp).not.toHaveBeenCalled();
  });

  it('error: mount_failure — propagates error when mountApp throws', () => {
    const mountError = new Error('mount_failure: createRoot is unavailable');
    mockMountApp.mockImplementation(() => {
      throw mountError;
    });

    const { initApp } = rootModule;

    expect(() => initApp()).toThrow(mountError);

    // createAppRouter should have been called before the mount failure
    expect(mockCreateAppRouter).toHaveBeenCalledTimes(1);
  });

  it('invariant: root module exports exactly one named runtime export: initApp', () => {
    // Filter out potential __esModule or default keys
    const exportKeys = Object.keys(rootModule).filter(
      (k) => k !== '__esModule' && k !== 'default'
    );

    expect(exportKeys).toEqual(['initApp']);
    expect(typeof rootModule.initApp).toBe('function');
  });
});

describe('root – main.tsx (side-effect entry point)', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="root"></div>';
    vi.resetModules();

    // Reset mock state
    mockInitApp.mockReset();
    mockCreateAppRouter.mockReset();
    mockMountApp.mockReset();

    mockCreateAppRouter.mockReturnValue({ routes: 'fake-router' });
    mockMountApp.mockImplementation(() => {});
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('happy path: importing main.tsx calls initApp exactly once', async () => {
    // We need to dynamically mock and import main.tsx to test its side effect
    // Mock the root module so we can track initApp calls
    vi.doMock('../../src/root', () => ({
      initApp: mockInitApp,
    }));

    // Mock CSS import (side-effect only)
    vi.doMock('../../src/root/index.css', () => ({}));

    // Dynamically import main.tsx — this triggers the side effect
    await import('../../src/root/main');

    expect(mockInitApp).toHaveBeenCalledTimes(1);
  });

  it('invariant: main.tsx has zero named exports', async () => {
    vi.doMock('../../src/root', () => ({
      initApp: mockInitApp,
    }));

    vi.doMock('../../src/root/index.css', () => ({}));

    const mainModule = await import('../../src/root/main');

    // Filter out meta keys like __esModule and default
    const namedExports = Object.keys(mainModule).filter(
      (k) => k !== '__esModule' && k !== 'default'
    );

    expect(namedExports).toEqual([]);
  });

  it('error: init_app_import_failure — fails when initApp cannot be resolved from root', async () => {
    // Mock root module to not export initApp at all
    vi.doMock('../../src/root', () => {
      throw new Error('init_app_import_failure: Named export initApp cannot be resolved');
    });

    vi.doMock('../../src/root/index.css', () => ({}));

    await expect(async () => {
      await import('../../src/root/main');
    }).rejects.toThrow();
  });

  it('error: css_import_failure — fails when index.css cannot be resolved', async () => {
    vi.doMock('../../src/root', () => ({
      initApp: mockInitApp,
    }));

    vi.doMock('../../src/root/index.css', () => {
      throw new Error('css_import_failure: src/index.css cannot be resolved');
    });

    await expect(async () => {
      await import('../../src/root/main');
    }).rejects.toThrow();
  });
});
