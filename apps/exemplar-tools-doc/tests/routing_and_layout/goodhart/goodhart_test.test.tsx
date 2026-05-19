
import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import {
  ensureLeadingSlash,
  getNavLinkClassName,
  ROUTE_ENTRY_LIST,
  ROUTE_SLUG_MAP,
  Sidebar,
  Layout,
  createAppRouter,
} from '../../../src/routing_and_layout';

describe('Routing, Layout & Navigation — Goodhart adversarial tests', () => {
  // === ensureLeadingSlash: input-space exploration beyond visible values ===

  it('goodhart: ensureLeadingSlash should prepend slash to multi-segment bare paths', () => {
    expect(ensureLeadingSlash('foo/bar/baz')).toBe('/foo/bar/baz');
  });

  it('goodhart: ensureLeadingSlash should handle a single non-slash character', () => {
    expect(ensureLeadingSlash('x')).toBe('/x');
  });

  it('goodhart: ensureLeadingSlash should prepend slash to whitespace-only strings', () => {
    expect(ensureLeadingSlash(' ')).toBe('/ ');
    expect(ensureLeadingSlash(' ').startsWith('/')).toBe(true);
  });

  it('goodhart: ensureLeadingSlash should preserve trailing slashes without modification', () => {
    expect(ensureLeadingSlash('/cartographer/')).toBe('/cartographer/');
    expect(ensureLeadingSlash('cartographer/')).toBe('/cartographer/');
  });

  it('goodhart: ensureLeadingSlash should handle numeric string inputs', () => {
    expect(ensureLeadingSlash('123')).toBe('/123');
  });

  it('goodhart: ensureLeadingSlash should handle special characters, only caring about leading slash', () => {
    expect(ensureLeadingSlash('#hash')).toBe('/#hash');
    expect(ensureLeadingSlash('?query=1')).toBe('/?query=1');
  });

  it('goodhart: ensureLeadingSlash should not modify triple slashes since input starts with /', () => {
    expect(ensureLeadingSlash('///triple')).toBe('///triple');
  });

  it('goodhart: ensureLeadingSlash is idempotent when applied to every actual slug in ROUTE_SLUG_MAP', () => {
    Object.values(ROUTE_SLUG_MAP).forEach((slug: string) => {
      expect(ensureLeadingSlash(ensureLeadingSlash(slug))).toBe(ensureLeadingSlash(slug));
    });
  });

  it('goodhart: ensureLeadingSlash applied to ROUTE_SLUG_MAP values returns them unchanged', () => {
    Object.values(ROUTE_SLUG_MAP).forEach((slug: string) => {
      expect(ensureLeadingSlash(slug)).toBe(slug);
    });
  });

  // === ROUTE_ENTRY_LIST: structure and content completeness ===

  it('goodhart: ROUTE_ENTRY_LIST must contain entries for every defined StepId', () => {
    const expectedIds = ['home', 'cartographer', 'constrain', 'ledger', 'pact', 'advocate', 'arbiter', 'baton', 'sentinel', 'chronicler', 'stigmergy', 'apprentice', 'kindex'];
    const actualIds = ROUTE_ENTRY_LIST.map((e: any) => e.stepId);
    expectedIds.forEach(id => expect(actualIds).toContain(id));
  });

  it('goodhart: ROUTE_ENTRY_LIST must contain all 13 expected human-readable labels', () => {
    const expectedLabels = [
      'Home', 'Step 0 — Cartographer', 'Step 1a — Constrain', 'Step 1b — Ledger',
      'Step 2a — Pact', 'Step 2b — Advocate', 'Step 3 — Arbiter', 'Step 4 — Baton',
      'Step 5a — Sentinel', 'Step 5b — Chronicler', 'Step 5c — Stigmergy',
      'Step 6 — Apprentice', 'Step 7 — Kindex'
    ];
    const actualLabels = ROUTE_ENTRY_LIST.map((e: any) => e.label);
    expectedLabels.forEach(l => expect(actualLabels).toContain(l));
  });

  it('goodhart: ROUTE_ENTRY_LIST must contain all 13 expected slug values', () => {
    const expectedSlugs = ['/', '/cartographer', '/constrain', '/ledger', '/pact', '/advocate', '/arbiter', '/baton', '/sentinel', '/chronicler', '/stigmergy', '/apprentice', '/kindex'];
    const actualSlugs = ROUTE_ENTRY_LIST.map((e: any) => e.slug);
    expectedSlugs.forEach(s => expect(actualSlugs).toContain(s));
  });

  it('goodhart: Each RouteEntry must have exactly the three required fields with string types', () => {
    ROUTE_ENTRY_LIST.forEach((entry: any) => {
      expect(entry).toHaveProperty('stepId');
      expect(entry).toHaveProperty('slug');
      expect(entry).toHaveProperty('label');
      expect(typeof entry.stepId).toBe('string');
      expect(typeof entry.slug).toBe('string');
      expect(typeof entry.label).toBe('string');
    });
  });

  it('goodhart: Each entry slug must correspond to its stepId — stepId "X" maps to slug "/X" except home maps to "/"', () => {
    ROUTE_ENTRY_LIST.forEach((entry: any) => {
      if (entry.stepId === 'home') {
        expect(entry.slug).toBe('/');
      } else {
        expect(entry.slug).toBe('/' + entry.stepId);
      }
    });
  });

  it('goodhart: Each stepId must map to its correct specific label', () => {
    const mapping = Object.fromEntries(ROUTE_ENTRY_LIST.map((e: any) => [e.stepId, e.label]));
    expect(mapping.home).toBe('Home');
    expect(mapping.cartographer).toBe('Step 0 — Cartographer');
    expect(mapping.constrain).toBe('Step 1a — Constrain');
    expect(mapping.ledger).toBe('Step 1b — Ledger');
    expect(mapping.pact).toBe('Step 2a — Pact');
    expect(mapping.advocate).toBe('Step 2b — Advocate');
    expect(mapping.arbiter).toBe('Step 3 — Arbiter');
    expect(mapping.baton).toBe('Step 4 — Baton');
    expect(mapping.sentinel).toBe('Step 5a — Sentinel');
    expect(mapping.chronicler).toBe('Step 5b — Chronicler');
    expect(mapping.stigmergy).toBe('Step 5c — Stigmergy');
    expect(mapping.apprentice).toBe('Step 6 — Apprentice');
    expect(mapping.kindex).toBe('Step 7 — Kindex');
  });

  it('goodhart: ROUTE_ENTRY_LIST entries must follow the exact pipeline ordering', () => {
    const expectedOrder = ['home', 'cartographer', 'constrain', 'ledger', 'pact', 'advocate', 'arbiter', 'baton', 'sentinel', 'chronicler', 'stigmergy', 'apprentice', 'kindex'];
    const actualOrder = ROUTE_ENTRY_LIST.map((e: any) => e.stepId);
    expect(actualOrder).toEqual(expectedOrder);
  });

  it('goodhart: All labels across ROUTE_ENTRY_LIST must be unique', () => {
    const labels = ROUTE_ENTRY_LIST.map((e: any) => e.label);
    const uniqueLabels = new Set(labels);
    expect(uniqueLabels.size).toBe(labels.length);
  });

  it('goodhart: All stepIds across ROUTE_ENTRY_LIST must be unique', () => {
    const ids = ROUTE_ENTRY_LIST.map((e: any) => e.stepId);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(ids.length);
  });

  // === ROUTE_SLUG_MAP: completeness and correctness ===

  it('goodhart: ROUTE_SLUG_MAP must have exactly the 13 StepId keys', () => {
    const expectedKeys = ['home', 'cartographer', 'constrain', 'ledger', 'pact', 'advocate', 'arbiter', 'baton', 'sentinel', 'chronicler', 'stigmergy', 'apprentice', 'kindex'];
    const actualKeys = Object.keys(ROUTE_SLUG_MAP);
    expect(actualKeys.sort()).toEqual(expectedKeys.sort());
    expect(actualKeys.length).toBe(13);
  });

  it('goodhart: ROUTE_SLUG_MAP.home must be exactly "/"', () => {
    expect((ROUTE_SLUG_MAP as any).home).toBe('/');
  });

  it('goodhart: ROUTE_SLUG_MAP values must match expected slugs for each stepId', () => {
    expect((ROUTE_SLUG_MAP as any).cartographer).toBe('/cartographer');
    expect((ROUTE_SLUG_MAP as any).constrain).toBe('/constrain');
    expect((ROUTE_SLUG_MAP as any).ledger).toBe('/ledger');
    expect((ROUTE_SLUG_MAP as any).pact).toBe('/pact');
    expect((ROUTE_SLUG_MAP as any).advocate).toBe('/advocate');
    expect((ROUTE_SLUG_MAP as any).arbiter).toBe('/arbiter');
    expect((ROUTE_SLUG_MAP as any).baton).toBe('/baton');
    expect((ROUTE_SLUG_MAP as any).sentinel).toBe('/sentinel');
    expect((ROUTE_SLUG_MAP as any).chronicler).toBe('/chronicler');
    expect((ROUTE_SLUG_MAP as any).stigmergy).toBe('/stigmergy');
    expect((ROUTE_SLUG_MAP as any).apprentice).toBe('/apprentice');
    expect((ROUTE_SLUG_MAP as any).kindex).toBe('/kindex');
  });

  it('goodhart: Non-home slugs in ROUTE_SLUG_MAP should not have trailing slashes', () => {
    Object.entries(ROUTE_SLUG_MAP).forEach(([key, slug]: [string, any]) => {
      if (key !== 'home') {
        expect(slug.endsWith('/')).toBe(false);
      }
    });
  });

  // === getNavLinkClassName: type and content validation ===

  it('goodhart: getNavLinkClassName must return string type for both states', () => {
    expect(typeof getNavLinkClassName(true)).toBe('string');
    expect(typeof getNavLinkClassName(false)).toBe('string');
  });

  it('goodhart: getNavLinkClassName should not return strings containing "undefined"', () => {
    expect(getNavLinkClassName(true)).not.toContain('undefined');
    expect(getNavLinkClassName(false)).not.toContain('undefined');
  });

  it('goodhart: Active NavLink className should contain a visual emphasis or color class', () => {
    const active = getNavLinkClassName(true);
    expect(
      active.includes('font-bold') ||
      active.includes('font-semibold') ||
      active.includes('bg-') ||
      active.includes('text-')
    ).toBe(true);
  });

  // === Sidebar: deeper structural checks ===

  it('goodhart: Sidebar should render semantic nav markup', () => {
    const { container } = render(
      React.createElement(MemoryRouter, { initialEntries: ['/'] },
        React.createElement(Sidebar)
      )
    );
    const nav = container.querySelector('nav');
    // Sidebar should use a <nav> element for accessibility
    expect(nav).not.toBeNull();
  });

  it('goodhart: Sidebar NavLinks for non-home routes should link to correct paths (spot-check middle entries)', () => {
    const { container } = render(
      React.createElement(MemoryRouter, { initialEntries: ['/'] },
        React.createElement(Sidebar)
      )
    );
    const links = container.querySelectorAll('a');
    // Spot-check that specific middle entries have correct hrefs
    const hrefs = Array.from(links).map(a => a.getAttribute('href'));
    expect(hrefs).toContain('/arbiter');
    expect(hrefs).toContain('/stigmergy');
    expect(hrefs).toContain('/kindex');
  });

  it('goodhart: Sidebar should render the label text with the em-dash character, not a plain hyphen', () => {
    const { container } = render(
      React.createElement(MemoryRouter, { initialEntries: ['/'] },
        React.createElement(Sidebar)
      )
    );
    // Labels use em-dash (—) not hyphen (-) or en-dash (–)
    const textContent = container.textContent || '';
    expect(textContent).toContain('Step 0 — Cartographer');
    expect(textContent).toContain('Step 7 — Kindex');
  });

  // === createAppRouter: deeper structural checks ===

  it('goodhart: createAppRouter child routes should have specific paths matching slug.slice(1)', () => {
    const router = createAppRouter();
    const routes = (router as any).routes || [];
    const parentRoute = routes[0];
    const children = parentRoute?.children || [];

    // Filter out the index route, check non-home paths
    const nonIndexChildren = children.filter((c: any) => !c.index);
    const expectedPaths = ROUTE_ENTRY_LIST
      .filter((e: any) => e.stepId !== 'home')
      .map((e: any) => e.slug.slice(1));

    const actualPaths = nonIndexChildren.map((c: any) => c.path);
    expectedPaths.forEach((p: string) => {
      expect(actualPaths).toContain(p);
    });
  });

  it('goodhart: createAppRouter parent route must have path exactly "/"', () => {
    const router = createAppRouter();
    const routes = (router as any).routes || [];
    const parentRoute = routes[0];
    expect(parentRoute.path).toBe('/');
  });

  it('goodhart: createAppRouter all child routes must have defined elements', () => {
    const router = createAppRouter();
    const routes = (router as any).routes || [];
    const parentRoute = routes[0];
    const children = parentRoute?.children || [];
    expect(children.length).toBe(13);
    children.forEach((child: any) => {
      // Each child must have an element (or lazy, for lazy-loaded routes)
      expect(child.element || child.lazy).toBeTruthy();
    });
  });
});
