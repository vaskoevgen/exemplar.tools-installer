const PACT_KEY = "PACT:fd4843:page_content";

export enum StepId {
  home = 'home',
  cartographer = 'cartographer',
  constrain = 'constrain',
  ledger = 'ledger',
  pact = 'pact',
  advocate = 'advocate',
  arbiter = 'arbiter',
  baton = 'baton',
  sentinel = 'sentinel',
  chronicler = 'chronicler',
  stigmergy = 'stigmergy',
  apprentice = 'apprentice',
  kindex = 'kindex',
}

export enum StepLabel {
  Home = 'Home',
  'Step 0 — Cartographer' = 'Step 0 — Cartographer',
  'Step 1a — Constrain' = 'Step 1a — Constrain',
  'Step 1b — Ledger' = 'Step 1b — Ledger',
  'Step 2a — Pact' = 'Step 2a — Pact',
  'Step 2b — Advocate' = 'Step 2b — Advocate',
  'Step 3 — Arbiter' = 'Step 3 — Arbiter',
  'Step 4 — Baton' = 'Step 4 — Baton',
  'Step 5a — Sentinel' = 'Step 5a — Sentinel',
  'Step 5b — Chronicler' = 'Step 5b — Chronicler',
  'Step 5c — Stigmergy' = 'Step 5c — Stigmergy',
  'Step 6 — Apprentice' = 'Step 6 — Apprentice',
  'Step 7 — Kindex' = 'Step 7 — Kindex',
}

export enum CalloutVariant {
  gotcha = 'gotcha',
  warning = 'warning',
  tip = 'tip',
}

export interface CommandEntry {
  command: string;
  description: string;
}

export interface CalloutItem {
  variant: CalloutVariant;
  text: string;
}

export interface StepContent {
  stepId: StepId;
  label: StepLabel;
  overview: string;
  commands: CommandEntry[];
  callouts: CalloutItem[];
  examples: string[];
  youtubeUrl?: string;
  version?: string;
}

export type StepContentRecord = Record<StepId, StepContent>;

export interface StepPageProps {
  content: StepContent;
}

export interface HomePageProps {}

export type CalloutItemList = CalloutItem[];
export type CommandEntryList = CommandEntry[];
export type OptionalString = string | undefined;
export type StringList = string[];
