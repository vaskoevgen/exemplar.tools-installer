
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// ---- hoisted mocks ----
const {
  mockGetRouteManifest,
  mockGetPageComponentMap,
  mockRenderEntryPoint,
  mockBuildPageComponentMap,
  mockApp,
  mockGetProjectManifest,
  mockGetRequiredDependencies,
} = vi.hoisted(() => ({
  mockGetRouteManifest: vi.fn(),
  mockGetPageComponentMap: vi.fn(),
  mockRenderEntryPoint: vi.fn(),
  mockBuildPageComponentMap: vi.fn(),
  mockApp: vi.fn(),
  mockGetProjectManifest: vi.fn(),
  mockGetRequiredDependencies: vi.fn(),
}));

vi.mock('../../../src/app_routing', () => ({
  getRouteManifest: mockGetRouteManifest,
  renderEntryPoint: mockRenderEntryPoint,
  buildPageComponentMap: mockBuildPageComponentMap,
  App: mockApp,
}));

vi.mock('../../../src/page_components', () => ({
  getPageComponentMap: mockGetPageComponentMap,
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
}));

vi.mock('../../../src/project_scaffold', () => ({
  getProjectManifest: mockGetProjectManifest,
  getRequiredDependencies: mockGetRequiredDependencies,
  generateScaffold: vi.fn(),
  validateScaffold: vi.fn(),
}));

vi.mock('../../../src/shared_components', () => ({
  CalloutBox: vi.fn(),
  CodeBlock: vi.fn(),
  VersionBadge: vi.fn(),
  VideoEmbed: vi.fn(),
  Sidebar: vi.fn(),
  PageLayout: vi.fn(),
}));

import {
  bootstrapApp,
  verifyManifestComponentBijection,
  getRouteManifest,
  getPageComponentMap,
  getProjectManifest,
  getRequiredDependencies,
} from '../../../src/root';

// Helper: all 13 page component keys
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
  const map: Record<string, () => null> = {};
  for (const k of keys) {
    map[k] = () => null;
  }
  return map;
}

function setupDom(id: string) {
  const el = document.createElement('div');
  el.id = id;
  document.body.appendChild(el);
  return el;
}

function setupHappyMocks(targetId = 'root') {
  mockGetRouteManifest.mockReturnValue(makeFakeManifest());
  mockGetPageComponentMap.mockReturnValue(makeFakeComponentMap());
  mockRenderEntryPoint.mockImplementation(() => {});
  setupDom(targetId);
}

describe('goodhart: verifyManifestComponentBijection', () => {
  it('goodhart: should report both missingInMap and extraInMap simultaneously when manifest and map have non-overlapping keys', () => {
    const manifest = [
      { path: '/alpha', label: 'Alpha', componentKey: 'Alpha' },
      { path: '/beta', label: 'Beta', componentKey: 'Beta' },
    ];
    const componentMap = { Gamma: () => null, Delta: () => null };

    const result = verifyManifestComponentBijection(manifest as any, componentMap as any);

    expect(result.isValid).toBe(false);
    expect(result.missingInMap).toContain('Alpha');
    expect(result.missingInMap).toContain('Beta');
    expect(result.extraInMap).toContain('Gamma');
    expect(result.extraInMap).toContain('Delta');
    expect(result.missingInMap.length).toBe(2);
    expect(result.extraInMap.length).toBe(2);
  });

  it('goodhart: should handle empty manifest with non-empty map, reporting all map keys as extra', () => {
    const manifest: any[] = [];
    const componentMap = { Foo: () => null, Bar: () => null };

    const result = verifyManifestComponentBijection(manifest as any, componentMap as any);

    expect(result.isValid).toBe(false);
    expect(result.manifestKeys).toEqual([]);
    expect(result.missingInMap).toEqual([]);
    expect(result.extraInMap).toContain('Foo');
    expect(result.extraInMap).toContain('Bar');
    expect(result.extraInMap.length).toBe(2);
  });

  it('goodhart: should handle non-empty manifest with empty map, reporting all manifest keys as missing', () => {
    const manifest = [
      { path: '/x', label: 'X', componentKey: 'X' },
      { path: '/y', label: 'Y', componentKey: 'Y' },
    ];
    const componentMap = {};

    const result = verifyManifestComponentBijection(manifest as any, componentMap as any);

    expect(result.isValid).toBe(false);
    expect(result.mapKeys).toEqual([]);
    expect(result.extraInMap).toEqual([]);
    expect(result.missingInMap).toContain('X');
    expect(result.missingInMap).toContain('Y');
    expect(result.missingInMap.length).toBe(2);
  });

  it('goodhart: should preserve manifestKeys in insertion order matching manifest entries', () => {
    const keys = ['Zulu', 'Alpha', 'Mike', 'Bravo'];
    const manifest = keys.map((k) => ({ path: `/${k.toLowerCase()}`, label: k, componentKey: k }));
    const componentMap = makeFakeComponentMap(keys);

    const result = verifyManifestComponentBijection(manifest as any, componentMap as any);

    expect(result.manifestKeys).toEqual(keys);
    expect(result.isValid).toBe(true);
  });

  it('goodhart: should include arbitrary non-PageComponentKey string keys from the map in mapKeys and extraInMap', () => {
    const manifest = [{ path: '/home', label: 'Home', componentKey: 'Home' }];
    const componentMap = { Home: () => null, RandomExtraKey: () => null, AnotherOne: () => null };

    const result = verifyManifestComponentBijection(manifest as any, componentMap as any);

    expect(result.isValid).toBe(false);
    expect(result.mapKeys).toContain('Home');
    expect(result.mapKeys).toContain('RandomExtraKey');
    expect(result.mapKeys).toContain('AnotherOne');
    expect(result.extraInMap).toContain('RandomExtraKey');
    expect(result.extraInMap).toContain('AnotherOne');
    expect(result.extraInMap).not.toContain('Home');
  });

  it('goodhart: should return isValid true with empty manifest and empty map since both sets are identical', () => {
    const result = verifyManifestComponentBijection([] as any, {} as any);

    expect(result.isValid).toBe(true);
    expect(result.manifestKeys).toEqual([]);
    expect(result.mapKeys).toEqual([]);
    expect(result.missingInMap).toEqual([]);
    expect(result.extraInMap).toEqual([]);
  });

  it('goodhart: should work correctly with a single-entry manifest matching a single-key map', () => {
    const manifest = [{ path: '/solo', label: 'Solo', componentKey: 'Solo' }];
    const componentMap = { Solo: () => null };

    const result = verifyManifestComponentBijection(manifest as any, componentMap as any);

    expect(result.isValid).toBe(true);
    expect(result.manifestKeys).toEqual(['Solo']);
    expect(result.mapKeys).toEqual(['Solo']);
    expect(result.missingInMap).toEqual([]);
    expect(result.extraInMap).toEqual([]);
  });

  it('goodhart: should handle duplicate componentKeys in manifest by including each occurrence in manifestKeys', () => {
    const manifest = [
      { path: '/a', label: 'A1', componentKey: 'Dup' },
      { path: '/b', label: 'A2', componentKey: 'Dup' },
    ];
    const componentMap = { Dup: () => null };

    const result = verifyManifestComponentBijection(manifest as any, componentMap as any);

    // manifestKeys should reflect every entry in order
    expect(result.manifestKeys).toEqual(['Dup', 'Dup']);
    expect(result.manifestKeys.length).toBe(2);
  });
});

describe('goodhart: bootstrapApp', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('goodhart: should dynamically set targetElementId from config, not hardcode any specific value', () => {
    const customId = 'my-app-container-xyz';
    setupHappyMocks(customId);

    const result = bootstrapApp({ targetElementId: customId, strictMode: true });

    expect(result.targetElementId).toBe(customId);
  });

  it('goodhart: should throw manifest_component_mismatch when map has extra keys even if all manifest keys are present', () => {
    const allKeysPlus = [...ALL_KEYS, 'BogusExtra'] as string[];
    mockGetRouteManifest.mockReturnValue(makeFakeManifest(ALL_KEYS));
    mockGetPageComponentMap.mockReturnValue(makeFakeComponentMap(allKeysPlus));
    setupDom('root');

    expect(() => bootstrapApp({ targetElementId: 'root', strictMode: true })).toThrow();
    // Verify it's specifically mismatch, not some other error
    try {
      bootstrapApp({ targetElementId: 'root', strictMode: true });
    } catch (e: any) {
      const msg = (e?.message ?? e ?? '').toString().toLowerCase();
      expect(
        msg.includes('mismatch') || msg.includes('bijection') || msg.includes('MANIFEST_COMPONENT_MISMATCH'.toLowerCase())
      ).toBe(true);
    }
  });

  it('goodhart: should not call renderEntryPoint when bijection verification fails', () => {
    // Map missing one key
    const missingKeys = ALL_KEYS.slice(0, 12);
    mockGetRouteManifest.mockReturnValue(makeFakeManifest(ALL_KEYS));
    mockGetPageComponentMap.mockReturnValue(makeFakeComponentMap(missingKeys));
    setupDom('root');

    try {
      bootstrapApp({ targetElementId: 'root', strictMode: true });
    } catch {
      // expected
    }

    expect(mockRenderEntryPoint).not.toHaveBeenCalled();
  });

  it('goodhart: should not call renderEntryPoint when target DOM element is missing', () => {
    mockGetRouteManifest.mockReturnValue(makeFakeManifest());
    mockGetPageComponentMap.mockReturnValue(makeFakeComponentMap());
    // Don't add any DOM element

    try {
      bootstrapApp({ targetElementId: 'nonexistent-element', strictMode: true });
    } catch {
      // expected
    }

    expect(mockRenderEntryPoint).not.toHaveBeenCalled();
  });

  it('goodhart: should call getRouteManifest and getPageComponentMap exactly once per invocation across multiple sequential calls', () => {
    setupHappyMocks('root');

    bootstrapApp({ targetElementId: 'root', strictMode: true });
    expect(mockGetRouteManifest).toHaveBeenCalledTimes(1);
    expect(mockGetPageComponentMap).toHaveBeenCalledTimes(1);

    // Second call
    bootstrapApp({ targetElementId: 'root', strictMode: true });
    expect(mockGetRouteManifest).toHaveBeenCalledTimes(2);
    expect(mockGetPageComponentMap).toHaveBeenCalledTimes(2);
  });

  it('goodhart: should reject a whitespace-only targetElementId with an error', () => {
    mockGetRouteManifest.mockReturnValue(makeFakeManifest());
    mockGetPageComponentMap.mockReturnValue(makeFakeComponentMap());

    expect(() => bootstrapApp({ targetElementId: '   ', strictMode: true })).toThrow();
  });

  it('goodhart: should propagate render_failure when renderEntryPoint throws even though bijection passes', () => {
    mockGetRouteManifest.mockReturnValue(makeFakeManifest());
    mockGetPageComponentMap.mockReturnValue(makeFakeComponentMap());
    mockRenderEntryPoint.mockImplementation(() => {
      throw new Error('React root creation failed');
    });
    setupDom('root');

    expect(() => bootstrapApp({ targetElementId: 'root', strictMode: true })).toThrow();

    // Verify the mocks were called up to the render point
    expect(mockGetRouteManifest).toHaveBeenCalledTimes(1);
    expect(mockGetPageComponentMap).toHaveBeenCalledTimes(1);
    expect(mockRenderEntryPoint).toHaveBeenCalledTimes(1);
  });

  it('goodhart: should return a BootstrapResult with routeCount and pageComponentCount both exactly 13, not derived from input', () => {
    setupHappyMocks('root');

    const result = bootstrapApp({ targetElementId: 'root', strictMode: true });

    expect(result.routeCount).toStrictEqual(13);
    expect(result.pageComponentCount).toStrictEqual(13);
    expect(result.allRoutesHaveComponents).toStrictEqual(true);
    // Verify these are numbers, not strings
    expect(typeof result.routeCount).toBe('number');
    expect(typeof result.pageComponentCount).toBe('number');
    expect(typeof result.allRoutesHaveComponents).toBe('boolean');
  });
});

describe('goodhart: getRouteManifest re-export', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('goodhart: should return entries where every path starts with a forward slash', () => {
    const fakeManifest = makeFakeManifest();
    mockGetRouteManifest.mockReturnValue(fakeManifest);

    const manifest = getRouteManifest();

    for (const entry of manifest) {
      expect(entry.path.startsWith('/')).toBe(true);
    }
  });

  it('goodhart: should return entries where every path contains only lowercase alphanumeric, hyphens, and slashes', () => {
    const fakeManifest = makeFakeManifest();
    mockGetRouteManifest.mockReturnValue(fakeManifest);

    const manifest = getRouteManifest();

    const validPathRegex = /^\/[a-z0-9\-\/]*$/;
    for (const entry of manifest) {
      expect(entry.path).toMatch(validPathRegex);
    }
  });

  it('goodhart: should return entries where every label is a non-empty string', () => {
    const fakeManifest = makeFakeManifest();
    mockGetRouteManifest.mockReturnValue(fakeManifest);

    const manifest = getRouteManifest();

    for (const entry of manifest) {
      expect(typeof entry.label).toBe('string');
      expect(entry.label.length).toBeGreaterThan(0);
    }
  });

  it('goodhart: should return entries each having path, label, and componentKey properties', () => {
    const fakeManifest = makeFakeManifest();
    mockGetRouteManifest.mockReturnValue(fakeManifest);

    const manifest = getRouteManifest();

    for (const entry of manifest) {
      expect(entry).toHaveProperty('path');
      expect(entry).toHaveProperty('label');
      expect(entry).toHaveProperty('componentKey');
    }
  });
});

describe('goodhart: getPageComponentMap re-export', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('goodhart: should return a map where every value is a function (React.ComponentType)', () => {
    const fakeMap = makeFakeComponentMap();
    mockGetPageComponentMap.mockReturnValue(fakeMap);

    const map = getPageComponentMap();

    for (const key of Object.keys(map)) {
      expect(typeof (map as any)[key]).toBe('function');
    }
  });
});

describe('goodhart: getProjectManifest re-export', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('goodhart: should return a manifest with exactly 12 files', () => {
    mockGetProjectManifest.mockReturnValue({
      projectRoot: './exemplar-tools-doc',
      files: Array.from({ length: 12 }, (_, i) => `file${i}`),
      projectName: 'exemplar-tools-doc',
      devServerPort: 4000,
    });

    const manifest = getProjectManifest();

    expect(manifest.files.length).toBe(12);
  });

  it('goodhart: should return a manifest with a non-empty projectRoot string', () => {
    mockGetProjectManifest.mockReturnValue({
      projectRoot: './exemplar-tools-doc',
      files: Array.from({ length: 12 }, (_, i) => `file${i}`),
      projectName: 'exemplar-tools-doc',
      devServerPort: 4000,
    });

    const manifest = getProjectManifest();

    expect(typeof manifest.projectRoot).toBe('string');
    expect(manifest.projectRoot.length).toBeGreaterThan(0);
  });
});

describe('goodhart: getRequiredDependencies re-export', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('goodhart: should return dependencies and devDependencies as arrays with proper entry structure', () => {
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

    const result = getRequiredDependencies();

    expect(Array.isArray(result.dependencies)).toBe(true);
    expect(Array.isArray(result.devDependencies)).toBe(true);

    for (const dep of result.dependencies) {
      expect(typeof dep.packageName).toBe('string');
      expect(typeof dep.versionRange).toBe('string');
    }

    for (const dep of result.devDependencies) {
      expect(typeof dep.packageName).toBe('string');
      expect(typeof dep.versionRange).toBe('string');
    }
  });
});
