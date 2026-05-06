# === Test Harness & Smoke Tests (tests) v1 ===
#  Dependencies: data
# Vitest test harness configuration and smoke test suite for the exemplar.tools documentation website. Provides: (1) vitest configuration surface via vite.config.ts test block and src/__tests__/setup.ts with jsdom environment and @testing-library/jest-dom matchers, (2) data layer smoke tests validating the canonical ToolDefList array (length === 11, slug order matches ToolSlug enum, required field presence/typing, kindex videoUrl undefined, vacuous truth guard for videoUrl existence), (3) component render smoke test using @testing-library/react with MemoryRouter wrapping and optional Convex mock, (4) devDependency contract (vitest, jsdom, @testing-library/react v14+, @testing-library/jest-dom installed via bun add -d), (5) execution contract ensuring `bunx vitest run` exits 0 and package.json scripts include "test": "vitest run".

# Module invariants:
#   - ToolDefList always contains exactly 11 entries — no more, no fewer
#   - Slug order in ToolDefList is fixed to the pipeline order: constrain, ledger, pact, advocate, arbiter, baton, sentinel, chronicler, stigmergy, apprentice, kindex
#   - Every ToolDef entry has defined, non-empty name, description, version, a valid step in [1,11], and accentColor matching /^#[0-9a-fA-F]{6}$/
#   - kindex.videoUrl is always undefined
#   - At least one tool (not kindex) has a defined videoUrl
#   - All test files are discovered under src/**/*.{test,spec}.{ts,tsx}
#   - vitest environment is always jsdom — never node or happy-dom
#   - src/__tests__/setup.ts is always the first file in test.setupFiles
#   - All packages are installed exclusively via bun — never npm, yarn, or npx
#   - bunx vitest run and bun run test produce identical results
#   - Component render tests always wrap in MemoryRouter when the component under test uses React Router

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

HexColorString = primitive  # A 6-digit hex color string prefixed with #, e.g. '#1A2B3C'.

StepNumber = primitive  # Integer 1–11 representing the tool's position in the exemplar.tools workflow order.

NonEmptyString = primitive  # A string that must contain at least one non-whitespace character.

class ToolRequiredFields:
    """The set of fields that every ToolDef entry must have defined and valid. Used as the assertion target shape in data smoke tests."""
    name: NonEmptyString                     # required, Human-readable tool name.
    description: NonEmptyString              # required, Tool description text.
    step: StepNumber                         # required, Pipeline step number 1–11.
    version: NonEmptyString                  # required, Semantic version string of the tool.
    accentColor: HexColorString              # required, Hex color used for UI theming of this tool.
    slug: ToolSlug                           # required, Canonical URL-safe slug identifier.

class VitestConfigBlock:
    """Shape of the `test` key added to vite.config.ts for vitest configuration."""
    globals: bool                            # required, When true, vitest globals (describe, it, expect) are available without import.
    environment: str                         # required, custom(value === 'jsdom'), The test environment. Must be 'jsdom' for DOM-based component tests.
    setupFiles: list                         # required, Array of setup file paths run before each test file.
    include: list                            # required, Glob patterns for test file discovery.

class TestResult:
    """Represents the outcome of a single test case assertion."""
    testName: str                            # required, Fully qualified test name including describe block.
    passed: bool                             # required, True if the assertion passed.
    errorMessage: str = None                 # optional, Empty string if passed, otherwise the assertion failure message.

class TestSuiteResult:
    """Aggregate result from running the full smoke test suite via `bunx vitest run`."""
    exitCode: int                            # required, range(0 <= value <= 1), Process exit code. 0 means all tests passed.
    totalTests: int                          # required, Total number of test cases executed.
    passedTests: int                         # required, Number of test cases that passed.
    failedTests: int                         # required, Number of test cases that failed.
    results: list                            # required, Individual test case results.

class RenderWithProvidersOptions:
    """Configuration options for the renderWithProviders test utility."""
    initialRoute: str = /                    # optional, Initial route path for MemoryRouter.
    mockConvex: bool = false                 # optional, Whether to mock convex/react hooks at module level.

class RenderResult:
    """Return type of renderWithProviders, wrapping @testing-library/react RenderResult with typed accessors."""
    container: any                           # required, The DOM container element from @testing-library/react render.
    getByText: any                           # required, Query function to find elements by text content.
    queryByText: any                         # required, Query function that returns null if no element matches.
    getByTestId: any                         # required, Query function to find elements by data-testid attribute.
    unmount: any                             # required, Function to unmount the rendered component tree.

SlugOrderArray = list[ToolSlug]
# The canonical ordered list of all 11 tool slugs as they must appear in ToolDefList.

def configureVitestSetup() -> None:
    """
    Creates src/__tests__/setup.ts that imports @testing-library/jest-dom for extended matchers and stubs browser globals (e.g., window.matchMedia) absent in jsdom. This file is referenced by vite.config.ts test.setupFiles.

    Preconditions:
      - devDependencies vitest, jsdom, @testing-library/react (>=14.0.0), and @testing-library/jest-dom are installed via bun add -d
      - vite.config.ts exists and exports a defineConfig call

    Postconditions:
      - src/__tests__/setup.ts exists and imports @testing-library/jest-dom
      - src/__tests__/setup.ts stubs window.matchMedia with a no-op implementation
      - vite.config.ts test block is set to: { globals: true, environment: 'jsdom', setupFiles: ['src/__tests__/setup.ts'], include: ['src/**/*.{test,spec}.{ts,tsx}'] }
      - package.json scripts contains "test": "vitest run"

    Errors:
      - missing_dev_dependency (DependencyResolutionError): One or more of vitest, jsdom, @testing-library/react, @testing-library/jest-dom not found in node_modules
          resolution: Run: bun add -d vitest jsdom @testing-library/react @testing-library/jest-dom
      - vite_config_not_found (FileNotFoundError): vite.config.ts does not exist in the project root
          resolution: Ensure vite.config.ts exists. Project must be initialized with bun create vite.

    Side effects: none
    Idempotent: yes
    """
    ...

def assertToolDefListLength(
    toolDefList: list,
) -> TestResult:
    """
    Asserts that the imported ToolDefList array has exactly 11 entries. This is the foundational data integrity check — all other data tests depend on this invariant.

    Preconditions:
      - toolDefList is imported from the data layer module and is a defined array

    Postconditions:
      - TestResult.passed === true iff toolDefList.length === 11

    Errors:
      - length_mismatch (AssertionError): toolDefList.length !== 11
          expected: 11
          detail: ToolDefList must contain exactly 11 entries, one per exemplar tool
      - import_failure (ImportResolutionError): ToolDefList import resolves to undefined or is not an array
          resolution: Verify that the data layer module exports ToolDefList as a named export of type ToolDef[]

    Side effects: none
    Idempotent: yes
    """
    ...

def assertSlugOrder(
    toolDefList: list,
    expectedSlugs: SlugOrderArray,
) -> TestResult:
    """
    Asserts that the slugs in ToolDefList appear in exact pipeline order: constrain, ledger, pact, advocate, arbiter, baton, sentinel, chronicler, stigmergy, apprentice, kindex. Uses ordered array comparison, not set equality.

    Preconditions:
      - toolDefList.length === 11
      - expectedSlugs.length === 11

    Postconditions:
      - TestResult.passed === true iff toolDefList.map(t => t.slug) deep-equals expectedSlugs

    Errors:
      - slug_order_mismatch (AssertionError): The slug at any index i does not match expectedSlugs[i]
          detail: Slugs must appear in exact pipeline order
      - unknown_slug (AssertionError): A slug value is not a member of the ToolSlug enum
          detail: All slugs must be valid ToolSlug enum variants

    Side effects: none
    Idempotent: yes
    """
    ...

def assertRequiredFieldsPerTool(
    toolDef: ToolRequiredFields,
) -> TestResult:
    """
    Uses describe.each over all 11 ToolDefList entries to assert each has the required fields: name (non-empty string), description (non-empty string), step (number 1–11), version (non-empty string), accentColor (string matching /^#[0-9a-fA-F]{6}$/). Each field is individually asserted for precise failure diagnostics.

    Preconditions:
      - toolDef is a defined object (not null/undefined)

    Postconditions:
      - TestResult.passed === true iff all of: toolDef.name is a non-empty string, toolDef.description is a non-empty string, toolDef.step is an integer in [1,11], toolDef.version is a non-empty string, toolDef.accentColor matches /^#[0-9a-fA-F]{6}$/

    Errors:
      - missing_name (AssertionError): toolDef.name is undefined, null, or empty string
          field: name
      - missing_description (AssertionError): toolDef.description is undefined, null, or empty string
          field: description
      - invalid_step (AssertionError): toolDef.step is not an integer or is outside range [1, 11]
          field: step
          constraint: integer in [1, 11]
      - missing_version (AssertionError): toolDef.version is undefined, null, or empty string
          field: version
      - invalid_accent_color (AssertionError): toolDef.accentColor does not match /^#[0-9a-fA-F]{6}$/
          field: accentColor
          constraint: regex: ^#[0-9a-fA-F]{6}$

    Side effects: none
    Idempotent: yes
    """
    ...

def assertKindexNoVideoUrl(
    toolDefList: list,
) -> TestResult:
    """
    Asserts that the tool entry with slug 'kindex' has videoUrl === undefined. This is a specific business rule: kindex does not have an associated video.

    Preconditions:
      - toolDefList contains an entry with slug === 'kindex'

    Postconditions:
      - TestResult.passed === true iff toolDefList.find(t => t.slug === 'kindex').videoUrl === undefined

    Errors:
      - kindex_not_found (AssertionError): No entry in toolDefList has slug === 'kindex'
          detail: ToolDefList must contain a kindex entry
      - kindex_has_video_url (AssertionError): The kindex entry has a defined, non-undefined videoUrl
          detail: kindex.videoUrl must be undefined per business rule

    Side effects: none
    Idempotent: yes
    """
    ...

def assertAtLeastOneVideoUrl(
    toolDefList: list,
) -> TestResult:
    """
    Asserts that at least one tool in ToolDefList has a defined videoUrl. This prevents vacuous truth in the kindex assertion — if no tool has videoUrl, the kindex check would pass trivially and mask a data layer defect.

    Preconditions:
      - toolDefList.length === 11

    Postconditions:
      - TestResult.passed === true iff toolDefList.some(t => t.videoUrl !== undefined)

    Errors:
      - no_video_urls (AssertionError): No tool in ToolDefList has a defined videoUrl
          detail: At least one tool must have a videoUrl to prevent vacuous truth in kindex assertion

    Side effects: none
    Idempotent: yes
    """
    ...

def renderWithProviders(
    component: any,
    options: RenderWithProvidersOptions = { initialRoute: '/', mockConvex: false },
) -> RenderResult:
    """
    Test utility function that renders a React component wrapped in MemoryRouter (for React Router context) and optionally mocks convex/react hooks at module level. Returns @testing-library/react RenderResult. Exported for reuse across future test files.

    Preconditions:
      - component is a valid React element
      - @testing-library/react is available as a devDependency
      - react-router-dom is available for MemoryRouter

    Postconditions:
      - Returned RenderResult.container is a mounted DOM node
      - If options.mockConvex is true, convex/react useQuery and useMutation are replaced with no-op stubs
      - Component is wrapped in <MemoryRouter initialEntries={[options.initialRoute]}>

    Errors:
      - render_throws (RenderError): The component throws during render (e.g., missing required context, undefined prop access)
          detail: Component render must complete without throwing. Check that all required providers and props are supplied.
      - missing_router_context (RouterContextError): Component uses useNavigate/useParams/Link but MemoryRouter wrapper is missing or misconfigured
          detail: Ensure MemoryRouter wraps components that use React Router hooks or components.

    Side effects: none
    Idempotent: no
    """
    ...

def smokeTestComponentRender(
    componentUnderTest: any,
    expectedTextContent: NonEmptyString,
) -> TestResult:
    """
    Smoke test that picks a simple presentational component (one that does not depend on Convex hooks, or uses Convex hooks that are mocked), wraps it via renderWithProviders, and asserts: (1) render completes without throwing, (2) a known text element is present in the rendered output. This validates the test harness end-to-end from jsdom environment through React rendering to DOM query.

    Preconditions:
      - jsdom environment is configured via vitest
      - src/__tests__/setup.ts has been loaded (jest-dom matchers available)
      - componentUnderTest is a valid React element with all required props supplied

    Postconditions:
      - TestResult.passed === true iff render completes without throwing AND getByText(expectedTextContent) returns a DOM node
      - Rendered component tree is unmounted after assertion (cleanup)

    Errors:
      - render_error (RenderError): Component throws during React render lifecycle
          detail: Smoke test failed: component threw during render
      - text_not_found (AssertionError): getByText(expectedTextContent) throws because no matching DOM node exists
          detail: Expected text content not found in rendered output
      - convex_hook_not_mocked (ConvexMockError): Component transitively imports convex/react hooks that are not mocked, causing runtime error in test environment
          resolution: Pass { mockConvex: true } to renderWithProviders or mock convex/react at module level with vi.mock

    Side effects: none
    Idempotent: yes
    """
    ...

def executeTestSuite() -> TestSuiteResult:
    """
    Runs the full smoke test suite via `bunx vitest run` (or equivalently `bun run test`). This is the top-level execution contract: all test files matching src/**/*.{test,spec}.{ts,tsx} are discovered, run in jsdom environment, and the aggregate result is produced. Exit code 0 means all tests pass.

    Preconditions:
      - vite.config.ts contains a valid test configuration block
      - src/__tests__/setup.ts exists and is referenced in test.setupFiles
      - All devDependencies are installed: vitest, jsdom, @testing-library/react (>=14.0.0), @testing-library/jest-dom
      - package.json scripts contains "test": "vitest run"
      - bun is available on PATH

    Postconditions:
      - TestSuiteResult.exitCode === 0 iff all tests pass
      - TestSuiteResult.totalTests >= 15 (minimum: 11 field checks via describe.each + length + slug order + kindex videoUrl + vacuous truth guard + 1 component render)
      - TestSuiteResult.failedTests === 0 when exitCode === 0

    Errors:
      - vitest_config_error (ConfigurationError): Vitest cannot parse or resolve the test configuration in vite.config.ts
          resolution: Verify vite.config.ts test block matches VitestConfigBlock shape
      - setup_file_missing (FileNotFoundError): src/__tests__/setup.ts referenced in setupFiles does not exist
          resolution: Run configureVitestSetup to create the setup file
      - bun_not_found (EnvironmentError): bun binary is not available on PATH
          resolution: Install bun: https://bun.sh
      - test_failures (TestFailureError): One or more test cases fail
          detail: Inspect TestSuiteResult.results for individual failure messages
      - jsdom_import_failure (DependencyResolutionError): jsdom package cannot be resolved, typically because it was not installed as devDependency
          resolution: Run: bun add -d jsdom

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['ToolSlug', 'ToolRequiredFields', 'VitestConfigBlock', 'TestResult', 'TestSuiteResult', 'RenderWithProvidersOptions', 'RenderResult', 'SlugOrderArray', 'configureVitestSetup', 'DependencyResolutionError', 'assertToolDefListLength', 'AssertionError', 'ImportResolutionError', 'assertSlugOrder', 'assertRequiredFieldsPerTool', 'assertKindexNoVideoUrl', 'assertAtLeastOneVideoUrl', 'renderWithProviders', 'RenderError', 'RouterContextError', 'smokeTestComponentRender', 'ConvexMockError', 'executeTestSuite', 'ConfigurationError', 'EnvironmentError', 'TestFailureError']
