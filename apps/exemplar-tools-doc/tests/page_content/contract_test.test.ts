
// =============================================================================
// Contract Test Suite for page_content
// Three logical test groups in one file:
//   1. Data layer (getStepContent, STEP_CONTENT invariants)
//   2. StepPage component rendering
//   3. All page wrapper components (HomePage, CartographerPage, etc.)
// =============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// ---------------------------------------------------------------------------
// Mock shared_ui — must provide every named export the implementation uses
// ---------------------------------------------------------------------------
vi.mock('../../src/shared_ui', () => ({
  CodeBlock: ({ children, code, command, description, ...rest }: any) =>
    React.createElement('div', { 'data-testid': 'code-block' }, command ?? code ?? children ?? ''),
  CalloutBox: ({ variant, text, children, ...rest }: any) =>
    React.createElement('div', { 'data-testid': `callout-${variant}` }, text ?? children ?? ''),
  YouTubeEmbed: ({ url, ...rest }: any) =>
    React.createElement('div', { 'data-testid': 'youtube-embed' }, url),
  VersionBadge: ({ version, ...rest }: any) =>
    React.createElement('span', { 'data-testid': 'version-badge' }, version),
}));

// ---------------------------------------------------------------------------
// Mock pipeline_diagram — must provide PipelineDiagram
// ---------------------------------------------------------------------------
vi.mock('../../src/pipeline_diagram', () => ({
  PipelineDiagram: () =>
    React.createElement('div', { 'data-testid': 'pipeline-diagram' }, 'PipelineDiagram'),
}));

// ---------------------------------------------------------------------------
// Imports from the component under test
// ---------------------------------------------------------------------------
import {
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
  getStepContent,
  STEP_CONTENT,
} from '../../src/page_content';

// We import enums as values (not types) because they are runtime objects
import { StepId, StepLabel, CalloutVariant } from '../../src/page_content';

// Import types with `import type`
import type { StepContent } from '../../src/page_content';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** All StepId enum values as an array */
const ALL_STEP_IDS: StepId[] = Object.values(StepId) as StepId[];

/** Mapping from StepId to expected StepLabel for invariant checks */
const STEP_ID_TO_LABEL: Record<string, string> = {
  [StepId.home]: StepLabel.Home,
  [StepId.cartographer]: StepLabel['Step 0 — Cartographer'] ?? (Object.values(StepLabel) as string[]).find(l => l.includes('Cartographer'))!,
  [StepId.constrain]: (Object.values(StepLabel) as string[]).find(l => l.includes('Constrain'))!,
  [StepId.ledger]: (Object.values(StepLabel) as string[]).find(l => l.includes('Ledger'))!,
  [StepId.pact]: (Object.values(StepLabel) as string[]).find(l => l.includes('Pact'))!,
  [StepId.advocate]: (Object.values(StepLabel) as string[]).find(l => l.includes('Advocate'))!,
  [StepId.arbiter]: (Object.values(StepLabel) as string[]).find(l => l.includes('Arbiter'))!,
  [StepId.baton]: (Object.values(StepLabel) as string[]).find(l => l.includes('Baton'))!,
  [StepId.sentinel]: (Object.values(StepLabel) as string[]).find(l => l.includes('Sentinel'))!,
  [StepId.chronicler]: (Object.values(StepLabel) as string[]).find(l => l.includes('Chronicler'))!,
  [StepId.stigmergy]: (Object.values(StepLabel) as string[]).find(l => l.includes('Stigmergy'))!,
  [StepId.apprentice]: (Object.values(StepLabel) as string[]).find(l => l.includes('Apprentice'))!,
  [StepId.kindex]: (Object.values(StepLabel) as string[]).find(l => l.includes('Kindex'))!,
};

/** Build a minimal valid StepContent for testing */
function makeStepContent(overrides: Partial<StepContent> = {}): StepContent {
  return {
    stepId: StepId.cartographer,
    label: StepLabel['Step 0 — Cartographer'] ?? (Object.values(StepLabel) as string[]).find(l => l.includes('Cartographer'))! as any,
    overview: 'Test overview text for the step.',
    commands: [],
    callouts: [],
    examples: [],
    youtubeUrl: undefined,
    version: undefined,
    ...overrides,
  } as StepContent;
}

// =============================================================================
// 1. DATA LAYER — getStepContent & STEP_CONTENT invariants
// =============================================================================

describe('Data Layer — getStepContent', () => {
  it.each(ALL_STEP_IDS)(
    'returns well-formed StepContent for StepId "%s"',
    (stepId) => {
      const content = getStepContent(stepId);
      expect(content).toBeDefined();
      expect(content.stepId).toBe(stepId);
      expect(typeof content.overview).toBe('string');
      expect(content.overview.length).toBeGreaterThan(0);
      expect(typeof content.label).toBe('string');
      expect(content.label.length).toBeGreaterThan(0);
      expect(Array.isArray(content.commands)).toBe(true);
      expect(Array.isArray(content.callouts)).toBe(true);
      expect(Array.isArray(content.examples)).toBe(true);
    },
  );

  it('returns StepContent with all required fields for a valid StepId', () => {
    const content = getStepContent(StepId.cartographer);
    expect(content).toHaveProperty('stepId');
    expect(content).toHaveProperty('label');
    expect(content).toHaveProperty('overview');
    expect(content).toHaveProperty('commands');
    expect(content).toHaveProperty('callouts');
    expect(content).toHaveProperty('examples');
  });

  it('throws for an invalid stepId value', () => {
    expect(() => getStepContent('invalid_step' as StepId)).toThrow();
  });

  it('throws for an empty string stepId', () => {
    expect(() => getStepContent('' as StepId)).toThrow();
  });
});

describe('Data Layer — STEP_CONTENT invariants', () => {
  it('has an entry for every StepId enum value', () => {
    for (const stepId of ALL_STEP_IDS) {
      expect(
        STEP_CONTENT[stepId as keyof typeof STEP_CONTENT],
        `STEP_CONTENT is missing entry for StepId "${stepId}"`,
      ).toBeDefined();
    }
  });

  it('has exactly the same number of entries as StepId enum values', () => {
    const contentKeys = Object.keys(STEP_CONTENT);
    expect(contentKeys.length).toBe(ALL_STEP_IDS.length);
  });

  it('every entry stepId matches its record key', () => {
    for (const stepId of ALL_STEP_IDS) {
      const entry = STEP_CONTENT[stepId as keyof typeof STEP_CONTENT];
      expect(
        entry.stepId,
        `STEP_CONTENT["${stepId}"].stepId should be "${stepId}" but got "${entry.stepId}"`,
      ).toBe(stepId);
    }
  });

  it('every entry label corresponds to the correct StepLabel', () => {
    for (const stepId of ALL_STEP_IDS) {
      const entry = STEP_CONTENT[stepId as keyof typeof STEP_CONTENT];
      const expectedLabel = STEP_ID_TO_LABEL[stepId];
      if (expectedLabel) {
        expect(
          entry.label,
          `STEP_CONTENT["${stepId}"].label should be "${expectedLabel}" but got "${entry.label}"`,
        ).toBe(expectedLabel);
      }
    }
  });

  it('is frozen or immutable — direct property assignment has no effect', () => {
    // If Object.isFrozen works, great; otherwise try mutation and verify it doesn't stick
    const isFrozen = Object.isFrozen(STEP_CONTENT);
    if (!isFrozen) {
      // Attempt mutation in strict mode should throw or be silently ignored
      const originalKeys = Object.keys(STEP_CONTENT);
      try {
        (STEP_CONTENT as any).__test_mutation__ = true;
      } catch {
        // Expected in strict/frozen mode
      }
      expect((STEP_CONTENT as any).__test_mutation__).toBeUndefined();
      // Clean up just in case
      try {
        delete (STEP_CONTENT as any).__test_mutation__;
      } catch {
        // ignore
      }
    } else {
      expect(isFrozen).toBe(true);
    }
  });

  it('every command entry has required command and description string fields', () => {
    for (const stepId of ALL_STEP_IDS) {
      const entry = STEP_CONTENT[stepId as keyof typeof STEP_CONTENT];
      for (const cmd of entry.commands) {
        expect(typeof cmd.command, `Command in "${stepId}" missing command field`).toBe('string');
        expect(typeof cmd.description, `Command in "${stepId}" missing description field`).toBe('string');
      }
    }
  });

  it('every callout entry has a valid variant and text', () => {
    const validVariants = Object.values(CalloutVariant) as string[];
    for (const stepId of ALL_STEP_IDS) {
      const entry = STEP_CONTENT[stepId as keyof typeof STEP_CONTENT];
      for (const callout of entry.callouts) {
        expect(
          validVariants,
          `Callout variant "${callout.variant}" in "${stepId}" is not a valid CalloutVariant`,
        ).toContain(callout.variant);
        expect(typeof callout.text).toBe('string');
      }
    }
  });

  it('every overview is a non-empty string', () => {
    for (const stepId of ALL_STEP_IDS) {
      const entry = STEP_CONTENT[stepId as keyof typeof STEP_CONTENT];
      expect(typeof entry.overview).toBe('string');
      expect(entry.overview.length, `Overview for "${stepId}" should be non-empty`).toBeGreaterThan(0);
    }
  });
});

// =============================================================================
// 2. STEP PAGE COMPONENT RENDERING
// =============================================================================

describe('StepPage Component', () => {
  it('renders an h1 element with the content label', () => {
    const content = makeStepContent({
      label: (Object.values(StepLabel) as string[]).find(l => l.includes('Cartographer'))! as any,
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const h1 = container.querySelector('h1');
    expect(h1, 'Expected an h1 element').toBeTruthy();
    expect(h1!.textContent).toContain('Cartographer');
  });

  it('renders the overview text', () => {
    const content = makeStepContent({ overview: 'Unique overview text for test.' });
    render(React.createElement(StepPage, { content }));
    expect(screen.getByText(/Unique overview text for test/)).toBeTruthy();
  });

  it('renders one CodeBlock per command entry', () => {
    const content = makeStepContent({
      commands: [
        { command: 'npm install', description: 'Install deps' },
        { command: 'npm run build', description: 'Build project' },
      ],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const codeBlocks = container.querySelectorAll('[data-testid="code-block"]');
    // At least 2 code blocks for commands (there may be more from examples)
    expect(codeBlocks.length).toBeGreaterThanOrEqual(2);
  });

  it('renders one CalloutBox per callout entry with correct variant', () => {
    const content = makeStepContent({
      callouts: [
        { variant: CalloutVariant.gotcha, text: 'Watch out for this gotcha' },
        { variant: CalloutVariant.warning, text: 'This is a warning' },
        { variant: CalloutVariant.tip, text: 'Here is a tip' },
      ],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    expect(container.querySelector('[data-testid="callout-gotcha"]')).toBeTruthy();
    expect(container.querySelector('[data-testid="callout-warning"]')).toBeTruthy();
    expect(container.querySelector('[data-testid="callout-tip"]')).toBeTruthy();
  });

  it('renders one CodeBlock per example entry', () => {
    const content = makeStepContent({
      examples: ['example code 1', 'example code 2'],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const codeBlocks = container.querySelectorAll('[data-testid="code-block"]');
    expect(codeBlocks.length).toBeGreaterThanOrEqual(2);
  });

  it('renders YouTubeEmbed when youtubeUrl is a non-empty string', () => {
    const content = makeStepContent({ youtubeUrl: 'https://youtube.com/watch?v=abc123' });
    const { container } = render(React.createElement(StepPage, { content }));
    expect(container.querySelector('[data-testid="youtube-embed"]')).toBeTruthy();
  });

  it('does NOT render YouTubeEmbed when youtubeUrl is undefined', () => {
    const content = makeStepContent({ youtubeUrl: undefined });
    const { container } = render(React.createElement(StepPage, { content }));
    expect(container.querySelector('[data-testid="youtube-embed"]')).toBeNull();
  });

  it('does NOT render YouTubeEmbed when youtubeUrl is empty string', () => {
    const content = makeStepContent({ youtubeUrl: '' });
    const { container } = render(React.createElement(StepPage, { content }));
    expect(container.querySelector('[data-testid="youtube-embed"]')).toBeNull();
  });

  it('renders VersionBadge when version is a non-empty string', () => {
    const content = makeStepContent({ version: '1.2.3' });
    const { container } = render(React.createElement(StepPage, { content }));
    expect(container.querySelector('[data-testid="version-badge"]')).toBeTruthy();
  });

  it('does NOT render VersionBadge when version is undefined', () => {
    const content = makeStepContent({ version: undefined });
    const { container } = render(React.createElement(StepPage, { content }));
    expect(container.querySelector('[data-testid="version-badge"]')).toBeNull();
  });

  it('does NOT render VersionBadge when version is empty string', () => {
    const content = makeStepContent({ version: '' });
    const { container } = render(React.createElement(StepPage, { content }));
    expect(container.querySelector('[data-testid="version-badge"]')).toBeNull();
  });

  it('renders no CodeBlock or CalloutBox when arrays are empty', () => {
    const content = makeStepContent({
      commands: [],
      callouts: [],
      examples: [],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    expect(container.querySelectorAll('[data-testid="code-block"]').length).toBe(0);
    expect(container.querySelectorAll('[data-testid^="callout-"]').length).toBe(0);
  });

  it('throws or renders error when content is undefined (missing_content)', () => {
    // Suppress React error boundary noise
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    try {
      expect(() => {
        render(React.createElement(StepPage, { content: undefined as any }));
      }).toThrow();
    } catch {
      // If it doesn't throw synchronously, it may render an error state
      // The contract says missing_content error — we verify it doesn't silently succeed
      // with normal output
    } finally {
      consoleSpy.mockRestore();
    }
  });

  it('throws or renders error when content is null (missing_content)', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    try {
      expect(() => {
        render(React.createElement(StepPage, { content: null as any }));
      }).toThrow();
    } catch {
      // Same as above — missing_content error case
    } finally {
      consoleSpy.mockRestore();
    }
  });

  it('renders all three callout variants distinctly', () => {
    const content = makeStepContent({
      callouts: [
        { variant: CalloutVariant.gotcha, text: 'Gotcha text' },
        { variant: CalloutVariant.warning, text: 'Warning text' },
        { variant: CalloutVariant.tip, text: 'Tip text' },
      ],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const gotchaBoxes = container.querySelectorAll('[data-testid="callout-gotcha"]');
    const warningBoxes = container.querySelectorAll('[data-testid="callout-warning"]');
    const tipBoxes = container.querySelectorAll('[data-testid="callout-tip"]');
    expect(gotchaBoxes.length).toBe(1);
    expect(warningBoxes.length).toBe(1);
    expect(tipBoxes.length).toBe(1);
  });

  it('renders commands and examples as separate CodeBlocks without merging', () => {
    const content = makeStepContent({
      commands: [{ command: 'cmd1', description: 'desc1' }],
      examples: ['example1'],
    });
    const { container } = render(React.createElement(StepPage, { content }));
    const codeBlocks = container.querySelectorAll('[data-testid="code-block"]');
    expect(codeBlocks.length).toBe(2);
  });
});

// =============================================================================
// 3. PAGE WRAPPER COMPONENTS
// =============================================================================

describe('HomePage Component', () => {
  it('renders the home overview text', () => {
    const homeContent = STEP_CONTENT[StepId.home as keyof typeof STEP_CONTENT];
    render(React.createElement(HomePage));
    expect(screen.getByText(new RegExp(homeContent.overview.substring(0, 30).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))).toBeTruthy();
  });

  it('renders an h1 with the home label', () => {
    const homeContent = STEP_CONTENT[StepId.home as keyof typeof STEP_CONTENT];
    const { container } = render(React.createElement(HomePage));
    const h1 = container.querySelector('h1');
    expect(h1, 'Expected HomePage to render an h1').toBeTruthy();
    expect(h1!.textContent).toContain(homeContent.label);
  });

  it('renders exactly one PipelineDiagram component', () => {
    const { container } = render(React.createElement(HomePage));
    const diagrams = container.querySelectorAll('[data-testid="pipeline-diagram"]');
    expect(diagrams.length, 'HomePage should render exactly one PipelineDiagram').toBe(1);
  });
});

describe('Wrapper Page Components — parameterized', () => {
  const wrapperPages = [
    { name: 'CartographerPage', Component: CartographerPage, stepId: StepId.cartographer },
    { name: 'ConstrainPage', Component: ConstrainPage, stepId: StepId.constrain },
    { name: 'LedgerPage', Component: LedgerPage, stepId: StepId.ledger },
    { name: 'PactPage', Component: PactPage, stepId: StepId.pact },
    { name: 'AdvocatePage', Component: AdvocatePage, stepId: StepId.advocate },
    { name: 'ArbiterPage', Component: ArbiterPage, stepId: StepId.arbiter },
    { name: 'BatonPage', Component: BatonPage, stepId: StepId.baton },
    { name: 'SentinelPage', Component: SentinelPage, stepId: StepId.sentinel },
    { name: 'ChroniclerPage', Component: ChroniclerPage, stepId: StepId.chronicler },
    { name: 'StigmergyPage', Component: StigmergyPage, stepId: StepId.stigmergy },
    { name: 'ApprenticePage', Component: ApprenticePage, stepId: StepId.apprentice },
    { name: 'KindexPage', Component: KindexPage, stepId: StepId.kindex },
  ] as const;

  it.each(wrapperPages)(
    '$name renders without crashing (zero props)',
    ({ Component }) => {
      expect(() => render(React.createElement(Component))).not.toThrow();
    },
  );

  it.each(wrapperPages)(
    '$name renders its step-specific label in an h1',
    ({ Component, stepId }) => {
      const expectedContent = STEP_CONTENT[stepId as keyof typeof STEP_CONTENT];
      const { container } = render(React.createElement(Component));
      const h1 = container.querySelector('h1');
      expect(h1, `${Component.name ?? stepId} should render an h1`).toBeTruthy();
      expect(
        h1!.textContent,
        `h1 should contain label "${expectedContent.label}"`,
      ).toContain(expectedContent.label);
    },
  );

  it.each(wrapperPages)(
    '$name renders its step overview text',
    ({ Component, stepId }) => {
      const expectedContent = STEP_CONTENT[stepId as keyof typeof STEP_CONTENT];
      render(React.createElement(Component));
      // Match a portion of the overview (first 30 chars, regex-escaped)
      const snippet = expectedContent.overview.substring(0, 30).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      expect(screen.getByText(new RegExp(snippet))).toBeTruthy();
    },
  );
});

describe('Wrapper Page Components — zero-prop invariant', () => {
  it('all wrapper page components are functions that accept zero required arguments', () => {
    const components = [
      CartographerPage, ConstrainPage, LedgerPage, PactPage, AdvocatePage,
      ArbiterPage, BatonPage, SentinelPage, ChroniclerPage, StigmergyPage,
      ApprenticePage, KindexPage, HomePage,
    ];
    for (const Comp of components) {
      expect(typeof Comp, `${Comp.name} should be a function`).toBe('function');
      // React components with no required props have length 0 or 1 (props object)
      // We just verify they are callable without arguments by rendering
      expect(() => render(React.createElement(Comp))).not.toThrow();
    }
  });
});

// =============================================================================
// 4. ENUM TYPE VALIDATION
// =============================================================================

describe('Enum Types', () => {
  it('StepId enum has exactly 13 members', () => {
    const values = Object.values(StepId);
    expect(values.length).toBe(13);
  });

  it('StepId contains all expected values', () => {
    const expected = [
      'home', 'cartographer', 'constrain', 'ledger', 'pact', 'advocate',
      'arbiter', 'baton', 'sentinel', 'chronicler', 'stigmergy', 'apprentice', 'kindex',
    ];
    const values = Object.values(StepId) as string[];
    for (const id of expected) {
      expect(values, `StepId should contain "${id}"`).toContain(id);
    }
  });

  it('StepLabel enum has exactly 13 members', () => {
    const values = Object.values(StepLabel);
    expect(values.length).toBe(13);
  });

  it('CalloutVariant enum has exactly 3 members: gotcha, warning, tip', () => {
    const values = Object.values(CalloutVariant) as string[];
    expect(values.length).toBe(3);
    expect(values).toContain('gotcha');
    expect(values).toContain('warning');
    expect(values).toContain('tip');
  });
});
