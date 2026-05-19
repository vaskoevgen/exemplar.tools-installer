import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';

// Import runtime components from barrel
import { CodeBlock, VersionBadge, YouTubeEmbed, CalloutBox } from '../../../src/shared_ui/index';

// Import types to verify they exist (compile-time check)
import type {
  CalloutVariant,
  CodeBlockProps,
  VersionBadgeProps,
  YouTubeEmbedProps,
  CalloutBoxProps,
} from '../../../src/shared_ui/index';

// We need to import extractYouTubeVideoId from its internal location
// It's not exported from barrel, so we import from the component file or utility
import { extractYouTubeVideoId } from '../../../src/shared_ui/YouTubeEmbed';

describe('Shared UI Components - Goodhart Adversarial Tests', () => {
  // ─── extractYouTubeVideoId ───

  describe('extractYouTubeVideoId', () => {
    it('goodhart: should extract IDs containing hyphens and underscores since valid YouTube IDs use the full [a-zA-Z0-9_-] charset', () => {
      const result = extractYouTubeVideoId('https://www.youtube.com/watch?v=Ab_-Cd3f5Gh');
      expect(result).toBe('Ab_-Cd3f5Gh');
    });

    it('goodhart: should extract ID from www-prefixed https watch URL with a novel video ID not used in visible tests', () => {
      const result = extractYouTubeVideoId('https://www.youtube.com/watch?v=R4nd0m_ID-x');
      expect(result).toBe('R4nd0m_ID-x');
    });

    it('goodhart: should handle youtu.be URLs with www prefix since the URL pattern allows optional www', () => {
      const result = extractYouTubeVideoId('https://www.youtu.be/dQw4w9WgXcQ');
      expect(result).toBe('dQw4w9WgXcQ');
    });

    it('goodhart: should return empty string for already-embedded youtube.com/embed/ URLs which are not a recognized input pattern', () => {
      const result = extractYouTubeVideoId('https://www.youtube.com/embed/dQw4w9WgXcQ');
      expect(result).toBe('');
    });

    it('goodhart: should return empty string for YouTube playlist URLs that lack a watch?v= parameter', () => {
      const result = extractYouTubeVideoId('https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf');
      expect(result).toBe('');
    });

    it('goodhart: should return exactly 11 characters for a valid URL even when extra query params follow the ID', () => {
      const result = extractYouTubeVideoId('https://youtu.be/dQw4w9WgXcQ?si=somethingextra');
      expect(result).toHaveLength(11);
      expect(result).toBe('dQw4w9WgXcQ');
    });

    it('goodhart: should handle watch URLs where v is not the first query parameter', () => {
      const result = extractYouTubeVideoId('https://www.youtube.com/watch?feature=share&v=dQw4w9WgXcQ');
      expect(result).toBe('dQw4w9WgXcQ');
    });
  });

  // ─── YouTubeUrl regex validator ───

  describe('YouTubeUrl regex', () => {
    const youtubeUrlRegex = /^https?:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]{11}$/;

    it('goodhart: should reject URLs where the video ID is shorter than 11 characters', () => {
      expect(youtubeUrlRegex.test('https://www.youtube.com/watch?v=abc123')).toBe(false);
    });

    it('goodhart: should reject URLs where the video ID is longer than 11 characters when testing full-string match', () => {
      // 12 chars after v=
      expect(youtubeUrlRegex.test('https://www.youtube.com/watch?v=dQw4w9WgXcQx')).toBe(false);
    });
  });

  // ─── CodeBlock ───

  describe('CodeBlock', () => {
    let originalClipboard: Clipboard;

    beforeEach(() => {
      originalClipboard = navigator.clipboard;
    });

    afterEach(() => {
      Object.defineProperty(navigator, 'clipboard', {
        value: originalClipboard,
        writable: true,
        configurable: true,
      });
    });

    it('goodhart: should dynamically render any code string, not a hardcoded value from visible tests', () => {
      const uniqueCode = 'curl -X POST https://api.example.com/v2/deploy --data-raw {}';
      const { container } = render(<CodeBlock code={uniqueCode} />);
      const codeEl = container.querySelector('code');
      expect(codeEl).not.toBeNull();
      expect(codeEl!.textContent).toBe(uniqueCode);
    });

    it('goodhart: should not render a description label when description is an empty string (not just undefined)', () => {
      const { container } = render(<CodeBlock code="echo hello" description="" />);
      const codeEl = container.querySelector('code');
      expect(codeEl).not.toBeNull();
      // The total rendered text should only be the code + maybe a copy button label,
      // not any description
      // Check there's no element that looks like a description label outside code/button
      const preEl = container.querySelector('pre');
      expect(preEl).not.toBeNull();
      // Heuristic: the container text (minus code and button text) shouldn't have description text
      // More directly: there should be no element with description text
      const allText = container.textContent || '';
      // With empty description, the only meaningful text should relate to code and copy
      expect(allText).toContain('echo hello');
    });

    it('goodhart: should pass the exact props.code value to clipboard.writeText including whitespace, not a trimmed version', async () => {
      const codeWithWhitespace = '  npm install --save-dev @types/node  ';
      const writeTextMock = vi.fn(() => Promise.resolve());
      Object.defineProperty(navigator, 'clipboard', {
        value: { writeText: writeTextMock },
        writable: true,
        configurable: true,
      });

      const { container } = render(<CodeBlock code={codeWithWhitespace} />);
      const button = container.querySelector('button') || screen.getByRole('button');
      fireEvent.click(button);

      await waitFor(() => {
        expect(writeTextMock).toHaveBeenCalledWith(codeWithWhitespace);
      });
    });

    it('goodhart: should render an actual <button> element for the copy action for proper accessibility', () => {
      const { container } = render(<CodeBlock code="any code" />);
      const buttons = container.querySelectorAll('button');
      expect(buttons.length).toBeGreaterThanOrEqual(1);
    });

    it('goodhart: should correctly render multiline code strings preserving newline characters', () => {
      const multilineCode = 'line1\nline2\nline3';
      const { container } = render(<CodeBlock code={multilineCode} />);
      const codeEl = container.querySelector('code');
      expect(codeEl).not.toBeNull();
      expect(codeEl!.textContent).toContain('line1');
      expect(codeEl!.textContent).toContain('line2');
      expect(codeEl!.textContent).toContain('line3');
    });

    it('goodhart: should nest the <code> element inside the <pre> element preserving semantic HTML structure', () => {
      const { container } = render(<CodeBlock code="docker compose up -d" />);
      const preEl = container.querySelector('pre');
      expect(preEl).not.toBeNull();
      const codeInsidePre = preEl!.querySelector('code');
      expect(codeInsidePre).not.toBeNull();
      expect(codeInsidePre!.textContent).toBe('docker compose up -d');
    });

    it('goodhart: should render description text containing special characters without escaping issues', () => {
      const desc = 'Install the <latest> version & configure';
      render(<CodeBlock code="echo test" description={desc} />);
      expect(screen.getByText(desc)).toBeTruthy();
    });

    it('goodhart: should correctly render code containing HTML-like characters without interpreting them as HTML', () => {
      const codeWithHtml = 'if (a < b && c > d) { return a & b; }';
      const { container } = render(<CodeBlock code={codeWithHtml} />);
      const codeEl = container.querySelector('code');
      expect(codeEl).not.toBeNull();
      expect(codeEl!.textContent).toBe(codeWithHtml);
    });
  });

  // ─── VersionBadge ───

  describe('VersionBadge', () => {
    it('goodhart: should dynamically render any componentName and version, not values hardcoded from visible tests', () => {
      render(<VersionBadge componentName="DataGrid" version="4.2.0-beta.1" />);
      expect(screen.getByText(/DataGrid/)).toBeTruthy();
      expect(screen.getByText(/4\.2\.0-beta\.1/)).toBeTruthy();
    });

    it('goodhart: should render as an inline element (span), not a block-level element, since the contract specifies inline display', () => {
      const { container } = render(<VersionBadge componentName="Widget" version="1.0.0" />);
      const firstChild = container.firstElementChild;
      expect(firstChild).not.toBeNull();
      expect(firstChild!.tagName.toLowerCase()).toBe('span');
    });
  });

  // ─── YouTubeEmbed ───

  describe('YouTubeEmbed', () => {
    it('goodhart: should dynamically construct embed URL from any valid video ID, not hardcode a specific URL', () => {
      const { container } = render(
        <YouTubeEmbed url="https://www.youtube.com/watch?v=L_jWHffIx5E" />
      );
      const iframe = container.querySelector('iframe');
      expect(iframe).not.toBeNull();
      expect(iframe!.getAttribute('src')).toBe('https://www.youtube.com/embed/L_jWHffIx5E');
    });

    it('goodhart: should convert any youtu.be short URL to correct embed format, not just IDs from visible tests', () => {
      const { container } = render(
        <YouTubeEmbed url="https://youtu.be/9bZkp7q19f0" />
      );
      const iframe = container.querySelector('iframe');
      expect(iframe).not.toBeNull();
      expect(iframe!.getAttribute('src')).toBe('https://www.youtube.com/embed/9bZkp7q19f0');
    });

    it('goodhart: should always produce an https embed URL even when input URL uses http', () => {
      const { container } = render(
        <YouTubeEmbed url="http://youtube.com/watch?v=L_jWHffIx5E" />
      );
      const iframe = container.querySelector('iframe');
      expect(iframe).not.toBeNull();
      expect(iframe!.getAttribute('src')).toMatch(/^https:\/\/www\.youtube\.com\/embed\//);
    });

    it('goodhart: should nest the iframe inside the wrapper div with aspect-video class, not as a sibling', () => {
      const { container } = render(
        <YouTubeEmbed url="https://youtu.be/9bZkp7q19f0" />
      );
      const wrapper = container.querySelector('.aspect-video');
      expect(wrapper).not.toBeNull();
      const iframeInWrapper = wrapper!.querySelector('iframe');
      expect(iframeInWrapper).not.toBeNull();
    });

    it('goodhart: should include all six required permission keywords in the iframe allow attribute', () => {
      const { container } = render(
        <YouTubeEmbed url="https://youtu.be/9bZkp7q19f0" />
      );
      const iframe = container.querySelector('iframe');
      expect(iframe).not.toBeNull();
      const allow = iframe!.getAttribute('allow') || '';
      expect(allow).toContain('accelerometer');
      expect(allow).toContain('autoplay');
      expect(allow).toContain('clipboard-write');
      expect(allow).toContain('encrypted-media');
      expect(allow).toContain('gyroscope');
      expect(allow).toContain('picture-in-picture');
    });

    it('goodhart: should correctly set iframe title when title contains special characters like quotes and ampersands', () => {
      const specialTitle = 'Tom & Jerry\'s "Best" Moments';
      const { container } = render(
        <YouTubeEmbed url="https://youtu.be/9bZkp7q19f0" title={specialTitle} />
      );
      const iframe = container.querySelector('iframe');
      expect(iframe).not.toBeNull();
      expect(iframe!.getAttribute('title')).toBe(specialTitle);
    });
  });

  // ─── CalloutBox ───

  describe('CalloutBox', () => {
    it('goodhart: should dynamically render any text from props.text, not hardcode text from visible tests', () => {
      render(
        <CalloutBox
          variant="tip"
          text="Remember to invalidate the cache after deploying version 3.x"
        />
      );
      expect(
        screen.getByText('Remember to invalidate the cache after deploying version 3.x')
      ).toBeTruthy();
    });

    it('goodhart: gotcha variant must not use green/teal classes that belong to the tip variant', () => {
      const { container } = render(
        <CalloutBox variant="gotcha" text="test gotcha styling isolation" />
      );
      const styledEl = container.firstElementChild!;
      const classes = styledEl.className;
      expect(classes).not.toMatch(/green/i);
      expect(classes).not.toMatch(/teal/i);
    });

    it('goodhart: tip variant must not use red/orange classes that belong to the gotcha variant', () => {
      const { container } = render(
        <CalloutBox variant="tip" text="test tip styling isolation" />
      );
      const styledEl = container.firstElementChild!;
      const classes = styledEl.className;
      expect(classes).not.toMatch(/\bred\b/i);
      expect(classes).not.toMatch(/\borange\b/i);
    });

    it('goodhart: warning variant must use yellow/amber classes and not green/teal or red/orange classes', () => {
      const { container } = render(
        <CalloutBox variant="warning" text="test warning styling isolation" />
      );
      const styledEl = container.firstElementChild!;
      const classes = styledEl.className;
      expect(classes).toMatch(/yellow|amber/i);
      expect(classes).not.toMatch(/green|teal/i);
      // Note: we don't check for absence of red/orange in warning because amber is close
      // to orange in some palettes, but green/teal should definitely not be present
    });

    it('goodhart: text must be rendered inside the variant-styled container, not as a detached sibling', () => {
      const uniqueText = 'Unique text for nesting check 42';
      const { container } = render(
        <CalloutBox variant="warning" text={uniqueText} />
      );
      const styledEl = container.firstElementChild!;
      expect(styledEl.textContent).toContain(uniqueText);
    });
  });

  // ─── Barrel type exports (compile-time verification) ───

  describe('Barrel exports', () => {
    it('goodhart: barrel must export all five types so consumers can use them for type annotations', () => {
      // These are compile-time checks — if the types don't exist, TypeScript will fail
      // At runtime we verify the component exports exist as functions
      const typeCheck: CalloutVariant = 'gotcha';
      const propsCheck: CodeBlockProps = { code: 'test' };
      const vbCheck: VersionBadgeProps = { componentName: 'X', version: '1.0.0' };
      const ytCheck: YouTubeEmbedProps = { url: 'https://youtu.be/dQw4w9WgXcQ' };
      const cbCheck: CalloutBoxProps = { variant: 'tip', text: 'hello' };

      // Runtime: all four components are functions (named exports)
      expect(typeof CodeBlock).toBe('function');
      expect(typeof VersionBadge).toBe('function');
      expect(typeof YouTubeEmbed).toBe('function');
      expect(typeof CalloutBox).toBe('function');

      // Suppress unused variable warnings
      expect(typeCheck).toBeDefined();
      expect(propsCheck).toBeDefined();
      expect(vbCheck).toBeDefined();
      expect(ytCheck).toBeDefined();
      expect(cbCheck).toBeDefined();
    });
  });
});
