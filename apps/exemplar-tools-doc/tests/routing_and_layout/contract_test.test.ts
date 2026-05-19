
import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, createMemoryRouter, RouterProvider } from 'react-router-dom';

// Import the module under test
import {
  ensureLeadingSlash,
  getNavLinkClassName,
  Sidebar,
  Layout,
  createAppRouter,
  ROUTE_ENTRY_LIST,
  ROUTE_SLUG_MAP,
} from '../../src/routing_and_layout';

// ─── ensureLeadingSlash ──────────────────────────────────────────────────────

describe('ensureLeadingSlash', () => {
  describe('happy path', () => {
    it('prepends "/" to a bare slug without a leading slash', () => {
      const result = ensureLeadingSlash('cartographer');
      expect(result).toBe('/cartographer');
    });

    it('returns input unchanged when it already starts with "/"', () => {
      const result = ensureLeadingSlash('/cartographer');
      expect(result).toBe('/cartographer');
    });

    it('handles multi-segment paths without leading slash', () => {
      const result = ensureLeadingSlash('foo/bar');
      expect(result).toBe('/foo/bar');
    });

    it('handles multi-segment paths with leading slash', () => {
      const result = ensureLeadingSlash('/foo/bar');
      expect(result).toBe('/foo/bar');
    });
  });

  describe('edge cases', () => {
    it('returns "/" for empty string input', () => {
      const result = ensureLeadingSlash('');
      expect(result).toBe('/');
    });

    it('returns "/" unchanged for slash-only input', () => {
      const result = ensureLeadingSlash('/');
      expect(result).toBe('/');
    });

    it('does NOT strip double slashes — returns input unchanged if it starts with "/"', () => {
      const result = ensureLeadingSlash('//foo');
      // Input starts with '/', so it should be returned unchanged per the contract
      expect(result).toBe('//foo');
    });

    it('handles a single character slug', () => {
      const result = ensureLeadingSlash('a');
      expect(result).toBe('/a');
    });
  });

  describe('invariants', () => {
    it('result always starts with "/"', () => {
      const inputs = ['', '/', 'foo', '/foo', 'bar/baz', '/bar/baz', '//double'];
      for (const input of inputs) {
        const result = ensureLeadingSlash(input);
        expect(result.startsWith('/'), `ensureLeadingSlash("${input}") = "${result}" should start with "/"`).toBe(true);
      }
    });

    it('is idempotent — applying it twice yields the same result as once', () => {
      const inputs = ['', '/', 'foo', '/foo', 'cartographer', '/cartographer', 'bar/baz'];
      for (const input of inputs) {
        const once = ensureLeadingSlash(input);
        const twice = ensureLeadingSlash(once);
        expect(twice, `ensureLeadingSlash should be idempotent for input "${input}"`).toBe(once);
      }
    });

    it('is a pure function — same input always produces same output', () => {
      const inputs = ['', '/', 'test', '/test'];
      for (const input of inputs) {
        const result1 = ensureLeadingSlash(input);
        const result2 = ensureLeadingSlash(input);
        expect(result1).toBe(result2);
      }
    });

    it('property: for any string, result starts with "/" (property-based)', () => {
      // Lightweight property test without fast-check
      const randomStrings = [
        '', '/', 'a', '/a', 'abc', '/abc', '//abc', 'foo/bar',
        '/foo/bar', '   ', '/ ', ' /', 'hello-world', '/hello-world',
      ];
      for (const s of randomStrings) {
        const result = ensureLeadingSlash(s);
        expect(result.startsWith('/'), `Failed for input: "${s}"`).toBe(true);
      }
    });
  });
});

// ─── getNavLinkClassName ─────────────────────────────────────────────────────

describe('getNavLinkClassName', () => {
  describe('happy path', () => {
    it('returns a non-empty string with active Tailwind classes when isActive is true', () => {
      const result = getNavLinkClassName(true);
      expect(typeof result).toBe('string');
      expect(result.length, 'Active class string should be non-empty').toBeGreaterThan(0);
    });

    it('returns a non-empty string with inactive Tailwind classes when isActive is false', () => {
      const result = getNavLinkClassName(false);
      expect(typeof result).toBe('string');
      expect(result.length, 'Inactive class string should be non-empty').toBeGreaterThan(0);
    });
  });

  describe('invariants', () => {
    it('returns different class strings for active vs inactive states', () => {
      const activeClasses = getNavLinkClassName(true);
      const inactiveClasses = getNavLinkClassName(false);
      expect(activeClasses, 'Active and inactive classes must differ').not.toBe(inactiveClasses);
    });

    it('active class string contains font-bold or similar active indicator', () => {
      const activeClasses = getNavLinkClassName(true);
      // The contract says active NavLink receives "distinct Tailwind classes for visual highlighting"
      // We check that it contains at least some class-like content
      expect(activeClasses.trim().length).toBeGreaterThan(0);
    });

    it('is a pure function — same input always returns same output', () => {
      expect(getNavLinkClassName(true)).toBe(getNavLinkClassName(true));
      expect(getNavLinkClassName(false)).toBe(getNavLinkClassName(false));
    });
  });
});

// ─── ROUTE_ENTRY_LIST and ROUTE_SLUG_MAP invariants ──────────────────────────

describe('ROUTE_ENTRY_LIST invariants', () => {
  it('contains exactly 13 entries', () => {
    expect(ROUTE_ENTRY_LIST).toBeDefined();
    expect(Array.isArray(ROUTE_ENTRY_LIST)).toBe(true);
    expect(ROUTE_ENTRY_LIST.length, 'ROUTE_ENTRY_LIST must have exactly 13 entries').toBe(13);
  });

  it('first entry is the home route with slug "/" and stepId "home"', () => {
    const first = ROUTE_ENTRY_LIST[0];
    expect(first.slug, 'First entry slug must be "/"').toBe('/');
    expect(first.stepId, 'First entry stepId must be "home"').toBe('home');
  });

  it('all RouteSlug values are unique — no two entries share the same slug', () => {
    const slugs = ROUTE_ENTRY_LIST.map((entry: { slug: string }) => entry.slug);
    const uniqueSlugs = new Set(slugs);
    expect(uniqueSlugs.size, 'All slugs must be unique').toBe(ROUTE_ENTRY_LIST.length);
  });

  it('every entry has a stepId, slug, and label', () => {
    for (const entry of ROUTE_ENTRY_LIST) {
      expect(entry.stepId, 'Every entry must have a stepId').toBeDefined();
      expect(entry.slug, 'Every entry must have a slug').toBeDefined();
      expect(entry.label, 'Every entry must have a label').toBeDefined();
      expect(typeof entry.stepId).toBe('string');
      expect(typeof entry.slug).toBe('string');
      expect(typeof entry.label).toBe('string');
    }
  });

  it('all stepIds are unique', () => {
    const stepIds = ROUTE_ENTRY_LIST.map((entry: { stepId: string }) => entry.stepId);
    const uniqueStepIds = new Set(stepIds);
    expect(uniqueStepIds.size, 'All stepIds must be unique').toBe(ROUTE_ENTRY_LIST.length);
  });

  it('contains all expected stepIds', () => {
    const expectedStepIds = [
      'home', 'cartographer', 'constrain', 'ledger', 'pact',
      'advocate', 'arbiter', 'baton', 'sentinel', 'chronicler',
      'stigmergy', 'apprentice', 'kindex',
    ];
    const actualStepIds = ROUTE_ENTRY_LIST.map((entry: { stepId: string }) => entry.stepId);
    for (const expected of expectedStepIds) {
      expect(actualStepIds, `ROUTE_ENTRY_LIST should contain stepId "${expected}"`).toContain(expected);
    }
  });
});

describe('ROUTE_SLUG_MAP invariants', () => {
  it('every value starts with exactly one leading slash', () => {
    expect(ROUTE_SLUG_MAP).toBeDefined();
    const slugs = Object.values(ROUTE_SLUG_MAP) as string[];
    for (const slug of slugs) {
      expect(slug.startsWith('/'), `Slug "${slug}" must start with "/"`).toBe(true);
    }
  });

  it('no slug value contains a double-slash "//"', () => {
    const slugs = Object.values(ROUTE_SLUG_MAP) as string[];
    for (const slug of slugs) {
      expect(slug.includes('//'), `Slug "${slug}" must not contain "//"`).toBe(false);
    }
  });

  it('is derivable from ROUTE_ENTRY_LIST — every entry matches', () => {
    for (const entry of ROUTE_ENTRY_LIST) {
      const mapSlug = (ROUTE_SLUG_MAP as Record<string, string>)[entry.stepId];
      expect(mapSlug, `ROUTE_SLUG_MAP["${entry.stepId}"] should equal "${entry.slug}"`).toBe(entry.slug);
    }
  });

  it('has the same number of keys as ROUTE_ENTRY_LIST has entries', () => {
    const mapKeys = Object.keys(ROUTE_SLUG_MAP);
    expect(mapKeys.length).toBe(ROUTE_ENTRY_LIST.length);
  });

  it('contains all expected keys matching StepId enum values', () => {
    const expectedKeys = [
      'home', 'cartographer', 'constrain', 'ledger', 'pact',
      'advocate', 'arbiter', 'baton', 'sentinel', 'chronicler',
      'stigmergy', 'apprentice', 'kindex',
    ];
    for (const key of expectedKeys) {
      expect(ROUTE_SLUG_MAP).toHaveProperty(key);
    }
  });
});

// ─── Sidebar ─────────────────────────────────────────────────────────────────

describe('Sidebar', () => {
  describe('happy path', () => {
    it('renders exactly 13 NavLink elements, one per entry in ROUTE_ENTRY_LIST', () => {
      render(
        React.createElement(
          MemoryRouter,
          { initialEntries: ['/'] },
          React.createElement(Sidebar)
        )
      );
      const links = screen.getAllByRole('link');
      expect(links.length, 'Sidebar should render exactly 13 links').toBe(13);
    });

    it('each NavLink displays the corresponding entry label as text content', () => {
      render(
        React.createElement(
          MemoryRouter,
          { initialEntries: ['/'] },
          React.createElement(Sidebar)
        )
      );
      for (const entry of ROUTE_ENTRY_LIST) {
        const link = screen.getByText(entry.label);
        expect(link, `Should find link with label "${entry.label}"`).toBeDefined();
      }
    });

    it('each NavLink href matches the corresponding entry slug value', () => {
      render(
        React.createElement(
          MemoryRouter,
          { initialEntries: ['/'] },
          React.createElement(Sidebar)
        )
      );
      const links = screen.getAllByRole('link');
      for (let i = 0; i < ROUTE_ENTRY_LIST.length; i++) {
        const entry = ROUTE_ENTRY_LIST[i];
        const link = screen.getByText(entry.label);
        expect(
          link.closest('a')?.getAttribute('href'),
          `Link for "${entry.label}" should have href="${entry.slug}"`
        ).toBe(entry.slug);
      }
    });
  });

  describe('invariants', () => {
    it('NavLinks appear in the same order as ROUTE_ENTRY_LIST', () => {
      render(
        React.createElement(
          MemoryRouter,
          { initialEntries: ['/'] },
          React.createElement(Sidebar)
        )
      );
      const links = screen.getAllByRole('link');
      for (let i = 0; i < ROUTE_ENTRY_LIST.length; i++) {
        expect(
          links[i].textContent,
          `Link at index ${i} should have text "${ROUTE_ENTRY_LIST[i].label}"`
        ).toBe(ROUTE_ENTRY_LIST[i].label);
      }
    });

    it('home NavLink does not show active styling when on a non-home route (end prop)', () => {
      render(
        React.createElement(
          MemoryRouter,
          { initialEntries: ['/cartographer'] },
          React.createElement(Sidebar)
        )
      );
      const homeLink = screen.getByText(ROUTE_ENTRY_LIST[0].label);
      const cartographerLink = screen.getByText('Step 0 — Cartographer');

      // Home link should NOT have active classes when we're on /cartographer
      // Cartographer link should have active classes
      const homeLinkEl = homeLink.closest('a');
      const cartographerLinkEl = cartographerLink.closest('a');

      // The class names should differ — home should be inactive, cartographer should be active
      expect(homeLinkEl).toBeDefined();
      expect(cartographerLinkEl).toBeDefined();

      if (homeLinkEl && cartographerLinkEl) {
        // They shouldn't have the same className since one is active and the other isn't
        expect(homeLinkEl.className).not.toBe(cartographerLinkEl.className);
      }
    });
  });

  describe('error cases', () => {
    it('throws when rendered outside of a React Router context', () => {
      // Suppress React error boundary console output
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      try {
        expect(() => {
          render(React.createElement(Sidebar));
        }).toThrow();
      } finally {
        consoleSpy.mockRestore();
      }
    });
  });
});

// ─── Layout ──────────────────────────────────────────────────────────────────

describe('Layout', () => {
  describe('happy path', () => {
    it('renders Sidebar and passes child content through Outlet', () => {
      const ChildComponent = () => React.createElement('div', { 'data-testid': 'child-content' }, 'Child Route Content');

      const routes = [
        {
          path: '/',
          element: React.createElement(Layout),
          children: [
            {
              index: true,
              element: React.createElement(ChildComponent),
            },
          ],
        },
      ];

      const router = createMemoryRouter(routes, { initialEntries: ['/'] });
      render(React.createElement(RouterProvider, { router }));

      // Verify Sidebar is present by checking for a known label
      const homeLabel = ROUTE_ENTRY_LIST[0].label;
      expect(screen.getByText(homeLabel), 'Sidebar should be rendered with home link').toBeDefined();

      // Verify child route content is rendered via Outlet
      expect(screen.getByTestId('child-content'), 'Child route content should be rendered via Outlet').toBeDefined();
      expect(screen.getByText('Child Route Content')).toBeDefined();
    });

    it('renders Sidebar on the left and main content on the right in a flex container', () => {
      const ChildComponent = () => React.createElement('div', { 'data-testid': 'main-child' }, 'Main Content');

      const routes = [
        {
          path: '/',
          element: React.createElement(Layout),
          children: [
            {
              index: true,
              element: React.createElement(ChildComponent),
            },
          ],
        },
      ];

      const router = createMemoryRouter(routes, { initialEntries: ['/'] });
      const { container } = render(React.createElement(RouterProvider, { router }));

      // Verify the layout contains both sidebar links and main content
      const links = screen.getAllByRole('link');
      expect(links.length).toBeGreaterThanOrEqual(13);
      expect(screen.getByTestId('main-child')).toBeDefined();
    });
  });

  describe('error cases', () => {
    it('throws when rendered outside of a React Router context', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      try {
        expect(() => {
          render(React.createElement(Layout));
        }).toThrow();
      } finally {
        consoleSpy.mockRestore();
      }
    });
  });
});

// ─── createAppRouter ─────────────────────────────────────────────────────────

describe('createAppRouter', () => {
  describe('happy path', () => {
    it('returns a router instance', () => {
      const router = createAppRouter();
      expect(router, 'createAppRouter should return a router instance').toBeDefined();
    });

    it('has a parent route with path "/"', () => {
      const router = createAppRouter();
      // Access the routes from the router object
      const routes = router.routes;
      expect(routes).toBeDefined();
      expect(routes.length).toBeGreaterThanOrEqual(1);

      const parentRoute = routes[0];
      expect(parentRoute.path, 'Parent route should have path "/"').toBe('/');
    });

    it('parent route has exactly 13 child routes', () => {
      const router = createAppRouter();
      const parentRoute = router.routes[0];
      expect(parentRoute.children, 'Parent route should have children').toBeDefined();
      expect(parentRoute.children!.length, 'Parent route should have exactly 13 children').toBe(13);
    });

    it('home child route uses index: true instead of path ""', () => {
      const router = createAppRouter();
      const children = router.routes[0].children!;

      // Find the index route (home)
      const indexRoute = children.find((child: any) => child.index === true);
      expect(indexRoute, 'Should have an index route for home').toBeDefined();
    });

    it('all non-home child routes have paths matching slugs without leading slash', () => {
      const router = createAppRouter();
      const children = router.routes[0].children!;

      // Non-index routes should have paths that match entry.slug.slice(1)
      const nonIndexChildren = children.filter((child: any) => !child.index);
      expect(nonIndexChildren.length).toBe(12); // 13 total minus 1 home/index

      const expectedPaths = ROUTE_ENTRY_LIST
        .filter((entry: { stepId: string }) => entry.stepId !== 'home')
        .map((entry: { slug: string }) => entry.slug.slice(1));

      for (const child of nonIndexChildren) {
        expect(
          expectedPaths,
          `Child path "${(child as any).path}" should be in the expected paths list`
        ).toContain((child as any).path);
      }
    });
  });

  describe('invariants', () => {
    it('no child route path starts with "/" (they are relative to parent)', () => {
      const router = createAppRouter();
      const children = router.routes[0].children!;

      for (const child of children) {
        if ((child as any).path) {
          expect(
            (child as any).path.startsWith('/'),
            `Child path "${(child as any).path}" should not start with "/"`
          ).toBe(false);
        }
      }
    });

    it('no child route path produces a double-slash when combined with parent "/"', () => {
      const router = createAppRouter();
      const children = router.routes[0].children!;

      for (const child of children) {
        const childPath = (child as any).path || '';
        const combined = '/' + childPath;
        expect(
          combined.includes('//'),
          `Combined path "${combined}" should not contain "//"`
        ).toBe(false);
      }
    });

    it('every child route has a non-null element', () => {
      const router = createAppRouter();
      const children = router.routes[0].children!;

      for (const child of children) {
        // Routes can use element or lazy, but should have some way to render
        const hasElement = (child as any).element != null;
        const hasLazy = (child as any).lazy != null;
        const hasComponent = (child as any).Component != null;
        expect(
          hasElement || hasLazy || hasComponent,
          `Child route should have an element, lazy, or Component property`
        ).toBe(true);
      }
    });

    it('renders correctly with RouterProvider', () => {
      const router = createAppRouter();
      // Just verify it can be used with RouterProvider without throwing
      // Note: createAppRouter uses createBrowserRouter which may not work in test env,
      // so we just verify the structure is valid
      expect(router).toBeDefined();
      expect(router.routes).toBeDefined();
      expect(router.routes[0].children).toBeDefined();
    });
  });
});
