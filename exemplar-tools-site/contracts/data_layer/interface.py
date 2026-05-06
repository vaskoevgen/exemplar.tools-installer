# === Data Constants & Convex Backend (data_layer) v1 ===
# Provides the canonical typed registry of all 11 exemplar.tools tool definitions (slug, name, description, step number, version, accent color, optional YouTube embed URL, and placeholder step-by-step instructions) as a static constant array exported from src/data/tools.ts. Also defines the Convex backend schema for user-submitted comments (convex/schema.ts) and exposes fully-typed Convex query/mutation functions (convex/comments.ts) for listing comments filtered by page and adding new comments with server-side timestamps. This component is the single source of truth for tool metadata and the comments data model.

# Module invariants:
#   - The TOOLS array always contains exactly 11 elements, one for each tool in the exemplar.tools suite.
#   - Each ToolDef.step value is unique and maps bijectively to exactly one ToolSlug.
#   - The TOOLS array is sorted by step ascending: TOOLS[i].step < TOOLS[i+1].step for all valid i.
#   - Exactly 10 of 11 tools have a defined videoUrl; kindex (step 11) has videoUrl undefined.
#   - All 11 accentColor values are distinct and belong to the canonical dark-theme palette: #00e5ff, #00bfa5, #69f0ae, #b2ff59, #ffd740, #ff9100, #ff5252, #ff4081, #e040fb, #7c4dff, #448aff.
#   - The Convex 'comments' table defines a compound index 'by_page_createdAt' on fields ['page', 'createdAt'] enabling efficient filtered-and-sorted queries.
#   - Every comment document in the 'comments' table has all four fields populated: page (non-empty string), author (non-empty string), body (non-empty string), createdAt (positive number).
#   - The createdAt field is always set server-side via Date.now() during addComment mutation; it is never client-supplied.
#   - listComments is a pure read query with no side effects on the 'comments' table.
#   - addComment is non-idempotent: repeated calls with identical arguments produce distinct documents.
#   - All Convex function args are validated by Convex's built-in v.string() and v.number() validators before handler execution.
#   - The TOOL_SLUGS runtime array and ToolSlug type always enumerate the same 11 values.

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

StepNumber = primitive  # Integer 1–11 representing the tool's position in the exemplar.tools workflow order.

HexColor = primitive  # CSS hex color string (e.g. '#00e5ff') used for per-tool accent theming.

class InstructionStep:
    """A single step-by-step instruction entry containing a human title and a bash snippet."""
    title: string                            # required, Short human-readable title for this instruction step.
    bash: string                             # required, Bash code block content to display in a terminal-styled card.

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

ToolDefArray = list[ToolDef]
# The TOOLS constant: an ordered array of exactly 11 ToolDef objects, one per tool, sorted by step number ascending.

ConvexDocumentId = primitive  # Convex-generated unique document identifier. Serialized as a string on the client side. Corresponds to Id<'comments'> in the Convex type system.

class Comment:
    """A user-submitted comment persisted in Convex, displayed in the CommentsSection."""
    _id: string                              # required, Convex-generated unique document ID.
    page: ToolSlug                           # required, Tool slug identifying which page this comment belongs to.
    author: string                           # required, length(1..100), Display name of the comment author.
    body: string                             # required, length(1..2000), Comment body text.
    createdAt: number                        # required, Unix epoch millisecond timestamp set via Date.now() at insertion time.

class ListCommentsArgs:
    """Arguments for the Convex listComments query function."""
    page: ToolSlug                           # required, Tool slug to filter comments by page.

class AddCommentArgs:
    """Arguments for the Convex addComment mutation, submitted from CommentsSection form."""
    page: ToolSlug                           # required, Tool slug identifying the target page.
    author: string                           # required, length(1..100), Display name of the comment author.
    body: string                             # required, length(1..2000), Comment body text.

CommentList = list[Comment]
# Array of Comment objects returned by the listComments query, sorted by createdAt ascending.

OptionalVideoUrl = Any | None

InstructionStepList = list[InstructionStep]
# Ordered array of InstructionStep objects for a tool's how-to section.

class number:
    """Auto-stubbed type — referenced but not defined in contract 'data_layer'"""
    pass

class string:
    """Auto-stubbed type — referenced but not defined in contract 'data_layer'"""
    pass

def getTools() -> ToolDefArray:
    """
    Returns the static TOOLS constant: a readonly array of all 11 ToolDef objects ordered by step number (1–11). Pure synchronous access to the in-memory tool registry. This is a module-level export, not a runtime function call — modeled here as a function for contract completeness.

    Postconditions:
      - Returned array has exactly 11 elements.
      - Elements are sorted by step field ascending (1 through 11).
      - All step values are unique across the array.
      - All slug values are unique across the array.
      - Exactly one element (kindex) has videoUrl undefined; all other 10 elements have a defined videoUrl.
      - Each element's instructions array contains between 3 and 5 InstructionStep objects.
      - Each accentColor is a unique 6-digit hex color from the canonical dark-theme palette.

    Side effects: none
    Idempotent: yes
    """
    ...

def getToolBySlugs(
    slug: str,                 # regex(^[a-z]+$)
) -> ToolDef:
    """
    Utility lookup: finds a ToolDef by its slug from the TOOLS array. Returns undefined if the slug does not match any of the 11 known tools. Pure synchronous function.

    Postconditions:
      - If slug matches a known ToolSlug variant, the returned ToolDef has that slug.
      - If slug does not match any ToolSlug variant, returns undefined.

    Side effects: none
    Idempotent: yes
    """
    ...

async def listComments(
    page: str,                 # regex(^[a-z]+$)
) -> CommentList:
    """
    Convex query function (convex/comments.ts). Retrieves all comments for a given page slug from the 'comments' table, using the compound index 'by_page_createdAt' to filter by page and sort by createdAt ascending. Returns Doc<'comments'>[] which maps to CommentList on the client. Invoked via useQuery(api.comments.listComments, { page }).

    Preconditions:
      - page is a non-empty string.

    Postconditions:
      - Returned array contains only comments where comment.page === args.page.
      - Returned array is sorted by createdAt ascending (oldest first).
      - Each element in the returned array is a complete Comment document with _id, page, author, body, and createdAt.
      - If no comments exist for the given page, returns an empty array.

    Errors:
      - missing_page_argument (ConvexValidationError): The 'page' argument is not provided or is not a string.
          message: Argument 'page' is required and must be a string.

    Side effects: none
    Idempotent: yes
    """
    ...

async def addComment(
    page: str,                 # regex(^[a-z]+$)
    author: str,               # length(1..100)
    body: str,                 # length(1..5000)
) -> ConvexDocumentId:
    """
    Convex mutation function (convex/comments.ts). Inserts a new comment document into the 'comments' table with the provided page slug, author name, body text, and a server-generated Date.now() timestamp for createdAt. Returns the Convex-generated Id<'comments'> of the new document. Invoked via useMutation(api.comments.addComment).

    Preconditions:
      - page is a non-empty string corresponding to a valid tool slug.
      - author is a non-empty string of at most 100 characters.
      - body is a non-empty string of at most 5000 characters.

    Postconditions:
      - A new document exists in the 'comments' table with the provided page, author, and body fields.
      - The new document's createdAt field is set to the server-side Date.now() value at insertion time.
      - The returned ConvexDocumentId uniquely identifies the newly created comment document.
      - Subsequent listComments({ page }) calls will include the newly created comment.

    Errors:
      - missing_page_argument (ConvexValidationError): The 'page' argument is not provided or is not a string.
          message: Argument 'page' is required and must be a string.
      - missing_author_argument (ConvexValidationError): The 'author' argument is not provided or is not a string.
          message: Argument 'author' is required and must be a string.
      - missing_body_argument (ConvexValidationError): The 'body' argument is not provided or is not a string.
          message: Argument 'body' is required and must be a string.
      - empty_author (ValidationError): The 'author' argument is an empty string after trimming.
          message: Author name must not be empty.
      - empty_body (ValidationError): The 'body' argument is an empty string after trimming.
          message: Comment body must not be empty.
      - convex_internal_error (ConvexInternalError): Convex runtime encounters an internal failure during the mutation (e.g. write conflict, system overload).
          message: An internal Convex error occurred while inserting the comment.

    Side effects: none
    Idempotent: no
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['ToolSlug', 'InstructionStep', 'ToolDef', 'ToolDefArray', 'Comment', 'ListCommentsArgs', 'AddCommentArgs', 'CommentList', 'OptionalVideoUrl', 'InstructionStepList', 'number', 'string', 'getTools', 'getToolBySlugs', 'listComments', 'ConvexValidationError', 'addComment', 'ValidationError', 'ConvexInternalError']
