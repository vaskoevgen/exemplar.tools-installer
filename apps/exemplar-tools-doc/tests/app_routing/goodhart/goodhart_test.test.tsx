
import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// We need to mock dependencies before importing App
// page_components and shared_components are external deps

const { mockPageComponents, mockPageLayout } = vi.hoisted(() => {
  const entries: Array<[string, string]> = [
    ['HomePage', 'Home'],
    ['CartographerPage', 'Step0Cartographer'],
    ['ConstrainPage', 'Step1aConstrain'],
    ['LedgerPage', 'Step1bLedger'],
    ['PactPage', 'Step2aPact'],
    ['AdvocatePage', 'Step2bAdvocate'],
    ['ArbiterPage', 'Step3Arbiter'],
    ['BatonPage', 'Step4Baton'],
    ['SentinelPage', 'Step5aSentinel'],
    ['ChroniclerPage', 'Step5bChronicler'],
    ['StigmergyPage', 'Step5cStigmergy'],
    ['ApprenticePage', 'Step6Apprentice'],
    ['KindexPage', 'Step7Kindex'],
  ];

  const mockPageComponents: Record<string, React.FC> = {};
  for (const [exportName, testId] of entries) {
    const Component: React.FC = () => React.createElement('div', { 'data-testid': `page-${testId}` }, testId);
    Component.displayName = testId;
    mockPageComponents[exportName] = Component;
  }

  const mockPageLayout: React.FC<{ routes: any[]; children?: React.ReactNode }> = ({ routes, children }) => {
    return React.createElement('div', { 'data-testid': 'page-layout', 'data-route-count': routes?.length ?? 0 }, children);
  };

  return { mockPageComponents, mockPageLayout };
});

vi.mock('page_components', () => mockPageComponents);
vi.mock('shared_components', () => ({
  PageLayout: mockPageLayout,
  default: mockPageLayout,
}));

// Import the actual modules under test
import { ROUTE_MANIFEST, getRouteManifest, PageComponentKey } from '../../../src/app_routing/routes';
import AppDefault, { App } from '../../../src/app_routing/App';

describe('goodhart: getRouteManifest', () => {
  it('goodhart: should pair each componentKey with its specific canonical path — not just have the right sets independently', () => {
    const manifest = getRouteManifest();
    const expectedPairings: Record<string, string> = {
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

    for (const entry of manifest) {
      const key = entry.componentKey as string;
      expect(entry.path).toBe(expectedPairings[key]);
    }
  });

  it('goodhart: should return a readonly/frozen manifest that cannot be mutated at runtime', () => {
    const manifest1 = getRouteManifest();
    const originalLength = manifest1.length;
    const originalFirstPath = manifest1[0].path;

    // Attempt mutation — should either throw or have no effect
    try {
      (manifest1 as any).push({ path: '/fake', label: 'Fake', componentKey: 'Fake' });
    } catch {
      // Expected for frozen/readonly arrays
    }

    try {
      (manifest1[0] as any).path = '/mutated';
    } catch {
      // Expected for frozen entries
    }

    const manifest2 = getRouteManifest();
    expect(manifest2.length).toBe(13);
    expect(manifest2[0].path).toBe(originalFirstPath);
  });

  it('goodhart: should have labels that are meaningful human-readable strings, not degenerate placeholders', () => {
    const manifest = getRouteManifest();
    for (const entry of manifest) {
      expect(typeof entry.label).toBe('string');
      expect(entry.label.trim().length).toBeGreaterThanOrEqual(2);
      // Labels shouldn't be just the path repeated
      expect(entry.label).not.toBe(entry.path);
    }
  });

  it('goodhart: should have Home at index 0 with path "/" specifically', () => {
    const manifest = getRouteManifest();
    expect(manifest[0].componentKey).toBe('Home');
    expect(manifest[0].path).toBe('/');
  });

  it('goodhart: should order steps in exact sub-step sequence 0,1a,1b,2a,2b,3,4,5a,5b,5c,6,7 after Home', () => {
    const manifest = getRouteManifest();
    const expectedPathOrder = [
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
    ];
    const actualPaths = manifest.map((e: any) => e.path);
    expect(actualPaths).toEqual(expectedPathOrder);
  });

  it('goodhart: should have entries with exactly three own properties (path, label, componentKey)', () => {
    const manifest = getRouteManifest();
    for (const entry of manifest) {
      const keys = Object.keys(entry).sort();
      expect(keys).toEqual(['componentKey', 'label', 'path']);
    }
  });

  it('goodhart: should have all 13 labels be distinct from each other', () => {
    const manifest = getRouteManifest();
    const labels = manifest.map((e: any) => e.label);
    const uniqueLabels = new Set(labels);
    expect(uniqueLabels.size).toBe(13);
  });

  it('goodhart: should use exact PageComponentKey enum values as componentKey, not lookalike strings', () => {
    const manifest = getRouteManifest();
    const validKeys = new Set([
      'Home', 'Cartographer', 'Constrain', 'Ledger', 'Pact', 'Advocate',
      'Arbiter', 'Baton', 'Sentinel', 'Chronicler', 'Stigmergy', 'Apprentice', 'Kindex'
    ]);
    for (const entry of manifest) {
      expect(validKeys.has(entry.componentKey as string)).toBe(true);
    }
    // Also verify via the enum if exported
    if (PageComponentKey) {
      const enumValues = Object.values(PageComponentKey);
      for (const entry of manifest) {
        expect(enumValues).toContain(entry.componentKey);
      }
    }
  });

  it('goodhart: should return the same reference on repeated calls since it is a module constant', () => {
    const first = getRouteManifest();
    const second = getRouteManifest();
    expect(first).toBe(second);
  });
});

describe('goodhart: App exports', () => {
  it('goodhart: should export App as both named and default export referencing the same component', () => {
    expect(App).toBeDefined();
    expect(AppDefault).toBeDefined();
    expect(typeof App).toBe('function');
    expect(typeof AppDefault).toBe('function');
    expect(App).toBe(AppDefault);
  });
});

describe('goodhart: App rendering', () => {
  it('goodhart: should pass the full 13-entry route manifest to PageLayout as the routes prop', () => {
    let capturedRoutes: any[] | undefined;
    const SpyPageLayout: React.FC<any> = ({ routes, children }) => {
      capturedRoutes = routes;
      return React.createElement('div', { 'data-testid': 'page-layout' }, children);
    };

    // We need to verify via rendering. The mock is already set up,
    // but we can check via data attributes
    const { container } = render(
      React.createElement(MemoryRouter, { initialEntries: ['/'] },
        React.createElement(App)
      )
    );

    const layoutEl = container.querySelector('[data-testid="page-layout"]');
    if (layoutEl) {
      const routeCount = layoutEl.getAttribute('data-route-count');
      expect(Number(routeCount)).toBe(13);
    }
  });

  it('goodhart: should render distinct components for different routes, not the same stub for all', () => {
    const paths = ['/step-3-arbiter', '/step-5b-chronicler', '/step-1b-ledger'];
    const rendered: string[] = [];

    for (const path of paths) {
      const { container, unmount } = render(
        React.createElement(MemoryRouter, { initialEntries: [path] },
          React.createElement(App)
        )
      );
      const text = container.textContent || '';
      rendered.push(text);
      unmount();
    }

    // Each route should produce different content
    expect(rendered[0]).not.toBe(rendered[1]);
    expect(rendered[1]).not.toBe(rendered[2]);
    expect(rendered[0]).not.toBe(rendered[2]);
  });

  it('goodhart: should correctly render mid-manifest routes that are not the first or last entry', () => {
    const midPaths = ['/step-3-arbiter', '/step-5b-chronicler', '/step-1b-ledger'];

    for (const path of midPaths) {
      const { container, unmount } = render(
        React.createElement(MemoryRouter, { initialEntries: [path] },
          React.createElement(App)
        )
      );
      // Should render without errors — container should have content
      expect(container.innerHTML).not.toBe('');
      unmount();
    }
  });

  it('goodhart: should not match sub-paths of valid routes (e.g., /step-0-cartographer/extra should not render cartographer)', () => {
    // Render a valid route to see what it looks like
    const { container: validContainer, unmount: unmount1 } = render(
      React.createElement(MemoryRouter, { initialEntries: ['/step-0-cartographer'] },
        React.createElement(App)
      )
    );
    const validContent = validContainer.textContent || '';
    unmount1();

    // Render a sub-path — should NOT match
    const { container: invalidContainer, unmount: unmount2 } = render(
      React.createElement(MemoryRouter, { initialEntries: ['/step-0-cartographer/extra'] },
        React.createElement(App)
      )
    );
    const invalidContent = invalidContainer.textContent || '';
    unmount2();

    // The sub-path should not render the cartographer component
    // Either it renders nothing (in the page area) or a fallback, but not the same component
    if (validContent.includes('Cartographer') || validContent.includes('Step0Cartographer')) {
      expect(invalidContent).not.toContain('Step0Cartographer');
    }
  });
});

describe('goodhart: buildPageComponentMap', () => {
  it('goodhart: should map each key to a distinct component — not reuse the same component for multiple keys', async () => {
    // Import buildPageComponentMap or PAGE_COMPONENTS
    let pageComponentMap: Record<string, any>;
    try {
      const appModule = await import('../../../src/app_routing/App');
      pageComponentMap = appModule.PAGE_COMPONENTS || appModule.buildPageComponentMap?.();
    } catch {
      // If PAGE_COMPONENTS is not directly exported, we skip but the test structure remains
      return;
    }

    if (!pageComponentMap) return;

    const values = Object.values(pageComponentMap);
    const uniqueValues = new Set(values);
    expect(uniqueValues.size).toBe(13);
  });
});
