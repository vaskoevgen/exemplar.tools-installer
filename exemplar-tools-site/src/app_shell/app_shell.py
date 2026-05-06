import logging
import os
import re
import time
from enum import Enum
from typing import Any, Callable, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

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


# ===================================================================
# ToolSlug Enum
# ===================================================================

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


# Frozen list of all tool slugs (immutable tuple)
TOOL_SLUGS: tuple = tuple(member.value for member in ToolSlug)


# ===================================================================
# Primitive validated types
# ===================================================================

class HexColorString(BaseModel):
    """A CSS hex color string (e.g. '#4F46E5'). Validated by regex."""
    model_config = ConfigDict(frozen=True)
    value: str

    @field_validator('value')
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        if not re.match(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', v):
            raise ValueError(f"Invalid hex color string: '{v}'. Must match ^#([0-9a-fA-F]{{3}}|[0-9a-fA-F]{{6}})$")
        return v


class ConvexUrl(BaseModel):
    """A validated Convex deployment URL string."""
    model_config = ConfigDict(frozen=True)
    value: str

    @field_validator('value')
    @classmethod
    def validate_convex_url(cls, v: str) -> str:
        if not isinstance(v, str) or len(v) < 10 or len(v) > 256:
            raise ValueError(
                f"ConvexUrl must be a string between 10 and 256 characters, got length {len(v) if isinstance(v, str) else 'non-string'}"
            )
        if not re.match(r'^https?://.+', v):
            raise ValueError(f"ConvexUrl must start with http:// or https://, got: '{v}'")
        return v


class StepNumber:
    """Integer 1-11 representing the tool's position in the exemplar.tools workflow order."""

    def __init__(self, value: int = None, **kwargs):
        if value is None and 'value' in kwargs:
            value = kwargs['value']
        if value is None:
            raise ValueError("StepNumber requires a value")
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"StepNumber must be an integer, got {type(value).__name__}")
        if value < 1 or value > 11:
            raise ValueError(f"StepNumber must be between 1 and 11 inclusive, got {value}")
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def __eq__(self, other):
        if isinstance(other, StepNumber):
            return self._value == other._value
        if isinstance(other, int):
            return self._value == other
        return NotImplemented

    def __int__(self) -> int:
        return self._value

    def __repr__(self) -> str:
        return f"StepNumber({self._value})"


HexColor = HexColorString  # Alias - CSS hex color string used for per-tool accent theming


# ===================================================================
# Structured types
# ===================================================================

class string:
    """Auto-stubbed type — referenced but not defined in contract 'app_shell'"""
    pass


class SidebarItem:
    """Derived view-model for a single sidebar navigation entry, projected from ToolDef."""

    def __init__(
        self,
        slug: Any = None,
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
        return f"SidebarItem(slug={self.slug!r}, name={self.name!r}, stepNumber={self.stepNumber}, accentColor={self.accentColor!r})"


class SidebarProps:
    """Props interface for the Sidebar component."""

    def __init__(
        self,
        items: list = None,
        currentSlug: Any = None,
        onNavigate: Any = None,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)

        self.items = items or []
        self.currentSlug = currentSlug
        self.onNavigate = onNavigate


class RoutesObject(BaseModel):
    """Frozen object containing all route path constants."""
    model_config = ConfigDict(frozen=True)
    HOME: str
    TOOL: str

    @field_validator('HOME')
    @classmethod
    def validate_home(cls, v: str) -> str:
        if v != '/':
            raise ValueError(f"HOME must be exactly '/', got '{v}'")
        return v

    @field_validator('TOOL')
    @classmethod
    def validate_tool(cls, v: str) -> str:
        if v != '/:toolSlug':
            raise ValueError(f"TOOL must be exactly '/:toolSlug', got '{v}'")
        return v


class FadeInKeyframes(BaseModel):
    """Tailwind keyframe definition for the animate-fadeIn utility class."""
    model_config = ConfigDict(frozen=True)
    from_opacity: float
    to_opacity: float
    duration: str
    easing: str

    @field_validator('from_opacity')
    @classmethod
    def validate_from_opacity(cls, v: float) -> float:
        if v != 0:
            raise ValueError(f"from_opacity must be exactly 0, got {v}")
        return v

    @field_validator('to_opacity')
    @classmethod
    def validate_to_opacity(cls, v: float) -> float:
        if v != 1:
            raise ValueError(f"to_opacity must be exactly 1, got {v}")
        return v

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v: str) -> str:
        if v != '200ms':
            raise ValueError(f"duration must be exactly '200ms', got '{v}'")
        return v

    @field_validator('easing')
    @classmethod
    def validate_easing(cls, v: str) -> str:
        if v != 'ease-out':
            raise ValueError(f"easing must be exactly 'ease-out', got '{v}'")
        return v


class TailwindFontConfig(BaseModel):
    """Font family extension in tailwind.config.ts for the Instrument Serif typeface."""
    model_config = ConfigDict(frozen=True)
    serif: list

    @field_validator('serif')
    @classmethod
    def validate_serif(cls, v: list) -> list:
        expected = ['Instrument Serif', 'serif']
        if v != expected:
            raise ValueError(f"serif must be {expected}, got {v}")
        return v


class GoogleFontLink(BaseModel):
    """Descriptor for a Google Fonts <link> tag to be placed in index.html."""
    model_config = ConfigDict(frozen=True)
    href: str
    preconnect_origins: list

    @field_validator('href')
    @classmethod
    def validate_href(cls, v: str) -> str:
        pattern = r'^https://fonts\.googleapis\.com/css2\?family=.+&display=swap$'
        if not re.match(pattern, v):
            raise ValueError(
                f"href must match Google Fonts CSS2 URL pattern with display=swap. Got: '{v}'"
            )
        return v


# ===================================================================
# Module-level constants
# ===================================================================

ROUTES = RoutesObject(HOME="/", TOOL="/:toolSlug")


# ===================================================================
# Pure functions
# ===================================================================

def isValidToolSlug(value: str) -> bool:
    """
    Type guard function that narrows an arbitrary string to the ToolSlug union type.
    Checks membership in the frozen TOOL_SLUGS array.
    """
    _log("debug", f"isValidToolSlug called with value={value!r}")
    return value in TOOL_SLUGS


def toolPath(slug: str) -> str:
    """
    Constructs a resolved route path string for a given tool slug.
    Replaces the :toolSlug parameter in ROUTES.TOOL with the provided slug value.
    """
    _log("debug", f"toolPath called with slug={slug!r}")
    return f"/{slug}"


def projectToolDefToSidebarItem(toolDef: Any) -> SidebarItem:
    """
    Pure mapping function that transforms a ToolDef (from data_layer) into a SidebarItem view-model.
    """
    _log("debug", f"projectToolDefToSidebarItem called for slug={toolDef.slug!r}")
    return SidebarItem(
        slug=toolDef.slug,
        name=toolDef.name,
        label=toolDef.name,
        stepNumber=toolDef.stepNumber,
        step=toolDef.stepNumber,
        accentColor=toolDef.accentColor,
    )


# ===================================================================
# Convex client singleton
# ===================================================================

_convex_client_instance = None


class _ConvexReactClient:
    """Mock/stand-in for the Convex React client in Python context."""

    def __init__(self, url: str):
        self.url = url

    def __repr__(self) -> str:
        return f"ConvexReactClient(url={self.url!r})"


def createConvexClient() -> Any:
    """
    Reads VITE_CONVEX_URL from environment, validates it is a non-empty string,
    and returns a singleton ConvexReactClient instance.
    """
    global _convex_client_instance

    _log("info", "createConvexClient invoked")

    url = os.environ.get("VITE_CONVEX_URL", None)

    if not url:
        raise Error(
            "VITE_CONVEX_URL environment variable is not set. Add it to your .env.local file."
        )

    if _convex_client_instance is not None:
        _log("debug", "Returning existing ConvexReactClient singleton")
        return _convex_client_instance

    _convex_client_instance = _ConvexReactClient(url)
    _log("info", f"Created ConvexReactClient singleton for URL: {url}")
    return _convex_client_instance


# ===================================================================
# Error class (matches REQUIRED EXPORT 'Error')
# ===================================================================

class Error(Exception):
    """Application error class for app_shell component."""
    pass


# ===================================================================
# Render functions (stubs for Python context, real implementations in TSX)
# ===================================================================

def renderApp() -> Any:
    """
    Top-level App component render function.
    In Python context, this validates that the Convex client can be created
    and returns a representation of the component tree.
    """
    _log("info", "renderApp invoked")
    try:
        client = createConvexClient()
    except Exception:
        raise Error("App cannot render: Convex client failed to initialize.")

    return {
        "component": "App",
        "tree": {
            "ConvexProvider": {
                "client": client,
                "children": {
                    "BrowserRouter": {
                        "Routes": {
                            "Route": {
                                "path": "/",
                                "element": "Layout",
                                "children": [
                                    {"Route": {"index": True, "element": "HomePage"}},
                                    {"Route": {"path": ":toolSlug", "element": "ToolPage"}},
                                ],
                            }
                        }
                    }
                },
            }
        },
    }


def renderLayout(event_handler=None, log_handler=None) -> Any:
    """
    Layout component render function.
    Returns a representation of the layout structure.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:f0d971:app_shell:renderLayout",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    result = {
        "component": "Layout",
        "sidebarOpen": False,
        "children": [
            {"div": {"className": "background-grid", "style": {"position": "fixed", "zIndex": 0}}},
            {"Sidebar": {"zIndex": 20}},
            {"button": {"className": "hamburger md:hidden", "zIndex": 30}},
            {"div": {"className": "animate-fadeIn", "key": "location.pathname", "children": "Outlet"}},
        ],
    }

    _emit({
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
    currentSlug: Any = None,
    onNavigate: Any = None,
    event_handler=None,
    log_handler=None,
) -> Any:
    """
    Sidebar presentational component.
    Returns a representation of the sidebar structure.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:f0d971:app_shell:renderSidebar",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    sidebar_entries = []
    for item in items:
        is_active = currentSlug is not None and (
            (hasattr(item, 'slug') and item.slug == currentSlug) or
            (isinstance(item, dict) and item.get('slug') == currentSlug)
        )
        accent = None
        if is_active:
            accent = item.accentColor if hasattr(item, 'accentColor') else (
                item.get('accentColor') if isinstance(item, dict) else None
            )
        sidebar_entries.append({
            "slug": item.slug if hasattr(item, 'slug') else item.get('slug'),
            "label": item.label if hasattr(item, 'label') else (item.name if hasattr(item, 'name') else item.get('name')),
            "stepNumber": item.stepNumber if hasattr(item, 'stepNumber') else item.get('stepNumber'),
            "isActive": is_active,
            "style": {"color": accent, "backgroundColor": accent} if accent else {},
        })

    result = {
        "component": "Sidebar",
        "logo": {"NavLink": {"to": "/", "onClick": "onNavigate"}},
        "entries": sidebar_entries,
    }

    _emit({
        "pact_key": "PACT:f0d971:app_shell:renderSidebar",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    return result


# ===================================================================
# REQUIRED EXPORTS
# ===================================================================

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
    'ROUTES',
    'HexColorString',
    'ConvexUrl',
    'StepNumber',
    'HexColor',
]
