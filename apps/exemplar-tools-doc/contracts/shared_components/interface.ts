// === Shared UI Components (shared_components) v1 ===
//  Dependencies: app_routing
// Reusable React components used across all documentation pages: Sidebar (persistent navigation with NavLink active highlighting for all 13 routes), CodeBlock (prism-react-renderer syntax highlighting with copy-to-clipboard button), VersionBadge (Tailwind pill badge for version strings), VideoEmbed (responsive 16:9 YouTube iframe), PageLayout (Sidebar + content area shell responsive to 768px), and CalloutBox (color-coded gotcha/warning/tip callouts). All components exported as named + default. Each has a vitest smoke test. Types re-export RouteEntry/RouteManifest from app_routing for consumer convenience.

// Module invariants:
//   - All six components (CalloutBox, CodeBlock, VersionBadge, VideoEmbed, Sidebar, PageLayout) are exported as both named and default exports from their respective .tsx files
//   - Every .tsx file begins with 'import React from "react"'
//   - index.ts barrel re-exports all types from types.ts and all named component exports from their respective files
//   - RouteEntry and RouteManifest are NEVER redefined in this component — always imported from app_routing and re-exported
//   - CalloutType variants are exactly 'gotcha', 'warning', 'tip' in lowercase — no other values accepted
//   - CodeBlock language prop defaults to 'bash' when omitted
//   - VideoEmbed container uses Tailwind 'aspect-video' class for 16:9 responsive ratio
//   - Sidebar renders exactly one NavLink per RouteEntry in the provided routes array
//   - PageLayout responsive breakpoint is md: (768px) — flex-col below, flex-row at and above
//   - No file in this component exceeds 300 lines
//   - Composition over inheritance: no class-based components, no component inheritance chains
//   - All component tests are runnable in vitest jsdom environment with no external services
//   - Sidebar and PageLayout tests must wrap rendered components in MemoryRouter
//   - CodeBlock copy button test must mock navigator.clipboard.writeText

/** Visual variant for a CalloutBox — determines border color, icon, and background tint. */
export type CalloutType = "gotcha" | "warning" | "tip";

/** React.ReactNode — opaque type representing renderable JSX children. */
export type ReactNode = unknown;

/** A single route definition consumed by both the router configuration and the Sidebar navigation. */
export interface RouteEntry {
  path: string;  // required, URL path segment, e.g. '/step-0-cartographer' or '/' for home.
  label: string;  // required, Human-readable navigation label shown in the Sidebar, e.g. 'Step 0 — Cartographer'.
  componentKey: PageComponentKey;  // required, Lookup key that maps this route to its lazy-loaded or statically-imported page component.
}

/** Ordered array of all 13 route entries; single source of truth for navigation and routing. */
export type RouteManifest = RouteEntry[];

/** Props accepted by the CalloutBox component; used by every page component to render callouts. */
export interface CalloutBoxProps {
  type: CalloutType;  // required, Visual style variant (gotcha, warning, or tip).
  title?: string;  // optional, Optional bold heading rendered above the body text.
  children: ReactNode;  // required, Body content of the callout (JSX).
}

/** Language identifier string accepted by prism-react-renderer. Defaults to 'bash' when not specified. */
export type CodeBlockLanguage = unknown;

/** Props accepted by the CodeBlock component; used by every page to render CLI commands with syntax highlighting and copy button. */
export interface CodeBlockProps {
  code: string;  // required, The verbatim CLI command or code snippet to display.
  language?: string;  // optional, default: bash, Prism language identifier for syntax highlighting.
  title?: string;  // optional, Optional filename or label shown above the code block.
}

/** A semver-like version string displayed in a badge. Must be non-empty. */
export type VersionString = unknown;

/** Props accepted by the VersionBadge component; used by page components to show component version pills. */
export interface VersionBadgeProps {
  version: string;  // required, Semantic version string to display, e.g. '1.2.3'.
  label?: string;  // optional, Optional tool name rendered before the version number.
}

/** A validated YouTube embed URL. Must match YouTube embed or watch URL patterns. */
export type YouTubeUrl = unknown;

/** Props accepted by the VideoEmbed component; used by page components to embed YouTube walkthroughs. */
export interface VideoEmbedProps {
  url: string;  // required, Full YouTube video URL (https://www.youtube.com/watch?v=... or https://youtu.be/...).
  title?: string;  // optional, Accessible title for the iframe element.
}

/** Props accepted by the Sidebar component; receives the route manifest to render navigation links. */
export interface SidebarProps {
  routes: RouteManifest;  // required, The full ordered list of routes to render as nav links.
}

/** Props accepted by the PageLayout shell component; wraps Sidebar + scrollable content area. */
export interface PageLayoutProps {
  routes: RouteManifest;  // required, Route manifest forwarded to the Sidebar for navigation rendering.
  children: ReactNode;  // required, Page content rendered in the main content area.
}

/** Discriminator enum identifying each of the 13 page components. */
export type PageComponentKey = "Home" | "Cartographer" | "Constrain" | "Ledger" | "Pact" | "Advocate" | "Arbiter" | "Baton" | "Sentinel" | "Chronicler" | "Stigmergy" | "Apprentice" | "Kindex";

/** Auto-stubbed type — referenced but not defined in contract 'shared_components' */
export interface string {
}

/**
 * React component that renders a callout box with color-coded border and icon based on CalloutType. 'gotcha' renders red/error styling, 'warning' renders amber/caution styling, 'tip' renders green/info styling. Exported as named + default from CalloutBox.tsx.
 *
 * @precondition props.type is one of 'gotcha' | 'warning' | 'tip' (exact lowercase)
 * @precondition props.children is a valid ReactNode
 * @postcondition Returned element contains a container div with border color matching props.type
 * @postcondition If props.title is provided and non-empty, a heading element is rendered with that text
 * @postcondition props.children is rendered inside the callout body area
 * @postcondition An icon element is rendered matching the callout type
 * @throws invalid_callout_type (TypeScript compile error or runtime mismatch) - props.type is not one of the three valid CalloutType variants
 * @sideEffects none
 * @idempotent yes
 */
export function CalloutBox(
  props: CalloutBoxProps,
): ReactNode;

/**
 * React component that wraps prism-react-renderer to display code/CLI commands with syntax highlighting. Includes a copy-to-clipboard button that invokes navigator.clipboard.writeText(props.code). Language defaults to 'bash'. Exported as named + default from CodeBlock.tsx.
 *
 * @precondition props.code is a non-empty string
 * @precondition navigator.clipboard API is available in the browser environment (graceful degradation if not)
 * @postcondition Code text is rendered with prism-react-renderer syntax highlighting
 * @postcondition A button element with accessible label (e.g. 'Copy' or copy icon) is present in the DOM
 * @postcondition Clicking the copy button calls navigator.clipboard.writeText with the exact props.code value
 * @postcondition If props.language is omitted, 'bash' is used as the Prism language
 * @postcondition If props.title is provided, it is rendered above the code block
 * @throws empty_code_string (ValidationError) - props.code is empty string
 * @throws clipboard_unavailable (ClipboardUnavailableError) - navigator.clipboard is undefined (e.g. insecure context)
 * @sideEffects none
 * @idempotent yes
 */
export function CodeBlock(
  props: CodeBlockProps,
): ReactNode;

/**
 * React component that displays a version string inside a styled Tailwind pill badge (rounded-full, px/py padding, bg/text color). Exported as named + default from VersionBadge.tsx.
 *
 * @precondition props.version is a non-empty string
 * @postcondition A span or inline element is rendered with Tailwind pill classes (rounded-full, inline-flex or similar)
 * @postcondition The text content of the badge is exactly props.version
 * @postcondition If props.className is provided, those classes are merged onto the badge element
 * @throws empty_version (ValidationError) - props.version is an empty string
 * @sideEffects none
 * @idempotent yes
 */
export function VersionBadge(
  props: VersionBadgeProps,
): ReactNode;

/**
 * React component that renders a responsive YouTube iframe with aspect-video (16:9) styling. The iframe src is set from the provided URL. Exported as named + default from VideoEmbed.tsx.
 *
 * @precondition props.url matches a valid YouTube embed or watch URL pattern
 * @postcondition An iframe element is rendered with src derived from props.url
 * @postcondition The iframe container has Tailwind aspect-video class for responsive 16:9 ratio
 * @postcondition The iframe title attribute is set to props.title (default 'Video')
 * @postcondition The iframe includes allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' and allowFullScreen
 * @throws invalid_youtube_url (ValidationError) - props.url does not match the YouTube URL regex pattern
 * @sideEffects none
 * @idempotent yes
 */
export function VideoEmbed(
  props: VideoEmbedProps,
): ReactNode;

/**
 * React component that renders a persistent navigation sidebar. Iterates over the RouteManifest and creates a react-router-dom NavLink for each RouteEntry, with active route highlighting via NavLink's className callback. Wrapped in a semantic <nav> element. Exported as named + default from Sidebar.tsx.
 *
 * @precondition props.routes is a non-empty array of RouteEntry objects
 * @precondition Component is rendered within a react-router-dom Router context (BrowserRouter, MemoryRouter, etc.)
 * @postcondition A <nav> element is rendered as the root container
 * @postcondition Exactly props.routes.length NavLink elements are rendered
 * @postcondition Each NavLink 'to' attribute matches the corresponding RouteEntry.path
 * @postcondition Each NavLink text content matches the corresponding RouteEntry.label
 * @postcondition The NavLink for the currently active route receives active styling (distinct className or aria-current)
 * @postcondition If props.className is provided, it is applied to the <nav> element
 * @throws no_router_context (React runtime error from react-router-dom: useLocation/useMatch called outside Router) - Sidebar is rendered outside of a Router provider
 * @sideEffects none
 * @idempotent yes
 */
export function Sidebar(
  props: SidebarProps,
): ReactNode;

/**
 * Shell component that composes Sidebar and a content area in a flex layout. At md: (768px+) breakpoint, sidebar is visible as a fixed-width column; below 768px, layout adapts (sidebar collapses or stacks). Exported as named + default from PageLayout.tsx.
 *
 * @precondition props.routes is a non-empty array of RouteEntry objects
 * @precondition props.children is a valid ReactNode
 * @precondition Component is rendered within a react-router-dom Router context
 * @postcondition A flex container div is rendered as the root element
 * @postcondition Sidebar component is rendered as a child, receiving props.routes
 * @postcondition props.children is rendered in a main content area element (<main> or content div)
 * @postcondition Layout uses Tailwind responsive classes: flex-col below md:, flex-row at md: and above
 * @postcondition Content area occupies remaining horizontal space (flex-1 or equivalent)
 * @throws no_router_context (React runtime error from react-router-dom) - PageLayout is rendered outside of a Router provider (propagated from Sidebar)
 * @sideEffects none
 * @idempotent yes
 */
export function PageLayout(
  props: PageLayoutProps,
): ReactNode;

// -- REQUIRED EXPORTS -----------------------------------------------
// Your implementation module MUST export ALL of these names
// with EXACTLY these spellings. Tests import them by name.
// exports: ['CalloutType', 'RouteEntry', 'RouteManifest', 'CalloutBoxProps', 'CodeBlockProps', 'VersionBadgeProps', 'VideoEmbedProps', 'SidebarProps', 'PageLayoutProps', 'PageComponentKey', 'CalloutBox', 'CodeBlock', 'ValidationError', 'ClipboardUnavailableError', 'VersionBadge', 'VideoEmbed', 'Sidebar', 'PageLayout']
