```bash
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> deactivate
yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> source ../exemplar.tools/apprentice/.venv/bin/activate.fish
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> apprentice init

============================================================
  Apprentice Setup Wizard
============================================================

Step 1: Task Definition
----------------------------------------
  Task name (snake_case) [classify_ticket]: calculator_eval
  Description [Classify support tickets]: 
  Prompt template (end with blank line):
    Given an arithmetic expression, return the numeric result.
Input: {expression}    
    expression
    
  Input fields (comma-sep) [text]: 
  Output fields (comma-sep) [category, priority]: result
  Evaluator [exact_match/semantic_similarity/llm_judge/regex_match/json_schema_match] (exact_match): 
  Match fields (comma-sep) [result]: 

Step 2: Remote Provider
----------------------------------------
  Provider [anthropic]: anthropic
  API key env var [ANTHROPIC_API_KEY]: 
  Model [claude-sonnet-4-5-20250929]: claude-haiku-4-5-20251001
    [warning] ANTHROPIC_API_KEY not found in environment

Step 3: Local Model
----------------------------------------
  Ollama URL [http://localhost:11434]: 
  Base model [llama3.1:8b]: 

Step 4: Budget
----------------------------------------
  Monthly limit USD [150.00]: 
  Daily limit USD [10.00]: 

Step 5: Generating config...
----------------------------------------
  Config written to: apprentice.yaml
  Config validation: PASSED

============================================================
  Setup complete!
  Config: apprentice.yaml
  Next:   apprentice serve --config apprentice.yaml
============================================================

(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> apprentice serve --config apprentice.yaml
usage: apprentice [-h] [--config CONFIG_PATH] [--json] [-v] {run,status,report,init,serve,pii-ingest,pii-evaluate,ingest} ...
apprentice: error: unrecognized arguments: --config apprentice.yaml
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration) [0|2]> apprentice serve
Loading config from ./apprentice.yaml...
/Users/yevhenvasko/source/exemplar.tools-installer/exemplar.tools/apprentice/src/apprentice/training_data_store.py:59: SyntaxWarning: invalid escape sequence '\-'
  f"task_type must match ^[a-zA-Z0-9_\-]+$, got '{v}'"
/Users/yevhenvasko/source/exemplar.tools-installer/exemplar.tools/apprentice/src/apprentice/training_data_store.py:517: SyntaxWarning: invalid escape sequence '\-'
  f"invalid_task_type: task_type must match ^[a-zA-Z0-9_\-]+$, got '{task_type}'"
{"timestamp": "2026-04-30T23:56:34.134685+00:00", "level": "ERROR", "logger": "root", "message": "Unexpected error: 1 validation error for TaskConfig\n  Value error, prompt_template references unknown input_schema properties: ['expression']. Available properties: ['text'] [type=value_error, input_value={'name': 'calculator_eval...mergency_threshold=0.3)}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/value_error"}
Error: 1 validation error for TaskConfig
  Value error, prompt_template references unknown input_schema properties: ['expression']. Available properties: ['text'] [type=value_error, input_value={'name': 'calculator_eval...mergency_threshold=0.3)}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/value_error
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration) [0|1]> apprentice serve
Loading config from ./apprentice.yaml...
{"timestamp": "2026-04-30T23:57:09.290539+00:00", "level": "ERROR", "logger": "root", "message": "Unexpected error: API key is unresolved: environment variable ANTHROPIC_API_KEY is not set. Set ANTHROPIC_API_KEY in your shell profile or environment."}
Error: API key is unresolved: environment variable ANTHROPIC_API_KEY is not set. Set ANTHROPIC_API_KEY in your shell profile or environment.
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration) [0|1]> export ANTHROPIC_API_KEY=sk-***
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> apprentice serve
Loading config from ./apprentice.yaml...
Apprentice serving on 127.0.0.1:8710
  Health:          http://127.0.0.1:8710/health
  Run:             POST http://127.0.0.1:8710/v1/run
  Status:          http://127.0.0.1:8710/v1/status
  Report:          http://127.0.0.1:8710/v1/report
  Events (WOS):    POST http://127.0.0.1:8710/v1/events
  Feedback (WOS):  POST http://127.0.0.1:8710/v1/feedback
  Recommend (WOS): POST http://127.0.0.1:8710/v1/recommendations
  Skills (WOS):    GET  http://127.0.0.1:8710/v1/skills
  Pipeline interval: 300s
  Security: auth=none
```

```bash
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> deactivate
yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> cd ~/source/exemplar.tools-installer/todo-list2
yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> source ../exemplar.tools/apprentice/.venv/bin/activate.fish
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)>  export ANTHROPIC_API_KEY=sk-***
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> clear
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> apprentice run calculator_eval --input '{"expression": "2 + 2"}'
/Users/yevhenvasko/source/exemplar.tools-installer/exemplar.tools/transmogrifier/src/transmogrifier/profiles.py:15: UserWarning: Field name "register" in "RegisterAccuracy" shadows an attribute in parent "BaseModel"
  class RegisterAccuracy(BaseModel):
Task: calculator_eval
Success: False
Error: 'TaskResponse' object has no attribute 'success'
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> apprentice status
Status Report - 2026-05-01T00:00:05.415371+00:00

Task: calculator_eval
  Phase: bootstrapping
  Confidence: 0.00
  Local Primary: True
  Budget: 0.00 / 10.00
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> apprentice report
{"timestamp": "2026-05-01T00:00:12.559903+00:00", "level": "ERROR", "logger": "root", "message": "Unexpected error: 'SystemReport' object has no attribute 'tasks'"}
Error: 'SystemReport' object has no attribute 'tasks'
```