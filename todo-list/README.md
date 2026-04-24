# Todo List

A web application for managing personal tasks — create, complete, and delete tasks.

**Stack:** Python + FastAPI backend · PostgreSQL database · Vanilla JS single-page frontend

---

## Quick start

### 1. Start PostgreSQL

```bash
docker run -d \
  --name todo-pg \
  -e POSTGRES_USER=todo \
  -e POSTGRES_PASSWORD=todo \
  -e POSTGRES_DB=todo_dev \
  -p 5432:5432 \
  arm64v8/postgres:17-alpine

# Wait until ready
until docker exec todo-pg pg_isready -U todo; do sleep 1; done
```

> The app auto-creates the `tasks` table on first startup.

### 2. Install dependencies

```bash
cd todo-list
python3 -m venv .venv
source .venv/bin/activate   # fish: source .venv/bin/activate.fish
pip install fastapi uvicorn psycopg2-binary
```

### 3. Run the backend

```bash
export DATABASE_URL=postgresql://todo:todo@127.0.0.1:5432/todo_dev
uvicorn src.root.root.main:app --reload --port 8000
```

### 4. Open the app

Visit [http://localhost:8000](http://localhost:8000) in your browser.

---

## API reference

All requests and responses use JSON. Errors return `{"detail": "message"}`.

| Method | Path | Body | Response | Description |
|--------|------|------|----------|-------------|
| `GET` | `/` | — | `text/html` | Serve the frontend |
| `GET` | `/tasks` | — | `Task[]` | List all tasks |
| `GET` | `/tasks?completed=true` | — | `Task[]` | List completed tasks |
| `GET` | `/tasks?completed=false` | — | `Task[]` | List active tasks |
| `POST` | `/tasks` | `{"title": "string"}` | `Task` (201) | Create a task |
| `PATCH` | `/tasks/{id}` | `{"completed": true}` | `Task` | Toggle completion |
| `DELETE` | `/tasks/{id}` | — | 204 No Content | Delete a task |

### Task object

```json
{
  "id": 1,
  "title": "Buy groceries",
  "completed": false,
  "created_at": "2026-04-24T12:00:00+00:00"
}
```

---

## Project structure

```
todo-list/
├── src/root/root/
│   ├── main.py          ← FastAPI backend (single file)
│   └── static/
│       └── index.html   ← Frontend (single file, no build step)
├── tests/root/
│   └── contract_test.py ← Contract tests (39 tests)
├── README.md
└── pact.yaml
```

---

## Run tests

```bash
PYTHONPATH=src python3 -m pytest tests/root/contract_test.py -v
```

---

## Frontend features

- Add tasks with the input field (press Enter or click Add)
- Check/uncheck the checkbox to mark tasks complete
- Click Delete to remove a task
- Filter buttons: **All** / **Active** / **Completed**
