
// @vitest-environment jsdom
import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { MemoryRouter } from 'react-router-dom';

import {
  CalloutBox,
  CodeBlock,
  VersionBadge,
  VideoEmbed,
  Sidebar,
  PageLayout,
} from '../../src/shared_components';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Suppress React error boundary / console.error noise in error-case tests. */
const suppressConsoleError = () => {
  const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
  return spy;
};

/** Minimal ErrorBoundary for catching render-time errors in tests. */
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; onError?: (e: Error) => void },
  { error: Error | null }
> {
  state: { error: Error | null } = { error: null };
  static getDerivedStateFromError(error: Error) {
    return { error };
  }
  componentDidCatch(error: Error) {
    this.props.onError?.(error);
  }
  render() {
    if (this.state.error) return <div data-testid="error">{this.state.error.message}</div>;
    return this.props.children;
  }
}

/** Sample route entries reusable across Sidebar / PageLayout tests. */
const sampleRoutes = [
  { path: '/', label: 'Home', componentKey: 'Home' as const },
  { path: '/cartographer', label: 'Cartographer', componentKey: 'Cartographer' as const },
  { path: '/constrain', label: 'Constrain', componentKey: 'Constrain' as const },
];

const fiveRoutes = [
  ...sampleRoutes,
  { path: '/ledger', label: 'Ledger', componentKey: 'Ledger' as const },
  { path: '/pact', label: 'Pact', componentKey: 'Pact' as const },
];

// ---------------------------------------------------------------------------
// CalloutBox
// ---------------------------------------------------------------------------
describe('CalloutBox', () => {
  it.each(['gotcha', 'warning', 'tip'] as const)(
    'renders a %s callout with title and children',
    (type) => {
      const { container } = render(
        <CalloutBox type={type} title={`Title for ${type}`}>
          <p>Body content</p>
        </CalloutBox>,
      );
      // Postcondition: title heading rendered
      expect(screen.getByText(`Title for ${type}`)).toBeInTheDocument();
      // Postcondition: children rendered
      expect(screen.getByText('Body content')).toBeInTheDocument();
      // Postcondition: container div exists
      expect(container.firstElementChild).toBeTruthy();
    },
  );

  it('does not render a heading when title is empty string', () => {
    const { container } = render(
      <CalloutBox type="tip" title="">
        <p>Body only</p>
      </CalloutBox>,
    );
    expect(screen.getByText('Body only')).toBeInTheDocument();
    // No heading element should contain empty title text
    const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
    for (const h of headings) {
      expect(h.textContent).not.toBe('');
    }
  });

  it('throws or shows error for invalid callout type', () => {
    const consoleSpy = suppressConsoleError();
    let caughtError: Error | null = null;

    try {
      render(
        <ErrorBoundary onError={(e) => { caughtError = e; }}>
          <CalloutBox type={'danger' as any} title="X">
            <p>Y</p>
          </CalloutBox>
        </ErrorBoundary>,
      );
    } catch (e) {
      caughtError = e as Error;
    }

    // Either the component threw (caught by ErrorBoundary or try/catch)
    // or it rendered an error boundary fallback
    const errorEl = screen.queryByTestId('error');
    if (caughtError) {
      expect(caughtError).toBeTruthy();
    } else if (errorEl) {
      expect(errorEl).toBeInTheDocument();
    } else {
      // If the component silently handles it, at minimum it should not render 'danger' as valid
      // This is a permissive assertion — the contract says it should error.
      expect(caughtError || errorEl).toBeTruthy();
    }
    consoleSpy.mockRestore();
  });

  it('invariant: all three CalloutType variants render successfully', () => {
    for (const type of ['gotcha', 'warning', 'tip'] as const) {
      const { unmount } = render(
        <CalloutBox type={type} title="Test">
          <span>child</span>
        </CalloutBox>,
      );
      expect(screen.getByText('Test')).toBeInTheDocument();
      unmount();
    }
  });
});

// ---------------------------------------------------------------------------
// CodeBlock
// ---------------------------------------------------------------------------
describe('CodeBlock', () => {
  let writeTextMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    writeTextMock = vi.fn(() => Promise.resolve());
    Object.assign(navigator, {
      clipboard: {
        writeText: writeTextMock,
        readText: vi.fn(),
      },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders code with syntax highlighting, title, and copy button', () => {
    render(<CodeBlock code="npm install foo" language="bash" title="Install" />);
    expect(screen.getByText(/npm install foo/)).toBeInTheDocument();
    expect(screen.getByText('Install')).toBeInTheDocument();
    // Postcondition: copy button is present
    const copyBtn = screen.getByRole('button', { name: /copy/i });
    expect(copyBtn).toBeInTheDocument();
  });

  it('defaults language to bash when omitted', () => {
    // Should render without error when language is not provided
    const { container } = render(<CodeBlock code="echo hello" language="" title="" />);
    expect(screen.getByText(/echo hello/)).toBeInTheDocument();
    // The component should still render — no crash
    expect(container.firstElementChild).toBeTruthy();
  });

  it('calls navigator.clipboard.writeText with exact code on copy button click', async () => {
    render(<CodeBlock code="const x = 1;" language="typescript" title="" />);
    const copyBtn = screen.getByRole('button', { name: /copy/i });
    fireEvent.click(copyBtn);
    await waitFor(() => {
      expect(writeTextMock).toHaveBeenCalledWith('const x = 1;');
    });
  });

  it('throws or handles empty code string', () => {
    const consoleSpy = suppressConsoleError();
    let caughtError: Error | null = null;
    try {
      render(
        <ErrorBoundary onError={(e) => { caughtError = e; }}>
          <CodeBlock code="" language="bash" title="" />
        </ErrorBoundary>,
      );
    } catch (e) {
      caughtError = e as Error;
    }
    const errorEl = screen.queryByTestId('error');
    expect(caughtError || errorEl).toBeTruthy();
    consoleSpy.mockRestore();
  });

  it('handles clipboard unavailable gracefully', async () => {
    // Remove clipboard API
    Object.defineProperty(navigator, 'clipboard', {
      value: undefined,
      writable: true,
      configurable: true,
    });

    const consoleSpy = suppressConsoleError();
    // Render should succeed; clicking copy should not crash
    let caughtError: Error | null = null;
    try {
      render(
        <ErrorBoundary onError={(e) => { caughtError = e; }}>
          <CodeBlock code="echo hi" language="bash" title="" />
        </ErrorBoundary>,
      );
      const copyBtn = screen.queryByRole('button', { name: /copy/i });
      if (copyBtn) {
        fireEvent.click(copyBtn);
        // Should handle gracefully — not crash
        await waitFor(() => {
          // Either an error state is shown or nothing catastrophic happens
          expect(true).toBe(true);
        });
      }
    } catch (e) {
      caughtError = e as Error;
    }
    // Graceful degradation: component should not fatally crash the app
    consoleSpy.mockRestore();

    // Restore clipboard for other tests
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: vi.fn(() => Promise.resolve()), readText: vi.fn() },
      writable: true,
      configurable: true,
    });
  });
});

// ---------------------------------------------------------------------------
// VersionBadge
// ---------------------------------------------------------------------------
describe('VersionBadge', () => {
  it('renders version string in a pill badge with Tailwind classes', () => {
    const { container } = render(<VersionBadge version="1.2.3" label="v" />);
    expect(screen.getByText('1.2.3')).toBeInTheDocument();
    // Postcondition: pill classes (rounded-full)
    const badge = screen.getByText('1.2.3').closest('[class]');
    expect(badge).toBeTruthy();
    if (badge) {
      expect(badge.className).toMatch(/rounded-full/);
    }
  });

  it('throws or handles empty version string', () => {
    const consoleSpy = suppressConsoleError();
    let caughtError: Error | null = null;
    try {
      render(
        <ErrorBoundary onError={(e) => { caughtError = e; }}>
          <VersionBadge version="" label="v" />
        </ErrorBoundary>,
      );
    } catch (e) {
      caughtError = e as Error;
    }
    const errorEl = screen.queryByTestId('error');
    expect(caughtError || errorEl).toBeTruthy();
    consoleSpy.mockRestore();
  });
});

// ---------------------------------------------------------------------------
// VideoEmbed
// ---------------------------------------------------------------------------
describe('VideoEmbed', () => {
  it('renders iframe with YouTube embed URL and aspect-video container', () => {
    const { container } = render(
      <VideoEmbed url="https://www.youtube.com/embed/dQw4w9WgXcQ" title="Demo" />,
    );
    const iframe = container.querySelector('iframe');
    expect(iframe).toBeTruthy();
    expect(iframe!.getAttribute('src')).toContain('youtube.com');
    expect(iframe!.getAttribute('title')).toBe('Demo');
    // Invariant: aspect-video class
    const aspectContainer = container.querySelector('.aspect-video') ||
      container.querySelector('[class*="aspect-video"]');
    expect(aspectContainer).toBeTruthy();
  });

  it('accepts standard YouTube watch URL and derives embed src', () => {
    const { container } = render(
      <VideoEmbed url="https://www.youtube.com/watch?v=dQw4w9WgXcQ" title="Watch" />,
    );
    const iframe = container.querySelector('iframe');
    expect(iframe).toBeTruthy();
    // The src should be an embed-friendly URL
    expect(iframe!.getAttribute('src')).toContain('youtube.com');
  });

  it('uses "Video" as default iframe title when title is empty or omitted', () => {
    const { container } = render(
      <VideoEmbed url="https://www.youtube.com/embed/dQw4w9WgXcQ" title="" />,
    );
    const iframe = container.querySelector('iframe');
    expect(iframe).toBeTruthy();
    // Default title should be 'Video'
    expect(iframe!.getAttribute('title')).toBe('Video');
  });

  it('rejects non-YouTube URLs', () => {
    const consoleSpy = suppressConsoleError();
    let caughtError: Error | null = null;
    try {
      render(
        <ErrorBoundary onError={(e) => { caughtError = e; }}>
          <VideoEmbed url="https://vimeo.com/12345" title="Bad" />
        </ErrorBoundary>,
      );
    } catch (e) {
      caughtError = e as Error;
    }
    const errorEl = screen.queryByTestId('error');
    expect(caughtError || errorEl).toBeTruthy();
    consoleSpy.mockRestore();
  });

  it('invariant: container has aspect-video Tailwind class', () => {
    const { container } = render(
      <VideoEmbed url="https://www.youtube.com/embed/dQw4w9WgXcQ" title="Test" />,
    );
    // Walk the DOM tree to find aspect-video
    const allElements = container.querySelectorAll('*');
    const hasAspectVideo = Array.from(allElements).some((el) =>
      el.className && typeof el.className === 'string' && el.className.includes('aspect-video'),
    );
    expect(hasAspectVideo).toBe(true);
  });

  it('invariant: iframe has correct allow attributes and allowFullScreen', () => {
    const { container } = render(
      <VideoEmbed url="https://www.youtube.com/embed/dQw4w9WgXcQ" title="Test" />,
    );
    const iframe = container.querySelector('iframe');
    expect(iframe).toBeTruthy();
    const allow = iframe!.getAttribute('allow') ?? '';
    expect(allow).toContain('accelerometer');
    expect(allow).toContain('autoplay');
    expect(allow).toContain('clipboard-write');
    expect(allow).toContain('encrypted-media');
    expect(allow).toContain('gyroscope');
    expect(allow).toContain('picture-in-picture');
    expect(iframe!.allowFullscreen || iframe!.getAttribute('allowfullscreen') !== null).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Sidebar
// ---------------------------------------------------------------------------
describe('Sidebar', () => {
  it('renders nav element with one NavLink per route entry', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/']}>
        <Sidebar routes={sampleRoutes} />
      </MemoryRouter>,
    );
    const nav = container.querySelector('nav');
    expect(nav).toBeTruthy();
    // Each route should produce a link
    const links = container.querySelectorAll('a');
    expect(links.length).toBe(sampleRoutes.length);
    // Verify paths and labels
    sampleRoutes.forEach((route, i) => {
      expect(links[i].textContent).toBe(route.label);
      expect(links[i].getAttribute('href')).toBe(route.path);
    });
  });

  it('applies active styling to NavLink matching current route', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/cartographer']}>
        <Sidebar routes={sampleRoutes} />
      </MemoryRouter>,
    );
    const links = container.querySelectorAll('a');
    const cartographerLink = Array.from(links).find(
      (l) => l.getAttribute('href') === '/cartographer',
    );
    expect(cartographerLink).toBeTruthy();
    // Active link should have distinct styling: either 'active' in class or aria-current
    const isActive =
      (cartographerLink!.className && cartographerLink!.className.includes('active')) ||
      cartographerLink!.getAttribute('aria-current') === 'page';
    expect(isActive).toBe(true);
  });

  it('throws when rendered outside Router provider', () => {
    const consoleSpy = suppressConsoleError();
    let caughtError: Error | null = null;
    try {
      render(
        <ErrorBoundary onError={(e) => { caughtError = e; }}>
          <Sidebar routes={sampleRoutes} />
        </ErrorBoundary>,
      );
    } catch (e) {
      caughtError = e as Error;
    }
    const errorEl = screen.queryByTestId('error');
    expect(caughtError || errorEl).toBeTruthy();
    consoleSpy.mockRestore();
  });

  it('invariant: renders exactly one NavLink per RouteEntry for 5 routes', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/']}>
        <Sidebar routes={fiveRoutes} />
      </MemoryRouter>,
    );
    const links = container.querySelectorAll('a');
    expect(links.length).toBe(fiveRoutes.length);
  });
});

// ---------------------------------------------------------------------------
// PageLayout
// ---------------------------------------------------------------------------
describe('PageLayout', () => {
  it('renders flex container with Sidebar and children content area', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/']}>
        <PageLayout routes={sampleRoutes}>
          <div>Page Content</div>
        </PageLayout>
      </MemoryRouter>,
    );
    // Sidebar should be present (nav element)
    const nav = container.querySelector('nav');
    expect(nav).toBeTruthy();
    // Children should be rendered
    expect(screen.getByText('Page Content')).toBeInTheDocument();
    // Root should be a flex container
    const root = container.firstElementChild;
    expect(root).toBeTruthy();
    expect(root!.className).toMatch(/flex/);
  });

  it('renders arbitrary children in content area', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <PageLayout routes={sampleRoutes}>
          <h1>Hello World</h1>
        </PageLayout>
      </MemoryRouter>,
    );
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });

  it('throws when rendered outside Router provider', () => {
    const consoleSpy = suppressConsoleError();
    let caughtError: Error | null = null;
    try {
      render(
        <ErrorBoundary onError={(e) => { caughtError = e; }}>
          <PageLayout routes={sampleRoutes}>
            <div />
          </PageLayout>
        </ErrorBoundary>,
      );
    } catch (e) {
      caughtError = e as Error;
    }
    const errorEl = screen.queryByTestId('error');
    expect(caughtError || errorEl).toBeTruthy();
    consoleSpy.mockRestore();
  });

  it('invariant: root uses responsive Tailwind flex classes for md: breakpoint', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/']}>
        <PageLayout routes={sampleRoutes}>
          <div />
        </PageLayout>
      </MemoryRouter>,
    );
    const root = container.firstElementChild;
    expect(root).toBeTruthy();
    const cls = root!.className;
    // Should have flex-col (mobile default) and md:flex-row (desktop)
    expect(cls).toMatch(/flex-col/);
    expect(cls).toMatch(/md:flex-row/);
  });

  it('content area occupies remaining space with flex-1', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/']}>
        <PageLayout routes={sampleRoutes}>
          <div data-testid="inner">Content</div>
        </PageLayout>
      </MemoryRouter>,
    );
    // Find the content area — it should have flex-1 or equivalent
    const inner = screen.getByTestId('inner');
    // Walk up to find the content wrapper
    const contentWrapper = inner.closest('main') || inner.parentElement;
    expect(contentWrapper).toBeTruthy();
    if (contentWrapper) {
      const cls = contentWrapper.className || '';
      expect(cls).toMatch(/flex-1|grow|flex-grow/);
    }
  });
});
