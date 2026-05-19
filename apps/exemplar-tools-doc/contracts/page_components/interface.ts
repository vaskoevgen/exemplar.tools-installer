// === Page Components (13 pages) (page_components) v1 ===
//  Dependencies: app_routing, shared_components
// One React component per page, each in its own .tsx file (<300 LOC). Content is manually transcribed from howto.md into JSX using shared components (CodeBlock, VideoEmbed, VersionBadge, CalloutBox). Pages: HomePage (pipeline diagram as SVG + overview), CartographerPage, ConstrainPage, LedgerPage, PactPage, AdvocatePage, ArbiterPage, BatonPage, SentinelPage, ChroniclerPage, StigmergyPage, ApprenticePage, KindexPage. Every CLI command, gotcha, warning, tip, and example is verbatim from howto.md. Each page component is a React.FC with no props, dual-exported (named + default). A pageComponentMap (Record<PageComponentKey, React.ComponentType>) is exported from the barrel index as the sole integration surface consumed by app_routing. Static pipeline diagram SVG is imported as a Vite static URL in HomePage and rendered as an <img> with alt text. Page components must NOT import from react-router-dom — they are pure content components.

// Module invariants:
//   - All 13 page components are React.FC with no props (zero-argument functional components)
//   - Every page component is dual-exported: named export + default export from its own .tsx file
//   - No page component imports from react-router-dom — all are pure content components
//   - Every .tsx file includes `import React from 'react'` at the top
//   - Every page file is under 300 lines of code
//   - All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md — no paraphrasing
//   - pageComponentMap keys are the exact PageComponentKey enum string values from app_routing — never inferred from component names
//   - pageComponentMap contains exactly 13 entries — one per PageComponentKey
//   - Pipeline diagram SVG is located at src/assets/pipeline-diagram.svg and imported as a Vite static URL in HomePage
//   - HomePage renders the pipeline diagram as <img src={importedSvgUrl} alt='exemplar.tools pipeline diagram' />
//   - Barrel export at src/pages/index.ts re-exports all 13 named page components plus pageComponentMap
//   - Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are imported from shared_components — never reimplemented
//   - Contract tests use vitest + @testing-library/react in jsdom environment with no external services

/** Discriminator enum identifying each of the 13 page components. */
export type PageComponentKey = "Home" | "Cartographer" | "Constrain" | "Ledger" | "Pact" | "Advocate" | "Arbiter" | "Baton" | "Sentinel" | "Chronicler" | "Stigmergy" | "Apprentice" | "Kindex";

/** React.FC — a React functional component type accepting no props and returning React.ReactElement | null. */
export type ReactFC = unknown;

/** React.ComponentType — a React component type (function or class) accepting no props. Used as the value type in pageComponentMap. */
export type ReactComponentType = unknown;

/** Record<PageComponentKey, React.ComponentType> — exhaustive lookup map from every PageComponentKey variant to its corresponding React page component. Defined in App.tsx. TypeScript compiler enforces that every enum variant has a mapping. */
export interface PageComponentMap {
  Home: ReactComponentType;  // required, HomePage component
  Step0Cartographer: ReactComponentType;  // required, Step0CartographerPage component
  Step1aConstrain: ReactComponentType;  // required, Step1aConstrainPage component
  Step1bLedger: ReactComponentType;  // required, Step1bLedgerPage component
  Step2aPact: ReactComponentType;  // required, Step2aPactPage component
  Step2bAdvocate: ReactComponentType;  // required, Step2bAdvocatePage component
  Step3Arbiter: ReactComponentType;  // required, Step3ArbiterPage component
  Step4Baton: ReactComponentType;  // required, Step4BatonPage component
  Step5aSentinel: ReactComponentType;  // required, Step5aSentinelPage component
  Step5bChronicler: ReactComponentType;  // required, Step5bChroniclerPage component
  Step5cStigmergy: ReactComponentType;  // required, Step5cStigmergyPage component
  Step6Apprentice: ReactComponentType;  // required, Step6ApprenticePage component
  Step7Kindex: ReactComponentType;  // required, Step7KindexPage component
}

/** Test-only type representing the expected h1 heading text for a given page component. Used in parameterized contract tests. */
export interface PageHeadingExpectation {
  componentName: string;  // required, The named export identifier, e.g. 'HomePage', 'CartographerPage'.
  expectedHeading: string;  // required, The exact text expected in the h1 element rendered by this component.
  pageKey: PageComponentKey;  // required, The corresponding PageComponentKey enum value for this page.
}

/** A string URL resolved by Vite's static asset import for the pipeline diagram SVG at src/assets/pipeline-diagram.svg. Imported via `import pipelineDiagramUrl from '../assets/pipeline-diagram.svg'` in HomePage.tsx. */
export type PipelineDiagramSvgUrl = unknown;

/**
 * React functional component rendering the exemplar.tools home/overview page. Displays the pipeline diagram as an <img> element (src = Vite-imported SVG URL, alt = 'exemplar.tools pipeline diagram') and an overview of the CLI suite. Uses shared components for CLI examples and callouts. Exported as both named and default from HomePage.tsx.
 *
 * @precondition Pipeline diagram SVG exists at src/assets/pipeline-diagram.svg
 * @precondition Shared components (CodeBlock, CalloutBox, etc.) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'exemplar.tools'
 * @postcondition Renders an img element with alt='exemplar.tools pipeline diagram' and src set to the imported SVG URL
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function HomePage(): ReactFC;

/**
 * React functional component rendering the Cartographer tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from CartographerPage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Cartographer'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function CartographerPage(): ReactFC;

/**
 * React functional component rendering the Constrain tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from ConstrainPage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Constrain'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function ConstrainPage(): ReactFC;

/**
 * React functional component rendering the Ledger tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from LedgerPage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Ledger'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function LedgerPage(): ReactFC;

/**
 * React functional component rendering the Pact tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from PactPage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Pact'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function PactPage(): ReactFC;

/**
 * React functional component rendering the Advocate tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from AdvocatePage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Advocate'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function AdvocatePage(): ReactFC;

/**
 * React functional component rendering the Arbiter tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from ArbiterPage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Arbiter'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function ArbiterPage(): ReactFC;

/**
 * React functional component rendering the Baton tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from BatonPage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Baton'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function BatonPage(): ReactFC;

/**
 * React functional component rendering the Sentinel tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from SentinelPage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Sentinel'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function SentinelPage(): ReactFC;

/**
 * React functional component rendering the Chronicler tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from ChroniclerPage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Chronicler'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function ChroniclerPage(): ReactFC;

/**
 * React functional component rendering the Stigmergy tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from StigmergyPage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Stigmergy'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function StigmergyPage(): ReactFC;

/**
 * React functional component rendering the Apprentice tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from ApprenticePage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Apprentice'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function ApprenticePage(): ReactFC;

/**
 * React functional component rendering the Kindex tool documentation page. All CLI commands, gotchas, warnings, tips, and examples are verbatim from howto.md. Exported as both named and default from KindexPage.tsx.
 *
 * @precondition Shared components (CodeBlock, CalloutBox, VideoEmbed, VersionBadge) are importable from shared_components
 * @postcondition Renders an h1 element containing the text 'Kindex'
 * @postcondition Does not import from react-router-dom
 * @postcondition File is under 300 lines
 * @sideEffects none
 * @idempotent yes
 */
export function KindexPage(): ReactFC;

/**
 * Returns the pageComponentMap: a Record<PageComponentKey, React.ComponentType> containing all 13 page components keyed by their exact PageComponentKey enum values. Exported as a constant from src/pages/index.ts. This is the sole integration surface consumed by app_routing to wire page components into routes. Keys MUST be the exact string values from the PageComponentKey enum defined in app_routing — never inferred from component names.
 *
 * @precondition All 13 page component modules are importable
 * @precondition PageComponentKey enum is importable from app_routing
 * @postcondition Returned map contains exactly 13 entries
 * @postcondition Every PageComponentKey enum value is present as a key
 * @postcondition Every value is a valid React.ComponentType
 * @postcondition Keys are the exact strings: 'home', 'cartographer', 'constrain', 'ledger', 'pact', 'advocate', 'arbiter', 'baton', 'sentinel', 'chronicler', 'stigmergy', 'apprentice', 'kindex'
 * @sideEffects none
 * @idempotent yes
 */
export function getPageComponentMap(): PageComponentMap;

// -- REQUIRED EXPORTS -----------------------------------------------
// Your implementation module MUST export ALL of these names
// with EXACTLY these spellings. Tests import them by name.
// exports: ['PageComponentKey', 'PageComponentMap', 'PageHeadingExpectation', 'HomePage', 'CartographerPage', 'ConstrainPage', 'LedgerPage', 'PactPage', 'AdvocatePage', 'ArbiterPage', 'BatonPage', 'SentinelPage', 'ChroniclerPage', 'StigmergyPage', 'ApprenticePage', 'KindexPage', 'getPageComponentMap']
