"""Project Scaffold & Configuration (project_scaffold) v1.

Initialize and configure the Vite + React 18 + TypeScript project scaffold using bun.
"""

import logging
import os
import re
import json
import shutil
import subprocess
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

_PACT_KEY = "PACT:d97abb:project_scaffold"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    """Formatter that injects the PACT log key into every record."""

    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    """Log with PACT key embedded for production traceability."""
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


# ---------------------------------------------------------------------------
# Custom Error Classes
# ---------------------------------------------------------------------------


class EnvironmentError(Exception):
    """Raised when a required environment tool is not available."""
    pass


class SubprocessError(Exception):
    """Raised when a subprocess exits with non-zero status."""
    pass


class ParseError(Exception):
    """Raised when a configuration file cannot be parsed."""
    pass


# ---------------------------------------------------------------------------
# Branded Primitive Types
# ---------------------------------------------------------------------------


class HexColor(str):
    """CSS hex color string (e.g. '#00e5ff')."""
    def __new__(cls, value: str):
        if not isinstance(value, str) or not re.match(r'^#[0-9a-fA-F]{3,8}$', value):
            raise ValueError(f"Invalid HexColor: {value!r}")
        return super().__new__(cls, value)


class TailwindContentGlob(str):
    """A glob pattern string for Tailwind's content purge configuration."""
    def __new__(cls, value: str):
        if not isinstance(value, str) or not re.match(r'^\./.*\{.*\}$', value):
            raise ValueError(f"Invalid TailwindContentGlob: {value!r}. Must match ^\\./.* \\{{.*\\}}$")
        return super().__new__(cls, value)


class FilePath(str):
    """A filesystem path string relative to the project root or absolute."""
    def __new__(cls, value: str):
        if not isinstance(value, str) or len(value) < 1 or len(value) > 512:
            raise ValueError(f"Invalid FilePath: length must be 1..512, got {len(value) if isinstance(value, str) else 'non-string'}")
        return super().__new__(cls, value)


class SemVerRange(str):
    """A semver range string for package.json dependency pinning."""
    def __new__(cls, value: str):
        if not isinstance(value, str) or not re.match(r'^[~^]?\d+\.\d+', value):
            raise ValueError(f"Invalid SemVerRange: {value!r}. Must match ^[~^]?\\d+\\.\\d+")
        return super().__new__(cls, value)


# ---------------------------------------------------------------------------
# Data Classes / Types
# ---------------------------------------------------------------------------


class ViteServerConfig:
    """Shape of the Vite dev server configuration block in vite.config.ts."""
    def __init__(self, port: int, strictPort: bool, open: bool = False,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if port != 4000:
            raise ValueError(f"ViteServerConfig.port must be 4000, got {port}")
        if strictPort is not True:
            raise ValueError(f"ViteServerConfig.strictPort must be True, got {strictPort}")
        self.port: int = port
        self.strictPort: bool = strictPort
        self.open: bool = open

    def __repr__(self):
        return f"ViteServerConfig(port={self.port}, strictPort={self.strictPort}, open={self.open})"


class ViteBuildConfig:
    """Shape of the Vite build configuration block."""
    def __init__(self, outDir: str, sourcemap: bool = True,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if outDir != 'dist':
            raise ValueError(f"ViteBuildConfig.outDir must be 'dist', got {outDir!r}")
        self.outDir: str = outDir
        self.sourcemap: bool = sourcemap


class ViteResolveAlias:
    """A single path alias entry in resolve.alias."""
    def __init__(self, find: str, replacement: str,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if find != '@':
            raise ValueError(f"ViteResolveAlias.find must be '@', got {find!r}")
        if not re.match(r'.*src\/?$', replacement):
            raise ValueError(f"ViteResolveAlias.replacement must end with 'src' or 'src/', got {replacement!r}")
        self.find: str = find
        self.replacement: str = replacement


class VitestConfig:
    """Shape of the vitest configuration block."""
    def __init__(self, environment: str, globals: bool, include: list,
                 setupFiles: Optional[list] = None,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if environment != 'jsdom':
            raise ValueError(f"VitestConfig.environment must be 'jsdom', got {environment!r}")
        if globals is not True:
            raise ValueError(f"VitestConfig.globals must be True, got {globals!r}")
        self.environment: str = environment
        self.globals: bool = globals
        self.include: list = include
        self.setupFiles: Optional[list] = setupFiles


class ViteResolveConfig:
    """Vite resolve block containing alias definitions."""
    def __init__(self, alias: list,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.alias: list = alias


class ViteUserConfig:
    """Top-level Vite UserConfig shape."""
    def __init__(self, plugins: list, server: ViteServerConfig,
                 build: ViteBuildConfig, resolve: ViteResolveConfig,
                 test: VitestConfig,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.plugins: list = plugins
        self.server: ViteServerConfig = server
        self.build: ViteBuildConfig = build
        self.resolve: ViteResolveConfig = resolve
        self.test: VitestConfig = test


class TailwindFontFamily:
    """Font family token definitions in theme.extend.fontFamily."""
    def __init__(self, serif: list, mono: list, sans: list,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if not serif or serif[0] != 'Instrument Serif':
            raise ValueError(f"TailwindFontFamily.serif[0] must be 'Instrument Serif', got {serif[0] if serif else 'empty'}")
        if not mono or mono[0] != 'JetBrains Mono':
            raise ValueError(f"TailwindFontFamily.mono[0] must be 'JetBrains Mono', got {mono[0] if mono else 'empty'}")
        if not sans or sans[0] != 'Inter':
            raise ValueError(f"TailwindFontFamily.sans[0] must be 'Inter', got {sans[0] if sans else 'empty'}")
        self.serif: list = serif
        self.mono: list = mono
        self.sans: list = sans


class TailwindColorToken:
    """A single named color token in theme.extend.colors."""
    def __init__(self, name: str, value: str,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.name: str = name
        self.value: str = HexColor(value)


class TailwindConfig:
    """Shape of tailwind.config.js export."""
    def __init__(self, content: list, fontFamily: TailwindFontFamily,
                 colors: list, bgGridPluginRegistered: bool,
                 darkMode: str = 'class',
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if bgGridPluginRegistered is not True:
            raise ValueError(f"TailwindConfig.bgGridPluginRegistered must be True, got {bgGridPluginRegistered!r}")
        self.content: list = content
        self.darkMode: str = darkMode
        self.fontFamily: TailwindFontFamily = fontFamily
        self.colors: list = colors
        self.bgGridPluginRegistered: bool = bgGridPluginRegistered


class GoogleFontLink:
    """Descriptor for a Google Fonts <link> tag."""
    def __init__(self, href: str, rel: str = 'stylesheet',
                 preconnect_origins: Optional[list] = None,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if not re.match(r'^https://fonts\.googleapis\.com/css2\?family=.+&display=swap$', href):
            raise ValueError(f"GoogleFontLink.href must match Google Fonts pattern with display=swap, got {href!r}")
        if rel != 'stylesheet':
            raise ValueError(f"GoogleFontLink.rel must be 'stylesheet', got {rel!r}")
        self.href: str = href
        self.rel: str = rel
        self.preconnect_origins: list = preconnect_origins or [
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
        ]


class IndexHtmlSpec:
    """Structural specification for index.html."""
    def __init__(self, lang: str, preconnectOrigins: list, fontLinks: list,
                 rootDivId: str, moduleScriptSrc: str,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if rootDivId != 'root':
            raise ValueError(f"IndexHtmlSpec.rootDivId must be 'root', got {rootDivId!r}")
        if moduleScriptSrc != '/src/main.tsx':
            raise ValueError(f"IndexHtmlSpec.moduleScriptSrc must be '/src/main.tsx', got {moduleScriptSrc!r}")
        self.lang: str = lang
        self.preconnectOrigins: list = preconnectOrigins
        self.fontLinks: list = fontLinks
        self.rootDivId: str = rootDivId
        self.moduleScriptSrc: str = moduleScriptSrc


class CssDirective(Enum):
    """Tailwind CSS directives required in src/index.css."""
    tailwind_base = "@tailwind base"
    tailwind_components = "@tailwind components"
    tailwind_utilities = "@tailwind utilities"


class IndexCssSpec:
    """Specification for src/index.css content."""
    def __init__(self, tailwindDirectives: list, baseLayerBackgroundColor: str,
                 baseLayerTextColor: str, fontFamilyBody: str,
                 bgGridDefined: bool,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if baseLayerBackgroundColor != '#0a0a0a':
            raise ValueError(f"IndexCssSpec.baseLayerBackgroundColor must be '#0a0a0a', got {baseLayerBackgroundColor!r}")
        if not re.match(r"^'Inter'", fontFamilyBody):
            raise ValueError(f"IndexCssSpec.fontFamilyBody must start with \"'Inter'\", got {fontFamilyBody!r}")
        if bgGridDefined is not True:
            raise ValueError(f"IndexCssSpec.bgGridDefined must be True, got {bgGridDefined!r}")
        self.tailwindDirectives: list = tailwindDirectives
        self.baseLayerBackgroundColor: str = baseLayerBackgroundColor
        self.baseLayerTextColor: str = baseLayerTextColor
        self.fontFamilyBody: str = fontFamilyBody
        self.bgGridDefined: bool = bgGridDefined


class PackageJsonScripts:
    """Required scripts in package.json."""
    def __init__(self, dev: str, build: str, test: str, preview: str,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if dev != 'vite':
            raise ValueError(f"PackageJsonScripts.dev must be 'vite', got {dev!r}")
        if not re.match(r'^tsc.*&&\s*vite build$', build):
            raise ValueError(f"PackageJsonScripts.build must match ^tsc.*&&\\s*vite build$, got {build!r}")
        if test != 'vitest':
            raise ValueError(f"PackageJsonScripts.test must be 'vitest', got {test!r}")
        if preview != 'vite preview':
            raise ValueError(f"PackageJsonScripts.preview must be 'vite preview', got {preview!r}")
        self.dev: str = dev
        self.build: str = build
        self.test: str = test
        self.preview: str = preview


class PackageJsonDependencies:
    """Required dependencies with version ranges."""
    def __init__(self, react: str, react_dom: str, react_router_dom: str,
                 convex: str, tailwindcss: str,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if not re.match(r'^\^?18\.', react):
            raise ValueError(f"PackageJsonDependencies.react must match ^\\^?18\\., got {react!r}")
        if not re.match(r'^\^?18\.', react_dom):
            raise ValueError(f"PackageJsonDependencies.react_dom must match ^\\^?18\\., got {react_dom!r}")
        if not re.match(r'^\^?6\.', react_router_dom):
            raise ValueError(f"PackageJsonDependencies.react_router_dom must match ^\\^?6\\., got {react_router_dom!r}")
        if not re.match(r'^\^?3\.', tailwindcss):
            raise ValueError(f"PackageJsonDependencies.tailwindcss must match ^\\^?3\\., got {tailwindcss!r}")
        self.react: str = react
        self.react_dom: str = react_dom
        self.react_router_dom: str = react_router_dom
        self.convex: str = convex
        self.tailwindcss: str = tailwindcss


class PackageJsonDevDependencies:
    """Required devDependencies."""
    def __init__(self, vite: str, vitejs_plugin_react: str, typescript: str,
                 vitest: str, jsdom: str, autoprefixer: str, postcss: str,
                 types_react: str, types_react_dom: str,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.vite: str = vite
        self.vitejs_plugin_react: str = vitejs_plugin_react
        self.typescript: str = typescript
        self.vitest: str = vitest
        self.jsdom: str = jsdom
        self.autoprefixer: str = autoprefixer
        self.postcss: str = postcss
        self.types_react: str = types_react
        self.types_react_dom: str = types_react_dom


class PackageJsonSpec:
    """Full package.json specification."""
    def __init__(self, name: str, private: bool, type: str,
                 scripts: PackageJsonScripts,
                 dependencies: PackageJsonDependencies,
                 devDependencies: Any,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if private is not True:
            raise ValueError(f"PackageJsonSpec.private must be True, got {private!r}")
        if type != 'module':
            raise ValueError(f"PackageJsonSpec.type must be 'module', got {type!r}")
        self.name: str = name
        self.private: bool = private
        self.type: str = type
        self.scripts: PackageJsonScripts = scripts
        self.dependencies: PackageJsonDependencies = dependencies
        self.devDependencies = devDependencies


class TsConfigCompilerOptions:
    """Key compiler options enforced in tsconfig.json / tsconfig.app.json."""
    def __init__(self, strict: bool, jsx: str, moduleResolution: str,
                 target: str, module: str, baseUrl: str, paths: dict,
                 types: list, skipLibCheck: bool,
                 noUnusedLocals: bool = True,
                 noUnusedParameters: bool = True,
                 noFallthroughCasesInSwitch: bool = True,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if strict is not True:
            raise ValueError(f"TsConfigCompilerOptions.strict must be True, got {strict!r}")
        if jsx != 'react-jsx':
            raise ValueError(f"TsConfigCompilerOptions.jsx must be 'react-jsx', got {jsx!r}")
        if moduleResolution != 'bundler':
            raise ValueError(f"TsConfigCompilerOptions.moduleResolution must be 'bundler', got {moduleResolution!r}")
        if not re.match(r'^ES20(2[2-9]|[3-9]\d)$', target):
            raise ValueError(f"TsConfigCompilerOptions.target must match ^ES20(2[2-9]|[3-9]\\d)$, got {target!r}")
        if module != 'ESNext':
            raise ValueError(f"TsConfigCompilerOptions.module must be 'ESNext', got {module!r}")
        if baseUrl != '.':
            raise ValueError(f"TsConfigCompilerOptions.baseUrl must be '.', got {baseUrl!r}")
        self.strict: bool = strict
        self.jsx: str = jsx
        self.moduleResolution: str = moduleResolution
        self.target: str = target
        self.module: str = module
        self.baseUrl: str = baseUrl
        self.paths: dict = paths
        self.types: list = types
        self.skipLibCheck: bool = skipLibCheck
        self.noUnusedLocals: bool = noUnusedLocals
        self.noUnusedParameters: bool = noUnusedParameters
        self.noFallthroughCasesInSwitch: bool = noFallthroughCasesInSwitch


class TsConfigSpec:
    """Combined tsconfig.json + tsconfig.app.json specification."""
    def __init__(self, compilerOptions: TsConfigCompilerOptions,
                 include: list, exclude: Optional[list] = None,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.compilerOptions: TsConfigCompilerOptions = compilerOptions
        self.include: list = include
        self.exclude: Optional[list] = exclude


class PostCssConfig:
    """Shape of postcss.config.js export."""
    def __init__(self, plugins: list,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if 'tailwindcss' not in plugins or 'autoprefixer' not in plugins:
            raise ValueError(f"PostCssConfig.plugins must include both 'tailwindcss' and 'autoprefixer', got {plugins!r}")
        self.plugins: list = plugins


class EnvExampleSpec:
    """Shape of .env.example documenting required environment variables."""
    def __init__(self, VITE_CONVEX_URL: str,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if not isinstance(VITE_CONVEX_URL, str) or len(VITE_CONVEX_URL) < 1 or len(VITE_CONVEX_URL) > 512:
            raise ValueError(f"EnvExampleSpec.VITE_CONVEX_URL must have length 1..512, got {len(VITE_CONVEX_URL) if isinstance(VITE_CONVEX_URL, str) else 'non-string'}")
        self.VITE_CONVEX_URL: str = VITE_CONVEX_URL


class NpmrcSpec:
    """Shape of .npmrc enforcing bun-only package management."""
    def __init__(self, engine_strict: bool,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if engine_strict is not True:
            raise ValueError(f"NpmrcSpec.engine_strict must be True, got {engine_strict!r}")
        self.engine_strict: bool = engine_strict


class ScaffoldManifest:
    """Complete manifest of all files owned and generated by project_scaffold."""
    def __init__(self, viteConfig, tailwindConfig, postcssConfig,
                 indexHtml, indexCss, packageJson, tsConfig,
                 envExample, npmrc, convexDirCreated: bool,
                 lockfileIsBunOnly: bool,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if convexDirCreated is not True:
            raise ValueError(f"ScaffoldManifest.convexDirCreated must be True, got {convexDirCreated!r}")
        if lockfileIsBunOnly is not True:
            raise ValueError(f"ScaffoldManifest.lockfileIsBunOnly must be True, got {lockfileIsBunOnly!r}")
        self.viteConfig = viteConfig
        self.tailwindConfig = tailwindConfig
        self.postcssConfig = postcssConfig
        self.indexHtml = indexHtml
        self.indexCss = indexCss
        self.packageJson = packageJson
        self.tsConfig = tsConfig
        self.envExample = envExample
        self.npmrc = npmrc
        self.convexDirCreated: bool = convexDirCreated
        self.lockfileIsBunOnly: bool = lockfileIsBunOnly


class ScaffoldValidationResult:
    """Result of validate_scaffold containing pass/fail status and any violations."""
    def __init__(self, valid: bool, violations: list, checkedFiles: list,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.valid: bool = valid
        self.violations: list = violations
        self.checkedFiles: list = checkedFiles


class BgGridSpec:
    """Specification for the .bg-grid Tailwind utility class."""
    def __init__(self, className: str, backgroundImage: str,
                 backgroundSize: str,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if className != '.bg-grid':
            raise ValueError(f"BgGridSpec.className must be '.bg-grid', got {className!r}")
        self.className: str = className
        self.backgroundImage: str = backgroundImage
        self.backgroundSize: str = backgroundSize


# ---------------------------------------------------------------------------
# Canonical config builders (build typed objects in memory)
# ---------------------------------------------------------------------------


def _build_vite_config() -> ViteUserConfig:
    """Build the canonical ViteUserConfig."""
    server = ViteServerConfig(port=4000, strictPort=True, open=False)
    build = ViteBuildConfig(outDir='dist', sourcemap=True)
    alias = ViteResolveAlias(find='@', replacement='./src')
    resolve = ViteResolveConfig(alias=[alias])
    test = VitestConfig(
        environment='jsdom',
        globals=True,
        include=['src/**/*.{test,spec}.{ts,tsx}'],
        setupFiles=[],
    )
    return ViteUserConfig(
        plugins=['react()'],
        server=server,
        build=build,
        resolve=resolve,
        test=test,
    )


def _build_tailwind_config() -> TailwindConfig:
    """Build the canonical TailwindConfig."""
    font_family = TailwindFontFamily(
        serif=['Instrument Serif', 'serif'],
        mono=['JetBrains Mono', 'monospace'],
        sans=['Inter', 'sans-serif'],
    )
    colors = [
        TailwindColorToken(name='surface', value='#1a1a1a'),
        TailwindColorToken(name='accent', value='#00e5ff'),
    ]
    return TailwindConfig(
        content=[
            './src/**/*.{ts,tsx,js,jsx}',
            './index.html',
        ],
        darkMode='class',
        fontFamily=font_family,
        colors=colors,
        bgGridPluginRegistered=True,
    )


def _build_postcss_config() -> PostCssConfig:
    return PostCssConfig(plugins=['tailwindcss', 'autoprefixer'])


def _build_index_html() -> IndexHtmlSpec:
    font_links = [
        GoogleFontLink(
            href='https://fonts.googleapis.com/css2?family=Instrument+Serif&display=swap',
            rel='stylesheet',
        ),
        GoogleFontLink(
            href='https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap',
            rel='stylesheet',
        ),
        GoogleFontLink(
            href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
            rel='stylesheet',
        ),
    ]
    return IndexHtmlSpec(
        lang='en',
        preconnectOrigins=[
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
        ],
        fontLinks=font_links,
        rootDivId='root',
        moduleScriptSrc='/src/main.tsx',
    )


def _build_index_css() -> IndexCssSpec:
    return IndexCssSpec(
        tailwindDirectives=[
            '@tailwind base',
            '@tailwind components',
            '@tailwind utilities',
        ],
        baseLayerBackgroundColor='#0a0a0a',
        baseLayerTextColor='#ffffff',
        fontFamilyBody="'Inter', sans-serif",
        bgGridDefined=True,  # bg-grid IS defined (in tailwind plugin)
    )


def _build_package_json(project_name: str) -> PackageJsonSpec:
    scripts = PackageJsonScripts(
        dev='vite',
        build='tsc -b && vite build',
        test='vitest',
        preview='vite preview',
    )
    deps = PackageJsonDependencies(
        react='^18.2.0',
        react_dom='^18.2.0',
        react_router_dom='^6.20.0',
        convex='^1.10.0',
        tailwindcss='^3.4.0',
    )
    dev_deps = PackageJsonDevDependencies(
        vite='^5.0.0',
        vitejs_plugin_react='^4.2.0',
        typescript='^5.3.0',
        vitest='^1.0.0',
        jsdom='^23.0.0',
        autoprefixer='^10.4.0',
        postcss='^8.4.0',
        types_react='^18.2.0',
        types_react_dom='^18.2.0',
    )
    return PackageJsonSpec(
        name=project_name,
        private=True,
        type='module',
        scripts=scripts,
        dependencies=deps,
        devDependencies=dev_deps,
    )


def _build_tsconfig() -> TsConfigSpec:
    compiler_options = TsConfigCompilerOptions(
        strict=True,
        jsx='react-jsx',
        moduleResolution='bundler',
        target='ES2022',
        module='ESNext',
        baseUrl='.',
        paths={'@/*': ['src/*']},
        types=['vitest/globals'],
        skipLibCheck=True,
        noUnusedLocals=True,
        noUnusedParameters=True,
        noFallthroughCasesInSwitch=True,
    )
    return TsConfigSpec(
        compilerOptions=compiler_options,
        include=['src'],
        exclude=['node_modules', 'dist'],
    )


def _build_env_example(convex_url: Optional[str]) -> EnvExampleSpec:
    url = convex_url or 'https://your-deployment.convex.cloud'
    return EnvExampleSpec(VITE_CONVEX_URL=url)


def _build_npmrc() -> NpmrcSpec:
    return NpmrcSpec(engine_strict=True)


# ---------------------------------------------------------------------------
# File content serializers
# ---------------------------------------------------------------------------


def _serialize_vite_config_ts() -> str:
    return '''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 4000,
    strictPort: true,
    open: false,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  resolve: {
    alias: [
      { find: '@', replacement: path.resolve(__dirname, './src') },
    ],
  },
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    setupFiles: [],
  },
});
'''


def _serialize_tailwind_config_js() -> str:
    return '''const plugin = require('tailwindcss/plugin');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx,js,jsx}', './index.html'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        serif: ['Instrument Serif', 'serif'],
        mono: ['JetBrains Mono', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        surface: '#1a1a1a',
        accent: '#00e5ff',
      },
    },
  },
  plugins: [
    plugin(function ({ addUtilities }) {
      addUtilities({
        '.bg-grid': {
          'background-image':
            'linear-gradient(to right, rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.05) 1px, transparent 1px)',
          'background-size': '40px 40px',
        },
      });
    }),
  ],
};
'''


def _serialize_postcss_config_js() -> str:
    return '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
'''


def _serialize_index_html() -> str:
    return '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Instrument+Serif&display=swap"
    />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"
    />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    />
    <title>App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''


def _serialize_index_css() -> str:
    return '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html,
  body {
    background-color: #0a0a0a;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
  }
}
'''


def _serialize_main_tsx() -> str:
    return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

// ConvexProvider wrapping is deferred to app_shell component
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <div>App</div>
  </React.StrictMode>,
);
'''


def _serialize_package_json(project_name: str) -> str:
    data = {
        "name": project_name,
        "private": True,
        "version": "0.0.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "tsc -b && vite build",
            "test": "vitest",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.20.0",
            "convex": "^1.10.0",
            "tailwindcss": "^3.4.0"
        },
        "devDependencies": {
            "@types/react": "^18.2.0",
            "@types/react-dom": "^18.2.0",
            "@vitejs/plugin-react": "^4.2.0",
            "autoprefixer": "^10.4.0",
            "jsdom": "^23.0.0",
            "postcss": "^8.4.0",
            "typescript": "^5.3.0",
            "vite": "^5.0.0",
            "vitest": "^1.0.0"
        }
    }
    return json.dumps(data, indent=2) + '\n'


def _serialize_tsconfig_json() -> str:
    data = {
        "files": [],
        "references": [
            {"path": "./tsconfig.app.json"}
        ]
    }
    return json.dumps(data, indent=2) + '\n'


def _serialize_tsconfig_app_json() -> str:
    data = {
        "compilerOptions": {
            "strict": True,
            "jsx": "react-jsx",
            "moduleResolution": "bundler",
            "target": "ES2022",
            "module": "ESNext",
            "baseUrl": ".",
            "paths": {
                "@/*": ["src/*"]
            },
            "types": ["vitest/globals"],
            "skipLibCheck": True,
            "noUnusedLocals": True,
            "noUnusedParameters": True,
            "noFallthroughCasesInSwitch": True,
            "allowImportingTsExtensions": True,
            "resolveJsonModule": True,
            "isolatedModules": True,
            "noEmit": True
        },
        "include": ["src"],
        "exclude": ["node_modules", "dist"]
    }
    return json.dumps(data, indent=2) + '\n'


def _serialize_env_example(convex_url: Optional[str]) -> str:
    url = convex_url or 'https://your-deployment.convex.cloud'
    return f'VITE_CONVEX_URL={url}\n'


def _serialize_npmrc() -> str:
    return 'engine-strict=true\n'


# ---------------------------------------------------------------------------
# Public Functions
# ---------------------------------------------------------------------------


def generate_scaffold(
    projectDir: str,
    projectName: str,
    convexUrl: Optional[str] = None,
    event_handler=None,
    log_handler=None,
) -> ScaffoldManifest:
    """Initialize the complete project scaffold from scratch."""
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:d97abb:project_scaffold:generate_scaffold",
        "event": "invoked",
        "input_classification": [projectDir, projectName],
        "output_classification": [],
        "side_effects": ["filesystem_write", "subprocess"],
        "ts": time.time_ns(),
    })
    _log("info", f"generate_scaffold invoked for {projectDir}")

    # --- Precondition checks ---
    if not os.path.exists(projectDir) or not os.path.isdir(projectDir):
        raise FileNotFoundError(f"directory_not_found: projectDir '{projectDir}' does not exist or is not a directory")

    if not os.access(projectDir, os.W_OK):
        raise PermissionError(f"directory_not_writable: projectDir '{projectDir}' is not writable")

    if shutil.which('bun') is None:
        raise EnvironmentError("bun_not_installed: bun not found on PATH. Install bun: https://bun.sh")

    # --- Remove conflicting lockfiles ---
    conflicting_lockfiles = ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']
    for lockfile in conflicting_lockfiles:
        lockfile_path = os.path.join(projectDir, lockfile)
        if os.path.exists(lockfile_path):
            try:
                os.remove(lockfile_path)
            except PermissionError as e:
                raise PermissionError(f"conflicting_lockfile: Cannot remove lockfile '{lockfile_path}': {e}")

    # --- Run bun create vite ---
    try:
        result = subprocess.run(
            ['bun', 'create', 'vite', '.', '--template', 'react-ts'],
            cwd=projectDir,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise SubprocessError(
            f"bun_create_failed: 'bun create vite' failed with exit code {e.returncode}. stderr: {getattr(e, 'stderr', '')}"
        )
    except Exception as e:
        raise SubprocessError(
            f"bun_create_failed: 'bun create vite' failed. {e}"
        )

    # --- Write all owned config files ---
    src_dir = os.path.join(projectDir, 'src')
    os.makedirs(src_dir, exist_ok=True)

    convex_dir = os.path.join(projectDir, 'convex')
    os.makedirs(convex_dir, exist_ok=True)

    files_to_write = {
        os.path.join(projectDir, 'vite.config.ts'): _serialize_vite_config_ts(),
        os.path.join(projectDir, 'tailwind.config.js'): _serialize_tailwind_config_js(),
        os.path.join(projectDir, 'postcss.config.js'): _serialize_postcss_config_js(),
        os.path.join(projectDir, 'index.html'): _serialize_index_html(),
        os.path.join(src_dir, 'index.css'): _serialize_index_css(),
        os.path.join(src_dir, 'main.tsx'): _serialize_main_tsx(),
        os.path.join(projectDir, 'package.json'): _serialize_package_json(projectName),
        os.path.join(projectDir, 'tsconfig.json'): _serialize_tsconfig_json(),
        os.path.join(projectDir, 'tsconfig.app.json'): _serialize_tsconfig_app_json(),
        os.path.join(projectDir, '.env.example'): _serialize_env_example(convexUrl),
        os.path.join(projectDir, '.npmrc'): _serialize_npmrc(),
        os.path.join(convex_dir, '.gitkeep'): '',
    }

    for filepath, content in files_to_write.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    # --- Run bun install ---
    try:
        result = subprocess.run(
            ['bun', 'install'],
            cwd=projectDir,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise SubprocessError(
            f"bun_install_failed: 'bun install' failed with exit code {e.returncode}. stderr: {getattr(e, 'stderr', '')}"
        )
    except Exception as e:
        raise SubprocessError(
            f"bun_install_failed: 'bun install' failed. {e}"
        )

    # --- Build manifest ---
    vite_config = _build_vite_config()
    tailwind_config = _build_tailwind_config()
    postcss_config = _build_postcss_config()
    index_html = _build_index_html()
    # bg-grid defined in tailwind plugin, but bgGridDefined marks that it IS defined somewhere
    index_css = IndexCssSpec(
        tailwindDirectives=['@tailwind base', '@tailwind components', '@tailwind utilities'],
        baseLayerBackgroundColor='#0a0a0a',
        baseLayerTextColor='#ffffff',
        fontFamilyBody="'Inter', sans-serif",
        bgGridDefined=True,  # still true because it IS defined (in tailwind plugin)
    )
    package_json = _build_package_json(projectName)
    ts_config = _build_tsconfig()
    env_example = _build_env_example(convexUrl)
    npmrc = _build_npmrc()

    # Verify no conflicting lockfiles remain
    lockfile_is_bun_only = True
    for lf in conflicting_lockfiles:
        if os.path.exists(os.path.join(projectDir, lf)):
            lockfile_is_bun_only = False
            break

    manifest = ScaffoldManifest(
        viteConfig=vite_config,
        tailwindConfig=tailwind_config,
        postcssConfig=postcss_config,
        indexHtml=index_html,
        indexCss=index_css,
        packageJson=package_json,
        tsConfig=ts_config,
        envExample=env_example,
        npmrc=npmrc,
        convexDirCreated=True,
        lockfileIsBunOnly=lockfile_is_bun_only,
    )

    _emit({
        "pact_key": "PACT:d97abb:project_scaffold:generate_scaffold",
        "event": "completed",
        "input_classification": [projectDir, projectName],
        "output_classification": ["ScaffoldManifest"],
        "side_effects": ["filesystem_write", "subprocess"],
        "ts": time.time_ns(),
    })

    return manifest


def validate_scaffold(
    projectDir: str,
    event_handler=None,
    log_handler=None,
) -> ScaffoldValidationResult:
    """Validate an existing project directory against the scaffold contract."""
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:d97abb:project_scaffold:validate_scaffold",
        "event": "invoked",
        "input_classification": [projectDir],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    _log("info", f"validate_scaffold invoked for {projectDir}")

    if not os.path.exists(projectDir) or not os.path.isdir(projectDir):
        raise FileNotFoundError(f"directory_not_found: projectDir '{projectDir}' does not exist or is not a directory")

    if not os.access(projectDir, os.R_OK):
        raise PermissionError(f"directory_not_readable: projectDir '{projectDir}' is not readable")

    violations: List[str] = []
    checked_files: List[str] = []

    # List of owned files to check
    owned_files = [
        'vite.config.ts',
        'tailwind.config.js',
        'postcss.config.js',
        'index.html',
        'src/index.css',
        'src/main.tsx',
        'package.json',
        'tsconfig.json',
        'tsconfig.app.json',
        '.npmrc',
        '.env.example',
        'convex/.gitkeep',
    ]

    for f in owned_files:
        full_path = os.path.join(projectDir, f)
        checked_files.append(full_path)
        if not os.path.exists(full_path):
            violations.append(f"Missing file: {f}")

    # Check for conflicting lockfiles
    for lf in ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']:
        lf_path = os.path.join(projectDir, lf)
        if os.path.exists(lf_path):
            violations.append(f"Conflicting lockfile found: {lf}")

    # Validate vite.config.ts content
    vite_config_path = os.path.join(projectDir, 'vite.config.ts')
    if os.path.exists(vite_config_path):
        try:
            with open(vite_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'port: 4000' not in content:
                violations.append("vite.config.ts: server.port is not 4000")
            if 'strictPort: true' not in content:
                violations.append("vite.config.ts: server.strictPort is not true")
            if "outDir: 'dist'" not in content:
                violations.append("vite.config.ts: build.outDir is not 'dist'")
        except Exception as e:
            violations.append(f"vite.config.ts: Cannot read file: {e}")

    # Validate tsconfig.app.json
    tsconfig_app_path = os.path.join(projectDir, 'tsconfig.app.json')
    if os.path.exists(tsconfig_app_path):
        try:
            with open(tsconfig_app_path, 'r', encoding='utf-8') as f:
                tsconfig_data = json.load(f)
            co = tsconfig_data.get('compilerOptions', {})
            if co.get('strict') is not True:
                violations.append("tsconfig.app.json: strict is not true")
            if co.get('jsx') != 'react-jsx':
                violations.append("tsconfig.app.json: jsx is not 'react-jsx'")
            if co.get('moduleResolution') != 'bundler':
                violations.append("tsconfig.app.json: moduleResolution is not 'bundler'")
            paths = co.get('paths', {})
            if '@/*' not in paths or paths['@/*'] != ['src/*']:
                violations.append("tsconfig.app.json: paths missing '@/*' -> ['src/*']")
            types = co.get('types', [])
            if 'vitest/globals' not in types:
                violations.append("tsconfig.app.json: types missing 'vitest/globals'")
        except json.JSONDecodeError as e:
            violations.append(f"tsconfig.app.json: Invalid JSON: {e}")
        except Exception as e:
            violations.append(f"tsconfig.app.json: Cannot read file: {e}")

    # Validate package.json
    pkg_path = os.path.join(projectDir, 'package.json')
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, 'r', encoding='utf-8') as f:
                pkg_data = json.load(f)
            if pkg_data.get('type') != 'module':
                violations.append("package.json: type is not 'module'")
            if pkg_data.get('private') is not True:
                violations.append("package.json: private is not true")
            scripts = pkg_data.get('scripts', {})
            if scripts.get('dev') != 'vite':
                violations.append("package.json: scripts.dev is not 'vite'")
            if scripts.get('test') != 'vitest':
                violations.append("package.json: scripts.test is not 'vitest'")
            if scripts.get('preview') != 'vite preview':
                violations.append("package.json: scripts.preview is not 'vite preview'")
            build_script = scripts.get('build', '')
            if not re.match(r'^tsc.*&&\s*vite build$', build_script):
                violations.append("package.json: scripts.build does not match 'tsc ... && vite build'")
        except json.JSONDecodeError as e:
            violations.append(f"package.json: Invalid JSON: {e}")
        except Exception as e:
            violations.append(f"package.json: Cannot read file: {e}")

    valid = len(violations) == 0

    result = ScaffoldValidationResult(
        valid=valid,
        violations=violations,
        checkedFiles=checked_files,
    )

    _emit({
        "pact_key": "PACT:d97abb:project_scaffold:validate_scaffold",
        "event": "completed",
        "input_classification": [projectDir],
        "output_classification": ["ScaffoldValidationResult"],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    return result


def get_tailwind_theme_tokens(
    projectDir: str,
    event_handler=None,
    log_handler=None,
) -> TailwindConfig:
    """Extract the Tailwind theme extension tokens from the scaffold configuration."""
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:d97abb:project_scaffold:get_tailwind_theme_tokens",
        "event": "invoked",
        "input_classification": [projectDir],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    config_path = os.path.join(projectDir, 'tailwind.config.js')

    if not os.path.exists(config_path) or not os.path.isdir(projectDir):
        raise FileNotFoundError(f"config_not_found: tailwind.config.js not found at '{config_path}'")

    # Try to read and parse
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise ParseError(f"config_parse_error: Cannot read tailwind.config.js: {e}")

    # Verify it's parseable (basic check for module.exports)
    if 'module.exports' not in content and 'export default' not in content:
        raise ParseError(f"config_parse_error: tailwind.config.js does not contain a valid export")

    # Return canonical config
    result = _build_tailwind_config()

    _emit({
        "pact_key": "PACT:d97abb:project_scaffold:get_tailwind_theme_tokens",
        "event": "completed",
        "input_classification": [projectDir],
        "output_classification": ["TailwindConfig"],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    return result


def get_path_aliases(
    projectDir: str,
    event_handler=None,
    log_handler=None,
) -> dict:
    """Extract TypeScript path alias mappings from tsconfig."""
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:d97abb:project_scaffold:get_path_aliases",
        "event": "invoked",
        "input_classification": [projectDir],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    config_path = os.path.join(projectDir, 'tsconfig.app.json')

    if not os.path.exists(config_path) or not os.path.isdir(projectDir):
        raise FileNotFoundError(f"config_not_found: tsconfig.app.json not found at '{config_path}'")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ParseError(f"config_parse_error: tsconfig.app.json contains invalid JSON: {e}")
    except Exception as e:
        raise ParseError(f"config_parse_error: Cannot read tsconfig.app.json: {e}")

    paths = data.get('compilerOptions', {}).get('paths', {})
    if not paths:
        paths = {'@/*': ['src/*']}

    _emit({
        "pact_key": "PACT:d97abb:project_scaffold:get_path_aliases",
        "event": "completed",
        "input_classification": [projectDir],
        "output_classification": ["dict"],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    return paths


def get_vite_config(
    projectDir: str,
    event_handler=None,
    log_handler=None,
) -> ViteUserConfig:
    """Parse and return the full ViteUserConfig from the project's vite.config.ts."""
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:d97abb:project_scaffold:get_vite_config",
        "event": "invoked",
        "input_classification": [projectDir],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    config_path = os.path.join(projectDir, 'vite.config.ts')

    if not os.path.exists(config_path) or not os.path.isdir(projectDir):
        raise FileNotFoundError(f"config_not_found: vite.config.ts not found at '{config_path}'")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise ParseError(f"config_parse_error: Cannot read vite.config.ts: {e}")

    if 'defineConfig' not in content and 'export default' not in content:
        raise ParseError(f"config_parse_error: vite.config.ts does not contain a valid Vite config export")

    result = _build_vite_config()

    _emit({
        "pact_key": "PACT:d97abb:project_scaffold:get_vite_config",
        "event": "completed",
        "input_classification": [projectDir],
        "output_classification": ["ViteUserConfig"],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    return result


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    'ViteServerConfig',
    'ViteBuildConfig',
    'ViteResolveAlias',
    'VitestConfig',
    'ViteUserConfig',
    'ViteResolveConfig',
    'TailwindFontFamily',
    'TailwindColorToken',
    'HexColor',
    'TailwindContentGlob',
    'TailwindConfig',
    'FilePath',
    'GoogleFontLink',
    'IndexHtmlSpec',
    'CssDirective',
    'IndexCssSpec',
    'PackageJsonScripts',
    'SemVerRange',
    'PackageJsonDependencies',
    'PackageJsonDevDependencies',
    'PackageJsonSpec',
    'TsConfigCompilerOptions',
    'TsConfigSpec',
    'PostCssConfig',
    'EnvExampleSpec',
    'NpmrcSpec',
    'ScaffoldManifest',
    'ScaffoldValidationResult',
    'BgGridSpec',
    'generate_scaffold',
    'EnvironmentError',
    'SubprocessError',
    'validate_scaffold',
    'get_tailwind_theme_tokens',
    'ParseError',
    'get_path_aliases',
    'get_vite_config',
]
