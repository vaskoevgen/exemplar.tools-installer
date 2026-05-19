// === Shared UI Components (shared_ui) v1 ===
// Reusable presentational React components used across all pages of the exemplar.tools documentation website. Barrel-exported collection of four components: CodeBlock (preformatted CLI commands with copy-to-clipboard), VersionBadge (inline component name + version badge), YouTubeEmbed (responsive YouTube iframe wrapper), and CalloutBox (variant-styled container for gotchas, warnings, and tips). All components use strict TypeScript annotations, named exports only (no defaults), and are tested with vitest + @testing-library/react. Mock surface: consumers mocking this module must provide exactly four runtime exports: { CodeBlock, VersionBadge, YouTubeEmbed, CalloutBox }.

// Module invariants:
//   - All four components (CodeBlock, VersionBadge, YouTubeEmbed, CalloutBox) are named exports from the barrel index.ts — no default exports anywhere
//   - All five type exports (CalloutVariant, CodeBlockProps, VersionBadgeProps, YouTubeEmbedProps, CalloutBoxProps) are exported via 'export type { }' syntax from the barrel
//   - The barrel file (index.ts) re-exports all runtime and type exports from individual component files and types.ts
//   - File structure: src/components/shared/{CodeBlock.tsx, VersionBadge.tsx, YouTubeEmbed.tsx, CalloutBox.tsx, types.ts, index.ts}
//   - Each component file has a corresponding .test.tsx file using vitest + @testing-library/react
//   - Consumers mocking this module via vi.mock() must provide exactly { CodeBlock, VersionBadge, YouTubeEmbed, CalloutBox } — all four runtime exports
//   - CalloutBox internally uses a Record<CalloutVariant, string> mapping to assign distinct Tailwind class strings per variant
//   - YouTubeEmbed wrapper div always has the Tailwind 'aspect-video' class for responsive sizing
//   - CodeBlock copy button calls navigator.clipboard.writeText(props.code) and handles both unavailable clipboard API and rejected promise gracefully
//   - All components are pure presentational — no internal state management beyond transient UI state (e.g. copy button feedback)
//   - All public function signatures have explicit TypeScript type annotations per project standards

/** Visual variant for CalloutBox components indicating the type of supplementary information. */
export type CalloutVariant = "gotcha" | "warning" | "tip";

/** Props for the CodeBlock shared component, used by page_content when rendering CLI commands. */
export interface CodeBlockProps {
  code: string;  // required, The preformatted CLI command text to display.
  description?: OptionalString;  // optional, Optional caption/description shown above or below the code.
}

/** Props for the VersionBadge shared component, used by page_content to display version info. */
export interface VersionBadgeProps {
  componentName: string;  // required, The name of the tool/component to display on the badge.
  version: string;  // required, The version string to display (e.g. 'v1.2.3').
}

/** Props for the YouTubeEmbed shared component, used by page_content to embed tutorial videos. */
export interface YouTubeEmbedProps {
  url: string;  // required, Full YouTube video URL to embed in a responsive iframe.
  title?: OptionalString;  // optional, Accessible title for the iframe element.
}

/** A validated YouTube video URL. Must be a youtube.com/watch or youtu.be short URL. */
export type YouTubeUrl = unknown;

/** Props for the CalloutBox shared component, used by page_content to render gotchas, warnings, and tips. */
export interface CalloutBoxProps {
  variant: CalloutVariant;  // required, Visual style variant: gotcha, warning, or tip.
  text: string;  // required, The callout body text to display.
}

/** Internal type representing the Record<CalloutVariant, string> mapping each variant to its Tailwind CSS class string. Not exported — used only within CalloutBox implementation. */
export interface CalloutVariantClassMap {
  gotcha: string;  // required, Tailwind classes for the 'gotcha' variant (e.g. red/orange border and background)
  warning: string;  // required, Tailwind classes for the 'warning' variant (e.g. yellow/amber border and background)
  tip: string;  // required, Tailwind classes for the 'tip' variant (e.g. green/teal border and background)
}

/** React.ReactElement — the return type of a React functional component. Represents a rendered JSX tree. */
export type ReactElement = unknown;

/** Result of a navigator.clipboard.writeText call, used internally by CodeBlock's copy button handler. */
export interface ClipboardWriteResult {
  success: boolean;  // required, Whether the clipboard write succeeded
  error?: string;  // optional, Error message if the clipboard write failed
}

/** TypeScript string primitive. */
export type string = unknown;

/** A string value that may be undefined or empty. */
export type OptionalString = string | undefined;

/**
 * React functional component that renders a preformatted CLI command or code snippet inside <pre><code> with syntax styling via Tailwind CSS and a copy-to-clipboard button. The copy button invokes navigator.clipboard.writeText(code) on click. File: src/components/shared/CodeBlock.tsx. Named export only.
 *
 * @precondition props.code is a non-empty string
 * @precondition Component is rendered within a React 18 tree
 * @postcondition Returns a <pre> element containing a <code> element with the code text
 * @postcondition A copy button element is present as a sibling or child of the <pre>
 * @postcondition If props.description is provided and non-empty, a descriptive label element is rendered above or within the block
 * @postcondition If props.description is omitted or empty, no description element is rendered
 * @postcondition Clicking the copy button calls navigator.clipboard.writeText with props.code
 * @throws clipboard_unavailable (ClipboardApiUnavailableError) - navigator.clipboard is undefined (e.g. non-HTTPS context or older browser)
 *   behavior: Copy button should degrade gracefully — either hide the button or show a fallback tooltip. Must not throw an unhandled exception.
 * @throws clipboard_write_rejected (ClipboardWriteError) - navigator.clipboard.writeText rejects (e.g. permission denied)
 *   behavior: The promise rejection must be caught. Component may show a brief error state on the button but must not propagate the error to the React error boundary.
 * @sideEffects none
 * @idempotent yes
 */
export function CodeBlock(
  props: CodeBlockProps,
): ReactElement;

/**
 * React functional component that renders a styled inline badge displaying a component name and version string. Uses Tailwind CSS for pill/badge styling. File: src/components/shared/VersionBadge.tsx. Named export only.
 *
 * @precondition props.componentName is a non-empty string
 * @precondition props.version matches semver-like pattern
 * @precondition Component is rendered within a React 18 tree
 * @postcondition Returns an inline element (e.g. <span>) with badge styling
 * @postcondition The rendered text contains both props.componentName and props.version
 * @postcondition The element uses Tailwind classes for pill/badge appearance (rounded, background color, padding)
 * @sideEffects none
 * @idempotent yes
 */
export function VersionBadge(
  props: VersionBadgeProps,
): ReactElement;

/**
 * React functional component that renders a responsive iframe wrapper for YouTube videos. Converts standard YouTube watch URLs (youtube.com/watch?v=ID) and short URLs (youtu.be/ID) to embed format (youtube.com/embed/ID). Uses Tailwind 'aspect-video' class on a wrapper div for responsive sizing. File: src/components/shared/YouTubeEmbed.tsx. Named export only.
 *
 * @precondition props.url is a valid YouTube watch URL or youtu.be short URL
 * @precondition Component is rendered within a React 18 tree
 * @postcondition Returns a wrapper <div> with Tailwind 'aspect-video' class for responsive sizing
 * @postcondition Contains an <iframe> element whose src is 'https://www.youtube.com/embed/{videoId}' derived from props.url
 * @postcondition The iframe has title attribute set to props.title (or 'YouTube video' if omitted)
 * @postcondition The iframe has allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' and allowFullScreen
 * @postcondition The iframe has frameBorder='0' and width='100%' height='100%'
 * @throws invalid_youtube_url (InvalidYouTubeUrlError) - props.url does not match expected YouTube URL patterns and video ID cannot be extracted
 *   behavior: Component renders a fallback element (e.g. a styled <div> with error text) instead of a broken iframe. Must not throw during render.
 * @sideEffects none
 * @idempotent yes
 */
export function YouTubeEmbed(
  props: YouTubeEmbedProps,
): ReactElement;

/**
 * React functional component that renders a styled container for gotchas, warnings, and tips. Uses a variant prop (gotcha | warning | tip) to select from a Record<CalloutVariant, string> mapping of Tailwind CSS class strings, producing distinct visual styling per variant. File: src/components/shared/CalloutBox.tsx. Named export only.
 *
 * @precondition props.variant is one of 'gotcha' | 'warning' | 'tip'
 * @precondition props.text is a non-empty string
 * @precondition Component is rendered within a React 18 tree
 * @postcondition Returns a container <div> (or <aside>) with variant-specific Tailwind classes applied
 * @postcondition The 'gotcha' variant renders with distinct border/background classes (e.g. red/orange tones)
 * @postcondition The 'warning' variant renders with distinct border/background classes (e.g. yellow/amber tones)
 * @postcondition The 'tip' variant renders with distinct border/background classes (e.g. green/teal tones)
 * @postcondition All three variants produce visually distinguishable containers (different class strings)
 * @postcondition props.text is rendered as visible text content within the container
 * @postcondition The container includes a role='alert' or appropriate ARIA attribute for accessibility
 * @sideEffects none
 * @idempotent yes
 */
export function CalloutBox(
  props: CalloutBoxProps,
): ReactElement;

/**
 * Internal utility function that extracts the 11-character YouTube video ID from a watch URL or short URL. Used by YouTubeEmbed to construct the embed src. Not exported from the barrel — internal to YouTubeEmbed.tsx or a shared utility.
 *
 * @precondition url is a non-empty string
 * @postcondition If url matches youtube.com/watch?v={id}, returns the 11-character video ID
 * @postcondition If url matches youtu.be/{id}, returns the 11-character video ID
 * @postcondition If url does not match either pattern, returns an empty string
 * @throws no_video_id_found (str) - URL does not contain a recognizable YouTube video ID pattern
 *   returns: empty string
 * @sideEffects none
 * @idempotent yes
 */
export function extractYouTubeVideoId(
  url: string,
): string;

// -- REQUIRED EXPORTS -----------------------------------------------
// Your implementation module MUST export ALL of these names
// with EXACTLY these spellings. Tests import them by name.
// exports: ['CalloutVariant', 'CodeBlockProps', 'VersionBadgeProps', 'YouTubeEmbedProps', 'CalloutBoxProps', 'CalloutVariantClassMap', 'ClipboardWriteResult', 'OptionalString', 'CodeBlock', 'ClipboardApiUnavailableError', 'ClipboardWriteError', 'VersionBadge', 'YouTubeEmbed', 'InvalidYouTubeUrlError', 'CalloutBox', 'extractYouTubeVideoId']
