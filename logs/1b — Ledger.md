```bash
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> deactivate
yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> source ../exemplar.tools/ledger/.venv/bin/activate.fish
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> ledger init
```

```
Use AI help

Good. Here are your next steps:

Step 1 — Add a backend to ledger.yaml (don't use the CLI command, it has a bug):

Edit ledger.yaml
Added 2 lines
Step 2 — Create a schema for your tasks table. Based on your constrain session (CRUD + priorities + due dates):

Write tasks.yaml
46 lines
name: tasks
version: 1

fields:
  - name: id
    field_type: uuid
    classification: PUBLIC
    nullable: false
    annotations:
      - name: immutable
      - name: not_null

  - name: title
    field_type: varchar(255)
    classification: PUBLIC
    nullable: false
    annotations:
      - name: not_null

  - name: completed
    field_type: boolean
    classification: PUBLIC
    nullable: false
    annotations:
      - name: not_null

  - name: priority
    field_type: integer
    classification: PUBLIC
    nullable: false
    annotations:
      - name: not_null

  - name: due_date
    field_type: date
    classification: PUBLIC
    nullable: true

  - name: created_at
    field_type: timestamptz
    classification: PUBLIC
    nullable: false
    annotations:
      - name: immutable
      - name: not_null
Step 3 — Register and validate (run in your terminal with the ledger venv active):


ledger schema add schemas/tasks.yaml
ledger schema validate
Step 4 — Export obligations (stubs, but run them to complete the step):


ledger export --format pact
ledger export --format arbiter
Then deactivate when done.

The schema I created matches what you described: title (NOT NULL), completed flag, priority (integer, NOT NULL with default implied), and optional due_date. You can tweak the priority field type or values to suit your design.
```

```bash
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> ledger schema add schemas/tasks.yaml
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> ledger schema validate
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> ledger export --format pact
{'contracts': []}
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> ledger export --format arbiter
{'contracts': []}
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> deactivate
yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> 
```