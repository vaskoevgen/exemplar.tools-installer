```
yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> source ../exemplar.tools/advocate/.venv/bin/activate.fish
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> advocate review src/ -o findings.json --html review-report.html
Reviewing /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src with 6 personas (in parallel, anthropic)...
/Users/yevhenvasko/source/exemplar.tools-installer/exemplar.tools/transmogrifier/src/transmogrifier/profiles.py:15: UserWarning: Field name "register" in "RegisterAccuracy" shadows an attribute in parent "BaseModel"
  class RegisterAccuracy(BaseModel):

======================================================================
  ADVOCATE REVIEW: /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src
  38 findings | $0.2355 | 6 personas
======================================================================

  Red Team — It's vulnerable; harden.
  -------------------------------------
      high [race_conditions] Global store concurrent access without synchronization
             The _store global variable is accessed concurrently by async operations without any locking or synchronization. Multiple concurrent requests can corrupt the internal dictionary state, leading to data loss, inconsistent reads, or crashes.
          -> Add async locks around all store operations or use a thread-safe data structure. Consider using asyncio.Lock() to protect critical sections.

      high [data_corruption] Task ID collision enables data corruption
             The create_task function generates UUIDs using uuid4() but doesn't check for collisions before adding to store. While UUID4 collisions are rare, they can occur and would silently overwrite existing tasks.
          -> Check for existing task ID before insertion, or use a collision-safe ID generation strategy.

    medium [injection] Log injection through PACT key logging
             The _log function directly interpolates user-controlled data into log messages without sanitization. An attacker could inject malicious content into logs by manipulating task titles or other user inputs that get logged.
          -> Sanitize log messages and use structured logging instead of string interpolation to prevent log injection attacks.

    medium [data_corruption] TimestampTZ validation bypass allows invalid timestamps
             The TimestampTZ class accepts any string value without validating it's a proper ISO 8601 timestamp with timezone. This can lead to storing invalid timestamp data that breaks downstream processing.
          -> Add proper ISO 8601 timestamp validation in TimestampTZ.__init__ similar to DateString validation.

    medium [race_conditions] Test fixture race condition with store clearing
             The _reset_store fixture clears the store before and after each test, but if tests run concurrently, the clear() operation can interfere with running tests, causing flaky test results or data corruption.
          -> Use test-isolated store instances instead of a global store, or ensure tests run sequentially.

       low [data_corruption] Priority integer overflow not handled
             The Priority class accepts any integer >= 1 without upper bounds checking. Extremely large integers could cause memory issues or overflow problems in downstream systems.
          -> Add reasonable upper bounds for priority values (e.g., max 1000000) to prevent resource exhaustion.

  Summary: This codebase has significant concurrency vulnerabilities that could lead to data corruption in a multi-user environment. The global store operations are completely unsynchronized, creating race condi
  (22888ms, $0.0374)

  Adversarial — It's wrong; defend.
  -----------------------------------
  critical [failure_modes] Global state corruption in concurrent environments
             The module uses a global `_store` instance that is shared across all imports. In web applications with concurrent requests, this creates race conditions where one request's operations can interfere with another's. The `_reset_store()` fixture in tests also demonstrates this is a known issue - clearing global state between tests indicates the design is fundamentally flawed for concurrent access.
          -> Use dependency injection or request-scoped storage instead of global state

      high [edge_cases] UUID collision handling missing
             The `create_task()` function generates UUID v4 without checking for collisions in the store. While UUID v4 collisions are extremely rare, they are theoretically possible. The store will silently overwrite an existing task if a collision occurs, leading to data loss.
          -> Check for existing ID in store and regenerate if collision detected

      high [wrong_assumptions] TimestampTZ validation completely missing
             TimestampTZ class accepts any string without validation that it's actually a valid ISO 8601 timestamp with timezone. This violates the contract that it represents 'an ISO 8601 timestamp string with timezone' and will cause failures when the timestamp is actually used.
          -> Add datetime.fromisoformat() validation like DateString does

      high [edge_cases] Memory exhaustion from unbounded store growth
             The in-memory store has no size limits or cleanup mechanisms. In a long-running application, tasks accumulate indefinitely leading to memory exhaustion. There's no LRU eviction, no maximum capacity, no cleanup of old tasks.
          -> Implement store size limits, LRU eviction, or TTL-based cleanup

    medium [edge_cases] Unicode normalization issues in TaskTitle
             TaskTitle validation doesn't handle Unicode normalization. Different Unicode representations of the same visual string (like é vs e+combining-accent) will be treated as different titles. This can lead to apparent duplicates and confused users.
          -> Normalize Unicode to NFC form before validation and storage

    medium [wrong_assumptions] Date validation assumes Gregorian calendar only
             DateString validation uses date.fromisoformat() which assumes Gregorian calendar. This may not handle all edge cases correctly for dates near calendar transitions or in different locales, though ISO 8601 does specify Gregorian.
          -> Document Gregorian assumption or add explicit calendar validation

    medium [failure_modes] Event handler exceptions can crash operations
             All async CRUD functions call event_handler() without exception handling. If the event handler throws an exception, it will propagate and crash the operation, even though event handling should be non-critical side-effect.
          -> Wrap event handler calls in try/except to prevent handler failures from affecting core operations

       low [backward_compatibility] Frozen dataclasses prevent future field additions
             All dataclasses use frozen=True, which prevents adding new fields through inheritance or monkey-patching. This makes it difficult to extend the API schema in backward-compatible ways without breaking changes.
          -> Consider whether frozen=True is necessary for all dataclasses or if some should allow extension

  Summary: This code has several critical flaws that make it unsuitable for production use. The global state design is fundamentally broken for concurrent environments - any web server handling multiple requests
  (29379ms, $0.0417)

  Sage — It's complicated; simplify.
  ------------------------------------
  critical [design] Duplicate type systems serving identical purpose
             The code implements two complete type systems for the same data: primitive wrapper classes (TaskUUID, TaskTitle, Priority, DateString) with full validation, AND separate validation functions that duplicate all the same logic. This is pure redundancy - you're validating the same constraints twice in different ways.
          -> Pick one approach. Either use the wrapper types throughout (and skip separate validation), or use simple validation functions and drop the wrapper classes entirely.

      high [design] Over-engineered sentinel pattern for optional updates
             Using a custom Sentinel enum with UNSET values adds cognitive overhead for a problem Python's None/Optional already solves elegantly. The validation logic becomes more complex to handle three states (UNSET, None, value) when two states would suffice.
          -> Use None as the default for optional update fields. Differentiate between 'not provided' and 'clear field' through separate request models or explicit nullable fields.

      high [design] Unnecessary async everywhere
             All CRUD operations are declared async but perform zero async operations - they just call synchronous in-memory store methods. This adds complexity and misleads about the actual behavior.
          -> Make functions synchronous unless they actually perform async I/O. If you need async compatibility for a future database, add it when you add the database.

    medium [concept] Domain logic mixed with instrumentation noise
             Every business function is cluttered with event emission boilerplate that obscures the actual logic. The _emit calls with identical empty classifications suggest this instrumentation isn't providing value yet.
          -> Extract instrumentation to a decorator or middleware layer. Keep business logic functions focused on business logic only.

    medium [blast_radius] Global mutable state with no isolation
             The global _store instance means all parts of the application share the same mutable state. Any corruption or unexpected modification affects everything, and testing requires careful cleanup coordination.
          -> Inject the store as a dependency or use a factory pattern. This enables different store instances for testing vs production and reduces coupling.

       low [design] Unused abstraction overhead
             Several classes and types are defined but serve no clear purpose: 'boolean' and 'string' stub classes, EndpointContract dataclass that's only used to return static data, PactFormatter that's defined but not used.
          -> Remove unused types. If EndpointContract is for future API documentation generation, comment that intent. Otherwise, a simple list of dicts suffices.

  Summary: This code suffers from severe over-engineering. You've built two complete validation systems for the same data, added async complexity where none exists, and buried simple CRUD operations under layers
  (29670ms, $0.0392)

  User — It's unintuitive; clarify.
  -----------------------------------
  critical [concept] No clear purpose or entry point documentation
             A new user has no idea what this code does, how to use it, or where to start. There's no README, no module docstring explaining the purpose, and no usage examples. The only clue is 'personal task management web app' buried in a docstring.
          -> Add a comprehensive README with purpose, installation, usage examples, and API documentation. Add module-level examples showing how to create and use tasks.

      high [concept] Confusing primitive wrapper types with unclear value
             The code defines wrapper classes like TaskUUID, TaskTitle, Priority that essentially duplicate built-in validation but aren't used consistently. The actual Task dataclass uses plain str/int types, making these wrappers seem pointless.
          -> Either use the wrapper types consistently throughout (Task should use TaskUUID for id field) or remove them entirely if plain types with validation functions are sufficient.

      high [design] Mysterious auto-stubbed types break understanding
             The code defines placeholder classes 'boolean' and 'string' described as 'Auto-stubbed type — referenced but not defined in contract'. This is confusing and suggests the code is incomplete or generated incorrectly.
          -> Remove these placeholder classes or explain their purpose. If they're artifacts from code generation, clean them up before presenting to users.

      high [design] Inconsistent typing makes API contracts unclear
             Request classes use 'Any' type for all fields, making it impossible to understand what types are expected. The validation happens at runtime, but there's no static type guidance for users.
          -> Use proper types (str, int, Optional[str]) with defaults, or provide clear documentation about expected types. The 'Any' typing provides no guidance to users.

    medium [edge_cases] Cryptic PACT logging system with no explanation
             The code is littered with PACT logging and event emission that a new user won't understand. There's no explanation of what PACT is or why these logs matter.
          -> Add documentation explaining the PACT system or make it optional/removable for basic usage. Provide a way to disable this instrumentation for simple use cases.

    medium [design] Validation error messages are user-unfriendly
             Validation functions return generic error strings that don't help users understand how to fix their input. For example, 'Title is required and must not be empty' when the real issue might be wrong type.
          -> Include the actual invalid value in error messages and provide specific guidance: 'Title must be a string, got int: 42' or 'Priority must be integer >= 1, got: "high"'.

    medium [edge_cases] No guidance on how to actually run or deploy this
             The code defines async CRUD operations but provides no web server, no CLI, no examples of how to actually use these functions. A user can't figure out how to make HTTP requests to this API.
          -> Provide a simple server setup example (FastAPI/Flask) or CLI interface that demonstrates how to actually interact with these functions. Show complete request/response examples.

  Summary: This codebase suffers from a severe documentation and usability gap. While the underlying task management logic appears sound, a new user would be completely lost trying to understand what this does o
  (32417ms, $0.0423)

  Subject Matter Expert — Peer-review.
  --------------------------------------
  critical [wrong_assumptions] Timestamp monotonicity assumption violated
             The code assumes timestamps can be safely generated using datetime.now() for ordering and traceability. However, system clocks can go backwards due to NTP adjustments, leap seconds, or manual changes. This breaks assumptions about task creation ordering and audit trails.
          -> Use time.time_ns() or a monotonic clock for ordering, and consider adding a sequence number. Store both wall-clock time (for display) and monotonic time (for ordering).

      high [design] Mixing validation concerns with business logic
             The validation functions return either validated objects OR error strings, forcing callers to type-check results. This violates single responsibility and makes error handling fragile. The ValidationResult union type obscures the actual error handling contract.
          -> Use Result types, exceptions, or separate validation from transformation. Return validation errors as structured objects, not strings.

      high [wrong_assumptions] UUID uniqueness assumption in single-process context
             The code assumes UUID4 generation provides sufficient uniqueness for task IDs, but uses Python's uuid.uuid4() without considering collision probability in high-throughput scenarios or distributed systems. While mathematically sound, this can fail under specific conditions.
          -> For production systems, consider UUIDv7 for better temporal ordering, or add collision detection in the store.add() method.

    medium [design] Inconsistent type safety between wrapper types and core entities
             The code defines strict wrapper types (TaskUUID, TaskTitle, etc.) with comprehensive validation, but the core Task dataclass uses primitive types (str, int) instead of these wrappers. This creates a validation gap where invalid data can bypass the type safety.
          -> Use the wrapper types consistently in the Task dataclass, or remove the wrapper types if they're not being used.

    medium [backward_compatibility] REST API violates HTTP semantics
             DELETE /tasks/:id returns the deleted task with 200 OK, but RFC 7231 suggests 204 No Content for successful deletions. Also, the API uses PATCH but doesn't follow RFC 7396 JSON Merge Patch semantics properly (uses sentinel values instead of JSON null handling).
          -> Return 204 for DELETE operations, or document why 200+body is needed. For PATCH, either implement proper JSON Merge Patch or use PUT for full updates.

       low [design] Event emission pattern adds complexity without clear benefit
             Every async function includes event_handler and log_handler parameters with complex emission logic, but the events contain mostly empty classifications and duplicate information. This pattern adds significant code complexity for unclear observability benefits.
          -> Simplify observability by using decorators, structured logging, or a proper tracing framework instead of manual event emission.

  Summary: This code shows solid engineering fundamentals but has several critical assumptions that could cause problems in production. The timestamp generation issue is the most serious - system clocks aren't m
  (25450ms, $0.0393)

  Good Friend — The harsh truth you need to hear.
  -------------------------------------------------
  critical [three_am_test] Global singleton store will corrupt data in production
             The `_store = _TaskStore()` global singleton will share state across all requests in a web server. When multiple users create/update tasks simultaneously, they'll see each other's data and operations will interfere with each other. This is a fundamental concurrency bug that will cause data corruption.
          -> Pass store instances explicitly or use proper database/session isolation. Never use global mutable state in web applications.

  critical [blast_radius] In-memory storage means all data lost on restart
             Every server restart, crash, or deployment will delete all user tasks permanently. No persistence, no backups, no recovery. This will destroy user trust immediately and make the application unusable in any real scenario.
          -> Implement persistent storage (database, file system with atomic writes) before any real usage.

      high [three_am_test] Silent validation failures will confuse users
             When validation fails, the API returns a generic 'VALIDATION_ERROR' without explaining what was wrong. Users won't know if it's title length, invalid date format, or something else. You'll get support tickets and frustrated users.
          -> Return the actual validation error message to users: ApiErrorResponse(status=400, error=validated)

      high [failure_modes] No error handling for datetime operations
             The datetime.now() call in create_task can fail in edge cases (system clock issues, timezone problems). When it fails, the entire task creation fails with an unclear error.
          -> Wrap datetime operations in try/catch and provide sensible fallbacks or clear error messages.

    medium [financial_risk] Elaborate type system adds complexity without persistence benefits
             You've built custom wrapper types (TaskUUID, TaskTitle, Priority, etc.) that enforce validation, but since you're using in-memory storage, this complexity provides no durability benefits. The validation happens anyway in the request handlers.
          -> Either simplify to basic types or implement proper persistence that benefits from the type safety.

  Summary: Look, this will probably work for a demo, but if you're planning to show this to anyone or use it for real tasks, you're going to hit problems fast. The global store issue is the killer - it's not jus
  (20623ms, $0.0357)

JSON: findings.json
HTML: review-report.html
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> deactivate
```

```
AI step 
can you help with 2b — Advocate step? /Users/yevhenvasko/source/exemplar.tools-installer/howto.md
Let me read the Advocate section of howto.md.

Bash Find Advocate section line number
IN
grep -n "2b — Advocate\|### 2b" /Users/yevhenvasko/source/exemplar.tools-installer/howto.md

OUT
558:### 2b — Advocate (Review gate)
Read howto.md (lines 559-658)
Bash List src and tests directories from pact output
IN
ls /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src/ 2>/dev/null && echo "---" && ls /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/ 2>/dev/null

OUT
root
---
root
Pact completed and put the code in src/root/. Here's what to do for the Advocate step:

Step 1 — Activate the venv (fish shell):


source ../exemplar.tools/advocate/.venv/bin/activate.fish
Step 2 — Set your API key (if not already set):


set -x ANTHROPIC_API_KEY sk-...
Step 3 — Run the review:


advocate review src/ -o findings.json --html review-report.html
This runs 6 AI personas in parallel (~30 seconds, ~$0.15–0.30). It will save results to findings.json and an HTML report.

Then deactivate:


deactivate
That's it — Advocate is the simplest step. Just run the command and read the findings. The HTML report is easier to read than the JSON. Once it finishes, share any output here if you want help interpreting the findings.
```