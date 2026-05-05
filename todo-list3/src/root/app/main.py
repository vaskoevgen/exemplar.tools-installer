"""FastAPI application factory with lifespan-managed connection pool."""
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any, Generator

import psycopg2
import psycopg2.pool
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.models import (
    DeleteConfirmation,
    ErrorDetail,
    HealthResponse,
    TaskCreateRequest,
    TaskResponse,
    TaskStatus,
    TaskUpdateRequest,
)
from app.db.helpers import (
    db_create_task,
    db_delete_task,
    db_get_task,
    db_list_tasks,
    db_update_task,
)

_PACT_KEY = "PACT:481349:root"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


def create_app(
    database_url: str | None = None,
    frontend_origin: str | None = None,
) -> FastAPI:
    """Application factory. Creates FastAPI app with lifespan pool management."""
    db_url = database_url or os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/taskdb"
    )
    fe_origin = frontend_origin or os.environ.get(
        "FRONTEND_ORIGIN", "http://localhost:5173"
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """CROSS-TIER-07: Pool init on startup, close on shutdown."""
        _log("info", "Initializing connection pool")
        try:
            pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=10,
                dsn=db_url,
            )
            app.state.pool = pool
            _log("info", "Connection pool initialized")
        except psycopg2.OperationalError as e:
            _log("error", f"Failed to initialize connection pool: {e}")
            app.state.pool = None

        # Run init.sql for schema setup
        if app.state.pool is not None:
            _init_schema(app.state.pool)

        yield

        if hasattr(app.state, "pool") and app.state.pool is not None:
            app.state.pool.closeall()
            _log("info", "Connection pool closed")

    app = FastAPI(title="Task Management API", lifespan=lifespan)

    # Serve static files and root UI
    _static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.isdir(_static_dir):
        app.mount("/static", StaticFiles(directory=_static_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def root_ui():
        return FileResponse(os.path.join(_static_dir, "index.html"))

    # CROSS-TIER-05: CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[fe_origin],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # -----------------------------------------------------------------------
    # Dependency: get DB connection from pool
    # -----------------------------------------------------------------------
    def get_db(request: Request) -> Generator:
        pool = getattr(request.app.state, "pool", None)
        if pool is None:
            raise HTTPException(status_code=500, detail="Database connection error")
        conn = None
        try:
            conn = pool.getconn()
            yield conn
        except psycopg2.pool.PoolError:
            raise HTTPException(status_code=500, detail="Database connection error")
        finally:
            if conn is not None:
                pool.putconn(conn)

    # -----------------------------------------------------------------------
    # Routes
    # -----------------------------------------------------------------------
    @app.get("/health", response_model=HealthResponse)
    async def health_check() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/tasks", response_model=list[TaskResponse])
    async def list_tasks(conn: Any = Depends(get_db)) -> list[TaskResponse]:
        try:
            rows = db_list_tasks(conn)
            return [TaskResponse(**row) for row in rows]
        except Exception as e:
            _log("error", f"db_list_tasks error: {e}")
            raise HTTPException(status_code=500, detail="Database connection error")

    @app.post("/tasks", response_model=TaskResponse, status_code=201)
    async def create_task(
        task: TaskCreateRequest, conn: Any = Depends(get_db)
    ) -> TaskResponse:
        try:
            row = db_create_task(
                conn,
                title=task.title,
                description=task.description,
                status=task.status.value,
            )
            return TaskResponse(**row)
        except Exception as e:
            _log("error", f"db_create_task error: {e}")
            raise HTTPException(status_code=500, detail="Database connection error")

    @app.get("/tasks/{task_id}", response_model=TaskResponse)
    async def get_task(task_id: int, conn: Any = Depends(get_db)) -> TaskResponse:
        try:
            row = db_get_task(conn, task_id)
        except Exception as e:
            _log("error", f"db_get_task error: {e}")
            raise HTTPException(status_code=500, detail="Database connection error")
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskResponse(**row)

    @app.put("/tasks/{task_id}", response_model=TaskResponse)
    async def update_task(
        task_id: int, task: TaskUpdateRequest, conn: Any = Depends(get_db)
    ) -> TaskResponse:
        # CROSS-TIER-12: Only update fields present in the request body
        fields = {}
        if "title" in task.model_fields_set:
            fields["title"] = task.title
        if "description" in task.model_fields_set:
            fields["description"] = task.description
        if "status" in task.model_fields_set:
            if task.status is not None:
                fields["status"] = task.status.value

        try:
            row = db_update_task(conn, task_id, fields)
        except Exception as e:
            _log("error", f"db_update_task error: {e}")
            raise HTTPException(status_code=500, detail="Database connection error")

        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskResponse(**row)

    @app.delete("/tasks/{task_id}", response_model=DeleteConfirmation)
    async def delete_task(
        task_id: int, conn: Any = Depends(get_db)
    ) -> DeleteConfirmation:
        try:
            result = db_delete_task(conn, task_id)
        except Exception as e:
            _log("error", f"db_delete_task error: {e}")
            raise HTTPException(status_code=500, detail="Database connection error")

        if result is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return DeleteConfirmation(detail="Task deleted", id=result["id"])

    return app


def _init_schema(pool: psycopg2.pool.ThreadedConnectionPool) -> None:
    """Run init.sql against the database if file exists."""
    init_paths = ["init.sql", "database/init.sql", "db/init.sql"]
    init_sql_path = None
    for p in init_paths:
        if os.path.isfile(p):
            init_sql_path = p
            break
    if init_sql_path is None:
        _log("warning", "init.sql not found, skipping schema init")
        return

    conn = pool.getconn()
    try:
        conn.autocommit = True
        cur = conn.cursor()
        with open(init_sql_path, "r") as f:
            cur.execute(f.read())
        cur.close()
        _log("info", "Schema initialized from init.sql")
    finally:
        conn.autocommit = False
        pool.putconn(conn)


# Module-level app for uvicorn
app = create_app()
