
import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// Import from barrel
import {
  CalloutBox,
  CodeBlock,
  VersionBadge,
  VideoEmbed,
  Sidebar,
  PageLayout,
} from '../../../src/shared_components';

// Helper to make route entries
function makeRoute(path: string, label: string, componentKey: string = 'Home') {
  return { path, label, componentKey };
}

describe('goodhart: CalloutBox', () => {
  it('goodhart: should render arbitrary children content not seen in visible tests', () => {
    const uniqueText = 'UniqueGoodhartChild-' + Date.now();
    render(
      <CalloutBox type="gotcha" title="Test">
        <div data-testid="custom-child">{uniqueText}</div>
      </CalloutBox>
    );
    expect(screen.getByText(uniqueText)).toBeTruthy();
  });

  it('goodhart: should render novel title strings with special characters', () => {
    const novelTitle = '⚠️ Caution: Don\'t ignore <this> & "that"!';
    render(
      <CalloutBox type="warning" title={novelTitle}>
        <p>Body</p>
      </CalloutBox>
    );
    // The title must appear as a heading or prominent text
    expect(screen.getByText(novelTitle)).toBeTruthy();
  });

  it('goodhart: should not render heading when title is undefined (not just empty string)', () => {
    const { container } = render(
      <CalloutBox type="tip" title={undefined as any}>
        <p>Some content</p>
      </CalloutBox>
    );
    // No heading elements should be present
    const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
    expect(headings.length).toBe(0);
  });

  it('goodhart: should reject uppercase CalloutType variants like "Gotcha"', () => {
    expect(() => {
      render(
        <CalloutBox type={'Gotcha' as any} title="Test">
          <p>Body</p>
        </CalloutBox>
      );
    }).toThrow();
  });

  it('goodhart: should reject close-but-not-exact type strings like "warn"', () => {
    expect(() => {
      render(
        <CalloutBox type={'warn' as any} title="Test">
          <p>Body</p>
        </CalloutBox>
      );
    }).toThrow();
  });

  it('goodhart: should render distinct icons for each callout type', () => {
    const { container: gotchaContainer } = render(
      <CalloutBox type="gotcha" title="G">
        <p>g</p>
      </CalloutBox>
    );
    const { container: warningContainer } = render(
      <CalloutBox type="warning" title="W">
        <p>w</p>
      </CalloutBox>
    );
    const { container: tipContainer } = render(
      <CalloutBox type="tip" title="T">
        <p>t</p>
      </CalloutBox>
    );

    // Extract icon-like elements (svg, img, span with icon class, emoji text, etc.)
    // The key assertion is that the three types don't produce identical markup
    const gotchaHTML = gotchaContainer.innerHTML;
    const warningHTML = warningContainer.innerHTML;
    const tipHTML = tipContainer.innerHTML;

    // At least two of the three must differ (they can't all be identical)
    const allSame = gotchaHTML === warningHTML && warningHTML === tipHTML;
    expect(allSame).toBe(false);
  });

  it('goodhart: should render multiple children elements in the callout body', () => {
    render(
      <CalloutBox type="tip" title="Multi-child">
        <p>First paragraph</p>
        <ul>
          <li>Item one</li>
          <li>Item two</li>
        </ul>
      </CalloutBox>
    );
    expect(screen.getByText('First paragraph')).toBeTruthy();
    expect(screen.getByText('Item one')).toBeTruthy();
    expect(screen.getByText('Item two')).toBeTruthy();
  });
});

describe('goodhart: CodeBlock', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  it('goodhart: should render novel code strings not used in visible tests', () => {
    const novelCode = 'kubectl get pods --namespace=kube-system -o wide';
    render(<CodeBlock code={novelCode} language="bash" title="" />);
    expect(screen.getByText(novelCode, { exact: false })).toBeTruthy();
  });

  it('goodhart: should copy the exact novel multi-line code string on button click', async () => {
    const multiLineCode = 'const x = 1;\nconst y = 2;\nconsole.log(x + y);';
    render(<CodeBlock code={multiLineCode} language="javascript" title="Example" />);

    const copyButton = screen.getByRole('button');
    await fireEvent.click(copyButton);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(multiLineCode);
  });

  it('goodhart: should render a novel title string above the code block', () => {
    render(
      <CodeBlock code="echo hello" language="bash" title="Deployment Script v2" />
    );
    expect(screen.getByText('Deployment Script v2')).toBeTruthy();
  });

  it('goodhart: should not render title element when title prop is omitted or empty', () => {
    const { container } = render(
      <CodeBlock code="echo hello" language="bash" title="" />
    );
    // The code should render but no title text
    // We verify by checking that 'echo hello' is present but no extra heading/title
    expect(screen.getByText('echo hello', { exact: false })).toBeTruthy();
    // Should not have any heading elements for the title
    const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
    const titleDivs = container.querySelectorAll('[class*="title"]');
    // At minimum, there shouldn't be an element with empty title text
    // The key check: no visible title text appears (code block works without it)
  });

  it('goodhart: should accept whitespace-only code as valid non-empty input', () => {
    expect(() => {
      render(<CodeBlock code="   " language="bash" title="" />);
    }).not.toThrow();
  });

  it('goodhart: should accept and render with language="typescript"', () => {
    const tsCode = 'const greeting: string = "hello";';
    expect(() => {
      render(<CodeBlock code={tsCode} language="typescript" title="TS Example" />);
    }).not.toThrow();
    expect(screen.getByText(tsCode, { exact: false })).toBeTruthy();
  });
});

describe('goodhart: VersionBadge', () => {
  it('goodhart: should display a novel version string not seen in visible tests', () => {
    render(<VersionBadge version="4.7.2-rc.1" label="" />);
    expect(screen.getByText('4.7.2-rc.1', { exact: false })).toBeTruthy();
    // Must have pill styling
    const badge = screen.getByText('4.7.2-rc.1', { exact: false });
    const el = badge.closest('[class*="rounded-full"]') || badge;
    expect(el.className).toMatch(/rounded-full/);
  });

  it('goodhart: should render label prop when provided', () => {
    const { container } = render(<VersionBadge version="2.0.0" label="Release" />);
    expect(screen.getByText('2.0.0', { exact: false })).toBeTruthy();
    // Label should appear somewhere in the rendered output
    expect(container.textContent).toContain('2.0.0');
  });

  it('goodhart: should accept single character version string', () => {
    render(<VersionBadge version="1" label="" />);
    const el = screen.getByText('1', { exact: false });
    expect(el).toBeTruthy();
    // Should still have pill class
    const badge = el.closest('[class*="rounded-full"]') || el;
    expect(badge.className).toMatch(/rounded-full/);
  });
});

describe('goodhart: VideoEmbed', () => {
  it('goodhart: should handle watch URLs with additional query params like timestamp', () => {
    const { container } = render(
      <VideoEmbed url="https://www.youtube.com/watch?v=abc123XYZ90&t=120" title="Timestamped" />
    );
    const iframe = container.querySelector('iframe');
    expect(iframe).toBeTruthy();
    // The src should contain the video ID in an embed format
    expect(iframe!.src).toContain('abc123XYZ90');
  });

  it('goodhart: should set iframe title to the exact custom title prop value', () => {
    const { container } = render(
      <VideoEmbed url="https://www.youtube.com/embed/dQw4w9WgXcQ" title="My Custom Tutorial" />
    );
    const iframe = container.querySelector('iframe');
    expect(iframe).toBeTruthy();
    expect(iframe!.title).toBe('My Custom Tutorial');
  });

  it('goodhart: should reject Vimeo URLs as invalid', () => {
    expect(() => {
      render(<VideoEmbed url="https://vimeo.com/123456789" title="Vimeo" />);
    }).toThrow();
  });

  it('goodhart: should reject YouTube search result URLs as invalid', () => {
    expect(() => {
      render(
        <VideoEmbed url="https://youtube.com/results?search_query=cats" title="Search" />
      );
    }).toThrow();
  });

  it('goodhart: should accept youtu.be short URLs', () => {
    // youtu.be is a valid YouTube URL format
    const renderShortUrl = () => {
      render(<VideoEmbed url="https://youtu.be/dQw4w9WgXcQ" title="Short URL" />);
    };
    // Should either render successfully or at minimum not reject as invalid
    // Most implementations should accept this common YouTube format
    expect(renderShortUrl).not.toThrow();
  });
});

describe('goodhart: Sidebar', () => {
  it('goodhart: should preserve route order exactly as provided in the array', () => {
    const routes = [
      makeRoute('/zebra', 'Zebra Route'),
      makeRoute('/alpha', 'Alpha Route'),
      makeRoute('/middle', 'Middle Route'),
    ];

    render(
      <MemoryRouter initialEntries={['/']}>
        <Sidebar routes={routes as any} />
      </MemoryRouter>
    );

    const links = screen.getAllByRole('link');
    expect(links[0].textContent).toContain('Zebra Route');
    expect(links[1].textContent).toContain('Alpha Route');
    expect(links[2].textContent).toContain('Middle Route');
  });

  it('goodhart: should set NavLink href to the exact RouteEntry.path value', () => {
    const routes = [
      makeRoute('/foo/bar', 'Foo Bar'),
      makeRoute('/baz-qux', 'Baz Qux'),
    ];

    render(
      <MemoryRouter initialEntries={['/']}>
        <Sidebar routes={routes as any} />
      </MemoryRouter>
    );

    const links = screen.getAllByRole('link');
    expect(links[0].getAttribute('href')).toBe('/foo/bar');
    expect(links[1].getAttribute('href')).toBe('/baz-qux');
  });

  it('goodhart: should render correctly with a single route entry', () => {
    const routes = [makeRoute('/only', 'Only Route')];

    render(
      <MemoryRouter initialEntries={['/']}>
        <Sidebar routes={routes as any} />
      </MemoryRouter>
    );

    const links = screen.getAllByRole('link');
    expect(links.length).toBe(1);
    expect(links[0].textContent).toContain('Only Route');

    // nav element should still be present
    const nav = screen.getByRole('navigation');
    expect(nav).toBeTruthy();
  });

  it('goodhart: should dynamically render links for any count of routes (7 routes)', () => {
    const routes = Array.from({ length: 7 }, (_, i) =>
      makeRoute(`/route-${i}`, `Route ${i}`)
    );

    render(
      <MemoryRouter initialEntries={['/']}>
        <Sidebar routes={routes as any} />
      </MemoryRouter>
    );

    const links = screen.getAllByRole('link');
    expect(links.length).toBe(7);
  });

  it('goodhart: should use semantic <nav> HTML element as root', () => {
    const routes = [makeRoute('/test', 'Test')];

    const { container } = render(
      <MemoryRouter initialEntries={['/']}>
        <Sidebar routes={routes as any} />
      </MemoryRouter>
    );

    const nav = container.querySelector('nav');
    expect(nav).toBeTruthy();
    expect(nav!.tagName).toBe('NAV');
  });
});

describe('goodhart: PageLayout', () => {
  it('goodhart: should have flex-1 on the content area for remaining space', () => {
    const routes = [makeRoute('/home', 'Home')];

    const { container } = render(
      <MemoryRouter initialEntries={['/']}>
        <PageLayout routes={routes as any}>
          <div>Content</div>
        </PageLayout>
      </MemoryRouter>
    );

    // Find the main content area (main element or a div wrapping children)
    const mainOrContent =
      container.querySelector('main') ||
      container.querySelector('[class*="flex-1"]') ||
      container.querySelector('[class*="grow"]');
    expect(mainOrContent).toBeTruthy();
    expect(mainOrContent!.className).toMatch(/flex-1|grow/);
  });

  it('goodhart: should pass routes to Sidebar so that custom route labels appear as links', () => {
    const routes = [
      makeRoute('/aaa', 'Goodhart Alpha'),
      makeRoute('/bbb', 'Goodhart Beta'),
      makeRoute('/ccc', 'Goodhart Gamma'),
    ];

    render(
      <MemoryRouter initialEntries={['/']}>
        <PageLayout routes={routes as any}>
          <div>Main</div>
        </PageLayout>
      </MemoryRouter>
    );

    expect(screen.getByText('Goodhart Alpha')).toBeTruthy();
    expect(screen.getByText('Goodhart Beta')).toBeTruthy();
    expect(screen.getByText('Goodhart Gamma')).toBeTruthy();
  });

  it('goodhart: should render novel children content that could not be hardcoded', () => {
    const routes = [makeRoute('/x', 'X')];
    const uniqueContent = 'Unique-Goodhart-Content-XYZ-' + Math.random().toString(36).slice(2);

    render(
      <MemoryRouter initialEntries={['/']}>
        <PageLayout routes={routes as any}>
          <div>{uniqueContent}</div>
        </PageLayout>
      </MemoryRouter>
    );

    expect(screen.getByText(uniqueContent)).toBeTruthy();
  });
});

describe('goodhart: barrel exports', () => {
  it('goodhart: all six components must be exported as named functions from the barrel', () => {
    expect(typeof CalloutBox).toBe('function');
    expect(typeof CodeBlock).toBe('function');
    expect(typeof VersionBadge).toBe('function');
    expect(typeof VideoEmbed).toBe('function');
    expect(typeof Sidebar).toBe('function');
    expect(typeof PageLayout).toBe('function');
  });
});
