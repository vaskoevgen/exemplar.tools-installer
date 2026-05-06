# === Tool Page & Comments Section (tool_page) v1 ===
#  Dependencies: shared_types, convex_schema
# Component group comprising ToolPage.tsx (page-level orchestrator), CommentsSection.tsx (stateful Convex-backed comment list + form), and four pure presentational sub-components (StepBadge, VersionBadge, CodeBlock, VideoEmbed), plus two utility functions (formatRelativeTime, isToolSlug) and one derived lookup map (TOOL_MAP). ToolPage extracts toolSlug from React Router useParams, validates via isToolSlug type guard, performs O(1) lookup from TOOL_MAP, and renders decomposed props into sub-components. CommentsSection manages real-time comment query/mutation via Convex hooks and local form state with validation. All props interfaces use canonical registry types (ToolSlug, StepNumber, HexColor) without redefinition.

# Module invariants:
#   - TOOL_MAP contains exactly one entry for each ToolSlug variant — no missing and no extra entries
#   - ToolPage renders not-found UI for any toolSlug value that fails the isToolSlug type guard — never throws an unhandled exception
#   - VideoEmbed is mounted if and only if the resolved ToolDef.videoUrl is a non-empty string (kindex tool omits this section)
#   - CommentsSection always renders one of exactly three states: loading (query undefined), empty (query returns []), or populated list (query returns non-empty array)
#   - Comment form submission is blocked when author or body is empty/whitespace-only after trimming — no mutation is invoked for invalid input
#   - All presentational components (StepBadge, VersionBadge, CodeBlock, VideoEmbed) are pure: given the same props, they produce the same rendered output
#   - accentColor from ToolDef is propagated to StepBadge, VersionBadge, and CommentsSection — never hardcoded in those components
#   - CodeBlock uses JetBrains Mono font-family for the pre > code element and a fixed dark terminal theme independent of accentColor
#   - Each file (ToolPage.tsx, CommentsSection.tsx, StepBadge.tsx, VersionBadge.tsx, CodeBlock.tsx, VideoEmbed.tsx) stays under 300 lines
#   - All exported functions and components have TypeScript type annotations
#   - Only React functional components are used — no class components
#   - Props interfaces use exact registry types (ToolSlug, StepNumber, HexColor) — no redefinitions of these types within this component group
#   - formatRelativeTime is a pure function that returns a non-empty string for any finite non-negative input

class ToolSlug(Enum):
    """URL-safe identifier for each tool, used as route param and Convex page key."""
    constrain = "constrain"
    ledger = "ledger"
    pact = "pact"
    advocate = "advocate"
    arbiter = "arbiter"
    baton = "baton"
    sentinel = "sentinel"
    chronicler = "chronicler"
    stigmergy = "stigmergy"
    apprentice = "apprentice"
    kindex = "kindex"

HexColor = primitive  # CSS hex color string (e.g. '#00e5ff') used for per-tool accent theming.

StepNumber = primitive  # Integer 1–11 representing the tool's position in the exemplar.tools workflow order.

class InstructionStep:
    """A single step-by-step instruction entry containing a human title and a bash snippet."""
    title: string                            # required, Short human-readable title for this instruction step.
    bash: string                             # required, Bash code block content to display in a terminal-styled card.

InstructionStepList = list[InstructionStep]
# Ordered array of InstructionStep objects for a tool's how-to section.

class ToolDef:
    """Complete static definition of one tool including display metadata, instructions, and video URL."""
    slug: ToolSlug                           # required, URL-safe identifier used as route parameter and sidebar key.
    name: string                             # required, Human-readable display name of the tool (e.g. 'Constrain').
    description: string                      # required, One-line description shown on the tool page and in the quick-start table.
    step: StepNumber                         # required, Workflow step number (1–11) displayed in the StepBadge.
    version: string                          # required, Semver version string displayed in the VersionBadge.
    accentColor: HexColor                    # required, Per-tool accent color hex for badges, headings, and diagram nodes.
    videoUrl: OptionalVideoUrl = undefined   # optional, YouTube embed URL; omitted for kindex.
    instructions: InstructionStepList        # required, Ordered step-by-step instructions rendered on the tool page.

ToolDefList = list[ToolDef]
# The canonical ordered array of all 11 ToolDef objects, indexed by workflow step order.

class ToolMap:
    """Record<ToolSlug, ToolDef> — O(1) lookup map derived from ToolDefList at module load time. Exported from the data constants module."""
    entries: dict                            # required, Keys are ToolSlug strings, values are ToolDef objects. Exhaustive over all ToolSlug variants.

class Comment:
    """A user-submitted comment persisted in Convex, displayed in the CommentsSection."""
    _id: string                              # required, Convex-generated unique document ID.
    page: ToolSlug                           # required, Tool slug identifying which page this comment belongs to.
    author: string                           # required, length(1..100), Display name of the comment author.
    body: string                             # required, length(1..2000), Comment body text.
    createdAt: number                        # required, Unix epoch millisecond timestamp set via Date.now() at insertion time.

CommentList = list[Comment]
# Array of Comment objects returned by the listComments query, sorted by createdAt ascending.

class ToolPageProps:
    """ToolPage receives no explicit props; it extracts toolSlug from React Router useParams internally. This type documents the implicit contract."""
    pass

class CommentsSectionProps:
    """Props interface for CommentsSection component."""
    page: ToolSlug                           # required, Tool slug identifying which page's comments to load and submit to.
    accentColor: HexColor                    # required, Accent color for the submit button and section heading.

class StepBadgeProps:
    """Props interface for StepBadge presentational component."""
    step: StepNumber                         # required, Step ordinal to display inside the pill.
    accentColor: HexColor                    # required, Background color for the pill, applied via inline style.

class VersionBadgeProps:
    """Props interface for VersionBadge presentational component."""
    version: str                             # required, regex(^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$), Semver string to display.
    accentColor: HexColor                    # required, Accent color for the badge border and text.

class CodeBlockProps:
    """Props interface for CodeBlock presentational component."""
    title: str                               # required, length(1..200), Title displayed in the terminal card title bar.
    bash: str                                # required, length(1..2000), Bash code content rendered in pre > code with JetBrains Mono font.

class VideoEmbedProps:
    """Props interface for VideoEmbed presentational component. url is required because parent only mounts this component when videoUrl is defined and non-empty."""
    url: str                                 # required, regex(^https://www\.youtube\.com/embed/[a-zA-Z0-9_-]{11}(\?.*)?$), YouTube embed URL. Required (not optional) — parent guards mounting.
    title: str = Video tutorial              # optional, Accessible title for the iframe element.

class CommentFormState:
    """Internal useState shape for the comment submission form in CommentsSection."""
    author: str                              # required, Current value of the author input field.
    body: str                                # required, Current value of the body textarea field.

ReactElement = primitive  # React JSX element returned by functional components. Opaque type in contract context.

OptionalVideoUrl = Any | None

class number:
    """Auto-stubbed type — referenced but not defined in contract 'tool_page'"""
    pass

class string:
    """Auto-stubbed type — referenced but not defined in contract 'tool_page'"""
    pass

def ToolPage() -> ReactElement:
    """
    Page-level React functional component at src/pages/ToolPage.tsx. Extracts toolSlug from useParams, validates via isToolSlug type guard, performs O(1) lookup from TOOL_MAP. On valid slug: renders tool name heading (with accentColor inline style), one-line description, StepBadge, VersionBadge, mapped InstructionStepList as CodeBlock cards, conditional VideoEmbed, and CommentsSection. On invalid slug: renders not-found UI. No explicit props — route params are the implicit input.

    Preconditions:
      - Component is rendered within a React Router v6 <Route path='/tools/:toolSlug'> context so useParams provides toolSlug
      - TOOL_MAP is loaded and contains entries for all valid ToolSlug variants
      - Convex provider is present in the component tree (required by CommentsSection child)

    Postconditions:
      - If toolSlug is a valid ToolSlug, renders complete tool page with heading, description, StepBadge, VersionBadge, instruction CodeBlocks, optional VideoEmbed, and CommentsSection
      - If toolSlug is not a valid ToolSlug, renders a not-found message without crashing
      - accentColor is applied via inline style to the heading element and propagated to StepBadge, VersionBadge, and CommentsSection
      - VideoEmbed is mounted if and only if toolDef.videoUrl is a non-empty string
      - CodeBlock components are rendered in instruction order with correct step titles and bash content

    Errors:
      - invalid_tool_slug (render_not_found_ui): useParams().toolSlug fails isToolSlug type guard (not in ToolSlug enum)
          behavior: Renders inline not-found message, does not throw or redirect
      - missing_tool_slug_param (render_not_found_ui): useParams() returns undefined for toolSlug (route misconfiguration)
          behavior: Treats undefined as invalid slug, renders not-found UI

    Side effects: none
    Idempotent: yes
    """
    ...

def CommentsSection(
    page: ToolSlug,
    accentColor: HexColor,
) -> ReactElement:
    """
    Stateful React functional component at src/components/CommentsSection.tsx. Accepts page (ToolSlug) and accentColor props. Uses Convex useQuery(api.comments.listComments, { page }) for real-time comment subscription and useMutation(api.comments.addComment) for submissions. Manages CommentFormState via useState. Validates non-empty author and body on submit. Renders three states: loading spinner (query returns undefined), empty state message, and populated comment list with author, body, and relative timestamp via formatRelativeTime.

    Preconditions:
      - Convex provider is present in the component tree with a valid client connection
      - api.comments.listComments and api.comments.addComment are deployed and accessible
      - page is a valid ToolSlug (parent ToolPage validates this before passing)

    Postconditions:
      - When useQuery returns undefined, a loading indicator is displayed
      - When useQuery returns an empty CommentList, an empty state message is displayed
      - When useQuery returns a populated CommentList, comments are rendered in order with author, body, and relative timestamp
      - On valid form submission (non-empty author and body), addComment mutation is invoked with { page, author: trimmed, body: trimmed }
      - After successful submission, form fields are reset to empty strings
      - Invalid form submission (empty author or body after trimming) does not invoke the mutation

    Errors:
      - empty_author (validation_error): User submits form with author field empty or whitespace-only after trimming
          behavior: Prevents submission, no mutation called, inline validation message displayed
      - empty_body (validation_error): User submits form with body field empty or whitespace-only after trimming
          behavior: Prevents submission, no mutation called, inline validation message displayed
      - mutation_failure (convex_mutation_error): Convex addComment mutation rejects (network error, server-side validation, rate limit)
          behavior: Error propagates to Convex error boundary or is caught and displayed inline; form state is preserved for retry
      - query_subscription_error (convex_query_error): Convex useQuery subscription fails (network disconnect, invalid query)
          behavior: useQuery returns undefined, component shows loading state; Convex client handles automatic reconnection

    Side effects: none
    Idempotent: no
    """
    ...

def StepBadge(
    step: StepNumber,
    accentColor: HexColor,
) -> ReactElement:
    """
    Pure presentational React functional component at src/components/StepBadge.tsx. Renders a styled pill displaying the step number with background color derived from accentColor via inline style. Tailwind classes for sizing/rounding, inline style for dynamic color.

    Preconditions:
      - step is a valid StepNumber (positive integer 1-99)
      - accentColor is a valid HexColor matching ^#[0-9A-Fa-f]{6}$

    Postconditions:
      - Rendered pill contains the step number as text content
      - Pill background color matches the provided accentColor
      - Pill uses Tailwind utility classes for rounded-full, px, py, text-white, font-bold sizing

    Side effects: none
    Idempotent: yes
    """
    ...

def VersionBadge(
    version: str,              # regex(^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$)
    accentColor: HexColor,
) -> ReactElement:
    """
    Pure presentational React functional component at src/components/VersionBadge.tsx. Renders a version string in a pill badge with border and text color derived from accentColor via inline style.

    Preconditions:
      - version is a non-empty valid semver string
      - accentColor is a valid HexColor

    Postconditions:
      - Rendered badge displays the version string prefixed with 'v' if not already prefixed
      - Badge border color and text color match the provided accentColor

    Side effects: none
    Idempotent: yes
    """
    ...

def CodeBlock(
    title: str,                # length(1..200)
    bash: str,                 # length(1..2000)
) -> ReactElement:
    """
    Pure presentational React functional component at src/components/CodeBlock.tsx. Renders a dark terminal card with a title bar containing the step title and a pre > code block with bash content styled in JetBrains Mono. Uses fixed dark theme colors (bg-gray-900, text-green-400 or similar), no accent color dependency.

    Preconditions:
      - title is a non-empty string
      - bash is a non-empty string
      - JetBrains Mono font is loaded (via Google Fonts link in index.html or Tailwind config)

    Postconditions:
      - Renders a container with dark background (e.g. bg-gray-900 or bg-[#1e1e1e])
      - Title bar displays the title text with subtle styling (e.g. text-gray-400, smaller font)
      - Terminal card includes decorative dots (red, yellow, green) in title bar mimicking macOS terminal
      - Code content is inside a pre > code element with font-family: 'JetBrains Mono', monospace
      - Code text uses light color on dark background for terminal aesthetic
      - Content does not overflow — horizontal scroll enabled on pre element if needed

    Side effects: none
    Idempotent: yes
    """
    ...

def VideoEmbed(
    url: str,                  # regex(^https://www\.youtube\.com/embed/[a-zA-Z0-9_-]{11}(\?.*)?$)
    title: str = Video tutorial,
) -> ReactElement:
    """
    Pure presentational React functional component at src/components/VideoEmbed.tsx. Renders a responsive 16:9 YouTube iframe embed. Only mounted by ToolPage when videoUrl is defined and non-empty, so url prop is required (not optional). Uses Tailwind aspect-video or padding-bottom trick for 16:9 ratio.

    Preconditions:
      - url is a valid YouTube embed URL (https://www.youtube.com/embed/{videoId})
      - Component is only mounted when parent has verified videoUrl is non-empty

    Postconditions:
      - Renders an iframe element with src={url} and title attribute
      - iframe is wrapped in a responsive 16:9 aspect ratio container (Tailwind aspect-video or equivalent)
      - iframe has width='100%' and appropriate Tailwind classes for rounded corners and shadow
      - iframe includes allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' and allowFullScreen attributes
      - iframe has loading='lazy' for performance

    Side effects: none
    Idempotent: yes
    """
    ...

def formatRelativeTime(
    createdAt: float,          # range(0..Infinity)
) -> str:
    """
    Pure utility function at src/utils/formatRelativeTime.ts. Converts a Convex _creationTime timestamp (milliseconds since epoch) to a human-readable relative time string (e.g. 'just now', '5 minutes ago', '2 hours ago', '3 days ago', 'Jan 15, 2024'). Falls back to absolute date for timestamps older than 30 days.

    Preconditions:
      - createdAt is a non-negative finite number representing milliseconds since Unix epoch
      - createdAt is not in the future relative to Date.now() (if it is, returns 'just now')

    Postconditions:
      - Returns 'just now' for timestamps less than 60 seconds ago
      - Returns '{n} minute(s) ago' for timestamps 1-59 minutes ago
      - Returns '{n} hour(s) ago' for timestamps 1-23 hours ago
      - Returns '{n} day(s) ago' for timestamps 1-30 days ago
      - Returns formatted absolute date (e.g. 'Jan 15, 2024') for timestamps older than 30 days
      - Returned string is always non-empty

    Errors:
      - nan_input (invalid_argument): createdAt is NaN
          behavior: Returns empty string or 'Unknown' — implementation should guard against NaN
      - negative_input (invalid_argument): createdAt is negative
          behavior: Treats as very old timestamp, returns absolute date format

    Side effects: none
    Idempotent: yes
    """
    ...

def isToolSlug(
    value: str,
) -> bool:
    """
    Type guard utility function at src/utils/isToolSlug.ts. Checks if an arbitrary string is a valid ToolSlug by testing membership in the set of known slug values. Returns boolean with TypeScript type narrowing: `value is ToolSlug`.

    Postconditions:
      - Returns true if and only if value is one of the known ToolSlug enum variants
      - When returns true, TypeScript narrows the type of value to ToolSlug
      - When returns false, value is not a valid ToolSlug and should not be used as a TOOL_MAP key

    Side effects: none
    Idempotent: yes
    """
    ...

def buildToolMap(
    tools: ToolDefList,
) -> ToolMap:
    """
    Derived lookup map factory. Converts ToolDefList array into TOOL_MAP: Record<ToolSlug, ToolDef> for O(1) access. Called once at module load time in the data constants module. Exported constant is `TOOL_MAP`.

    Preconditions:
      - tools array is non-empty
      - All ToolDef.slug values in tools are unique
      - All ToolDef.slug values are valid ToolSlug enum variants

    Postconditions:
      - Returned map contains exactly one entry per element in the input array
      - Each key is a ToolSlug, each value is the corresponding ToolDef
      - Map is exhaustive: every ToolSlug variant has a corresponding entry
      - Lookup by valid ToolSlug key returns in O(1) time

    Errors:
      - duplicate_slugs (invariant_violation): Two or more ToolDef entries share the same slug value
          behavior: Later entry overwrites earlier — implementation should assert uniqueness in development
      - empty_tools_array (invariant_violation): Input tools array is empty
          behavior: Returns empty map — development assertion should catch this

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['ToolSlug', 'InstructionStep', 'InstructionStepList', 'ToolDef', 'ToolDefList', 'ToolMap', 'Comment', 'CommentList', 'ToolPageProps', 'CommentsSectionProps', 'StepBadgeProps', 'VersionBadgeProps', 'CodeBlockProps', 'VideoEmbedProps', 'CommentFormState', 'OptionalVideoUrl', 'number', 'string', 'ToolPage', 'render_not_found_ui', 'CommentsSection', 'validation_error', 'convex_mutation_error', 'convex_query_error', 'StepBadge', 'VersionBadge', 'CodeBlock', 'VideoEmbed', 'formatRelativeTime', 'invalid_argument', 'isToolSlug', 'buildToolMap', 'invariant_violation']
