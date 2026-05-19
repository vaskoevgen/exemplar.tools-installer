
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render } from '@testing-library/react';

// Mock shared_components to isolate page components
vi.mock('shared_components', () => ({
  CodeBlock: ({ children, ...props }: any) => React.createElement('pre', { 'data-testid': 'codeblock', ...props }, children),
  CalloutBox: ({ children, ...props }: any) => React.createElement('div', { 'data-testid': 'calloutbox', ...props }, children),
  VideoEmbed: (props: any) => React.createElement('div', { 'data-testid': 'videoembed', ...props }),
  VersionBadge: (props: any) => React.createElement('span', { 'data-testid': 'versionbadge', ...props }),
}));

// Mock the SVG asset import
vi.mock('../../../src/page_components/assets/pipeline-diagram.svg', () => ({
  default: 'mocked-pipeline-diagram.svg',
}));

// Also mock via the src/assets path in case it's imported that way
vi.mock('../../../src/assets/pipeline-diagram.svg', () => ({
  default: 'mocked-pipeline-diagram.svg',
}));

describe('Page Components - Goodhart Tests', () => {
  it('goodhart: each component in pageComponentMap renders an h1 heading matching its key identity', async () => {
    // This catches: map with swapped components, map with dummy/placeholder components,
    // or a map that hardcodes keys but assigns wrong components to them.
    const barrel = await import('../../../src/page_components');
    const map = (barrel as any).pageComponentMap;

    const keyToExpectedHeading: Record<string, string> = {
      home: 'exemplar.tools',
      cartographer: 'Cartographer',
      constrain: 'Constrain',
      ledger: 'Ledger',
      pact: 'Pact',
      advocate: 'Advocate',
      arbiter: 'Arbiter',
      baton: 'Baton',
      sentinel: 'Sentinel',
      chronicler: 'Chronicler',
      stigmergy: 'Stigmergy',
      apprentice: 'Apprentice',
      kindex: 'Kindex',
    };

    for (const [key, expectedText] of Object.entries(keyToExpectedHeading)) {
      const Component = map[key];
      expect(Component, `map['${key}'] should be defined`).toBeDefined();
      const { container, unmount } = render(React.createElement(Component));
      const h1 = container.querySelector('h1');
      expect(h1, `map['${key}'] should render an h1`).not.toBeNull();
      expect(h1!.textContent, `map['${key}'] h1 should contain '${expectedText}'`).toContain(expectedText);
      unmount();
    }
  });

  it('goodhart: barrel index re-exports all 13 named page components as importable symbols', async () => {
    // Catches: barrel that only exports pageComponentMap but not the individual named components
    const barrel = await import('../../../src/page_components');

    const expectedNamedExports = [
      'HomePage',
      'CartographerPage',
      'ConstrainPage',
      'LedgerPage',
      'PactPage',
      'AdvocatePage',
      'ArbiterPage',
      'BatonPage',
      'SentinelPage',
      'ChroniclerPage',
      'StigmergyPage',
      'ApprenticePage',
      'KindexPage',
    ];

    for (const name of expectedNamedExports) {
      expect((barrel as any)[name], `barrel should export '${name}'`).toBeDefined();
      expect(typeof (barrel as any)[name], `'${name}' should be a function`).toBe('function');
    }
  });

  it('goodhart: barrel index exports pageComponentMap as a named export', async () => {
    const barrel = await import('../../../src/page_components');
    expect((barrel as any).pageComponentMap).toBeDefined();
    expect(typeof (barrel as any).pageComponentMap).toBe('object');
    expect(Object.keys((barrel as any).pageComponentMap).length).toBe(13);
  });

  it('goodhart: HomePage renders exactly one h1 element (not zero, not multiple)', async () => {
    const { HomePage } = await import('../../../src/page_components');
    const { container } = render(React.createElement(HomePage));
    const h1s = container.querySelectorAll('h1');
    expect(h1s.length).toBe(1);
  });

  it('goodhart: every page component renders exactly one h1 element', async () => {
    const barrel = await import('../../../src/page_components');
    const map = (barrel as any).pageComponentMap;

    for (const key of Object.keys(map)) {
      const Component = map[key];
      const { container, unmount } = render(React.createElement(Component));
      const h1s = container.querySelectorAll('h1');
      expect(h1s.length, `map['${key}'] should render exactly one h1`).toBe(1);
      unmount();
    }
  });

  it('goodhart: HomePage img alt text is exactly the contract-specified string', async () => {
    const { HomePage } = await import('../../../src/page_components');
    const { container } = render(React.createElement(HomePage));
    const imgs = container.querySelectorAll('img');
    const pipelineImg = Array.from(imgs).find(
      (img) => img.getAttribute('alt') === 'exemplar.tools pipeline diagram'
    );
    expect(pipelineImg, 'Should find img with exact alt text').not.toBeNull();

    // Ensure the alt is exact, not a superset
    expect(pipelineImg!.getAttribute('alt')).toBe('exemplar.tools pipeline diagram');
  });

  it('goodhart: HomePage pipeline diagram img src is a non-empty string', async () => {
    const { HomePage } = await import('../../../src/page_components');
    const { container } = render(React.createElement(HomePage));
    const img = container.querySelector('img[alt="exemplar.tools pipeline diagram"]');
    expect(img).not.toBeNull();
    const src = img!.getAttribute('src');
    expect(src, 'img src should be a string').toBeTruthy();
    expect(typeof src).toBe('string');
    expect(src!.length).toBeGreaterThan(0);
    expect(src).not.toBe('undefined');
    expect(src).not.toBe('null');
  });

  it('goodhart: page components render substantive content beyond just a heading', async () => {
    // Catches: minimal stub components that only render <h1>Name</h1>
    const barrel = await import('../../../src/page_components');
    const map = (barrel as any).pageComponentMap;

    // Check a subset of non-Home pages for substantive content
    const keysToCheck = ['cartographer', 'constrain', 'ledger', 'pact', 'advocate',
      'arbiter', 'baton', 'sentinel', 'chronicler', 'stigmergy', 'apprentice', 'kindex'];

    for (const key of keysToCheck) {
      const Component = map[key];
      const { container, unmount } = render(React.createElement(Component));
      const innerHTML = container.innerHTML;
      // A real documentation page should have significantly more content than just an h1
      expect(
        innerHTML.length,
        `map['${key}'] should render substantive content (got ${innerHTML.length} chars)`
      ).toBeGreaterThan(100);
      // Should have multiple child elements, not just a single h1
      const firstChild = container.firstElementChild;
      expect(firstChild, `map['${key}'] should have a root element`).not.toBeNull();
      if (firstChild) {
        const childCount = firstChild.querySelectorAll('*').length;
        expect(
          childCount,
          `map['${key}'] should have multiple descendant elements (got ${childCount})`
        ).toBeGreaterThan(2);
      }
      unmount();
    }
  });

  it('goodhart: pageComponentMap has no keys beyond the 13 specified PageComponentKey values', async () => {
    const barrel = await import('../../../src/page_components');
    const map = (barrel as any).pageComponentMap;
    const validKeys = new Set([
      'home', 'cartographer', 'constrain', 'ledger', 'pact', 'advocate',
      'arbiter', 'baton', 'sentinel', 'chronicler', 'stigmergy', 'apprentice', 'kindex',
    ]);
    const actualKeys = Object.keys(map);
    expect(actualKeys.length).toBe(13);
    for (const key of actualKeys) {
      expect(validKeys.has(key), `Unexpected key '${key}' in pageComponentMap`).toBe(true);
    }
  });

  it('goodhart: pageComponentMap keys are lowercase strings, not PascalCase or component names', async () => {
    const barrel = await import('../../../src/page_components');
    const map = (barrel as any).pageComponentMap;
    const keys = Object.keys(map);

    for (const key of keys) {
      expect(key, `Key '${key}' should be lowercase`).toBe(key.toLowerCase());
      expect(key.endsWith('Page'), `Key '${key}' should not end with 'Page'`).toBe(false);
    }

    // Specifically verify these are not PascalCase
    expect(keys).not.toContain('Home');
    expect(keys).not.toContain('Cartographer');
    expect(keys).toContain('home');
    expect(keys).toContain('cartographer');
  });

  it('goodhart: dual export (named === default) for all 12 non-Home page modules', async () => {
    // The visible test only checks HomePage. This checks ALL other page modules.
    const moduleMap: Record<string, string> = {
      CartographerPage: '../../../src/page_components/CartographerPage',
      ConstrainPage: '../../../src/page_components/ConstrainPage',
      LedgerPage: '../../../src/page_components/LedgerPage',
      PactPage: '../../../src/page_components/PactPage',
      AdvocatePage: '../../../src/page_components/AdvocatePage',
      ArbiterPage: '../../../src/page_components/ArbiterPage',
      BatonPage: '../../../src/page_components/BatonPage',
      SentinelPage: '../../../src/page_components/SentinelPage',
      ChroniclerPage: '../../../src/page_components/ChroniclerPage',
      StigmergyPage: '../../../src/page_components/StigmergyPage',
      ApprenticePage: '../../../src/page_components/ApprenticePage',
      KindexPage: '../../../src/page_components/KindexPage',
    };

    for (const [name, path] of Object.entries(moduleMap)) {
      try {
        const mod = await import(path);
        expect(mod[name], `${name} should have a named export`).toBeDefined();
        expect(mod.default, `${name} should have a default export`).toBeDefined();
        expect(mod[name], `${name} named and default exports should be identical`).toBe(mod.default);
      } catch (e) {
        // If the path doesn't resolve, try pages/ subfolder pattern
        // This is acceptable — the test will fail if neither works
        throw new Error(`Could not import ${name} from ${path}: ${e}`);
      }
    }
  });

  it('goodhart: all page components are callable with no arguments and produce valid React elements', async () => {
    // Catches: components that require props but happen to work in visible tests due to mocking
    const barrel = await import('../../../src/page_components');
    const map = (barrel as any).pageComponentMap;

    for (const [key, Component] of Object.entries(map)) {
      expect(() => {
        const { unmount } = render(React.createElement(Component as React.ComponentType));
        unmount();
      }, `map['${key}'] should render without errors when given no props`).not.toThrow();
    }
  });

  it('goodhart: all h1 headings in rendered map components have distinct text', async () => {
    // Catches: all components rendering the same generic heading
    const barrel = await import('../../../src/page_components');
    const map = (barrel as any).pageComponentMap;
    const headingTexts = new Set<string>();

    for (const [key, Component] of Object.entries(map)) {
      const { container, unmount } = render(React.createElement(Component as React.ComponentType));
      const h1 = container.querySelector('h1');
      expect(h1, `map['${key}'] should render an h1`).not.toBeNull();
      headingTexts.add(h1!.textContent || '');
      unmount();
    }

    // All 13 headings should be distinct
    expect(headingTexts.size, 'All 13 page components should have distinct h1 text').toBe(13);
  });

  it('goodhart: HomePage renders substantive content beyond just heading and img', async () => {
    const { HomePage } = await import('../../../src/page_components');
    const { container } = render(React.createElement(HomePage));

    // Should have text beyond just the heading
    const textContent = container.textContent || '';
    // Remove heading text and check there's more
    const withoutHeading = textContent.replace('exemplar.tools', '');
    expect(
      withoutHeading.trim().length,
      'HomePage should contain text content beyond just the heading'
    ).toBeGreaterThan(20);

    // Should have multiple elements
    const allElements = container.querySelectorAll('*');
    expect(allElements.length, 'HomePage should render multiple DOM elements').toBeGreaterThan(5);
  });
});
