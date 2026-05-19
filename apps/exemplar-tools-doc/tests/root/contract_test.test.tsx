
// @vitest-environment jsdom
// tests/root/contract_test.test.ts
//
// This file is split into three describe blocks corresponding to the three
// logical test areas: bootstrap/bijection, accessors, and components.

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';

// ─── Hoisted mocks ───────────────────────────────────────────────────────────

const {
  mockGetRouteManifest,
  mockGetPageComponentMap,
  mockRenderEntryPoint,
  mockBuildPageComponentMap,
  mockApp,
  mockGetProjectManifest,
  mockGetRequiredDependencies,
  mockGenerateScaffold,
  mockValidateScaffold,
  mockCalloutBox,
  mockCodeBlock,
  mockVersionBadge,
  mockVideoEmbed,
  mockSidebar,
  mockPageLayout,
  mockHomePage,
  mockCartographerPage,
  mockConstrainPage,
  mockLedgerPage,
  mockPactPage,
  mockAdvocatePage,
  mockArbiterPage,
  mockBatonPage,
  mockSentinelPage,
  mockChroniclerPage,
  mockStigmergyPage,
  mockApprenticePage,
  mockKindexPage,
} = vi.hoisted(() => {
  const page = () => React.createElement('div', null, 'page');
  return {
    mockGetRouteManifest: vi.fn(),
    mockGetPageComponentMap: vi.fn(),
    mockRenderEntryPoint: vi.fn(),
    mockBuildPageComponentMap: vi.fn(),
    mockApp: vi.fn(() => React.createElement('div', null, 'App')),
    mockGetProjectManifest: vi.fn(),
    mockGetRequiredDependencies: vi.fn(),
    mockGenerateScaffold: vi.fn(),
    mockValidateScaffold: vi.fn(),
    mockCalloutBox: vi.fn((props: { title: string; children?: React.ReactNode }) =>
      React.createElement('div', { 'data-testid': 'callout' }, props.title, props.children)
    ),
    mockCodeBlock: vi.fn((props: { code: string }) =>
      React.createElement('pre', { 'data-testid': 'codeblock' }, props.code)
    ),
    mockVersionBadge: vi.fn((props: { version: string; label: string }) =>
      React.createElement('span', { 'data-testid': 'badge' }, `${props.label} ${props.version}`)
    ),
    mockVideoEmbed: vi.fn((props: { title: string }) =>
      React.createElement('iframe', { 'data-testid': 'video', title: props.title })
    ),
    mockSidebar: vi.fn(() => React.createElement('nav', { 'data-testid': 'sidebar' }, 'Sidebar')),
    mockPageLayout: vi.fn((props: { children?: React.ReactNode }) =>
      React.createElement('div', { 'data-testid': 'layout' }, props.children)
    ),
    mockHomePage: vi.fn(page),
    mockCartographerPage: vi.fn(page),
    mockConstrainPage: vi.fn(page),
    mockLedgerPage: vi.fn(page),
    mockPactPage: vi.fn(page),
    mockAdvocatePage: vi.fn(page),
    mockArbiterPage: vi.fn(page),
    mockBatonPage: vi.fn(page),
    mockSentinelPage: vi.fn(page),
    mockChroniclerPage: vi.fn(page),
    mockStigmergyPage: vi.fn(page),
    mockApprenticePage: vi.fn(page),
    mockKindexPage: vi.fn(page),
  };
});

// ─── vi.mock() declarations ──────────────────────────────────────────────────

vi.mock('../../src/app_routing', () => ({
  getRouteManifest: mockGetRouteManifest,
  App: mockApp,
  renderEntryPoint: mockRenderEntryPoint,
  buildPageComponentMap: mockBuildPageComponentMap,
}));

vi.mock('../../src/page_components', () => ({
  HomePage: mockHomePage,
  CartographerPage: mockCartographerPage,
  ConstrainPage: mockConstrainPage,
  LedgerPage: mockLedgerPage,
  PactPage: mockPactPage,
  AdvocatePage: mockAdvocatePage,
  ArbiterPage: mockArbiterPage,
  BatonPage: mockBatonPage,
  SentinelPage: mockSentinelPage,
  ChroniclerPage: mockChroniclerPage,
  StigmergyPage: mockStigmergyPage,
  ApprenticePage: mockApprenticePage,
  KindexPage: mockKindexPage,
  getPageComponentMap: mockGetPageComponentMap,
}));

vi.mock('../../src/project_scaffold', () => ({
  generateScaffold: mockGenerateScaffold,
  getProjectManifest: mockGetProjectManifest,
  getRequiredDependencies: mockGetRequiredDependencies,
  validateScaffold: mockValidateScaffold,
}));

vi.mock('../../src/shared_components', () => ({
  CalloutBox: mockCalloutBox,
  CodeBlock: mockCodeBlock,
  VersionBadge: mockVersionBadge,
  VideoEmbed: mockVideoEmbed,
  Sidebar: mockSidebar,
  PageLayout: mockPageLayout,
}));

// ─── Shared test fixtures ────────────────────────────────────────────────────

const ALL_KEYS = [
  'Home', 'Cartographer', 'Constrain', 'Ledger', 'Pact',
  'Advocate', 'Arbiter', 'Baton', 'Sentinel', 'Chronicler',
  'Stigmergy', 'Apprentice', 'Kindex',
] as const;

function makeFakeManifest(keys: readonly string[] = ALL_KEYS) {
  return keys.map((k, i) => ({
    path: `/${k.toLowerCase()}`,
    label: `${k} Page`,
    componentKey: k,
  }));
}

function makeFakeComponentMap(keys: readonly string[] = ALL_KEYS) {
  const map: Record<string, () => React.ReactElement> = {};
  for (const k of keys) {
    map[k] = () => React.createElement('div', null, k);
  }
  return map;
}

// ─── Import SUT ──────────────────────────────────────────────────────────────

import {
  bootstrapApp,
  verifyManifestComponentBijection,
  getRouteManifest,
  getPageComponentMap,
  buildPageComponentMap,
  getProjectManifest,
  getRequiredDependencies,
  App,
  renderEntryPoint,
  CalloutBox,
  CodeBlock,
  VersionBadge,
  VideoEmbed,
  Sidebar,
  PageLayout,
} from '../../src/root';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: bootstrapApp & verifyManifestComponentBijection
// ═══════════════════════════════════════════════════════════════════════════════

describe('bootstrapApp', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Set up default mocks returning valid data
    mockGetRouteManifest.mockReturnValue(makeFakeManifest());
    mockGetPageComponentMap.mockReturnValue(makeFakeComponentMap());
    mockRenderEntryPoint.mockReturnValue(undefined);
  });

  afterEach(() => {
    // Clean up any created DOM elements
    const el = document.getElementById('root');
    if (el) el.remove();
    const el2 = document.getElementById('app-mount');
    if (el2) el2.remove();
  });

  function createTarget(id = 'root') {
    const el = document.createElement('div');
    el.id = id;
    document.body.appendChild(el);
    return el;
  }

  it('returns BootstrapResult with 13 routes, 13 components, allRoutesHaveComponents=true, and matching targetElementId', () => {
    createTarget('root');
    const result = bootstrapApp({ targetElementId: 'root', strictMode: true });

    expect(result.routeCount, 'routeCount must be 13').toBe(13);
    expect(result.pageComponentCount, 'pageComponentCount must be 13').toBe(13);
    expect(result.allRoutesHaveComponents, 'allRoutesHaveComponents must be true').toBe(true);
    expect(result.targetElementId, 'targetElementId must match config').toBe('root');
  });

  it('calls getRouteManifest and getPageComponentMap exactly once each', () => {
    createTarget('root');
    bootstrapApp({ targetElementId: 'root', strictMode: true });

    expect(mockGetRouteManifest, 'getRouteManifest should be called once').toHaveBeenCalledTimes(1);
    expect(mockGetPageComponentMap, 'getPageComponentMap should be called once').toHaveBeenCalledTimes(1);
  });

  it('calls renderEntryPoint exactly once after bijection verification', () => {
    createTarget('root');
    bootstrapApp({ targetElementId: 'root', strictMode: true });

    expect(mockRenderEntryPoint, 'renderEntryPoint should be called once').toHaveBeenCalledTimes(1);
  });

  it('works with a custom targetElementId', () => {
    createTarget('app-mount');
    const result = bootstrapApp({ targetElementId: 'app-mount', strictMode: false });

    expect(result.targetElementId, 'should use custom target ID').toBe('app-mount');
    expect(result.routeCount).toBe(13);
  });

  it('throws TARGET_ELEMENT_NOT_FOUND when the DOM element is missing', () => {
    expect(() =>
      bootstrapApp({ targetElementId: 'nonexistent', strictMode: true })
    ).toThrow(/target.?element.?not.?found|TARGET_ELEMENT_NOT_FOUND/i);
  });

  it('throws MANIFEST_COMPONENT_MISMATCH when page component map is missing a key', () => {
    createTarget('root');
    const incompleteMap = makeFakeComponentMap(ALL_KEYS.slice(0, 12));
    mockGetPageComponentMap.mockReturnValue(incompleteMap);

    expect(() =>
      bootstrapApp({ targetElementId: 'root', strictMode: true })
    ).toThrow(/mismatch|MANIFEST_COMPONENT_MISMATCH/i);
  });

  it('does NOT call renderEntryPoint when bijection fails', () => {
    createTarget('root');
    const incompleteMap = makeFakeComponentMap(ALL_KEYS.slice(0, 12));
    mockGetPageComponentMap.mockReturnValue(incompleteMap);

    try {
      bootstrapApp({ targetElementId: 'root', strictMode: true });
    } catch {
      // expected
    }

    expect(mockRenderEntryPoint, 'renderEntryPoint should not be called on mismatch').not.toHaveBeenCalled();
  });

  it('throws RENDER_FAILURE when renderEntryPoint throws', () => {
    createTarget('root');
    mockRenderEntryPoint.mockImplementation(() => {
      throw new Error('React root creation failed');
    });

    expect(() =>
      bootstrapApp({ targetElementId: 'root', strictMode: true })
    ).toThrow(/render.?failure|RENDER_FAILURE|React root/i);
  });

  it('rejects empty targetElementId per BootstrapConfig validator', () => {
    expect(() =>
      bootstrapApp({ targetElementId: '', strictMode: true })
    ).toThrow();
  });
});

describe('verifyManifestComponentBijection', () => {
  it('returns isValid=true when manifest keys and map keys match exactly', () => {
    const manifest = makeFakeManifest();
    const map = makeFakeComponentMap();
    const result = verifyManifestComponentBijection(manifest, map);

    expect(result.isValid, 'should be valid when keys match').toBe(true);
    expect(result.missingInMap, 'no keys should be missing from map').toHaveLength(0);
    expect(result.extraInMap, 'no extra keys in map').toHaveLength(0);
    expect(result.manifestKeys, 'manifestKeys should have 13 entries').toHaveLength(13);
    expect(result.mapKeys, 'mapKeys should have 13 entries').toHaveLength(13);
  });

  it.each([
    {
      desc: 'key missing from map',
      manifestKeys: ALL_KEYS,
      mapKeys: ALL_KEYS.slice(0, 12), // missing Kindex
      expectedMissing: ['Kindex'],
      expectedExtra: [],
    },
    {
      desc: 'extra key in map not in manifest',
      manifestKeys: ALL_KEYS.slice(0, 12), // missing Kindex in manifest
      mapKeys: ALL_KEYS,
      expectedMissing: [],
      expectedExtra: ['Kindex'],
    },
    {
      desc: 'both missing and extra',
      manifestKeys: [...ALL_KEYS.slice(0, 12), 'Unknown'] as string[],
      mapKeys: [...ALL_KEYS] as string[],
      expectedMissing: ['Unknown'],
      expectedExtra: ['Kindex'],
    },
  ])('detects $desc', ({ manifestKeys, mapKeys, expectedMissing, expectedExtra }) => {
    const manifest = makeFakeManifest(manifestKeys);
    const map = makeFakeComponentMap(mapKeys);
    const result = verifyManifestComponentBijection(manifest, map);

    expect(result.isValid, 'should be invalid on mismatch').toBe(false);
    for (const k of expectedMissing) {
      expect(result.missingInMap, `missingInMap should contain ${k}`).toContain(k);
    }
    for (const k of expectedExtra) {
      expect(result.extraInMap, `extraInMap should contain ${k}`).toContain(k);
    }
  });

  it('is a pure function — identical inputs produce identical outputs', () => {
    const manifest = makeFakeManifest();
    const map = makeFakeComponentMap();
    const result1 = verifyManifestComponentBijection(manifest, map);
    const result2 = verifyManifestComponentBijection(manifest, map);

    expect(result1, 'two calls with same inputs must return equal results').toEqual(result2);
  });

  it('returns correct manifestKeys in order', () => {
    const manifest = makeFakeManifest();
    const map = makeFakeComponentMap();
    const result = verifyManifestComponentBijection(manifest, map);

    const expectedKeys = ALL_KEYS.map(k => k);
    expect(result.manifestKeys).toEqual(expectedKeys);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: Accessor functions (re-exports)
// ═══════════════════════════════════════════════════════════════════════════════

describe('getRouteManifest (re-export)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetRouteManifest.mockReturnValue(makeFakeManifest());
  });

  it('returns exactly 13 RouteEntry objects', () => {
    const manifest = getRouteManifest();
    expect(manifest, 'manifest must be an array').toBeInstanceOf(Array);
    expect(manifest).toHaveLength(13);
  });

  it('every entry has path, label, and componentKey fields', () => {
    const manifest = getRouteManifest();
    for (const entry of manifest) {
      expect(entry).toHaveProperty('path');
      expect(entry).toHaveProperty('label');
      expect(entry).toHaveProperty('componentKey');
      expect(typeof entry.path).toBe('string');
      expect(typeof entry.label).toBe('string');
      expect(entry.label.length).toBeGreaterThan(0);
    }
  });

  it('all paths are unique', () => {
    const manifest = getRouteManifest();
    const paths = manifest.map((e: { path: string }) => e.path);
    expect(new Set(paths).size, 'all route paths must be unique').toBe(13);
  });

  it('every PageComponentKey variant appears exactly once', () => {
    const manifest = getRouteManifest();
    const keys = manifest.map((e: { componentKey: string }) => e.componentKey);
    const keySet = new Set(keys);
    for (const k of ALL_KEYS) {
      expect(keySet.has(k), `manifest should contain componentKey '${k}'`).toBe(true);
    }
    expect(keySet.size).toBe(13);
  });
});

describe('getPageComponentMap (re-export)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetPageComponentMap.mockReturnValue(makeFakeComponentMap());
  });

  it('returns a map with exactly 13 entries', () => {
    const map = getPageComponentMap();
    expect(Object.keys(map)).toHaveLength(13);
  });

  it('every value is a function (React.ComponentType)', () => {
    const map = getPageComponentMap();
    for (const [key, value] of Object.entries(map)) {
      expect(typeof value, `${key} should be a function`).toBe('function');
    }
  });

  it('has every PageComponentKey as a key', () => {
    const map = getPageComponentMap();
    for (const k of ALL_KEYS) {
      expect(map).toHaveProperty(k);
    }
  });
});

describe('buildPageComponentMap (re-export)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockBuildPageComponentMap.mockReturnValue(makeFakeComponentMap());
  });

  it('returns a map with exactly 13 entries keyed by PageComponentKey', () => {
    const map = buildPageComponentMap();
    const keys = Object.keys(map);
    expect(keys).toHaveLength(13);
    for (const k of ALL_KEYS) {
      expect(keys, `map should include key '${k}'`).toContain(k);
    }
  });
});

describe('getProjectManifest (re-export)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetProjectManifest.mockReturnValue({
      projectRoot: '/tmp/exemplar-tools-doc',
      files: Array.from({ length: 12 }, (_, i) => `file-${i}`),
      projectName: 'exemplar-tools-doc',
      devServerPort: 4000,
    });
  });

  it('returns manifest with projectName, devServerPort, and 12 files', () => {
    const manifest = getProjectManifest();
    expect(manifest.projectName, 'projectName must be exemplar-tools-doc').toBe('exemplar-tools-doc');
    expect(manifest.devServerPort, 'devServerPort must be 4000').toBe(4000);
    expect(manifest.files, 'files must have 12 entries').toHaveLength(12);
  });
});

describe('getRequiredDependencies (re-export)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetRequiredDependencies.mockReturnValue({
      dependencies: [
        { packageName: 'react', versionRange: '^18.0.0', isDev: false },
        { packageName: 'react-dom', versionRange: '^18.0.0', isDev: false },
        { packageName: 'react-router-dom', versionRange: '^6.0.0', isDev: false },
      ],
      devDependencies: Array.from({ length: 13 }, (_, i) => ({
        packageName: `dev-dep-${i}`,
        versionRange: '^1.0.0',
        isDev: true,
      })),
    });
  });

  it('returns 3 dependencies and 13 devDependencies', () => {
    const deps = getRequiredDependencies();
    expect(deps.dependencies, 'dependencies must have 3 entries').toHaveLength(3);
    expect(deps.devDependencies, 'devDependencies must have 13 entries').toHaveLength(13);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: Component re-exports
// ═══════════════════════════════════════════════════════════════════════════════

// We test that re-exported components are callable and forward to mocks.
// For deeper rendering tests, use @testing-library/react in a .tsx file.

describe('App (re-export)', () => {
  it('is a function (React component)', () => {
    expect(typeof App).toBe('function');
  });
});

describe('CalloutBox (re-export)', () => {
  it('is re-exported as a function', () => {
    expect(typeof CalloutBox).toBe('function');
  });

  it.each(['gotcha', 'warning', 'tip'] as const)('can be called with type=%s', (variant) => {
    // Verify the mock is invocable with each variant
    const props = { type: variant, title: `${variant} title`, children: 'content' };
    const result = CalloutBox(props);
    expect(result).toBeDefined();
  });
});

describe('CodeBlock (re-export)', () => {
  it('is re-exported as a function', () => {
    expect(typeof CodeBlock).toBe('function');
  });
});

describe('VersionBadge (re-export)', () => {
  it('is re-exported as a function', () => {
    expect(typeof VersionBadge).toBe('function');
  });
});

describe('VideoEmbed (re-export)', () => {
  it('is re-exported as a function', () => {
    expect(typeof VideoEmbed).toBe('function');
  });
});

describe('Sidebar (re-export)', () => {
  it('is re-exported as a function', () => {
    expect(typeof Sidebar).toBe('function');
  });

  it('can be called with routes prop', () => {
    const routes = makeFakeManifest();
    const result = Sidebar({ routes });
    expect(result).toBeDefined();
  });
});

describe('PageLayout (re-export)', () => {
  it('is re-exported as a function', () => {
    expect(typeof PageLayout).toBe('function');
  });

  it('can be called with routes and children props', () => {
    const routes = makeFakeManifest();
    const result = PageLayout({ routes, children: React.createElement('div', null, 'child') });
    expect(result).toBeDefined();
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: Cross-cutting Invariants
// ═══════════════════════════════════════════════════════════════════════════════

describe('Root Module Invariants', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetRouteManifest.mockReturnValue(makeFakeManifest());
    mockGetPageComponentMap.mockReturnValue(makeFakeComponentMap());
  });

  it('manifest componentKey set equals page component map key set', () => {
    const manifest = getRouteManifest();
    const map = getPageComponentMap();
    const manifestKeys = new Set(manifest.map((e: { componentKey: string }) => e.componentKey));
    const mapKeys = new Set(Object.keys(map));

    expect(manifestKeys, 'manifest componentKeys must equal map keys').toEqual(mapKeys);
  });

  it('route manifest has exactly 13 entries', () => {
    const manifest = getRouteManifest();
    expect(manifest).toHaveLength(13);
  });

  it('page component map has exactly 13 entries', () => {
    const map = getPageComponentMap();
    expect(Object.keys(map)).toHaveLength(13);
  });

  it('all 13 PageComponentKey values are present in both manifest and map', () => {
    const manifest = getRouteManifest();
    const map = getPageComponentMap();
    const manifestKeys = manifest.map((e: { componentKey: string }) => e.componentKey);
    const mapKeys = Object.keys(map);

    for (const k of ALL_KEYS) {
      expect(manifestKeys, `manifest should include '${k}'`).toContain(k);
      expect(mapKeys, `map should include '${k}'`).toContain(k);
    }
  });
});
