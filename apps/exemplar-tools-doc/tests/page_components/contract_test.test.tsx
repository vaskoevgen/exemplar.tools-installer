// @vitest-environment jsdom
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';

// ---------------------------------------------------------------------------
// Mock shared_components — all shared components render simple stubs
// ---------------------------------------------------------------------------
vi.mock('../../src/shared_components', () => ({
  CodeBlock: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('pre', { 'data-testid': 'code-block' }, children),
  CalloutBox: ({ children }: { children?: React.ReactNode }) =>
    React.createElement('div', { 'data-testid': 'callout-box' }, children),
  VideoEmbed: ({ src }: { src?: string }) =>
    React.createElement('div', { 'data-testid': 'video-embed', 'data-src': src }),
  VersionBadge: ({ version }: { version?: string }) =>
    React.createElement('span', { 'data-testid': 'version-badge' }, version),
}));

// ---------------------------------------------------------------------------
// Mock the pipeline-diagram SVG asset import (Vite static asset)
// ---------------------------------------------------------------------------
vi.mock('../../src/assets/pipeline-diagram.svg', () => ({
  default: '/mocked-pipeline-diagram.svg',
}));

// ---------------------------------------------------------------------------
// Mock app_routing to provide the PageComponentKey enum
// ---------------------------------------------------------------------------
vi.mock('../../src/app_routing', () => ({
  PageComponentKey: {
    Home: 'home',
    Cartographer: 'cartographer',
    Constrain: 'constrain',
    Ledger: 'ledger',
    Pact: 'pact',
    Advocate: 'advocate',
    Arbiter: 'arbiter',
    Baton: 'baton',
    Sentinel: 'sentinel',
    Chronicler: 'chronicler',
    Stigmergy: 'stigmergy',
    Apprentice: 'apprentice',
    Kindex: 'kindex',
  },
}));

// ---------------------------------------------------------------------------
// Imports under test — named exports from barrel
// ---------------------------------------------------------------------------
import {
  HomePage,
  CartographerPage,
  ConstrainPage,
  LedgerPage,
  PactPage,
  AdvocatePage,
  ArbiterPage,
  BatonPage,
  SentinelPage,
  ChroniclerPage,
  StigmergyPage,
  ApprenticePage,
  KindexPage,
  pageComponentMap,
} from '../../src/page_components';

// ---------------------------------------------------------------------------
// Also import individual modules to verify dual (named + default) exports
// ---------------------------------------------------------------------------
import HomePageDefault from '../../src/page_components/HomePage';
import CartographerPageDefault from '../../src/page_components/CartographerPage';
import ConstrainPageDefault from '../../src/page_components/ConstrainPage';
import LedgerPageDefault from '../../src/page_components/LedgerPage';
import PactPageDefault from '../../src/page_components/PactPage';
import AdvocatePageDefault from '../../src/page_components/AdvocatePage';
import ArbiterPageDefault from '../../src/page_components/ArbiterPage';
import BatonPageDefault from '../../src/page_components/BatonPage';
import SentinelPageDefault from '../../src/page_components/SentinelPage';
import ChroniclerPageDefault from '../../src/page_components/ChroniclerPage';
import StigmergyPageDefault from '../../src/page_components/StigmergyPage';
import ApprenticePageDefault from '../../src/page_components/ApprenticePage';
import KindexPageDefault from '../../src/page_components/KindexPage';

// ---------------------------------------------------------------------------
// Fixture: PageHeadingExpectation[]
// ---------------------------------------------------------------------------
interface PageHeadingExpectation {
  componentName: string;
  expectedHeading: string;
  pageKey: string;
  Component: React.ComponentType;
}

const PAGE_EXPECTATIONS: PageHeadingExpectation[] = [
  { componentName: 'HomePage', expectedHeading: 'exemplar.tools', pageKey: 'home', Component: HomePage },
  { componentName: 'CartographerPage', expectedHeading: 'Cartographer', pageKey: 'cartographer', Component: CartographerPage },
  { componentName: 'ConstrainPage', expectedHeading: 'Constrain', pageKey: 'constrain', Component: ConstrainPage },
  { componentName: 'LedgerPage', expectedHeading: 'Ledger', pageKey: 'ledger', Component: LedgerPage },
  { componentName: 'PactPage', expectedHeading: 'Pact', pageKey: 'pact', Component: PactPage },
  { componentName: 'AdvocatePage', expectedHeading: 'Advocate', pageKey: 'advocate', Component: AdvocatePage },
  { componentName: 'ArbiterPage', expectedHeading: 'Arbiter', pageKey: 'arbiter', Component: ArbiterPage },
  { componentName: 'BatonPage', expectedHeading: 'Baton', pageKey: 'baton', Component: BatonPage },
  { componentName: 'SentinelPage', expectedHeading: 'Sentinel', pageKey: 'sentinel', Component: SentinelPage },
  { componentName: 'ChroniclerPage', expectedHeading: 'Chronicler', pageKey: 'chronicler', Component: ChroniclerPage },
  { componentName: 'StigmergyPage', expectedHeading: 'Stigmergy', pageKey: 'stigmergy', Component: StigmergyPage },
  { componentName: 'ApprenticePage', expectedHeading: 'Apprentice', pageKey: 'apprentice', Component: ApprenticePage },
  { componentName: 'KindexPage', expectedHeading: 'Kindex', pageKey: 'kindex', Component: KindexPage },
];

const EXPECTED_KEYS = [
  'home', 'cartographer', 'constrain', 'ledger', 'pact',
  'advocate', 'arbiter', 'baton', 'sentinel', 'chronicler',
  'stigmergy', 'apprentice', 'kindex',
] as const;

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

beforeEach(() => {
  cleanup();
});

describe('Page Components — parameterized heading tests', () => {
  describe.each(PAGE_EXPECTATIONS)(
    '$componentName',
    ({ componentName, expectedHeading, Component }) => {
      it(`renders an h1 containing '${expectedHeading}'`, () => {
        render(React.createElement(Component));
        const heading = screen.getByRole('heading', { level: 1 });
        expect(heading).toBeDefined();
        expect(heading.textContent).toContain(
          expectedHeading,
        );
      });
    },
  );
});

describe('HomePage — pipeline diagram image', () => {
  it('renders an img with the correct alt text and src from the SVG import', () => {
    render(React.createElement(HomePage));
    const img = screen.getByAltText('exemplar.tools pipeline diagram') as HTMLImageElement;
    expect(img).toBeDefined();
    expect(img.tagName).toBe('IMG');
    // src should be the mocked SVG URL
    expect(img.getAttribute('src')).toBe('/mocked-pipeline-diagram.svg');
  });
});

describe('getPageComponentMap() — registry contract', () => {
  it('returns a map with exactly 13 entries', () => {
    const keys = Object.keys(pageComponentMap);
    expect(keys).toHaveLength(13);
  });

  it('keys match exactly the 13 PageComponentKey strings from the contract', () => {
    const keys = Object.keys(pageComponentMap).sort();
    const expected = [...EXPECTED_KEYS].sort();
    expect(keys).toEqual(expected);
  });

  it('every value is a function (React.ComponentType)', () => {
    for (const key of EXPECTED_KEYS) {
      const value = (pageComponentMap as Record<string, unknown>)[key];
      expect(typeof value).toBe('function');
    }
  });

  it('map values are identity-equal to the named-exported page components', () => {
    const identityMap: Record<string, React.ComponentType> = {
      home: HomePage,
      cartographer: CartographerPage,
      constrain: ConstrainPage,
      ledger: LedgerPage,
      pact: PactPage,
      advocate: AdvocatePage,
      arbiter: ArbiterPage,
      baton: BatonPage,
      sentinel: SentinelPage,
      chronicler: ChroniclerPage,
      stigmergy: StigmergyPage,
      apprentice: ApprenticePage,
      kindex: KindexPage,
    };
    for (const key of EXPECTED_KEYS) {
      expect(
        (pageComponentMap as Record<string, React.ComponentType>)[key],
        `pageComponentMap['${key}'] should be identity-equal to the named export`,
      ).toBe(identityMap[key]);
    }
  });

  it('no two keys in pageComponentMap point to the same component reference', () => {
    const values = Object.values(pageComponentMap);
    const uniqueValues = new Set(values);
    expect(uniqueValues.size).toBe(
      13,
    );
  });
});

describe('Render-each-from-map — non-empty HTML guard', () => {
  it.each(EXPECTED_KEYS)(
    'pageComponentMap["%s"] renders non-empty HTML',
    (key) => {
      const Component = (pageComponentMap as Record<string, React.ComponentType>)[key];
      const { container } = render(React.createElement(Component));
      expect(
        container.innerHTML.length,
        `Component for key '${key}' rendered empty HTML`,
      ).toBeGreaterThan(0);
      cleanup();
    },
  );
});

describe('Dual export invariant — named export === default export', () => {
  const dualExportPairs: Array<[string, React.ComponentType, React.ComponentType]> = [
    ['HomePage', HomePage, HomePageDefault],
    ['CartographerPage', CartographerPage, CartographerPageDefault],
    ['ConstrainPage', ConstrainPage, ConstrainPageDefault],
    ['LedgerPage', LedgerPage, LedgerPageDefault],
    ['PactPage', PactPage, PactPageDefault],
    ['AdvocatePage', AdvocatePage, AdvocatePageDefault],
    ['ArbiterPage', ArbiterPage, ArbiterPageDefault],
    ['BatonPage', BatonPage, BatonPageDefault],
    ['SentinelPage', SentinelPage, SentinelPageDefault],
    ['ChroniclerPage', ChroniclerPage, ChroniclerPageDefault],
    ['StigmergyPage', StigmergyPage, StigmergyPageDefault],
    ['ApprenticePage', ApprenticePage, ApprenticePageDefault],
    ['KindexPage', KindexPage, KindexPageDefault],
  ];

  it.each(dualExportPairs)(
    '%s named export is identical to its default export',
    (name, named, defaultExport) => {
      expect(
        named,
        `${name}: named export should be identity-equal to default export`,
      ).toBe(defaultExport);
    },
  );
});
