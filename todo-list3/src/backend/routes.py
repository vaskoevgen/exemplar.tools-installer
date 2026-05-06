# Re-export from backend.routes for test import compatibility
from backend.routes import *  # noqa: F401,F403
from backend.routes import (
    health_check,
    list_tasks,
    create_task,
    get_task,
    update_task,
    delete_task,
)
