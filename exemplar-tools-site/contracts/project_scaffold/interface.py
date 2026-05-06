# === Project Scaffold & Configuration (project_scaffold) v1 ===
# Initialize and configure the Vite + React 18 + TypeScript project scaffold using bun. Owns all build/dev/test configuration files (vite.config.ts, tailwind.config.js, postcss.config.js, tsconfig.json, tsconfig.app.json, package.json, .npmrc), the HTML entry point (index.html with Google Fonts preconnect/stylesheet links), the global CSS entry point (src/index.css with Tailwind directives, dark background, grid utility), and the minimal React 18 createRoot entry (src/main.tsx). Provides extension points for downstream components: Tailwind theme tokens (fontFamily, colors), path alias @/ → src/, bg-grid utility class, and a ConvexProvider mount point stub in main.tsx deferred to app_shell. Creates an empty convex/ directory skeleton for data_layer to populate. Does NOT define any canonical registry types (ToolSlug, ToolDef, Comment, etc.) — those are owned by data_layer.

# Module invariants:
#   - bun.lockb is the sole lockfile in the project root — no package-lock.json, yarn.lock, or pnpm-lock.yaml may coexist.
#   - vite.config.ts server.port is always 4000 and server.strictPort is always true.
#   - Build output directory is always 'dist'.
#   - tailwind.config.js content globs always cover './src/**/*.{ts,tsx,js,jsx}' and './index.html'.
#   - The three font families (Instrument Serif, JetBrains Mono, Inter) are present in both tailwind.config.js theme.extend.fontFamily and index.html Google Fonts links.
#   - All Google Fonts links use display=swap parameter.
#   - The .bg-grid utility class is registered either via Tailwind plugin in tailwind.config.js (preferred) or in src/index.css @layer utilities — never in both.
#   - src/index.css @layer base sets html,body background-color to #0a0a0a.
#   - tsconfig.app.json strict is true, jsx is 'react-jsx', moduleResolution is 'bundler'.
#   - tsconfig.app.json compilerOptions.paths contains '@/*' → ['src/*'] and vite.config.ts resolve.alias contains '@' → 'src/'.
#   - tsconfig.app.json compilerOptions.types includes 'vitest/globals'.
#   - package.json type is 'module' and private is true.
#   - package.json scripts.build uses 'tsc -b && vite build' to type-check before building.
#   - postcss.config.js plugins include tailwindcss and autoprefixer in that order.
#   - index.html contains preconnect links for https://fonts.googleapis.com and https://fonts.gstatic.com (crossorigin).
#   - src/main.tsx uses React 18 createRoot API targeting document.getElementById('root'). ConvexProvider wrapping is deferred to app_shell component.
#   - .env.example contains VITE_CONVEX_URL as the sole documented environment variable.
#   - No canonical domain types (ToolSlug, ToolDef, Comment, etc.) are defined in this component — those are owned by data_layer.

class ViteServerConfig:
    """Shape of the Vite dev server configuration block in vite.config.ts."""
    port: int                                # required, range(value == 4000), Dev server listen port. Must be 4000.
    strictPort: bool                         # required, custom(value == true), If true, Vite exits with error when port is already in use rather than trying the next available port.
    open: bool = false                       # optional, Whether to open the browser on dev server start.

class ViteBuildConfig:
    """Shape of the Vite build configuration block."""
    outDir: str                              # required, custom(value == 'dist'), Build output directory relative to project root.
    sourcemap: bool = true                   # optional, Whether to emit source maps in production build.

class ViteResolveAlias:
    """A single path alias entry in resolve.alias."""
    find: str                                # required, custom(value == '@'), Alias pattern to match in imports.
    replacement: FilePath                    # required, regex(.*src\/?$), Absolute or relative path the alias resolves to.

class VitestConfig:
    """Shape of the vitest configuration block embedded in vite.config.ts or vitest.config.ts."""
    environment: str                         # required, custom(value == 'jsdom'), Test environment. Must be jsdom for React component testing.
    globals: bool                            # required, custom(value == true), If true, vitest globals (describe, it, expect) are injected without imports.
    include: list                            # required, Glob patterns for test file discovery.
    setupFiles: list = None                  # optional, Optional setup files run before each test suite.

class ViteUserConfig:
    """Top-level Vite UserConfig shape exported from vite.config.ts. Includes plugins array, server, build, resolve, and test blocks."""
    plugins: list                            # required, Vite plugins array. Must include react() at minimum.
    server: ViteServerConfig                 # required, Dev server configuration.
    build: ViteBuildConfig                   # required, Build configuration.
    resolve: ViteResolveConfig               # required, Module resolution configuration including aliases.
    test: VitestConfig                       # required, Vitest test runner configuration.

class ViteResolveConfig:
    """Vite resolve block containing alias definitions."""
    alias: list                              # required, Array of path alias mappings.

class TailwindFontFamily:
    """Font family token definitions in theme.extend.fontFamily."""
    serif: list                              # required, custom(value[0] == 'Instrument Serif'), Serif font stack. Primary: Instrument Serif.
    mono: list                               # required, custom(value[0] == 'JetBrains Mono'), Monospace font stack. Primary: JetBrains Mono.
    sans: list                               # required, custom(value[0] == 'Inter'), Sans-serif font stack. Primary: Inter.

class TailwindColorToken:
    """A single named color token in theme.extend.colors."""
    name: str                                # required, Token name used as Tailwind class suffix, e.g. 'surface'.
    value: HexColor                          # required, CSS hex color value.

HexColor = primitive  # CSS hex color string (e.g. '#00e5ff') used for per-tool accent theming.

TailwindContentGlob = primitive  # A glob pattern string for Tailwind's content purge configuration.

class TailwindConfig:
    """Shape of tailwind.config.js export."""
    content: list                            # required, Content glob patterns for class purging. Must cover ./src/**/*.{ts,tsx,js,jsx} and ./index.html.
    darkMode: str = class                    # optional, Dark mode strategy.
    fontFamily: TailwindFontFamily           # required, Font family tokens in theme.extend.
    colors: list                             # required, Custom color tokens in theme.extend.colors.
    bgGridPluginRegistered: bool             # required, custom(value == true), Whether the plugin registering .bg-grid utility via addUtilities is present.

FilePath = primitive  # A filesystem path string relative to the project root or absolute.

class GoogleFontLink:
    """Descriptor for a Google Fonts <link> tag to be placed in index.html."""
    href: str                                # required, regex(^https://fonts\.googleapis\.com/css2\?family=.+&display=swap$), Full Google Fonts CSS2 URL including family and display=swap parameters.
    preconnect_origins: list                 # required, Origins requiring preconnect hints. Must include 'https://fonts.googleapis.com' and 'https://fonts.gstatic.com'.

class IndexHtmlSpec:
    """Structural specification for index.html."""
    lang: str                                # required, HTML lang attribute.
    preconnectOrigins: list                  # required, Origins for <link rel='preconnect'>. Must include fonts.googleapis.com and fonts.gstatic.com.
    fontLinks: list                          # required, Google Fonts stylesheet links. One per font family.
    rootDivId: str                           # required, custom(value == 'root'), ID of the root mount div.
    moduleScriptSrc: str                     # required, custom(value == '/src/main.tsx'), Path to the main TSX entry point loaded as type=module.

class CssDirective(Enum):
    """Tailwind CSS directives required in src/index.css."""
    @tailwind base = "@tailwind base"
    @tailwind components = "@tailwind components"
    @tailwind utilities = "@tailwind utilities"

class IndexCssSpec:
    """Specification for src/index.css content."""
    tailwindDirectives: list                 # required, Tailwind directives in order.
    baseLayerBackgroundColor: HexColor       # required, custom(value == '#0a0a0a'), Background color applied to html,body in @layer base. Must be #0a0a0a.
    baseLayerTextColor: HexColor             # required, Default text color applied in @layer base for dark-on-dark readability.
    fontFamilyBody: str                      # required, regex(^'Inter'), CSS font-family value assigned to body.
    bgGridDefined: bool                      # required, custom(value == true), Whether the .bg-grid utility is defined (either here via @layer utilities or in the Tailwind plugin). At least one location must define it.

class PackageJsonScripts:
    """Required scripts in package.json."""
    dev: str                                 # required, custom(value == 'vite'), Start dev server.
    build: str                               # required, regex(^tsc.*&&\s*vite build$), Type-check then build.
    test: str                                # required, custom(value == 'vitest'), Run vitest.
    preview: str                             # required, custom(value == 'vite preview'), Preview production build.

SemVerRange = primitive  # A semver range string for package.json dependency pinning.

class PackageJsonDependencies:
    """Required dependencies with version ranges in package.json."""
    react: str                               # required, regex(^\^?18\.), React 18.x.
    react_dom: str                           # required, regex(^\^?18\.), React DOM 18.x, must match react version.
    react_router_dom: str                    # required, regex(^\^?6\.), React Router v6.x.
    convex: str                              # required, Convex npm package.
    tailwindcss: str                         # required, regex(^\^?3\.), Tailwind CSS v3.x.

class PackageJsonDevDependencies:
    """Required devDependencies."""
    vite: str                                # required, Vite bundler.
    vitejs_plugin_react: str                 # required, @vitejs/plugin-react.
    typescript: str                          # required, TypeScript compiler.
    vitest: str                              # required, Vitest test runner.
    jsdom: str                               # required, jsdom for vitest DOM environment.
    autoprefixer: str                        # required, Autoprefixer PostCSS plugin.
    postcss: str                             # required, PostCSS processor.
    types_react: str                         # required, @types/react.
    types_react_dom: str                     # required, @types/react-dom.

class PackageJsonSpec:
    """Full package.json specification."""
    name: str                                # required, Package name.
    private: bool                            # required, custom(value == true), Must be true to prevent accidental publish.
    type: str                                # required, custom(value == 'module'), Module type.
    scripts: PackageJsonScripts              # required, NPM scripts.
    dependencies: PackageJsonDependencies    # required, Runtime dependencies.
    devDependencies: PackageJsonDevDependencies # required, Development dependencies.

class TsConfigCompilerOptions:
    """Key compiler options enforced in tsconfig.json / tsconfig.app.json."""
    strict: bool                             # required, custom(value == true)
    jsx: str                                 # required, custom(value == 'react-jsx')
    moduleResolution: str                    # required, custom(value == 'bundler')
    target: str                              # required, regex(^ES20(2[2-9]|[3-9]\d)$), ECMAScript target.
    module: str                              # required, custom(value == 'ESNext')
    baseUrl: str                             # required, custom(value == '.')
    paths: dict                              # required, Path alias map. Must contain '@/*' → ['src/*'].
    types: list                              # required, Type roots. Must include 'vitest/globals' for global test API.
    skipLibCheck: bool                       # required, Skip type checking of declaration files for build speed.
    noUnusedLocals: bool = true              # optional, Error on unused local variables.
    noUnusedParameters: bool = true          # optional, Error on unused function parameters.
    noFallthroughCasesInSwitch: bool = true  # optional, Error on fallthrough cases in switch statements.

class TsConfigSpec:
    """Combined tsconfig.json + tsconfig.app.json specification."""
    compilerOptions: TsConfigCompilerOptions # required
    include: list                            # required, Source file include globs.
    exclude: list = None                     # optional, Excluded directories.

class PostCssConfig:
    """Shape of postcss.config.js export."""
    plugins: list                            # required, custom('tailwindcss' in value and 'autoprefixer' in value), PostCSS plugins. Must include tailwindcss and autoprefixer.

class EnvExampleSpec:
    """Shape of .env.example documenting required environment variables."""
    VITE_CONVEX_URL: str                     # required, length(1..512), Placeholder for Convex deployment URL. Value is a comment/placeholder, actual URL injected at runtime.

class NpmrcSpec:
    """Shape of .npmrc enforcing bun-only package management."""
    engine_strict: bool                      # required, custom(value == true), Enforce engine requirements.

class ScaffoldManifest:
    """Complete manifest of all files owned and generated by project_scaffold. Used as the return type of generate_scaffold to allow downstream verification."""
    viteConfig: ViteUserConfig               # required
    tailwindConfig: TailwindConfig           # required
    postcssConfig: PostCssConfig             # required
    indexHtml: IndexHtmlSpec                 # required
    indexCss: IndexCssSpec                   # required
    packageJson: PackageJsonSpec             # required
    tsConfig: TsConfigSpec                   # required
    envExample: EnvExampleSpec               # required
    npmrc: NpmrcSpec                         # required
    convexDirCreated: bool                   # required, custom(value == true), Whether the empty convex/ directory (with .gitkeep) was created.
    lockfileIsBunOnly: bool                  # required, custom(value == true), Confirms bun.lockb is the only lockfile (no package-lock.json, yarn.lock, pnpm-lock.yaml).

class ScaffoldValidationResult:
    """Result of validate_scaffold containing pass/fail status and any violations."""
    valid: bool                              # required, True if all validations passed.
    violations: list                         # required, List of human-readable violation descriptions. Empty if valid.
    checkedFiles: list                       # required, List of file paths that were checked.

class BgGridSpec:
    """Specification for the .bg-grid Tailwind utility class."""
    className: str                           # required, custom(value == '.bg-grid'), The utility class name.
    backgroundImage: str                     # required, CSS background-image value producing the subtle grid pattern. Typically a linear-gradient or repeating-linear-gradient.
    backgroundSize: str                      # required, CSS background-size controlling grid cell dimensions.

def generate_scaffold(
    projectDir: FilePath,
    projectName: str,          # regex(^[a-z0-9][a-z0-9._-]*$)
    convexUrl: str = None,
) -> ScaffoldManifest:
    """
    Initialize the complete project scaffold from scratch. Runs bun create vite to bootstrap the project, then writes/overwrites all 12 owned configuration and entry-point files to match the contract specification. Installs dependencies via bun install. Creates the empty convex/ directory with .gitkeep. Removes any non-bun lockfiles (package-lock.json, yarn.lock, pnpm-lock.yaml) if present. Returns a ScaffoldManifest describing every generated artifact for downstream verification.

    Preconditions:
      - projectDir exists and is a writable directory.
      - bun >= 1.0.0 is installed and on PATH.
      - Network access is available for bun create vite and bun install to fetch packages.

    Postconditions:
      - All 12 owned files exist at their specified paths relative to projectDir.
      - bun.lockb exists and is the sole lockfile (no package-lock.json, yarn.lock, pnpm-lock.yaml).
      - node_modules/ directory exists with all dependencies installed.
      - convex/ directory exists containing .gitkeep.
      - vite.config.ts exports a config with server.port=4000, server.strictPort=true, build.outDir='dist'.
      - tailwind.config.js registers the bg-grid utility plugin and defines fontFamily tokens for serif, mono, sans.
      - postcss.config.js includes tailwindcss and autoprefixer plugins.
      - index.html contains preconnect links for fonts.googleapis.com and fonts.gstatic.com, stylesheet links for Instrument Serif, JetBrains Mono, and Inter with display=swap, a div#root, and a module script src='/src/main.tsx'.
      - src/index.css contains @tailwind base/components/utilities directives, @layer base with background-color #0a0a0a, and the bg-grid utility definition.
      - src/main.tsx contains React 18 createRoot rendering to document.getElementById('root').
      - package.json has scripts dev='vite', build='tsc -b && vite build', test='vitest', preview='vite preview'.
      - tsconfig.app.json has strict=true, jsx='react-jsx', moduleResolution='bundler', paths '@/*'→'src/*', types includes 'vitest/globals'.

    Errors:
      - directory_not_found (FileNotFoundError): projectDir does not exist on the filesystem.
          path: The projectDir value that was not found.
      - directory_not_writable (PermissionError): projectDir exists but the process lacks write permissions.
          path: The projectDir value.
      - bun_not_installed (EnvironmentError): bun executable is not found on PATH.
          detail: bun not found on PATH. Install bun: https://bun.sh
      - bun_create_failed (SubprocessError): bun create vite exits with non-zero status.
          command: bun create vite
          exitCode: non-zero exit code
          stderr: stderr output
      - bun_install_failed (SubprocessError): bun install exits with non-zero status after scaffold generation.
          command: bun install
          exitCode: non-zero exit code
          stderr: stderr output
      - conflicting_lockfile (PermissionError): A non-bun lockfile exists and cannot be removed (e.g. permission denied).
          path: Path to the conflicting lockfile.

    Side effects: Writes 12 configuration/entry-point files to projectDir., Runs bun create vite as a subprocess., Runs bun install as a subprocess., Creates node_modules/ directory., Creates convex/ directory with .gitkeep., May delete conflicting lockfiles (package-lock.json, yarn.lock, pnpm-lock.yaml).
    Idempotent: yes
    """
    ...

def validate_scaffold(
    projectDir: FilePath,
) -> ScaffoldValidationResult:
    """
    Validate an existing project directory against the scaffold contract. Checks that all 12 owned files exist with correct structure, content, and configuration values. Verifies no conflicting lockfiles are present. Does NOT modify any files. Returns a ScaffoldValidationResult with pass/fail and detailed violation messages.

    Preconditions:
      - projectDir exists and is a readable directory.

    Postconditions:
      - No files are modified, created, or deleted.
      - result.valid == true implies result.violations is empty.
      - result.valid == false implies result.violations is non-empty.
      - result.checkedFiles contains the path of every file that was inspected.

    Errors:
      - directory_not_found (FileNotFoundError): projectDir does not exist on the filesystem.
          path: The projectDir value that was not found.
      - directory_not_readable (PermissionError): projectDir exists but the process lacks read permissions.
          path: The projectDir value.

    Side effects: none
    Idempotent: yes
    """
    ...

def get_tailwind_theme_tokens(
    projectDir: FilePath,
) -> TailwindConfig:
    """
    Extract the Tailwind theme extension tokens (font families, colors, utility class names) from the scaffold configuration. Downstream components use this to reference shared design tokens without hardcoding values. Pure function that reads from the canonical TailwindConfig specification.

    Preconditions:
      - projectDir exists and contains a tailwind.config.js generated by generate_scaffold.

    Postconditions:
      - Returned TailwindConfig matches the canonical specification.
      - fontFamily.serif[0] == 'Instrument Serif'.
      - fontFamily.mono[0] == 'JetBrains Mono'.
      - fontFamily.sans[0] == 'Inter'.
      - bgGridPluginRegistered == true.

    Errors:
      - config_not_found (FileNotFoundError): tailwind.config.js does not exist at projectDir.
          path: Expected path to tailwind.config.js.
      - config_parse_error (ParseError): tailwind.config.js exists but cannot be parsed.
          detail: Description of the parse failure.

    Side effects: none
    Idempotent: yes
    """
    ...

def get_path_aliases(
    projectDir: FilePath,
) -> dict:
    """
    Extract TypeScript path alias mappings from tsconfig. Downstream components use this to verify their imports resolve correctly via the '@/' alias. Pure read-only function.

    Preconditions:
      - projectDir exists and contains tsconfig.app.json generated by generate_scaffold.

    Postconditions:
      - Returned dict contains key '@/*' mapping to ['src/*'].
      - All alias keys start with '@'.

    Errors:
      - config_not_found (FileNotFoundError): tsconfig.app.json does not exist at projectDir.
          path: Expected path to tsconfig.app.json.
      - config_parse_error (ParseError): tsconfig.app.json exists but cannot be parsed.
          detail: Description of the parse failure.

    Side effects: none
    Idempotent: yes
    """
    ...

def get_vite_config(
    projectDir: FilePath,
) -> ViteUserConfig:
    """
    Parse and return the full ViteUserConfig from the project's vite.config.ts. Used by downstream components to verify dev server port, build output, resolve aliases, and test configuration.

    Preconditions:
      - projectDir exists and contains vite.config.ts generated by generate_scaffold.

    Postconditions:
      - Returned ViteUserConfig has server.port == 4000.
      - Returned ViteUserConfig has server.strictPort == true.
      - Returned ViteUserConfig has build.outDir == 'dist'.
      - Returned ViteUserConfig has test.environment == 'jsdom'.
      - Returned ViteUserConfig has test.globals == true.

    Errors:
      - config_not_found (FileNotFoundError): vite.config.ts does not exist at projectDir.
          path: Expected path to vite.config.ts.
      - config_parse_error (ParseError): vite.config.ts exists but cannot be parsed.
          detail: Description of the parse failure.

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['ViteServerConfig', 'ViteBuildConfig', 'ViteResolveAlias', 'VitestConfig', 'ViteUserConfig', 'ViteResolveConfig', 'TailwindFontFamily', 'TailwindColorToken', 'TailwindConfig', 'GoogleFontLink', 'IndexHtmlSpec', 'CssDirective', 'IndexCssSpec', 'PackageJsonScripts', 'PackageJsonDependencies', 'PackageJsonDevDependencies', 'PackageJsonSpec', 'TsConfigCompilerOptions', 'TsConfigSpec', 'PostCssConfig', 'EnvExampleSpec', 'NpmrcSpec', 'ScaffoldManifest', 'ScaffoldValidationResult', 'BgGridSpec', 'generate_scaffold', 'EnvironmentError', 'SubprocessError', 'validate_scaffold', 'get_tailwind_theme_tokens', 'ParseError', 'get_path_aliases', 'get_vite_config']
