```
source ../exemplar.tools/pact/.venv/bin/activate.fish
(.venv) yevhenvasko@yevhens-mbp ~/s/e/todo-app-test2 (feature/howto-next-iteration)> pact deploy .
Generated baton.yaml: /Users/yevhenvasko/source/exemplar.tools-installer/todo-app-test2/baton.yaml
  Nodes: 1
  Edges: 0
  Observability: jsonl
  Canary thresholds: error_rate < 5.0%, p95 < 500.0ms

Next steps:
  1. Review /Users/yevhenvasko/source/exemplar.tools-installer/todo-app-test2/baton.yaml
  2. baton up --mock       # Boot with mocks
  3. baton slot <node> <cmd> # Slot live services
(.venv) yevhenvasko@yevhens-mbp ~/s/e/todo-app-test2 (feature/howto-next-iteration)> deactivate
yevhenvasko@yevhens-mbp ~/s/e/todo-app-test2 (feature/howto-next-iteration)> source ../exemplar.tools/baton/.venv/bin/activate.fish
(.venv) yevhenvasko@yevhens-mbp ~/s/e/todo-app-test2 (feature/howto-next-iteration)> baton status
Circuit: root (v1)
Nodes:   1
Edges:   0

  Name                 Role       Port     Mode   Contract
  ──────────────────── ────────── ──────── ────── ──────────────────────────────
  root                 [ingress]  3000     http   —
(.venv) yevhenvasko@yevhens-mbp ~/s/e/todo-app-test2 (feature/howto-next-iteration)> baton up --mock 
Circuit 'root' is up (1 nodes)
  root: active

Entry points:
  root: 127.0.0.1:3000

Press Ctrl+C to stop

Second terminal

(.venv) yevhenvasko@yevhens-mbp ~/s/e/todo-app-test2 (feature/howto-next-iteration)> source ../exemplar.tools/baton/.venv/bin/activate.fish
(.venv) yevhenvasko@yevhens-mbp ~/s/e/todo-app-test2 (feature/howto-next-iteration)> curl http://127.0.0.1:3000/
{"status": "mock", "port": 23000}⏎                                                                                                                                                                                                                                                           (.venv) yevhenvasko@yevhens-mbp ~/s/e/todo-app-test2 (feature/howto-next-iteration)> baton signals
No signal data found.
(.venv) yevhenvasko@yevhens-mbp ~/s/e/todo-app-test2 (feature/howto-next-iteration) [0|1]> baton metrics
No metrics data found. Run 'baton up' with telemetry first.

```