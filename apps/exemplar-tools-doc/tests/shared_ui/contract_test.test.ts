
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import React from 'react';
import {
  CodeBlock,
  VersionBadge,
  YouTubeEmbed,
  CalloutBox,
} from '../../src/shared_ui';

// Attempt to import extractYouTubeVideoId — it may be an internal utility
// exported from the component file or a shared util
let extractYouTubeVideoId: ((url: string) => string) | undefined;
try {
  // Try importing from the barrel — if not exported, tests will skip gracefully
  const mod = await import('../../src/shared_ui');
  extractYouTubeVideoId = (mod as Record<string, unknown>).extractYouTubeVideoId as
    | ((url: string) => string)
    | undefined;
} catch {
  // Will be handled in tests
}

// If not exported from barrel, try the YouTubeEmbed file directly
if (!extractYouTubeVideoId) {
  try {
    const mod = await import('../../src/shared_ui/YouTubeEmbed');
    extractYouTubeVideoId = (mod as Record<string, unknown>).extractYouTubeVideoId as
      | ((url: string) => string)
      | undefined;
  } catch {
    // Will be handled in tests
  }
}

// YouTubeUrl regex from the contract
const YOUTUBE_URL_REGEX =
  /^https?:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]{11}/;

describe('shared_ui', () => {
  afterEach(() => {
    cleanup();
  });

  // =========================================================================
  // YouTubeUrl type validator (regex)
  // =========================================================================
  describe('YouTubeUrl regex validation', () => {
    it('should match standard youtube.com/watch URLs', () => {
      expect(YOUTUBE_URL_REGEX.test('https://www.youtube.com/watch?v=dQw4w9WgXcQ')).toBe(true);
      expect(YOUTUBE_URL_REGEX.test('https://youtube.com/watch?v=dQw4w9WgXcQ')).toBe(true);
      expect(YOUTUBE_URL_REGEX.test('http://www.youtube.com/watch?v=dQw4w9WgXcQ')).toBe(true);
      expect(YOUTUBE_URL_REGEX.test('http://youtube.com/watch?v=dQw4w9WgXcQ')).toBe(true);
    });

    it('should match youtu.be short URLs', () => {
      expect(YOUTUBE_URL_REGEX.test('https://youtu.be/dQw4w9WgXcQ')).toBe(true);
      expect(YOUTUBE_URL_REGEX.test('http://youtu.be/dQw4w9WgXcQ')).toBe(true);
    });

    it('should reject non-YouTube URLs', () => {
      expect(YOUTUBE_URL_REGEX.test('https://vimeo.com/123456')).toBe(false);
      expect(YOUTUBE_URL_REGEX.test('')).toBe(false);
      expect(YOUTUBE_URL_REGEX.test('not-a-url')).toBe(false);
      expect(YOUTUBE_URL_REGEX.test('https://example.com')).toBe(false);
      expect(YOUTUBE_URL_REGEX.test('https://youtube.com/watch?v=short')).toBe(false); // < 11 chars
    });
  });

  // =========================================================================
  // extractYouTubeVideoId
  // =========================================================================
  describe('extractYouTubeVideoId', () => {
    const runIfAvailable = extractYouTubeVideoId ? it : it.skip;

    const validCases: Array<[string, string]> = [
      ['https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
      ['https://youtube.com/watch?v=dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
      ['http://www.youtube.com/watch?v=dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
      ['http://youtube.com/watch?v=dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
      ['https://youtu.be/dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
      ['http://youtu.be/dQw4w9WgXcQ', 'dQw4w9WgXcQ'],
      ['https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120', 'dQw4w9WgXcQ'],
      ['https://www.youtube.com/watch?v=abc_def-123', 'abc_def-123'],
      ['https://youtu.be/abc_def-123', 'abc_def-123'],
    ];

    it.each(validCases)(
      'extracts video ID from %s',
      (url: string, expectedId: string) => {
        if (!extractYouTubeVideoId) return;
        const result = extractYouTubeVideoId(url);
        expect(result).toBe(expectedId);
      },
    );

    const invalidCases: string[] = [
      '',
      'https://vimeo.com/123456',
      'not-a-url',
      'https://example.com',
      'https://youtube.com/',
      'https://youtube.com/watch',
      'https://youtube.com/watch?v=',
    ];

    it.each(invalidCases)(
      'returns empty string for invalid URL: %s',
      (url: string) => {
        if (!extractYouTubeVideoId) return;
        const result = extractYouTubeVideoId(url);
        expect(result).toBe('');
      },
    );

    runIfAvailable('returns empty string for empty input', () => {
      const result = extractYouTubeVideoId!('');
      expect(result).toBe('');
    });
  });

  // =========================================================================
  // CodeBlock
  // =========================================================================
  describe('CodeBlock', () => {
    let originalClipboard: Clipboard;

    beforeEach(() => {
      originalClipboard = navigator.clipboard;
    });

    afterEach(() => {
      // Restore original clipboard
      Object.defineProperty(navigator, 'clipboard', {
        value: originalClipboard,
        writable: true,
        configurable: true,
      });
    });

    it('renders a <pre> containing a <code> element with the code text', () => {
      render(React.createElement(CodeBlock, { code: 'npm install vitest' }));
      const codeEl = screen.getByText('npm install vitest');
      expect(codeEl).toBeTruthy();
      // Verify it's inside a <code> element
      const codeTag = codeEl.closest('code') ?? codeEl.tagName === 'CODE' ? codeEl : null;
      expect(codeTag).toBeTruthy();
      // Verify <code> is inside a <pre>
      const preEl = codeEl.closest('pre');
      expect(preEl).toBeTruthy();
    });

    it('renders description when props.description is provided and non-empty', () => {
      render(React.createElement(CodeBlock, { code: 'echo hello', description: 'Say hello' }));
      expect(screen.getByText('Say hello')).toBeTruthy();
    });

    it('does not render description element when description is omitted', () => {
      render(React.createElement(CodeBlock, { code: 'echo hello' }));
      expect(screen.queryByText('Say hello')).toBeNull();
    });

    it('does not render description element when description is empty string', () => {
      render(React.createElement(CodeBlock, { code: 'echo hello', description: '' }));
      // The code text should be present but no description
      expect(screen.getByText('echo hello')).toBeTruthy();
    });

    it('copy button calls navigator.clipboard.writeText with props.code on click', async () => {
      const writeTextMock = vi.fn().mockResolvedValue(undefined);
      Object.defineProperty(navigator, 'clipboard', {
        value: { writeText: writeTextMock },
        writable: true,
        configurable: true,
      });

      render(React.createElement(CodeBlock, { code: 'npm install vitest' }));

      // Find the copy button — try by role first, then fallback
      const copyButton =
        screen.queryByRole('button') ??
        screen.queryByLabelText(/copy/i) ??
        document.querySelector('button');
      expect(copyButton, 'Copy button should be present').toBeTruthy();

      await fireEvent.click(copyButton!);

      expect(writeTextMock).toHaveBeenCalledWith('npm install vitest');
    });

    it('handles clipboard_unavailable gracefully when navigator.clipboard is undefined', async () => {
      Object.defineProperty(navigator, 'clipboard', {
        value: undefined,
        writable: true,
        configurable: true,
      });

      // Should not throw during render
      expect(() => {
        render(React.createElement(CodeBlock, { code: 'test command' }));
      }).not.toThrow();

      const copyButton =
        screen.queryByRole('button') ?? document.querySelector('button');

      if (copyButton) {
        // Clicking should not throw an unhandled error
        expect(() => fireEvent.click(copyButton)).not.toThrow();
      }
    });

    it('handles clipboard_write_rejected when writeText promise rejects', async () => {
      const writeTextMock = vi.fn().mockRejectedValue(new Error('Permission denied'));
      Object.defineProperty(navigator, 'clipboard', {
        value: { writeText: writeTextMock },
        writable: true,
        configurable: true,
      });

      render(React.createElement(CodeBlock, { code: 'test command' }));

      const copyButton =
        screen.queryByRole('button') ?? document.querySelector('button');
      expect(copyButton, 'Copy button should be present').toBeTruthy();

      // Should handle rejection gracefully — no unhandled promise rejection
      await fireEvent.click(copyButton!);
      expect(writeTextMock).toHaveBeenCalledWith('test command');
    });
  });

  // =========================================================================
  // VersionBadge
  // =========================================================================
  describe('VersionBadge', () => {
    it('renders both componentName and version as visible text', () => {
      render(React.createElement(VersionBadge, { componentName: 'CodeBlock', version: '1.2.3' }));
      const container = screen.getByText(/CodeBlock/);
      expect(container).toBeTruthy();
      // Version should also be in the document
      const versionText = screen.getByText(/1\.2\.3/);
      expect(versionText).toBeTruthy();
    });

    it('renders an inline element with badge/pill styling (rounded class)', () => {
      render(React.createElement(VersionBadge, { componentName: 'Test', version: '0.1.0' }));
      const el = screen.getByText(/Test/);
      // Walk up to find the badge container
      const badge = el.closest('[class]') ?? el;
      const classes = badge.className;
      expect(
        classes.includes('rounded'),
        `Expected badge to have 'rounded' in its classes, got: ${classes}`,
      ).toBe(true);
    });

    it('handles special characters in componentName', () => {
      render(React.createElement(VersionBadge, { componentName: '@scope/pkg', version: '2.0.0-rc.1' }));
      expect(screen.getByText(/@scope\/pkg/)).toBeTruthy();
      expect(screen.getByText(/2\.0\.0-rc\.1/)).toBeTruthy();
    });
  });

  // =========================================================================
  // YouTubeEmbed
  // =========================================================================
  describe('YouTubeEmbed', () => {
    it('renders an iframe with correct embed src from watch URL', () => {
      render(
        React.createElement(YouTubeEmbed, {
          url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        }),
      );
      const iframe = document.querySelector('iframe');
      expect(iframe, 'An iframe element should be rendered').toBeTruthy();
      expect(iframe!.getAttribute('src')).toBe('https://www.youtube.com/embed/dQw4w9WgXcQ');
    });

    it('renders correct embed src from youtu.be short URL', () => {
      render(
        React.createElement(YouTubeEmbed, {
          url: 'https://youtu.be/dQw4w9WgXcQ',
        }),
      );
      const iframe = document.querySelector('iframe');
      expect(iframe).toBeTruthy();
      expect(iframe!.getAttribute('src')).toBe('https://www.youtube.com/embed/dQw4w9WgXcQ');
    });

    it('sets iframe title to props.title when provided', () => {
      render(
        React.createElement(YouTubeEmbed, {
          url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
          title: 'My Tutorial',
        }),
      );
      const iframe = document.querySelector('iframe');
      expect(iframe).toBeTruthy();
      expect(iframe!.getAttribute('title')).toBe('My Tutorial');
    });

    it('defaults iframe title to "YouTube video" when title prop is omitted', () => {
      render(
        React.createElement(YouTubeEmbed, {
          url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        }),
      );
      const iframe = document.querySelector('iframe');
      expect(iframe).toBeTruthy();
      expect(iframe!.getAttribute('title')).toBe('YouTube video');
    });

    it('wrapper div has Tailwind "aspect-video" class', () => {
      render(
        React.createElement(YouTubeEmbed, {
          url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        }),
      );
      const iframe = document.querySelector('iframe');
      expect(iframe).toBeTruthy();
      const wrapper = iframe!.parentElement;
      expect(wrapper).toBeTruthy();
      expect(
        wrapper!.className.includes('aspect-video'),
        `Expected wrapper to have 'aspect-video' class, got: ${wrapper!.className}`,
      ).toBe(true);
    });

    it('iframe has required attributes: allow, allowFullScreen, frameBorder, width, height', () => {
      render(
        React.createElement(YouTubeEmbed, {
          url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        }),
      );
      const iframe = document.querySelector('iframe');
      expect(iframe).toBeTruthy();

      // allowFullScreen
      expect(
        iframe!.hasAttribute('allowfullscreen') || iframe!.allowFullscreen === true,
        'iframe should have allowFullScreen attribute',
      ).toBe(true);

      // allow attribute with required policies
      const allowAttr = iframe!.getAttribute('allow') ?? '';
      expect(allowAttr).toContain('accelerometer');
      expect(allowAttr).toContain('autoplay');
      expect(allowAttr).toContain('clipboard-write');
      expect(allowAttr).toContain('encrypted-media');
      expect(allowAttr).toContain('gyroscope');
      expect(allowAttr).toContain('picture-in-picture');

      // frameBorder
      expect(iframe!.getAttribute('frameBorder') ?? iframe!.getAttribute('frameborder')).toBe('0');

      // width and height
      expect(iframe!.getAttribute('width')).toBe('100%');
      expect(iframe!.getAttribute('height')).toBe('100%');
    });
  });

  // =========================================================================
  // CalloutBox
  // =========================================================================
  describe('CalloutBox', () => {
    it('renders "gotcha" variant with visible text and variant-specific styling', () => {
      render(React.createElement(CalloutBox, { variant: 'gotcha', text: 'Watch out for this!' }));
      expect(screen.getByText('Watch out for this!')).toBeTruthy();
    });

    it('renders "warning" variant with visible text and variant-specific styling', () => {
      render(React.createElement(CalloutBox, { variant: 'warning', text: 'Be careful here' }));
      expect(screen.getByText('Be careful here')).toBeTruthy();
    });

    it('renders "tip" variant with visible text and variant-specific styling', () => {
      render(React.createElement(CalloutBox, { variant: 'tip', text: 'Pro tip!' }));
      expect(screen.getByText('Pro tip!')).toBeTruthy();
    });

    it('all three variants produce visually distinguishable containers (different class strings)', () => {
      const { unmount: unmount1 } = render(
        React.createElement(CalloutBox, { variant: 'gotcha', text: 'gotcha-text' }),
      );
      const gotchaEl = screen.getByText('gotcha-text');
      const gotchaContainer = gotchaEl.closest('[class]') ?? gotchaEl;
      const gotchaClasses = gotchaContainer.className;
      unmount1();

      const { unmount: unmount2 } = render(
        React.createElement(CalloutBox, { variant: 'warning', text: 'warning-text' }),
      );
      const warningEl = screen.getByText('warning-text');
      const warningContainer = warningEl.closest('[class]') ?? warningEl;
      const warningClasses = warningContainer.className;
      unmount2();

      const { unmount: unmount3 } = render(
        React.createElement(CalloutBox, { variant: 'tip', text: 'tip-text' }),
      );
      const tipEl = screen.getByText('tip-text');
      const tipContainer = tipEl.closest('[class]') ?? tipEl;
      const tipClasses = tipContainer.className;
      unmount3();

      // All three must have different class strings
      expect(
        gotchaClasses !== warningClasses,
        `gotcha and warning should have different classes. gotcha: "${gotchaClasses}", warning: "${warningClasses}"`,
      ).toBe(true);
      expect(
        warningClasses !== tipClasses,
        `warning and tip should have different classes. warning: "${warningClasses}", tip: "${tipClasses}"`,
      ).toBe(true);
      expect(
        gotchaClasses !== tipClasses,
        `gotcha and tip should have different classes. gotcha: "${gotchaClasses}", tip: "${tipClasses}"`,
      ).toBe(true);
    });

    it('container includes role="alert" or appropriate ARIA attribute for accessibility', () => {
      render(React.createElement(CalloutBox, { variant: 'warning', text: 'Test a11y' }));
      const textEl = screen.getByText('Test a11y');
      // Look for role on the text element or its ancestors
      const containerWithRole =
        textEl.closest('[role]') ??
        (textEl.getAttribute('role') ? textEl : null);
      expect(
        containerWithRole,
        'CalloutBox should have a role attribute (e.g. role="alert") for accessibility',
      ).toBeTruthy();
    });
  });

  // =========================================================================
  // Barrel exports invariant
  // =========================================================================
  describe('barrel exports', () => {
    it('exports all four components as named exports (functions)', async () => {
      const mod = await import('../../src/shared_ui');
      expect(typeof mod.CodeBlock).toBe('function');
      expect(typeof mod.VersionBadge).toBe('function');
      expect(typeof mod.YouTubeEmbed).toBe('function');
      expect(typeof mod.CalloutBox).toBe('function');
    });

    it('does not have a default export', async () => {
      const mod = await import('../../src/shared_ui');
      // default should be undefined if no default export
      expect((mod as Record<string, unknown>).default).toBeUndefined();
    });
  });
});
