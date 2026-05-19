// === Root (root) v1 ===
//  Dependencies: app_routing, page_components, project_scaffold, shared_components
// Thin composition layer and barrel re-export module for the exemplar.tools documentation website. The root is the ONLY integration point where app_routing and page_components meet — it retrieves the route manifest from app_routing, the page component map from page_components, and passes both into the entry point renderer. All canonical types from child components are re-exported (never redefined) for consumer convenience. Defines one root-owned function bootstrapApp() that orchestrates the composition, and one root-specific type BootstrapConfig for optional configuration. This module enforces the dependency inversion constraint: page_components never imports from app_routing directly; the root wires them together.

// Module invariants:
//   - Root module is a pure composition layer — it never redefines types owned by child components, only re-exports them
//   - Root is the ONLY module where app_routing and page_components are both imported — enforcing dependency inversion
//   - bootstrapApp() always verifies the manifest-to-component-map bijection before attempting to render
//   - getRouteManifest() always returns exactly 13 RouteEntry objects
//   - getPageComponentMap() always returns a map with exactly 13 entries keyed by PageComponentKey values
//   - The set of componentKey values in the route manifest is identical to the set of keys in the page component map
//   - No .js or .py source files exist in the root module — all source files are .ts or .tsx
//   - All re-exported types preserve their owner_component attribution — root claims no authority over child-owned types
//   - bootstrapApp() calls getRouteManifest() and getPageComponentMap() exactly once each per invocation
//   - verifyManifestComponentBijection() is a pure function with no side effects

/** Optional configuration for the bootstrapApp function controlling where and how the React application is mounted. */
export interface BootstrapConfig {
  targetElementId?: string;  // optional, default: root, length(length >= 1), DOM element ID to mount the React root onto. Defaults to 'root' matching the scaffold's index.html <div id="root">.
  strictMode?: boolean;  // optional, default: true, Whether to wrap the App component in React.StrictMode. Defaults to true matching the scaffold's src/main.tsx.
}

/** Result returned by bootstrapApp confirming successful mount and providing diagnostics. */
export interface BootstrapResult {
  routeCount: number;  // required, range(value == 13), Number of route entries in the manifest (must be 13).
  pageComponentCount: number;  // required, range(value == 13), Number of entries in the page component map (must be 13).
  targetElementId: string;  // required, The DOM element ID that was used for mounting.
  allRoutesHaveComponents: boolean;  // required, custom(value === true), True if every componentKey in the route manifest has a corresponding entry in the page component map (bijection verified).
}

/** Discriminator enum identifying each of the 13 page components. */
export type PageComponentKey = "Home" | "Cartographer" | "Constrain" | "Ledger" | "Pact" | "Advocate" | "Arbiter" | "Baton" | "Sentinel" | "Chronicler" | "Stigmergy" | "Apprentice" | "Kindex";

/** A single route definition consumed by both the router configuration and the Sidebar navigation. */
export interface RouteEntry {
  path: string;  // required, URL path segment, e.g. '/step-0-cartographer' or '/' for home.
  label: string;  // required, Human-readable navigation label shown in the Sidebar, e.g. 'Step 0 — Cartographer'.
  componentKey: PageComponentKey;  // required, Lookup key that maps this route to its lazy-loaded or statically-imported page component.
}

/** Ordered array of all 13 route entries; single source of truth for navigation and routing. */
export type RouteManifest = RouteEntry[];

/** A validated URL path string. Must start with '/' and contain only lowercase alphanumeric characters, hyphens, and forward slashes. Matches the AS3 slug pattern. */
export type RoutePath = unknown;

/** A validated non-empty string used as the sidebar display label for a route. */
export type RouteLabel = unknown;

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

/** Re-exported from app_routing. Opaque reference to React.ComponentType — a function or class component. */
export type ReactComponentType = unknown;

/** Re-exported from app_routing. Empty props for the App root component. */
export interface AppProps {
}

/** Visual variant for a CalloutBox — determines border color, icon, and background tint. */
export type CalloutType = "gotcha" | "warning" | "tip";

/** Props accepted by the CalloutBox component; used by every page component to render callouts. */
export interface CalloutBoxProps {
  type: CalloutType;  // required, Visual style variant (gotcha, warning, or tip).
  title?: string;  // optional, Optional bold heading rendered above the body text.
  children: ReactNode;  // required, Body content of the callout (JSX).
}

/** Props accepted by the CodeBlock component; used by every page to render CLI commands with syntax highlighting and copy button. */
export interface CodeBlockProps {
  code: string;  // required, The verbatim CLI command or code snippet to display.
  language?: string;  // optional, default: bash, Prism language identifier for syntax highlighting.
  title?: string;  // optional, Optional filename or label shown above the code block.
}

/** Props accepted by the VersionBadge component; used by page components to show component version pills. */
export interface VersionBadgeProps {
  version: string;  // required, Semantic version string to display, e.g. '1.2.3'.
  label?: string;  // optional, Optional tool name rendered before the version number.
}

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

/** React.ReactNode — opaque type representing renderable JSX children. */
export type ReactNode = unknown;

/** Re-exported from project_scaffold. Manifest enumerating all produced file paths and project metadata. */
export interface ProjectManifest {
  projectRoot: string;  // required, Absolute path to the exemplar-tools-doc/ project directory.
  files: unknown[];  // required, Ordered array of all 12 file paths relative to projectRoot.
  projectName: string;  // required, The npm package name: 'exemplar-tools-doc'.
  devServerPort: number;  // required, Vite dev server port, must be 4000.
}

/** Re-exported from project_scaffold. A single npm dependency with its pinned semver range. */
export interface DependencyEntry {
  packageName: string;  // required, npm package name.
  versionRange: string;  // required, Semver range string.
  isDev: boolean;  // required, True if devDependency.
}

/** Re-exported from project_scaffold. Complete set of pinned dependencies the scaffold must declare. */
export interface RequiredDependencies {
  dependencies: unknown[];  // required, Runtime dependencies.
  devDependencies: unknown[];  // required, Dev dependencies.
}

/** Re-exported from project_scaffold. Result of scaffold generation. */
export interface ScaffoldResult {
  manifest: ProjectManifest;  // required, The complete project manifest.
  filesWritten: number;  // required, Number of files written (must be 12).
  hasJsFiles: boolean;  // required, Must be false.
  hasPyFiles: boolean;  // required, Must be false.
}

/** Re-exported from project_scaffold. Options controlling scaffold generation. */
export interface ScaffoldOptions {
  outputDir: string;  // required, Target project directory path.
  overwrite?: boolean;  // optional, default: false, Whether to overwrite existing files.
}

/** Re-exported from project_scaffold. Literal string union of every file path produced by the scaffold. */
export type ScaffoldFilePath = "package.json" | "tsconfig.json" | "tsconfig.node.json" | "vite.config.ts" | "tailwind.config.ts" | "postcss.config.mjs" | "vercel.json" | "index.html" | "vitest.setup.ts" | "src/main.tsx" | "src/index.css" | "src/App.tsx";

/** Re-exported from project_scaffold. Discriminated error types for scaffold generation failures. */
export type ScaffoldError = "DIRECTORY_NOT_FOUND" | "FILE_ALREADY_EXISTS" | "WRITE_PERMISSION_DENIED" | "INVALID_OUTPUT_DIR";

/** Root-owned error type for bootstrapApp failures. */
export type BootstrapError = "MANIFEST_COMPONENT_MISMATCH" | "TARGET_ELEMENT_NOT_FOUND" | "RENDER_FAILURE";

/** Root-owned diagnostic type returned by verifyManifestComponentBijection, confirming that every route manifest componentKey has a matching page component map entry and vice versa. */
export interface ManifestComponentBijectionResult {
  isValid: boolean;  // required, True if every componentKey in the manifest has a corresponding page component map entry and the counts match.
  manifestKeys: unknown[];  // required, Array of PageComponentKey strings extracted from the route manifest.
  mapKeys: unknown[];  // required, Array of key strings from the page component map.
  missingInMap: unknown[];  // required, componentKey values present in the manifest but missing from the page component map. Empty if isValid.
  extraInMap: unknown[];  // required, Key values present in the page component map but not referenced by any manifest entry. Empty if isValid.
}

/** Auto-stubbed type — referenced but not defined in contract 'root' */
export interface string {
}

/**
 * Main composition function and the sole integration point where app_routing and page_components meet. Retrieves the route manifest from app_routing via getRouteManifest(), retrieves the page component map from page_components via getPageComponentMap(), verifies the bijection between manifest componentKeys and map keys, then calls renderEntryPoint() from app_routing to mount the React application into the DOM. This function enforces the architectural constraint that page_components never imports from app_routing directly — the root wires them together via dependency inversion.
 *
 * @precondition document contains an element with the ID specified by config.targetElementId (default 'root')
 * @precondition getRouteManifest() is callable and returns a valid RouteManifest with exactly 13 entries
 * @precondition getPageComponentMap() is callable and returns a valid PageComponentMap with exactly 13 entries
 * @precondition Every componentKey in the route manifest has a corresponding key in the page component map (bijection holds)
 * @postcondition getRouteManifest() was called exactly once and its result contains exactly 13 RouteEntry objects
 * @postcondition getPageComponentMap() was called exactly once and its result contains exactly 13 entries
 * @postcondition Bijection between manifest componentKeys and map keys was verified before rendering
 * @postcondition renderEntryPoint() was called to mount <App /> into the target DOM element
 * @postcondition Returned BootstrapResult.routeCount === 13
 * @postcondition Returned BootstrapResult.pageComponentCount === 13
 * @postcondition Returned BootstrapResult.allRoutesHaveComponents === true
 * @postcondition Returned BootstrapResult.targetElementId matches the config value used
 * @throws manifest_component_mismatch (MANIFEST_COMPONENT_MISMATCH) - At least one componentKey in the route manifest has no corresponding entry in the page component map, or vice versa
 *   missingInMap: JSON array of componentKey values missing from page component map
 *   extraInMap: JSON array of map keys not referenced by any manifest entry
 * @throws target_element_not_found (TARGET_ELEMENT_NOT_FOUND) - document.getElementById(config.targetElementId) returns null — the mount target does not exist in the DOM
 *   targetElementId: The element ID that was not found in the document
 * @throws render_failure (RENDER_FAILURE) - renderEntryPoint() throws during React root creation or initial render
 *   cause: String representation of the underlying error
 * @sideEffects none
 * @idempotent no
 */
export function bootstrapApp(
  config?: BootstrapConfig,
): BootstrapResult;

/**
 * Pure diagnostic function that checks whether every componentKey in the route manifest has a corresponding entry in the page component map and vice versa. Used internally by bootstrapApp before rendering, and exported for contract test verification. Does not perform any side effects — purely compares the two data structures.
 *
 * @precondition manifest is a non-null array of RouteEntry objects
 * @precondition componentMap is a non-null object with string keys
 * @postcondition result.isValid is true if and only if manifestKeys and mapKeys are identical sets
 * @postcondition result.missingInMap contains every componentKey present in manifest but absent from componentMap
 * @postcondition result.extraInMap contains every key present in componentMap but not referenced by any manifest entry
 * @postcondition result.manifestKeys contains the componentKey from every manifest entry in order
 * @postcondition result.mapKeys contains every key from componentMap
 * @sideEffects none
 * @idempotent yes
 */
export function verifyManifestComponentBijection(
  manifest: RouteManifest,
  componentMap: PageComponentMap,
): ManifestComponentBijectionResult;

/**
 * Re-exported from app_routing. Returns the ROUTE_MANIFEST constant — the canonical readonly array of all 13 RouteEntry objects. See app_routing contract for full specification.
 *
 * @postcondition Returned array has exactly 13 entries
 * @postcondition Every PageComponentKey variant appears exactly once across all entries
 * @postcondition All path values are unique
 * @postcondition All label values are non-empty strings
 * @sideEffects none
 * @idempotent yes
 */
export function getRouteManifest(): RouteManifest;

/**
 * Re-exported from page_components. Returns the pageComponentMap: Record<PageComponentKey, React.ComponentType> containing all 13 page components keyed by their exact PageComponentKey enum values. See page_components contract for full specification.
 *
 * @postcondition Returned map contains exactly 13 entries
 * @postcondition Every PageComponentKey enum value is present as a key
 * @postcondition Every value is a valid React.ComponentType
 * @sideEffects none
 * @idempotent yes
 */
export function getPageComponentMap(): PageComponentMap;

/**
 * Re-exported from app_routing. Root React component that renders BrowserRouter wrapping PageLayout with Routes for all 13 pages. See app_routing contract for full specification.
 *
 * @postcondition Renders a BrowserRouter at the root
 * @postcondition Renders exactly 13 Route elements
 * @sideEffects none
 * @idempotent yes
 */
export function App(): unknown;

/**
 * Re-exported from app_routing. Minimal entry point that calls ReactDOM.createRoot and renders <App /> inside React.StrictMode. See app_routing contract for full specification.
 *
 * @postcondition React root is created and mounted on #root element
 * @postcondition App component is rendered inside React.StrictMode
 * @throws missing_root_element (TypeError) - document.getElementById('root') returns null
 * @sideEffects none
 * @idempotent no
 */
export function renderEntryPoint(): null;

/**
 * Re-exported from app_routing. Constructs the PAGE_COMPONENTS constant mapping every PageComponentKey to its imported page component. See app_routing contract for full specification.
 *
 * @postcondition Returned map contains exactly 13 entries
 * @postcondition Every PageComponentKey variant is a key in the map
 * @sideEffects none
 * @idempotent yes
 */
export function buildPageComponentMap(): PageComponentMap;

/**
 * Re-exported from project_scaffold. Returns the canonical ProjectManifest for the exemplar-tools-doc project. See project_scaffold contract for full specification.
 *
 * @postcondition Returned manifest.files has exactly 12 entries
 * @postcondition Returned manifest.projectName === 'exemplar-tools-doc'
 * @postcondition Returned manifest.devServerPort === 4000
 * @sideEffects none
 * @idempotent yes
 */
export function getProjectManifest(): ProjectManifest;

/**
 * Re-exported from project_scaffold. Returns the complete list of pinned npm dependencies. See project_scaffold contract for full specification.
 *
 * @postcondition dependencies contains exactly 3 entries
 * @postcondition devDependencies contains exactly 13 entries
 * @sideEffects none
 * @idempotent yes
 */
export function getRequiredDependencies(): RequiredDependencies;

/**
 * Re-exported from shared_components. Renders a color-coded callout box. See shared_components contract for full specification.
 *
 * @postcondition Renders a callout with border color matching props.type
 * @sideEffects none
 * @idempotent yes
 */
export function CalloutBox(
  props: CalloutBoxProps,
): unknown;

/**
 * Re-exported from shared_components. Renders syntax-highlighted code with copy button. See shared_components contract for full specification.
 *
 * @postcondition Renders code with prism-react-renderer highlighting and copy button
 * @sideEffects none
 * @idempotent yes
 */
export function CodeBlock(
  props: CodeBlockProps,
): unknown;

/**
 * Re-exported from shared_components. Renders a Tailwind pill badge for version strings. See shared_components contract for full specification.
 *
 * @postcondition Renders a pill badge with the version string
 * @sideEffects none
 * @idempotent yes
 */
export function VersionBadge(
  props: VersionBadgeProps,
): unknown;

/**
 * Re-exported from shared_components. Renders a responsive 16:9 YouTube iframe. See shared_components contract for full specification.
 *
 * @postcondition Renders an iframe with aspect-video styling
 * @sideEffects none
 * @idempotent yes
 */
export function VideoEmbed(
  props: VideoEmbedProps,
): unknown;

/**
 * Re-exported from shared_components. Renders persistent navigation sidebar with NavLink per route. See shared_components contract for full specification.
 *
 * @postcondition Renders a nav element with one NavLink per route entry
 * @sideEffects none
 * @idempotent yes
 */
export function Sidebar(
  props: SidebarProps,
): unknown;

/**
 * Re-exported from shared_components. Shell component composing Sidebar and content area in responsive flex layout. See shared_components contract for full specification.
 *
 * @postcondition Renders flex container with Sidebar and main content area
 * @sideEffects none
 * @idempotent yes
 */
export function PageLayout(
  props: PageLayoutProps,
): unknown;

// -- REQUIRED EXPORTS -----------------------------------------------
// Your implementation module MUST export ALL of these names
// with EXACTLY these spellings. Tests import them by name.
// exports: ['BootstrapConfig', 'BootstrapResult', 'PageComponentKey', 'RouteEntry', 'RouteManifest', 'PageComponentMap', 'AppProps', 'CalloutType', 'CalloutBoxProps', 'CodeBlockProps', 'VersionBadgeProps', 'VideoEmbedProps', 'SidebarProps', 'PageLayoutProps', 'ProjectManifest', 'DependencyEntry', 'RequiredDependencies', 'ScaffoldResult', 'ScaffoldOptions', 'ScaffoldFilePath', 'ScaffoldError', 'BootstrapError', 'ManifestComponentBijectionResult', 'bootstrapApp', 'MANIFEST_COMPONENT_MISMATCH', 'TARGET_ELEMENT_NOT_FOUND', 'RENDER_FAILURE', 'verifyManifestComponentBijection', 'getRouteManifest', 'getPageComponentMap', 'App', 'renderEntryPoint', 'buildPageComponentMap', 'getProjectManifest', 'getRequiredDependencies', 'CalloutBox', 'CodeBlock', 'VersionBadge', 'VideoEmbed', 'Sidebar', 'PageLayout']
