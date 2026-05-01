```bash
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> deactivate
yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> source ../exemplar.tools/arbiter/.venv/bin/activate.fish
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> arbiter init

  Created /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/.arbiter/registry/trust_ledger.jsonl
  Created /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/arbiter.yaml
Arbiter initialized.
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> arbiter register access_graph.json

Error: Graph contains no nodes
```

```
AI step
can you help with Step 3 — Govern: Arbiter /Users/yevhenvasko/source/exemplar.tools-installer/howto.md
Read howto.md (lines 627-706)
Bash List todo-list2 contents and src/root
IN
ls /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/ && echo "---" && ls /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src/root/ 2>/dev/null | head -20

OUT
TASKS.md
_test
access_graph.json
changelog.yaml
component_map.yaml
constraints.yaml
contracts
decomposition
design.json
design.md
findings.json
learnings
ledger.yaml
pact.yaml
plans
prompt.md
review-report.html
schema_hints.yaml
schemas
sops.md
src
standards.json
start
task.md
tasks.json
tests
trust_policy.yaml
---
__pycache__
conftest.py
root.py
Read access_graph.json
The Arbiter step is partially functional — the init, canary, and trust commands work, but arbiter register access_graph.json will fail because Pact uses a components schema and Arbiter expects a nodes schema (schema mismatch bug, not yet fixed).

Here's what you can do right now:

Step 1 — Activate:


source ../exemplar.tools/arbiter/.venv/bin/activate.fish
Step 2 — Initialize:


arbiter init
Step 3 — Try registering (expect it to fail or produce empty results):


arbiter register access_graph.json
If it errors with a schema/nodes mismatch, that's the known bug — skip ahead.

Step 4 — Deactivate:


deactivate
The Arbiter step is essentially a no-op for now on this project. The access_graph.json Pact generated uses components but Arbiter reads nodes — the integration isn't wired up yet. You can run arbiter init to confirm the tool works, then move on to Step 4 — Baton.

Would you like to proceed to the Baton step?
```