```
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> deactivate
yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> source ../exemplar.tools/sentinel/.venv/bin/activate.fish
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> sentinel init
Created sentinel.yaml
Initialized .sentinel/
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> sentinel register .
  Registered: root

Registered 1 components from .
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> sentinel report
No incidents recorded.
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> sentinel serve
^C⏎                                                                                                                                                                                        (.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> deactivate
```

```
AI Step

can you help with 5a — Sentinel /Users/yevhenvasko/source/exemplar.tools-installer/howto.md
The Sentinel step is simple — four commands in sequence:

Step 1 — Activate:


source ../exemplar.tools/sentinel/.venv/bin/activate.fish
Step 2 — Initialize (creates sentinel.yaml and .sentinel/ in your project):


sentinel init
Step 3 — Register your Pact components (imports PACT keys from root.py):


sentinel register .
Step 4 — View incident report:


sentinel report
Step 5 — Optionally start the HTTP watcher (leave it running in a terminal to watch logs):


sentinel serve
Step 6 — Deactivate when done:


deactivate
Run from your todo-list2/ directory. Paste any output here if something errors and I'll help debug.

what is it "sentinel serve"
sentinel serve starts an HTTP API that watches your application logs in real-time. When it sees errors in the logs, it:

Matches them to the PACT key embedded in the code (e.g. PACT:481349:root:create_task)
Attributes the error to the specific component that caused it
Records it as an incident
Over time, tightens the contracts so that error class can't recur
For your project it's not very useful right now because the app isn't running and generating real logs. You can skip it — sentinel init, sentinel register ., and sentinel report are enough to complete the step.

```