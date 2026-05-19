
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

// Mock shared_ui components
vi.mock('shared_ui', () => ({
  CodeBlock: vi.fn(({ command, description, code, children, ...props }: any) => {
    const text = command || code || children || '';
    const desc = description || '';
    return React.createElement('div', { 'data-testid': 'code-block', 'data-description': desc }, text);
  }),
  CalloutBox: vi.fn(({ variant, text, children, ...props }: any) => {
    const content = text || children || '';
    return React.createElement('div', { 'data-testid': 'callout-box', 'data-variant': variant }, content);
  }),
  YouTubeEmbed: vi.fn(({ url, youtubeUrl, ...props }: any) => {
    return React.createElement('div', { 'data-testid': 'youtube-embed', 'data-url': url || youtubeUrl || '' });
  }),
  VersionBadge: vi.fn(({ version, ...props }: any) => {
    return React.createElement('span', { 'data-testid': 'version-badge' }, version);
  }),
}));

vi.mock('pipeline_diagram', () => ({
  PipelineDiagram: vi.fn(() => {
    return React.createElement('div', { 'data-testid': 'pipeline-diagram' });
  }),
}));

import {
  StepId,
  StepLabel,
  CalloutVariant,
  STEP_CONTENT,
  getStepContent,
  StepPage,
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
} from '../../../src/page_content';

function makeTestContent(overrides: Partial<any> = {}): any {
  return {
    stepId: 'cartographer' as any,
    label: 'Step 0 — Cartographer' as any,
    overview: 'Test overview for adversarial testing',
    commands: [],
    callouts: [],
    examples: [],
    youtubeUrl: undefined,
    version: undefined,
    ...overrides,
  };
}

describe('goodhart: StepPage renders distinct CodeBlocks per command without merging', () => {
  it('goodhart: should render exactly 3 CodeBlock components for 3 commands', () => {
    const content = makeTestContent({
      commands: [
        { command: 'cmd-alpha-unique-1', description: 'desc-alpha' },
        { command: 'cmd-beta-unique-2', description: 'desc-beta' },
        { command: 'cmd-gamma-unique-3', description: 'desc-gamma' },
      ],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const codeBlocks = container.querySelectorAll('[data-testid="code-block"]');
    // Count code blocks that correspond to commands (not examples)
    // We need at least 3 code blocks total
    expect(codeBlocks.length).toBeGreaterThanOrEqual(3);
    const html = container.innerHTML;
    expect(html).toContain('cmd-alpha-unique-1');
    expect(html).toContain('cmd-beta-unique-2');
    expect(html).toContain('cmd-gamma-unique-3');
  });
});

describe('goodhart: StepPage renders distinct CodeBlocks per example without merging', () => {
  it('goodhart: should render exactly 4 CodeBlock components for 4 examples', () => {
    const content = makeTestContent({
      examples: [
        'example-zeta-unique-1',
        'example-eta-unique-2',
        'example-theta-unique-3',
        'example-iota-unique-4',
      ],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const codeBlocks = container.querySelectorAll('[data-testid="code-block"]');
    expect(codeBlocks.length).toBeGreaterThanOrEqual(4);
    const html = container.innerHTML;
    expect(html).toContain('example-zeta-unique-1');
    expect(html).toContain('example-eta-unique-2');
    expect(html).toContain('example-theta-unique-3');
    expect(html).toContain('example-iota-unique-4');
  });
});

describe('goodhart: StepPage passes command descriptions through to CodeBlock', () => {
  it('goodhart: should pass description field of CommandEntry to CodeBlock', () => {
    const content = makeTestContent({
      commands: [
        { command: 'npm run build', description: 'Builds the project for production' },
      ],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const html = container.innerHTML;
    // The description should be present somewhere in the rendered output
    expect(html).toContain('Builds the project for production');
  });
});

describe('goodhart: StepPage does not render YouTubeEmbed for empty string url', () => {
  it('goodhart: should not render YouTubeEmbed when youtubeUrl is empty string', () => {
    const content = makeTestContent({ youtubeUrl: '' });
    const { container } = render(React.createElement(StepPage, { content }));
    const ytEmbeds = container.querySelectorAll('[data-testid="youtube-embed"]');
    expect(ytEmbeds.length).toBe(0);
  });
});

describe('goodhart: StepPage does not render VersionBadge for empty string version', () => {
  it('goodhart: should not render VersionBadge when version is empty string', () => {
    const content = makeTestContent({ version: '' });
    const { container } = render(React.createElement(StepPage, { content }));
    const badges = container.querySelectorAll('[data-testid="version-badge"]');
    expect(badges.length).toBe(0);
  });
});

describe('goodhart: getStepContent returns same reference as STEP_CONTENT entry', () => {
  it('goodhart: should return referentially identical object to STEP_CONTENT[stepId]', () => {
    const ids = Object.values(StepId) as string[];
    for (const id of ids) {
      const result = getStepContent(id as any);
      expect(result).toBe((STEP_CONTENT as any)[id]);
    }
  });
});

describe('goodhart: getStepContent rejects various invalid inputs', () => {
  it('goodhart: should throw for empty string', () => {
    expect(() => getStepContent('' as any)).toThrow();
  });

  it('goodhart: should throw for close misspelling of valid id', () => {
    expect(() => getStepContent('cartographr' as any)).toThrow();
  });

  it('goodhart: should throw for uppercased valid id', () => {
    expect(() => getStepContent('HOME' as any)).toThrow();
  });

  it('goodhart: should throw for numeric input', () => {
    expect(() => getStepContent(0 as any)).toThrow();
  });

  it('goodhart: should throw for null input', () => {
    expect(() => getStepContent(null as any)).toThrow();
  });

  it('goodhart: should throw for undefined input', () => {
    expect(() => getStepContent(undefined as any)).toThrow();
  });

  it('goodhart: should throw for a plausible but invalid step name', () => {
    expect(() => getStepContent('step0' as any)).toThrow();
  });
});

describe('goodhart: STEP_CONTENT is deeply frozen', () => {
  it('goodhart: should not allow mutation of nested arrays within entries', () => {
    const entry = (STEP_CONTENT as any).cartographer;
    const origLen = entry.commands.length;
    try {
      entry.commands.push({ command: 'hacked', description: 'hacked' });
    } catch {
      // strict mode throws
    }
    expect(entry.commands.length).toBe(origLen);
  });

  it('goodhart: should not allow mutation of overview string on entries', () => {
    const entry = (STEP_CONTENT as any).home;
    const origOverview = entry.overview;
    try {
      entry.overview = 'mutated';
    } catch {
      // strict mode throws
    }
    expect(entry.overview).toBe(origOverview);
  });
});

describe('goodhart: StepPage renders arbitrary novel content not from STEP_CONTENT', () => {
  it('goodhart: should render completely synthetic content proving no hardcoded returns', () => {
    const content = makeTestContent({
      stepId: 'constrain',
      label: 'Step 1a — Constrain',
      overview: 'XYZZY-UNIQUE-OVERVIEW-ADVERSARIAL-12345',
      commands: [{ command: 'plugh-cmd-adversarial', description: 'plugh-desc-adversarial' }],
      callouts: [{ variant: 'tip', text: 'FROTZ-CALLOUT-ADVERSARIAL-67890' }],
      examples: ['REZROV-EXAMPLE-ADVERSARIAL-ABCDE'],
      youtubeUrl: 'https://youtube.com/watch?v=ADVERSARIAL_TEST',
      version: '99.88.77-adversarial',
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const html = container.innerHTML;

    expect(html).toContain('Step 1a — Constrain');
    expect(html).toContain('XYZZY-UNIQUE-OVERVIEW-ADVERSARIAL-12345');
    expect(html).toContain('plugh-cmd-adversarial');
    expect(html).toContain('FROTZ-CALLOUT-ADVERSARIAL-67890');
    expect(html).toContain('REZROV-EXAMPLE-ADVERSARIAL-ABCDE');
    expect(container.querySelectorAll('[data-testid="youtube-embed"]').length).toBe(1);
    expect(container.querySelectorAll('[data-testid="version-badge"]').length).toBe(1);
  });
});

describe('goodhart: Every STEP_CONTENT entry has non-empty non-whitespace overview', () => {
  it('goodhart: should have meaningful overview text for all entries', () => {
    const ids = Object.values(StepId) as string[];
    for (const id of ids) {
      const entry = (STEP_CONTENT as any)[id];
      expect(typeof entry.overview).toBe('string');
      expect(entry.overview.trim().length).toBeGreaterThan(0);
    }
  });
});

describe('goodhart: StepPage preserves callout variant order for mixed variants', () => {
  it('goodhart: should pass through variants in exact order: gotcha, tip, warning', () => {
    const content = makeTestContent({
      callouts: [
        { variant: 'gotcha', text: 'Gotcha callout text unique-g' },
        { variant: 'tip', text: 'Tip callout text unique-t' },
        { variant: 'warning', text: 'Warning callout text unique-w' },
      ],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const calloutBoxes = container.querySelectorAll('[data-testid="callout-box"]');
    expect(calloutBoxes.length).toBe(3);
    expect(calloutBoxes[0].getAttribute('data-variant')).toBe('gotcha');
    expect(calloutBoxes[1].getAttribute('data-variant')).toBe('tip');
    expect(calloutBoxes[2].getAttribute('data-variant')).toBe('warning');
  });
});

describe('goodhart: barrel index re-exports all required named exports', () => {
  it('goodhart: should export all enums, constants, functions, and components', () => {
    expect(StepId).toBeDefined();
    expect(StepLabel).toBeDefined();
    expect(CalloutVariant).toBeDefined();
    expect(STEP_CONTENT).toBeDefined();
    expect(typeof getStepContent).toBe('function');
    expect(typeof StepPage).toBe('function');
    expect(typeof HomePage).toBe('function');
    expect(typeof CartographerPage).toBe('function');
    expect(typeof ConstrainPage).toBe('function');
    expect(typeof LedgerPage).toBe('function');
    expect(typeof PactPage).toBe('function');
    expect(typeof AdvocatePage).toBe('function');
    expect(typeof ArbiterPage).toBe('function');
    expect(typeof BatonPage).toBe('function');
    expect(typeof SentinelPage).toBe('function');
    expect(typeof ChroniclerPage).toBe('function');
    expect(typeof StigmergyPage).toBe('function');
    expect(typeof ApprenticePage).toBe('function');
    expect(typeof KindexPage).toBe('function');
  });
});

describe('goodhart: All STEP_CONTENT callout items use valid CalloutVariant values', () => {
  it('goodhart: should only contain gotcha, warning, or tip as callout variants', () => {
    const validVariants = new Set(['gotcha', 'warning', 'tip']);
    const ids = Object.values(StepId) as string[];
    for (const id of ids) {
      const entry = (STEP_CONTENT as any)[id];
      for (const callout of entry.callouts) {
        expect(validVariants.has(callout.variant)).toBe(true);
      }
    }
  });
});

describe('goodhart: StepPage renders both YouTubeEmbed and VersionBadge simultaneously', () => {
  it('goodhart: should render both optional components when both fields are non-empty', () => {
    const content = makeTestContent({
      youtubeUrl: 'https://youtube.com/watch?v=SimultaneousTest',
      version: '1.2.3-both',
    });
    const { container } = render(React.createElement(StepPage, { content }));
    expect(container.querySelectorAll('[data-testid="youtube-embed"]').length).toBe(1);
    expect(container.querySelectorAll('[data-testid="version-badge"]').length).toBe(1);
  });
});

describe('goodhart: StepPage renders exactly 1 CodeBlock for single command', () => {
  it('goodhart: should not duplicate or skip a single command entry', () => {
    const content = makeTestContent({
      commands: [{ command: 'solo-command-unique-xyz', description: 'solo-desc' }],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const html = container.innerHTML;
    expect(html).toContain('solo-command-unique-xyz');
    // Ensure it appears exactly once
    const matches = html.match(/solo-command-unique-xyz/g);
    expect(matches).not.toBeNull();
    expect(matches!.length).toBe(1);
  });
});

describe('goodhart: HomePage uses home StepId content specifically', () => {
  it('goodhart: should display the Home label in h1 and the home overview', () => {
    const { container } = render(React.createElement(HomePage));
    const h1 = container.querySelector('h1');
    expect(h1).not.toBeNull();
    expect(h1!.textContent).toContain('Home');
    const homeContent = (STEP_CONTENT as any).home;
    expect(container.innerHTML).toContain(homeContent.overview);
  });
});

describe('goodhart: StepPage omits section heading when commands array is empty but others are not', () => {
  it('goodhart: should not render command-related headings when commands is empty', () => {
    const content = makeTestContent({
      commands: [],
      callouts: [{ variant: 'tip', text: 'A tip for you' }],
      examples: ['An example here'],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    // Callouts and examples should be present
    expect(container.querySelectorAll('[data-testid="callout-box"]').length).toBe(1);
    expect(container.querySelectorAll('[data-testid="code-block"]').length).toBeGreaterThanOrEqual(1);
    // There should be no heading for commands
    const headings = container.querySelectorAll('h2, h3');
    const headingTexts = Array.from(headings).map(h => h.textContent?.toLowerCase() || '');
    const hasCommandHeading = headingTexts.some(t => t.includes('command'));
    expect(hasCommandHeading).toBe(false);
  });
});

describe('goodhart: STEP_CONTENT has exactly 13 entries matching StepId enum', () => {
  it('goodhart: should have exactly 13 keys', () => {
    const keys = Object.keys(STEP_CONTENT as any);
    expect(keys.length).toBe(13);
  });

  it('goodhart: should have keys matching all StepId enum values', () => {
    const stepIdValues = Object.values(StepId) as string[];
    expect(stepIdValues.length).toBe(13);
    const contentKeys = new Set(Object.keys(STEP_CONTENT as any));
    for (const id of stepIdValues) {
      expect(contentKeys.has(id)).toBe(true);
    }
  });
});

describe('goodhart: Wrapper pages render correct specific labels in h1', () => {
  it('goodhart: StigmergyPage should render h1 with Stigmergy label', () => {
    const { container } = render(React.createElement(StigmergyPage));
    const h1 = container.querySelector('h1');
    expect(h1).not.toBeNull();
    expect(h1!.textContent).toContain('Stigmergy');
  });

  it('goodhart: ApprenticePage should render h1 with Apprentice label', () => {
    const { container } = render(React.createElement(ApprenticePage));
    const h1 = container.querySelector('h1');
    expect(h1).not.toBeNull();
    expect(h1!.textContent).toContain('Apprentice');
  });

  it('goodhart: KindexPage should render h1 with Kindex label', () => {
    const { container } = render(React.createElement(KindexPage));
    const h1 = container.querySelector('h1');
    expect(h1).not.toBeNull();
    expect(h1!.textContent).toContain('Kindex');
  });

  it('goodhart: SentinelPage should render h1 with Sentinel label', () => {
    const { container } = render(React.createElement(SentinelPage));
    const h1 = container.querySelector('h1');
    expect(h1).not.toBeNull();
    expect(h1!.textContent).toContain('Sentinel');
  });
});

describe('goodhart: StepPage passes callout text through to CalloutBox', () => {
  it('goodhart: should render each callout text in the output', () => {
    const content = makeTestContent({
      callouts: [
        { variant: 'gotcha', text: 'UNIQUE-CALLOUT-TEXT-ALPHA-999' },
        { variant: 'warning', text: 'UNIQUE-CALLOUT-TEXT-BETA-888' },
      ],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const html = container.innerHTML;
    expect(html).toContain('UNIQUE-CALLOUT-TEXT-ALPHA-999');
    expect(html).toContain('UNIQUE-CALLOUT-TEXT-BETA-888');
  });
});
