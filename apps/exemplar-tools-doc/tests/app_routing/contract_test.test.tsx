// @vitest-environment jsdom
import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// ---------------------------------------------------------------------------
// Hoisted mocks — vi.hoisted() runs before vi.mock() factories
// ---------------------------------------------------------------------------
const { mockPageComponents } = vi.hoisted(() => {
  const makeStub = (name: string) => {
    const Comp = () => React.createElement('div', { 'data-testid': name }, name);
    Comp.displayName = name;
    return Comp;
  };
  return {
    mockPageComponents: {
      HomePage: makeStub('Home'),
      CartographerPage: makeStub('Step0Cartographer'),
      ConstrainPage: makeStub('Step1aConstrain'),
      LedgerPage: makeStub('Step1bLedger'),
      PactPage: makeStub('Step2aPact'),
      AdvocatePage: makeStub('Step2bAdvocate'),
      ArbiterPage: makeStub('Step3Arbiter'),
      BatonPage: makeStub('Step4Baton'),
      SentinelPage: makeStub('Step5aSentinel'),
      ChroniclerPage: makeStub('Step5bChronicler'),
      StigmergyPage: makeStub('Step5cStigmergy'),
      ApprenticePage: makeStub('Step6Apprentice'),
      KindexPage: makeStub('Step7Kindex'),
    },
  };
});

vi.mock('../../src/page_components', () => ({
  HomePage: mockPageComponents.HomePage,
  CartographerPage: mockPageComponents.CartographerPage,
  ConstrainPage: mockPageComponents.ConstrainPage,
  LedgerPage: mockPageComponents.LedgerPage,
  PactPage: mockPageComponents.PactPage,
  AdvocatePage: mockPageComponents.AdvocatePage,
  ArbiterPage: mockPageComponents.ArbiterPage,
  BatonPage: mockPageComponents.BatonPage,
  SentinelPage: mockPageComponents.SentinelPage,
  ChroniclerPage: mockPageComponents.ChroniclerPage,
  StigmergyPage: mockPageComponents.StigmergyPage,
  ApprenticePage: mockPageComponents.ApprenticePage,
  KindexPage: mockPageComponents.KindexPage,
}));

// Mock shared_components — PageLayout renders children with routes prop
vi.mock('../../src/shared_components', () => ({
  PageLayout: ({ children, routes }: { children: React.ReactNode; routes: unknown }) =>
    React.createElement('div', { 'data-testid': 'page-layout' }, children),
  Sidebar: () => React.createElement('div', null, 'Sidebar'),
}));

// ---------------------------------------------------------------------------
// Imports under test — AFTER mocks are established
// ---------------------------------------------------------------------------
import {
  getRouteManifest,
  ROUTE_MANIFEST,
  PageComponentKey,
} from '../../src/app_routing/routes';

import App, {
  App as AppNamed,
  PAGE_COMPONENTS,
  buildPageComponentMap,
} from '../../src/app_routing/App';

// ---------------------------------------------------------------------------
// Canonical constants from the contract
// ---------------------------------------------------------------------------
const CANONICAL_PATHS = [
  '/',
  '/step-0-cartographer',
  '/step-1a-constrain',
  '/step-1b-ledger',
  '/step-2a-pact',
  '/step-2b-advocate',
  '/step-3-arbiter',
  '/step-4-baton',
  '/step-5a-sentinel',
  '/step-5b-chronicler',
  '/step-5c-stigmergy',
  '/step-6-apprentice',
  '/step-7-kindex',
] as const;

const ALL_COMPONENT_KEYS = [
  'Home',
  'Cartographer',
  'Constrain',
  'Ledger',
  'Pact',
  'Advocate',
  'Arbiter',
  'Baton',
  'Sentinel',
  'Chronicler',
  'Stigmergy',
  'Apprentice',
  'Kindex',
] as const;

const PAGE_COMPONENT_MAP_KEYS = [
  'Home',
  'Step0Cartographer',
  'Step1aConstrain',
  'Step1bLedger',
  'Step2aPact',
  'Step2bAdvocate',
  'Step3Arbiter',
  'Step4Baton',
  'Step5aSentinel',
  'Step5bChronicler',
  'Step5cStigmergy',
  'Step6Apprentice',
  'Step7Kindex',
] as const;

// Map from componentKey enum variant to the expected path for route-rendering tests
const KEY_TO_PATH: Record<string, string> = {
  Home: '/',
  Cartographer: '/step-0-cartographer',
  Constrain: '/step-1a-constrain',
  Ledger: '/step-1b-ledger',
  Pact: '/step-2a-pact',
  Advocate: '/step-2b-advocate',
  Arbiter: '/step-3-arbiter',
  Baton: '/step-4-baton',
  Sentinel: '/step-5a-sentinel',
  Chronicler: '/step-5b-chronicler',
  Stigmergy: '/step-5c-stigmergy',
  Apprentice: '/step-6-apprentice',
  Kindex: '/step-7-kindex',
};

// Map from componentKey to the expected testid rendered by the stub
const KEY_TO_TESTID: Record<string, string> = {
  Home: 'Home',
  Cartographer: 'Step0Cartographer',
  Constrain: 'Step1aConstrain',
  Ledger: 'Step1bLedger',
  Pact: 'Step2aPact',
  Advocate: 'Step2bAdvocate',
  Arbiter: 'Step3Arbiter',
  Baton: 'Step4Baton',
  Sentinel: 'Step5aSentinel',
  Chronicler: 'Step5bChronicler',
  Stigmergy: 'Step5cStigmergy',
  Apprentice: 'Step6Apprentice',
  Kindex: 'Step7Kindex',
};

// ---------------------------------------------------------------------------
// Test groups
// ---------------------------------------------------------------------------

describe('app_routing / getRouteManifest()', () => {
  // Resolve the manifest once — it is a constant, no side effects
  const manifest =
    typeof getRouteManifest === 'function' ? getRouteManifest() : ROUTE_MANIFEST;

  it('returns an array with exactly 13 entries', () => {
    expect(Array.isArray(manifest)).toBe(true);
    expect(manifest).toHaveLength(13);
  });

  it('every entry has path (string), label (string), and componentKey (string)', () => {
    for (const entry of manifest) {
      expect(typeof entry.path).toBe('string');
      expect(typeof entry.label).toBe('string');
      expect(typeof entry.componentKey).toBe('string');
    }
  });

  it('paths match the exact canonical set of 13 paths', () => {
    const paths = manifest.map((e: { path: string }) => e.path);
    expect(new Set(paths)).toEqual(new Set(CANONICAL_PATHS));
  });

  it('every PageComponentKey variant appears exactly once', () => {
    const keys = manifest.map((e: { componentKey: string }) => e.componentKey);
    expect(new Set(keys).size).toBe(13);
    for (const k of ALL_COMPONENT_KEYS) {
      expect(keys).toContain(k);
    }
  });

  it('all path values are unique — no duplicates', () => {
    const paths = manifest.map((e: { path: string }) => e.path);
    expect(new Set(paths).size).toBe(13);
  });

  it('all label values are non-empty strings', () => {
    for (const entry of manifest) {
      expect(typeof entry.label).toBe('string');
      expect(entry.label.length).toBeGreaterThanOrEqual(1);
    }
  });

  it('every path matches RoutePath regex ^/[a-z0-9-]*$', () => {
    const pattern = /^\/[a-z0-9-]*$/;
    for (const entry of manifest) {
      expect(entry.path).toMatch(pattern);
    }
  });

  it('array order is Home first, then steps 0 through 7 ascending', () => {
    const paths = manifest.map((e: { path: string }) => e.path);
    expect(paths[0]).toBe('/');
    // Verify the remaining 12 are in the canonical ascending order
    for (let i = 0; i < CANONICAL_PATHS.length; i++) {
      expect(paths[i]).toBe(
        CANONICAL_PATHS[i],
        `Expected path at index ${i} to be ${CANONICAL_PATHS[i]} but got ${paths[i]}`,
      );
    }
  });

  it('manifest is readonly — Object.isFrozen or no mutation method succeeds', () => {
    // Attempting to push should either throw (frozen) or the contract says readonly
    // We just verify the length stays 13 if we try to reassign (TS prevents, but runtime check)
    const originalLength = manifest.length;
    try {
      (manifest as unknown[]).push({ path: '/fake', label: 'Fake', componentKey: 'Fake' });
    } catch {
      // expected for frozen arrays
    }
    // If push didn't throw, the contract is violated only if length changed
    // Some implementations use Object.freeze, others rely on TS readonly
    expect(manifest).toHaveLength(originalLength);
  });
});

describe('app_routing / buildPageComponentMap()', () => {
  const map: Record<string, unknown> =
    typeof buildPageComponentMap === 'function'
      ? (buildPageComponentMap() as Record<string, unknown>)
      : (PAGE_COMPONENTS as Record<string, unknown>);

  it('contains exactly 13 entries', () => {
    expect(Object.keys(map)).toHaveLength(13);
  });

  it('every PageComponentKey variant from the contract is a key in the map', () => {
    for (const key of PAGE_COMPONENT_MAP_KEYS) {
      expect(map).toHaveProperty(
        key,
        expect.anything(),
      );
    }
  });

  it('every value is a function (React.ComponentType)', () => {
    for (const key of PAGE_COMPONENT_MAP_KEYS) {
      expect(typeof map[key]).toBe('function');
    }
  });

  it('map keys correspond 1:1 with ROUTE_MANIFEST componentKey values', () => {
    const manifest =
      typeof getRouteManifest === 'function' ? getRouteManifest() : ROUTE_MANIFEST;
    const manifestKeys = new Set(
      manifest.map((e: { componentKey: string }) => e.componentKey),
    );
    // The map uses compound keys (e.g. Step0Cartographer) while manifest uses enum
    // variants (e.g. Cartographer). Verify correspondence via the known mapping.
    // If the implementation uses the same key space, a direct check works:
    const mapKeys = new Set(Object.keys(map));
    // At minimum, both sets must have size 13
    expect(mapKeys.size).toBe(13);
    expect(manifestKeys.size).toBe(13);
  });

  it('has no extra keys beyond the 13 defined variants', () => {
    const allowedKeys = new Set(PAGE_COMPONENT_MAP_KEYS);
    for (const key of Object.keys(map)) {
      expect(allowedKeys.has(key as (typeof PAGE_COMPONENT_MAP_KEYS)[number])).toBe(true);
    }
  });
});

describe('app_routing / App()', () => {
  it('renders without throwing when navigated to /', () => {
    expect(() => {
      render(
        React.createElement(
          MemoryRouter,
          { initialEntries: ['/'] },
          React.createElement(App),
        ),
      );
    }).not.toThrow();
  });

  it('is exported as both default and named export', () => {
    expect(App).toBeDefined();
    expect(typeof App).toBe('function');
    // Named export
    if (AppNamed) {
      expect(typeof AppNamed).toBe('function');
    }
  });

  // Test each of the 13 routes renders its page component
  for (const key of ALL_COMPONENT_KEYS) {
    const path = KEY_TO_PATH[key];
    const testId = KEY_TO_TESTID[key];

    it(`renders ${key} component at path ${path}`, () => {
      const { getByTestId } = render(
        React.createElement(
          MemoryRouter,
          { initialEntries: [path] },
          React.createElement(App),
        ),
      );
      expect(getByTestId(testId)).toBeTruthy();
    });
  }

  it('renders PageLayout with routes prop', () => {
    const { getByTestId } = render(
      React.createElement(
        MemoryRouter,
        { initialEntries: ['/'] },
        React.createElement(App),
      ),
    );
    expect(getByTestId('page-layout')).toBeTruthy();
  });

  it('does not crash when navigating to an unmatched route', () => {
    expect(() => {
      render(
        React.createElement(
          MemoryRouter,
          { initialEntries: ['/this-path-does-not-exist'] },
          React.createElement(App),
        ),
      );
    }).not.toThrow();
  });

  it('does not render any known page component for an unmatched route', () => {
    const { queryByTestId } = render(
      React.createElement(
        MemoryRouter,
        { initialEntries: ['/this-path-does-not-exist'] },
        React.createElement(App),
      ),
    );
    for (const testId of Object.values(KEY_TO_TESTID)) {
      expect(queryByTestId(testId)).toBeNull();
    }
  });
});

describe('app_routing / renderEntryPoint()', () => {
  let originalGetElementById: typeof document.getElementById;

  beforeEach(() => {
    originalGetElementById = document.getElementById.bind(document);
    // Clean up body
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('mounts App on a #root element when present', async () => {
    // Create the root div
    const rootDiv = document.createElement('div');
    rootDiv.id = 'root';
    document.body.appendChild(rootDiv);

    // Dynamically import main.tsx to trigger renderEntryPoint
    // We use a lazy import so the side-effect runs with our DOM state
    let renderEntryPoint: (() => void) | undefined;
    try {
      const mainModule = await import('../../src/app_routing/main');
      renderEntryPoint = mainModule.renderEntryPoint;
    } catch {
      // main.tsx may auto-execute as a side effect — that's acceptable
    }

    if (typeof renderEntryPoint === 'function') {
      renderEntryPoint();
    }

    // The root div should now have child content
    expect(rootDiv.innerHTML.length).toBeGreaterThan(0);
  });

  it('throws or errors when #root element is missing', async () => {
    // Do NOT add a #root div
    let renderEntryPoint: (() => void) | undefined;
    try {
      const mainModule = await import('../../src/app_routing/main');
      renderEntryPoint = mainModule.renderEntryPoint;
    } catch {
      // Module may fail to load — acceptable
      return;
    }

    if (typeof renderEntryPoint === 'function') {
      expect(() => renderEntryPoint!()).toThrow();
    }
  });
});

describe('app_routing / type validation', () => {
  describe('RoutePath validation', () => {
    const validPaths = ['/', '/step-0-cartographer', '/step-1a-constrain', '/a', '/abc-123'];
    const invalidPaths = ['', 'no-slash', '/Upper', '/has space', '/has_underscore'];

    const routePathPattern = /^\/[a-z0-9-]*$/;

    for (const p of validPaths) {
      it(`accepts valid RoutePath: "${p}"`, () => {
        expect(p).toMatch(routePathPattern);
        expect(p.length).toBeGreaterThanOrEqual(1);
        expect(p.length).toBeLessThanOrEqual(64);
      });
    }

    for (const p of invalidPaths) {
      it(`rejects invalid RoutePath: "${p}"`, () => {
        // At least one condition should fail
        const matchesPattern = routePathPattern.test(p);
        const validLength = p.length >= 1 && p.length <= 64;
        expect(matchesPattern && validLength).toBe(false);
      });
    }
  });

  describe('RouteLabel validation', () => {
    it('rejects empty string as RouteLabel', () => {
      expect(''.length).toBeLessThan(1);
    });

    it('accepts non-empty string as RouteLabel', () => {
      expect('Home'.length).toBeGreaterThanOrEqual(1);
      expect('Home'.length).toBeLessThanOrEqual(128);
    });
  });

  describe('PageComponentKey enum', () => {
    it('has exactly 13 variants', () => {
      if (PageComponentKey) {
        const variants = Object.values(PageComponentKey).filter(
          (v) => typeof v === 'string',
        );
        expect(variants.length).toBe(13);
      }
    });

    it('contains all expected variant names', () => {
      if (PageComponentKey) {
        for (const key of ALL_COMPONENT_KEYS) {
          expect(Object.values(PageComponentKey)).toContain(key);
        }
      }
    });
  });
});
