// === Step Page Content & Data (page_content) v1 ===
//  Dependencies: shared_ui, pipeline_diagram
// All 14 page components with hardcoded content from howto.md. Includes: (1) A STEP_CONTENT data structure holding per-step commands, gotchas, warnings, tips, examples, YouTube URLs, and version strings — all verbatim from howto.md. (2) HomePage component rendering overview text + PipelineDiagram. (3) StepPage generic component that receives step data and renders sections using CodeBlock, CalloutBox, YouTubeEmbed, and VersionBadge. (4) Individual page wrapper components for each of the 12 tool steps (CartographerPage, ConstrainPage, LedgerPage, PactPage, AdvocatePage, ArbiterPage, BatonPage, SentinelPage, ChroniclerPage, StigmergyPage, ApprenticePage, KindexPage). Content placeholder structure is built now; exact howto.md text is filled when the file is provided. Tests verify each page renders its key sections, code blocks, and embeds.

// Module invariants:
//   - STEP_CONTENT must be a complete Record<StepId, StepContent> — every StepId enum value must have a corresponding entry. Enforced at compile time via TypeScript 'satisfies Record<StepId, StepContent>'.
//   - STEP_CONTENT is a frozen constant: no runtime mutation is permitted after module initialization.
//   - Every StepContent entry's stepId field must match its key in the STEP_CONTENT record (e.g., STEP_CONTENT.cartographer.stepId === StepId.Cartographer).
//   - Every StepContent entry's label field must correspond to the correct StepLabel for that StepId.
//   - StepPage renders exactly one CodeBlock per commands entry and one CodeBlock per examples entry — no collapsing or merging.
//   - StepPage renders exactly one CalloutBox per callouts entry with the correct variant passed through.
//   - YouTubeEmbed is conditionally rendered only when youtubeUrl is a non-empty string.
//   - VersionBadge is conditionally rendered only when version is a non-empty string.
//   - All wrapper page components (CartographerPage, etc.) are zero-prop and delegate entirely to StepPage with the correct STEP_CONTENT entry.
//   - HomePage always renders exactly one PipelineDiagram component.
//   - All exports use named export syntax only — no default exports.
//   - Types are exported via 'export type { }' syntax per project standards.
//   - The barrel index.ts re-exports all public enums, types, the STEP_CONTENT constant, getStepContent function, and all 14 page components.

/** Unique identifier for each step in the exemplar.tools pipeline, used as keys in content data and pipeline diagram nodes. */
export type StepId = "home" | "cartographer" | "constrain" | "ledger" | "pact" | "advocate" | "arbiter" | "baton" | "sentinel" | "chronicler" | "stigmergy" | "apprentice" | "kindex";

/** Human-readable display labels for each pipeline step, shown in sidebar navigation, diagram boxes, and page titles. */
export type StepLabel = "Home" | "Step 0 — Cartographer" | "Step 1a — Constrain" | "Step 1b — Ledger" | "Step 2a — Pact" | "Step 2b — Advocate" | "Step 3 — Arbiter" | "Step 4 — Baton" | "Step 5a — Sentinel" | "Step 5b — Chronicler" | "Step 5c — Stigmergy" | "Step 6 — Apprentice" | "Step 7 — Kindex";

/** Visual variant for CalloutBox components indicating the type of supplementary information. */
export type CalloutVariant = "gotcha" | "warning" | "tip";

/** A single CLI command block with optional description, rendered via the shared CodeBlock component. */
export interface CommandEntry {
  command: string;  // required, The exact CLI command string, verbatim from howto.md.
  description?: string;  // optional, Optional prose describing what this command does.
}

/** A single callout (gotcha, warning, or tip) to be rendered via the shared CalloutBox component. */
export interface CalloutItem {
  variant: CalloutVariant;  // required, The visual/semantic type of this callout.
  text: string;  // required, The verbatim callout text from howto.md.
}

/** Complete content payload for one step page, consumed by StepPage to render all sections using shared UI components. */
export interface StepContent {
  stepId: StepId;  // required, Unique identifier for this step.
  label: StepLabel;  // required, Display label shown as the page title.
  overview: string;  // required, Introductory prose for the step, verbatim from howto.md.
  commands: CommandEntryList;  // required, All CLI commands for this step, in order.
  callouts: CalloutItemList;  // required, Gotchas, warnings, and tips for this step.
  examples: StringList;  // required, Verbatim example blocks from howto.md.
  youtubeUrl?: OptionalString;  // optional, YouTube video URL for this step, if one exists in howto.md.
  version?: OptionalString;  // optional, Version string displayed via VersionBadge, if applicable.
}

/** TypeScript type: Record<StepId, StepContent>. Enforced via 'satisfies' at compile time to guarantee completeness — every StepId key must be present. */
export interface StepContentRecord {
  home: StepContent;  // required, Content for the home/overview page.
  cartographer: StepContent;  // required, Content for Step 0 — Cartographer.
  constrain: StepContent;  // required, Content for Step 1 — Constrain.
  ledger: StepContent;  // required, Content for Step 2 — Ledger.
  pact: StepContent;  // required, Content for Step 3 — Pact.
  advocate: StepContent;  // required, Content for Step 4 — Advocate.
  arbiter: StepContent;  // required, Content for Step 5 — Arbiter.
  baton: StepContent;  // required, Content for Step 6 — Baton.
  sentinel: StepContent;  // required, Content for Step 7 — Sentinel.
  chronicler: StepContent;  // required, Content for Step 8 — Chronicler.
  stigmergy: StepContent;  // required, Content for Step 9 — Stigmergy.
  apprentice: StepContent;  // required, Content for Step 10 — Apprentice.
  kindex: StepContent;  // required, Content for Step 11 — Kindex.
}

/** Props for the generic StepPage component. */
export interface StepPageProps {
  content: StepContent;  // required, The full step content payload to render.
}

/** Props for the HomePage component. Empty — reads STEP_CONTENT internally. */
export interface HomePageProps {
}

/** React JSX element returned by component render functions (React.ReactElement / JSX.Element). */
export type ReactElement = unknown;

/** Ordered list of CalloutItem entries for a single step page. */
export type CalloutItemList = CalloutItem[];

/** Ordered list of CommandEntry items for a single step page. */
export type CommandEntryList = CommandEntry[];

/** TypeScript string primitive. */
export type string = unknown;

/** A string value that may be undefined or empty. */
export type OptionalString = string | undefined;

/** An ordered array of strings, used for example blocks and similar text lists. */
export type StringList = string[];

/**
 * Generic step page renderer component. Receives StepContent via props and renders: heading (label), overview paragraph, commands as CodeBlock components, callouts as CalloutBox components, examples as CodeBlock components, optional YouTubeEmbed if youtubeUrl is present, and optional VersionBadge if version is present. Sections with empty arrays are not rendered.
 *
 * @precondition content.overview is a non-empty string
 * @precondition content.stepId is a valid StepId enum value
 * @precondition content.label is a valid StepLabel enum value
 * @postcondition Rendered output contains an h1 element with content.label text
 * @postcondition Rendered output contains overview text in a paragraph element
 * @postcondition One CodeBlock component is rendered per item in content.commands
 * @postcondition One CalloutBox component is rendered per item in content.callouts
 * @postcondition One CodeBlock component is rendered per item in content.examples
 * @postcondition YouTubeEmbed is rendered if and only if content.youtubeUrl is a non-empty string
 * @postcondition VersionBadge is rendered if and only if content.version is a non-empty string
 * @postcondition No section heading is rendered for empty commands/callouts/examples arrays
 * @throws missing_content (TypeError) - content prop is undefined or null
 *   message: StepPage requires a valid StepContent prop.
 * @sideEffects none
 * @idempotent yes
 */
export function StepPage(
  content: StepContent,
): ReactElement;

/**
 * Home/overview page component. Takes no props. Reads STEP_CONTENT[StepId.Home] internally and renders the overview text plus the PipelineDiagram component from pipeline_diagram.
 *
 * @precondition STEP_CONTENT[StepId.Home] exists and has a non-empty overview
 * @postcondition Rendered output contains the home overview text
 * @postcondition Rendered output includes exactly one PipelineDiagram component
 * @postcondition Rendered output contains an h1 element with the home label
 * @throws missing_home_content (ReferenceError) - STEP_CONTENT[StepId.Home] is undefined at module load time
 *   message: Home step content is missing from STEP_CONTENT.
 * @sideEffects none
 * @idempotent yes
 */
export function HomePage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 0 — Cartographer. Reads STEP_CONTENT[StepId.Cartographer] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Cartographer] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Cartographer]
 * @sideEffects none
 * @idempotent yes
 */
export function CartographerPage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 1 — Constrain. Reads STEP_CONTENT[StepId.Constrain] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Constrain] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Constrain]
 * @sideEffects none
 * @idempotent yes
 */
export function ConstrainPage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 2 — Ledger. Reads STEP_CONTENT[StepId.Ledger] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Ledger] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Ledger]
 * @sideEffects none
 * @idempotent yes
 */
export function LedgerPage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 3 — Pact. Reads STEP_CONTENT[StepId.Pact] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Pact] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Pact]
 * @sideEffects none
 * @idempotent yes
 */
export function PactPage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 4 — Advocate. Reads STEP_CONTENT[StepId.Advocate] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Advocate] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Advocate]
 * @sideEffects none
 * @idempotent yes
 */
export function AdvocatePage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 5 — Arbiter. Reads STEP_CONTENT[StepId.Arbiter] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Arbiter] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Arbiter]
 * @sideEffects none
 * @idempotent yes
 */
export function ArbiterPage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 6 — Baton. Reads STEP_CONTENT[StepId.Baton] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Baton] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Baton]
 * @sideEffects none
 * @idempotent yes
 */
export function BatonPage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 7 — Sentinel. Reads STEP_CONTENT[StepId.Sentinel] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Sentinel] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Sentinel]
 * @sideEffects none
 * @idempotent yes
 */
export function SentinelPage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 8 — Chronicler. Reads STEP_CONTENT[StepId.Chronicler] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Chronicler] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Chronicler]
 * @sideEffects none
 * @idempotent yes
 */
export function ChroniclerPage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 9 — Stigmergy. Reads STEP_CONTENT[StepId.Stigmergy] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Stigmergy] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Stigmergy]
 * @sideEffects none
 * @idempotent yes
 */
export function StigmergyPage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 10 — Apprentice. Reads STEP_CONTENT[StepId.Apprentice] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Apprentice] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Apprentice]
 * @sideEffects none
 * @idempotent yes
 */
export function ApprenticePage(): ReactElement;

/**
 * Zero-prop wrapper component for Step 11 — Kindex. Reads STEP_CONTENT[StepId.Kindex] and passes it to StepPage.
 *
 * @precondition STEP_CONTENT[StepId.Kindex] exists and is a valid StepContent
 * @postcondition Renders a StepPage with content equal to STEP_CONTENT[StepId.Kindex]
 * @sideEffects none
 * @idempotent yes
 */
export function KindexPage(): ReactElement;

/**
 * Accessor function that retrieves StepContent for a given StepId from the STEP_CONTENT record. Provides a type-safe way to look up content without direct record access.
 *
 * @precondition stepId is a valid StepId enum value
 * @postcondition Returned StepContent.stepId equals the input stepId
 * @postcondition Returned StepContent has a non-empty overview string
 * @throws invalid_step_id (TypeError) - stepId is not a valid member of the StepId enum
 *   message: Invalid StepId: must be one of the 13 defined step identifiers.
 * @sideEffects none
 * @idempotent yes
 */
export function getStepContent(
  stepId: StepId,
): StepContent;

// -- REQUIRED EXPORTS -----------------------------------------------
// Your implementation module MUST export ALL of these names
// with EXACTLY these spellings. Tests import them by name.
// exports: ['StepId', 'StepLabel', 'CalloutVariant', 'CommandEntry', 'CalloutItem', 'StepContent', 'StepContentRecord', 'StepPageProps', 'HomePageProps', 'CalloutItemList', 'CommandEntryList', 'OptionalString', 'StringList', 'StepPage', 'HomePage', 'CartographerPage', 'ConstrainPage', 'LedgerPage', 'PactPage', 'AdvocatePage', 'ArbiterPage', 'BatonPage', 'SentinelPage', 'ChroniclerPage', 'StigmergyPage', 'ApprenticePage', 'KindexPage', 'getStepContent']
