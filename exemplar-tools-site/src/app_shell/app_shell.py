"""App Shell, Routing & Layout (app_shell) v1 — Python contract implementation.

This module implements the contract types, validators, and pure functions
for the app_shell component. It is designed to pass all 24 contract tests.
"""

import logging
import os
import re
import time
from enum import Enum
from typing import Any, Callable, List, Optional

_PACT_KEY = "PACT:f0d971:app_shell"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    """Formatter that injects the PACT log key into every record."""

    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    """Log with PACT key embedded for production traceability."""
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


# ── ToolSlug Enum ─────────────────────────────────────

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


# ── TOOL_SLUGS frozen array ───────────────────────────

TOOL_SLUGS: tuple = tuple(member.value for member in ToolSlug)
"""Frozen (immutable tuple) array of all 11 tool slug strings."""


# ── Primitive validated types ─────────────────────────

_HEX_COLOR_RE = re.compile(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')


class HexColorString:
    """A CSS hex color string (e.g. '#4F46E5'). Validated by regex."""

    __slots__ = ('value',)

    def __init__(self, value: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log_handler = log_handler or (lambda level, msg, ctx: None)
        if not isinstance(value, str) or not _HEX_COLOR_RE.match(value):
            raise ValueError(
                f"Invalid HexColorString: '{value}'. "
                f"Must match pattern #RGB or #RRGGBB."
            )
        # Use object.__setattr__ since we have __slots__ without _emit/_log_handler
        object.__setattr__(self, 'value', value)

    def __repr__(self) -> str:
        return f"HexColorString(value={self.value!r})"

    # Allow attribute setting during __init__ despite __slots__
    def __setattr__(self, name, val):
        if name in ('_emit', '_log_handler'):
            pass  # silently ignore these; they're only used during init
        else:
            object.__setattr__(self, name, val)


# Alias for the contract
HexColor = HexColorString


_CONVEX_URL_RE = re.compile(r'^https?://.+')


class ConvexUrl:
    """A validated Convex deployment URL string."""

    __slots__ = ('value',)

    def __init__(self, value: str = None, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log_handler = log_handler or (lambda level, msg, ctx: None)
        if not isinstance(value, str):
            raise TypeError(f"ConvexUrl requires a string, got {type(value).__name__}")
        if len(value) < 10:
            raise ValueError(
                f"ConvexUrl too short ({len(value)} chars). Minimum length is 10."
            )
        if len(value) > 256:
            raise ValueError(
                f"ConvexUrl too long ({len(value)} chars). Maximum length is 256."
            )
        if not _CONVEX_URL_RE.match(value):
            raise ValueError(
                f"ConvexUrl must start with http:// or https://. Got: '{value}'"
            )
        object.__setattr__(self, 'value', value)

    def __repr__(self) -> str:
        return f"ConvexUrl(value={self.value!r})"

    def __setattr__(self, name, val):
        if name in ('_emit', '_log_handler'):
            pass
        else:
            object.__setattr__(self, name, val)


class StepNumber:
    """Integer 1-11 representing the tool's position in the workflow order."""

    __slots__ = ('value',)

    def __init__(self, value: int = None, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log_handler = log_handler or (lambda level, msg, ctx: None)
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"StepNumber requires an integer, got {type(value).__name__}")
        if value < 1 or value > 11:
            raise ValueError(
                f"StepNumber must be between 1 and 11 inclusive. Got: {value}"
            )
        object.__setattr__(self, 'value', value)

    def __repr__(self) -> str:
        return f"StepNumber(value={self.value!r})"

    def __eq__(self, other):
        if isinstance(other, StepNumber):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return NotImplemented

    def __int__(self) -> int:
        return self.value

    def __setattr__(self, name, val):
        if name in ('_emit', '_log_handler'):
            pass
        else:
            object.__setattr__(self, name, val)


# ── Composite types ───────────────────────────────────

class SidebarItem:
    """Derived view-model for a single sidebar navigation entry."""

    def __init__(
        self,
        slug: str = None,
        name: str = None,
        label: str = None,
        step: int = None,
        stepNumber: int = None,
        accentColor: str = None,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.slug = slug
        # Support both 'name' and 'label' for the display name
        self.name = name if name is not None else label
        self.label = label if label is not None else name
        # Support both 'step' and 'stepNumber'
        self.stepNumber = stepNumber if stepNumber is not None else step
        self.step = step if step is not None else stepNumber
        self.accentColor = accentColor

    def __repr__(self) -> str:
        return (
            f"SidebarItem(slug={self.slug!r}, name={self.name!r}, "
            f"stepNumber={self.stepNumber!r}, accentColor={self.accentColor!r})"
        )


class SidebarProps:
    """Props interface for the Sidebar component."""

    def __init__(
        self,
        items: list = None,
        currentSlug: Optional[str] = None,
        onNavigate: str = None,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.items = items or []
        self.currentSlug = currentSlug
        self.onNavigate = onNavigate


class RoutesObject:
    """Frozen object containing all route path constants."""

    def __init__(
        self,
        HOME: str = None,
        TOOL: str = None,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if HOME != '/':
            raise ValueError(
                f"RoutesObject.HOME must be exactly '/'. Got: {HOME!r}"
            )
        if TOOL != '/:toolSlug':
            raise ValueError(
                f"RoutesObject.TOOL must be exactly '/:toolSlug'. Got: {TOOL!r}"
            )
        self.HOME = HOME
        self.TOOL = TOOL

    def __repr__(self) -> str:
        return f"RoutesObject(HOME={self.HOME!r}, TOOL={self.TOOL!r})"


class FadeInKeyframes:
    """Tailwind keyframe definition for animate-fadeIn."""

    def __init__(
        self,
        from_opacity: float = None,
        to_opacity: float = None,
        duration: str = None,
        easing: str = None,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if from_opacity != 0:
            raise ValueError(
                f"FadeInKeyframes.from_opacity must be exactly 0. Got: {from_opacity!r}"
            )
        if to_opacity != 1:
            raise ValueError(
                f"FadeInKeyframes.to_opacity must be exactly 1. Got: {to_opacity!r}"
            )
        if duration != '200ms':
            raise ValueError(
                f"FadeInKeyframes.duration must be exactly '200ms'. Got: {duration!r}"
            )
        if easing != 'ease-out':
            raise ValueError(
                f"FadeInKeyframes.easing must be exactly 'ease-out'. Got: {easing!r}"
            )
        self.from_opacity = from_opacity
        self.to_opacity = to_opacity
        self.duration = duration
        self.easing = easing


class TailwindFontConfig:
    """Font family extension for Instrument Serif."""

    def __init__(
        self,
        serif: list = None,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.serif = serif or ['Instrument Serif', 'serif']


_GOOGLE_FONT_HREF_RE = re.compile(
    r'^https://fonts\.googleapis\.com/css2\?family=.+&display=swap$'
)


class GoogleFontLink:
    """Descriptor for a Google Fonts <link> tag."""

    def __init__(
        self,
        href: str = None,
        preconnect_origins: list = None,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if not isinstance(href, str) or not _GOOGLE_FONT_HREF_RE.match(href):
            raise ValueError(
                f"GoogleFontLink.href must match Google Fonts CSS2 pattern "
                f"with display=swap. Got: {href!r}"
            )
        self.href = href
        self.preconnect_origins = preconnect_origins or [
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
        ]


class string:
    """Auto-stubbed type — referenced but not defined in contract 'app_shell'."""
    pass


# ── Pure functions ────────────────────────────────────

def isValidToolSlug(value: str) -> bool:
    """Type guard: returns True iff value is one of the 11 ToolSlug variants."""
    _log("debug", f"isValidToolSlug called with {value!r}")
    return isinstance(value, str) and value in TOOL_SLUGS


def toolPath(slug: str) -> str:
    """Constructs '/' + slug for a given tool slug."""
    _log("debug", f"toolPath called with {slug!r}")
    return f"/{slug}"


def projectToolDefToSidebarItem(toolDef: Any) -> SidebarItem:
    """Pure mapping: ToolDef -> SidebarItem."""
    _log("debug", f"projectToolDefToSidebarItem called for slug={toolDef.slug!r}")
    return SidebarItem(
        slug=toolDef.slug,
        name=toolDef.name,
        label=toolDef.name,
        stepNumber=toolDef.stepNumber,
        step=toolDef.stepNumber,
        accentColor=toolDef.accentColor,
    )


# ── Convex client singleton ───────────────────────────

_convex_client_instance = None
_convex_client_url = None


class _MockConvexReactClient:
    """Lightweight stand-in for ConvexReactClient in Python test context."""

    def __init__(self, url: str):
        self.url = url

    def __repr__(self) -> str:
        return f"ConvexReactClient(url={self.url!r})"


def createConvexClient(event_handler=None, log_handler=None) -> Any:
    """
    Reads VITE_CONVEX_URL from os.environ, validates it is a non-empty string,
    and returns a singleton ConvexReactClient-like instance.

    Raises:
        Error: If VITE_CONVEX_URL is undefined, None, or empty string.
    """
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:f0d971:app_shell:createConvexClient",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    global _convex_client_instance, _convex_client_url

    url = os.environ.get('VITE_CONVEX_URL', None)

    if not url or not isinstance(url, str) or url.strip() == '':
        raise Error(
            "VITE_CONVEX_URL environment variable is not set. "
            "Add it to your .env.local file."
        )

    # Singleton: return existing instance if URL matches
    if _convex_client_instance is not None and _convex_client_url == url:
        _emit({
            "pact_key": "PACT:f0d971:app_shell:createConvexClient",
            "event": "completed",
            "input_classification": [],
            "output_classification": ["singleton_reuse"],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        return _convex_client_instance

    _convex_client_instance = _MockConvexReactClient(url)
    _convex_client_url = url

    _emit({
        "pact_key": "PACT:f0d971:app_shell:createConvexClient",
        "event": "completed",
        "input_classification": [],
        "output_classification": ["new_instance"],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    _log("info", f"ConvexReactClient created for {url}")
    return _convex_client_instance


# ── Error class ───────────────────────────────────────

class Error(Exception):
    """Generic error class for the app_shell module."""
    pass


# ── Render stubs (Python-side placeholders) ───────────

def renderApp(event_handler=None, log_handler=None) -> Any:
    """Top-level App component render function (placeholder in Python)."""
    _emit_fn = event_handler or (lambda event: None)
    _emit_fn({
        "pact_key": "PACT:f0d971:app_shell:renderApp",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    try:
        client = createConvexClient(event_handler=event_handler, log_handler=log_handler)
    except Error:
        raise Error("App cannot render: Convex client failed to initialize.")

    result = {
        'type': 'ConvexProvider',
        'client': client,
        'children': {
            'type': 'BrowserRouter',
            'children': {
                'type': 'Routes',
                'children': [
                    {
                        'type': 'Route',
                        'path': '/',
                        'element': 'Layout',
                        'children': [
                            {'type': 'Route', 'index': True, 'element': 'HomePage'},
                            {'type': 'Route', 'path': ':toolSlug', 'element': 'ToolPage'},
                        ],
                    }
                ],
            },
        },
    }
    _emit_fn({
        "pact_key": "PACT:f0d971:app_shell:renderApp",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    return result


def renderLayout(event_handler=None, log_handler=None) -> Any:
    """Layout component render function (placeholder in Python)."""
    _emit_fn = event_handler or (lambda event: None)
    _emit_fn({
        "pact_key": "PACT:f0d971:app_shell:renderLayout",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    result = {
        'type': 'Layout',
        'sidebarOpen': False,
        'backgroundGrid': True,
        'fadeInKey': 'location.pathname',
    }
    _emit_fn({
        "pact_key": "PACT:f0d971:app_shell:renderLayout",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    return result


def renderSidebar(
    items: list,
    currentSlug: Optional[str] = None,
    onNavigate: str = None,
    event_handler=None,
    log_handler=None,
) -> Any:
    """Sidebar presentational component (placeholder in Python)."""
    _emit_fn = event_handler or (lambda event: None)
    _emit_fn({
        "pact_key": "PACT:f0d971:app_shell:renderSidebar",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    result = {
        'type': 'Sidebar',
        'items': items,
        'currentSlug': currentSlug,
        'onNavigate': onNavigate,
    }
    _emit_fn({
        "pact_key": "PACT:f0d971:app_shell:renderSidebar",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    return result


# ── REQUIRED EXPORTS ──────────────────────────────────
__all__ = [
    'ToolSlug',
    'SidebarItem',
    'SidebarProps',
    'RoutesObject',
    'FadeInKeyframes',
    'TailwindFontConfig',
    'GoogleFontLink',
    'string',
    'createConvexClient',
    'Error',
    'isValidToolSlug',
    'toolPath',
    'renderApp',
    'renderLayout',
    'renderSidebar',
    'projectToolDefToSidebarItem',
    'TOOL_SLUGS',
    'HexColorString',
    'ConvexUrl',
    'StepNumber',
    'HexColor',
]
