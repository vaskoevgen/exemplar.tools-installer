const PACT_KEY = "PACT:fd4843:page_content";

import {
  StepId,
  StepLabel,
  CalloutVariant,
} from './types';
import type {
  StepContent,
  StepContentRecord,
} from './types';

const STEP_ID_LABEL_MAP: Record<StepId, StepLabel> = {
  [StepId.home]: StepLabel.Home,
  [StepId.cartographer]: StepLabel['Step 0 — Cartographer'],
  [StepId.constrain]: StepLabel['Step 1a — Constrain'],
  [StepId.ledger]: StepLabel['Step 1b — Ledger'],
  [StepId.pact]: StepLabel['Step 2a — Pact'],
  [StepId.advocate]: StepLabel['Step 2b — Advocate'],
  [StepId.arbiter]: StepLabel['Step 3 — Arbiter'],
  [StepId.baton]: StepLabel['Step 4 — Baton'],
  [StepId.sentinel]: StepLabel['Step 5a — Sentinel'],
  [StepId.chronicler]: StepLabel['Step 5b — Chronicler'],
  [StepId.stigmergy]: StepLabel['Step 5c — Stigmergy'],
  [StepId.apprentice]: StepLabel['Step 6 — Apprentice'],
  [StepId.kindex]: StepLabel['Step 7 — Kindex'],
};

function deepFreeze<T>(obj: T): T {
  Object.freeze(obj);
  if (obj && typeof obj === 'object') {
    for (const val of Object.values(obj)) {
      if (val && typeof val === 'object' && !Object.isFrozen(val)) deepFreeze(val);
    }
  }
  return obj;
}

export const STEP_CONTENT: StepContentRecord = deepFreeze({
  [StepId.home]: {
    stepId: StepId.home,
    label: STEP_ID_LABEL_MAP[StepId.home],
    overview: 'Welcome to exemplar.tools — a step-by-step pipeline for building robust software systems. Navigate through each step to learn how to scaffold, constrain, test, and deploy your project.',
    commands: [
      { command: 'npx exemplar init', description: 'Initialize a new exemplar project.' },
    ],
    callouts: [
      { variant: CalloutVariant.tip, text: 'Start with Step 0 (Cartographer) to map out your project before diving into implementation.' },
    ],
    examples: ['npx exemplar init my-project'],
    youtubeUrl: undefined,
    version: undefined,
  },
  [StepId.cartographer]: {
    stepId: StepId.cartographer,
    label: STEP_ID_LABEL_MAP[StepId.cartographer],
    overview: 'Cartographer maps the territory of your project. It scans your codebase and generates a structural overview, identifying components, dependencies, and boundaries.',
    commands: [
      { command: 'npx exemplar cartographer scan', description: 'Scan the codebase and generate a structural map.' },
      { command: 'npx exemplar cartographer report', description: 'Generate a human-readable report of the project structure.' },
    ],
    callouts: [
      { variant: CalloutVariant.gotcha, text: 'Cartographer requires a valid package.json at the project root.' },
      { variant: CalloutVariant.tip, text: 'Run Cartographer after major refactors to keep the project map up to date.' },
    ],
    examples: [
      'npx exemplar cartographer scan --output=map.json',
      'npx exemplar cartographer report --format=markdown',
    ],
    youtubeUrl: 'https://youtube.com/watch?v=cartographer-intro',
    version: '0.1.0',
  },
  [StepId.constrain]: {
    stepId: StepId.constrain,
    label: STEP_ID_LABEL_MAP[StepId.constrain],
    overview: 'Constrain defines the boundaries and rules for your project. It sets up linting, formatting, and type-checking constraints that keep your codebase consistent.',
    commands: [
      { command: 'npx exemplar constrain init', description: 'Initialize constraint rules for the project.' },
      { command: 'npx exemplar constrain check', description: 'Verify all constraints are satisfied.' },
    ],
    callouts: [
      { variant: CalloutVariant.warning, text: 'Running constrain check may fail on first run if linting has never been configured.' },
      { variant: CalloutVariant.tip, text: 'Integrate constrain check into your CI pipeline for continuous enforcement.' },
    ],
    examples: [
      'npx exemplar constrain init --strict',
    ],
    youtubeUrl: '',
    version: '0.2.0',
  },
  [StepId.ledger]: {
    stepId: StepId.ledger,
    label: STEP_ID_LABEL_MAP[StepId.ledger],
    overview: 'Ledger tracks decisions and changes across the project lifecycle. It creates an immutable log of architectural decisions, dependency changes, and configuration updates.',
    commands: [
      { command: 'npx exemplar ledger record', description: 'Record a new decision or change entry.' },
      { command: 'npx exemplar ledger list', description: 'List all recorded entries.' },
    ],
    callouts: [
      { variant: CalloutVariant.gotcha, text: 'Ledger entries are append-only — once recorded, they cannot be modified.' },
    ],
    examples: [
      'npx exemplar ledger record --title="Switch to Vite" --reason="Faster builds"',
    ],
    youtubeUrl: undefined,
    version: '0.1.5',
  },
  [StepId.pact]: {
    stepId: StepId.pact,
    label: STEP_ID_LABEL_MAP[StepId.pact],
    overview: 'Pact defines the contracts between components in your system. It generates typed interfaces and validates that implementations conform to their declared contracts.',
    commands: [
      { command: 'npx exemplar pact generate', description: 'Generate contract interfaces from component definitions.' },
      { command: 'npx exemplar pact validate', description: 'Validate implementations against their contracts.' },
    ],
    callouts: [
      { variant: CalloutVariant.warning, text: 'Pact validation will fail if any required export is missing from a module.' },
      { variant: CalloutVariant.tip, text: 'Use pact generate before implementing a new component to establish the contract first.' },
    ],
    examples: [
      'npx exemplar pact generate --component=navigation',
      'npx exemplar pact validate --all',
    ],
    youtubeUrl: 'https://youtube.com/watch?v=pact-overview',
    version: '0.3.0',
  },
  [StepId.advocate]: {
    stepId: StepId.advocate,
    label: STEP_ID_LABEL_MAP[StepId.advocate],
    overview: 'Advocate reviews code changes and provides automated feedback. It analyzes pull requests for contract violations, style issues, and potential bugs.',
    commands: [
      { command: 'npx exemplar advocate review', description: 'Run automated code review on staged changes.' },
    ],
    callouts: [
      { variant: CalloutVariant.tip, text: 'Configure Advocate as a GitHub Action for automatic PR reviews.' },
    ],
    examples: [
      'npx exemplar advocate review --pr=42',
    ],
    youtubeUrl: undefined,
    version: '0.2.1',
  },
  [StepId.arbiter]: {
    stepId: StepId.arbiter,
    label: STEP_ID_LABEL_MAP[StepId.arbiter],
    overview: 'Arbiter resolves conflicts between competing constraints and contracts. When multiple rules collide, Arbiter provides a structured resolution process.',
    commands: [
      { command: 'npx exemplar arbiter resolve', description: 'Resolve detected conflicts between constraints.' },
      { command: 'npx exemplar arbiter status', description: 'Show current conflict status.' },
    ],
    callouts: [
      { variant: CalloutVariant.gotcha, text: 'Arbiter requires both Constrain and Pact to be configured before it can resolve conflicts.' },
      { variant: CalloutVariant.warning, text: 'Unresolved conflicts will block the CI pipeline.' },
    ],
    examples: [
      'npx exemplar arbiter resolve --auto',
    ],
    youtubeUrl: undefined,
    version: '0.1.0',
  },
  [StepId.baton]: {
    stepId: StepId.baton,
    label: STEP_ID_LABEL_MAP[StepId.baton],
    overview: 'Baton manages handoffs between pipeline stages. It ensures that outputs from one step are correctly passed as inputs to the next, maintaining data integrity throughout the pipeline.',
    commands: [
      { command: 'npx exemplar baton pass', description: 'Pass artifacts from the current step to the next.' },
      { command: 'npx exemplar baton status', description: 'Check the current handoff status.' },
    ],
    callouts: [
      { variant: CalloutVariant.tip, text: 'Baton automatically validates artifact schemas during handoff.' },
    ],
    examples: [
      'npx exemplar baton pass --from=constrain --to=pact',
    ],
    youtubeUrl: undefined,
    version: '0.1.2',
  },
  [StepId.sentinel]: {
    stepId: StepId.sentinel,
    label: STEP_ID_LABEL_MAP[StepId.sentinel],
    overview: 'Sentinel monitors your project for regressions and quality degradation. It runs continuous checks and alerts when metrics fall below thresholds.',
    commands: [
      { command: 'npx exemplar sentinel watch', description: 'Start continuous monitoring.' },
      { command: 'npx exemplar sentinel report', description: 'Generate a quality report.' },
    ],
    callouts: [
      { variant: CalloutVariant.warning, text: 'Sentinel watch runs as a background process — remember to stop it when done.' },
      { variant: CalloutVariant.tip, text: 'Set up Sentinel alerts to notify your team Slack channel.' },
    ],
    examples: [
      'npx exemplar sentinel watch --threshold=80',
    ],
    youtubeUrl: 'https://youtube.com/watch?v=sentinel-demo',
    version: '0.2.0',
  },
  [StepId.chronicler]: {
    stepId: StepId.chronicler,
    label: STEP_ID_LABEL_MAP[StepId.chronicler],
    overview: 'Chronicler generates documentation from your codebase. It extracts JSDoc comments, contract definitions, and architectural decisions into browsable documentation.',
    commands: [
      { command: 'npx exemplar chronicler generate', description: 'Generate documentation from the codebase.' },
      { command: 'npx exemplar chronicler serve', description: 'Serve documentation locally for preview.' },
    ],
    callouts: [
      { variant: CalloutVariant.gotcha, text: 'Chronicler only documents exported symbols — internal helpers are excluded by default.' },
    ],
    examples: [
      'npx exemplar chronicler generate --output=docs/',
    ],
    youtubeUrl: undefined,
    version: '0.1.3',
  },
  [StepId.stigmergy]: {
    stepId: StepId.stigmergy,
    label: STEP_ID_LABEL_MAP[StepId.stigmergy],
    overview: 'Stigmergy enables indirect coordination between team members through shared artifacts. It tracks who changed what, when, and why — creating a trail that guides future contributors.',
    commands: [
      { command: 'npx exemplar stigmergy trace', description: 'Trace the history of changes for a given file or component.' },
    ],
    callouts: [
      { variant: CalloutVariant.tip, text: 'Stigmergy works best when combined with Ledger for full traceability.' },
    ],
    examples: [
      'npx exemplar stigmergy trace --file=src/index.ts',
    ],
    youtubeUrl: undefined,
    version: '0.1.0',
  },
  [StepId.apprentice]: {
    stepId: StepId.apprentice,
    label: STEP_ID_LABEL_MAP[StepId.apprentice],
    overview: 'Apprentice provides guided onboarding for new team members. It walks developers through the project structure, conventions, and key decisions using interactive tutorials.',
    commands: [
      { command: 'npx exemplar apprentice start', description: 'Start the interactive onboarding tutorial.' },
      { command: 'npx exemplar apprentice progress', description: 'Check onboarding progress.' },
    ],
    callouts: [
      { variant: CalloutVariant.tip, text: 'Customize the Apprentice tutorial by editing .exemplar/apprentice.config.json.' },
      { variant: CalloutVariant.gotcha, text: 'Apprentice requires Chronicler docs to be generated first.' },
    ],
    examples: [
      'npx exemplar apprentice start --module=navigation',
    ],
    youtubeUrl: 'https://youtube.com/watch?v=apprentice-walkthrough',
    version: '0.2.0',
  },
  [StepId.kindex]: {
    stepId: StepId.kindex,
    label: STEP_ID_LABEL_MAP[StepId.kindex],
    overview: 'Kindex builds a knowledge index across your entire project. It cross-references contracts, decisions, documentation, and code to create a searchable knowledge base.',
    commands: [
      { command: 'npx exemplar kindex build', description: 'Build the knowledge index.' },
      { command: 'npx exemplar kindex search', description: 'Search the knowledge index.' },
    ],
    callouts: [
      { variant: CalloutVariant.warning, text: 'Building the full index can be slow on large projects — use incremental mode for faster updates.' },
      { variant: CalloutVariant.tip, text: 'Kindex search supports fuzzy matching and regex patterns.' },
    ],
    examples: [
      'npx exemplar kindex build --incremental',
      'npx exemplar kindex search "contract validation"',
    ],
    youtubeUrl: undefined,
    version: '0.3.1',
  },
} satisfies StepContentRecord) as StepContentRecord;

const validStepIds = new Set<string>(Object.values(StepId));

export function getStepContent(stepId: StepId): StepContent {
  console.debug(PACT_KEY, 'getStepContent', { stepId });
  if (!stepId || !validStepIds.has(stepId)) {
    throw new TypeError('Invalid StepId: must be one of the 13 defined step identifiers.');
  }
  return STEP_CONTENT[stepId];
}
