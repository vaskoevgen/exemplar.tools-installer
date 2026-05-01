```bash
can I run app from /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src to test it?
Let me check what Pact actually generated.

Bash List all files in src directory
IN
find /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src -type f | sort

OUT
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src/.pytest_cache/.gitignore
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src/.pytest_cache/CACHEDIR.TAG
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src/.pytest_cache/README.md
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src/.pytest_cache/v/cache/lastfailed
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src/.pytest_cache/v/cache/nodeids
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src/root/__pycache__/root.cpython-312.pyc
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src/root/conftest.py
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/src/root/root.py
Read root.py
Bash List test files
IN
find /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests -type f | sort

OUT
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/__pycache__/contract_test.cpython-312-pytest-9.0.2.pyc
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/contract_test.py
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/contract_test_suite.json
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/emission_test.py
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/goodhart/__pycache__/goodhart_test.cpython-312-pytest-9.0.2.pyc
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/goodhart/goodhart_test.py
/Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/goodhart/goodhart_test_suite.json
root.py is a pure Python library — it has no HTTP server built in. Pact generated the business logic layer (in-memory store, validation, CRUD functions), but not a web server you can curl.

You have two options:

Option A — Run the contract tests (what Pact intended):


cd /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2
PYTHONPATH=src/root pytest tests/root/contract_test.py -v
This verifies all the API behavior works correctly without needing a running server.

Option B — Wrap it in FastAPI to get a real HTTP server you can hit in the browser. That would take ~30 lines of code to wire up the existing create_task, list_tasks, etc. functions to HTTP endpoints.

The task you described (React + Express + PostgreSQL) was supposed to be Node.js, but Pact defaulted to Python. The generated code is correct and testable — it just needs an HTTP adapter if you want to actually run it as a server.

Would you like to run the tests first, or add a FastAPI wrapper to make it runnable?
```

```bash
yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> PYTHONPATH=src/root pytest tests/root/contract_test.py -v
=================================================================================== test session starts ===================================================================================
platform darwin -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0 -- /Users/yevhenvasko/.local/share/uv/tools/pytest/bin/python
cachedir: .pytest_cache
rootdir: /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2
collected 90 items                                                                                                                                                                        

tests/root/contract_test.py::TestTaskUUIDType::test_valid_uuid_v4 PASSED                                                                                                            [  1%]
tests/root/contract_test.py::TestTaskUUIDType::test_rejects_uppercase PASSED                                                                                                        [  2%]
tests/root/contract_test.py::TestTaskUUIDType::test_rejects_non_v4 PASSED                                                                                                           [  3%]
tests/root/contract_test.py::TestTaskUUIDType::test_rejects_invalid_variant PASSED                                                                                                  [  4%]
tests/root/contract_test.py::TestTaskTitleType::test_valid_title PASSED                                                                                                             [  5%]
tests/root/contract_test.py::TestTaskTitleType::test_accepts_500_chars PASSED                                                                                                       [  6%]
tests/root/contract_test.py::TestTaskTitleType::test_rejects_empty PASSED                                                                                                           [  7%]
tests/root/contract_test.py::TestTaskTitleType::test_rejects_whitespace_only PASSED                                                                                                 [  8%]
tests/root/contract_test.py::TestTaskTitleType::test_rejects_leading_trailing_whitespace PASSED                                                                                     [ 10%]
tests/root/contract_test.py::TestTaskTitleType::test_rejects_over_500 PASSED                                                                                                        [ 11%]
tests/root/contract_test.py::TestTaskTitleType::test_single_char PASSED                                                                                                             [ 12%]
tests/root/contract_test.py::TestSentinelType::test_unset_not_none PASSED                                                                                                           [ 13%]
tests/root/contract_test.py::TestSentinelType::test_unset_identity PASSED                                                                                                           [ 14%]
tests/root/contract_test.py::TestValidateCreateTask::test_happy_path_full PASSED                                                                                                    [ 15%]
tests/root/contract_test.py::TestValidateCreateTask::test_strips_whitespace PASSED                                                                                                  [ 16%]
tests/root/contract_test.py::TestValidateCreateTask::test_minimal_request PASSED                                                                                                    [ 17%]
tests/root/contract_test.py::TestValidateCreateTask::test_title_exactly_500 PASSED                                                                                                  [ 18%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_empty_title[] PASSED                                                                                                [ 20%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_empty_title[   ] PASSED                                                                                             [ 21%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_empty_title[\t\n] PASSED                                                                                            [ 22%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_none_title PASSED                                                                                                   [ 23%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_title_too_long PASSED                                                                                               [ 24%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_invalid_priority_value[0] PASSED                                                                                    [ 25%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_invalid_priority_value[-1] PASSED                                                                                   [ 26%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_invalid_priority_value[-100] PASSED                                                                                 [ 27%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_invalid_priority_type PASSED                                                                                        [ 28%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_invalid_due_date[not-a-date] PASSED                                                                                 [ 30%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_invalid_due_date[2025/06/15] PASSED                                                                                 [ 31%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_invalid_due_date[15-06-2025] PASSED                                                                                 [ 32%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_invalid_due_date[2025-13-01] PASSED                                                                                 [ 33%]
tests/root/contract_test.py::TestValidateCreateTask::test_error_invalid_due_date[2025-02-30] PASSED                                                                                 [ 34%]
tests/root/contract_test.py::TestValidateCreateTask::test_valid_leap_day PASSED                                                                                                     [ 35%]
tests/root/contract_test.py::TestValidateUpdateTask::test_happy_path_title PASSED                                                                                                   [ 36%]
tests/root/contract_test.py::TestValidateUpdateTask::test_happy_path_completed PASSED                                                                                               [ 37%]
tests/root/contract_test.py::TestValidateUpdateTask::test_happy_path_clear_due_date PASSED                                                                                          [ 38%]
tests/root/contract_test.py::TestValidateUpdateTask::test_happy_path_set_due_date PASSED                                                                                            [ 40%]
tests/root/contract_test.py::TestValidateUpdateTask::test_happy_path_multiple_fields PASSED                                                                                         [ 41%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_no_fields PASSED                                                                                                    [ 42%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_empty_title[] PASSED                                                                                                [ 43%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_empty_title[   ] PASSED                                                                                             [ 44%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_empty_title[\t] PASSED                                                                                              [ 45%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_title_too_long PASSED                                                                                               [ 46%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_invalid_priority[0] PASSED                                                                                          [ 47%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_invalid_priority[-1] PASSED                                                                                         [ 48%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_invalid_due_date PASSED                                                                                             [ 50%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_invalid_completed[1] PASSED                                                                                         [ 51%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_invalid_completed[0] PASSED                                                                                         [ 52%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_invalid_completed[true] PASSED                                                                                      [ 53%]
tests/root/contract_test.py::TestValidateUpdateTask::test_error_invalid_completed[None] PASSED                                                                                      [ 54%]
tests/root/contract_test.py::TestCreateTask::test_happy_path FAILED                                                                                                                 [ 55%]
tests/root/contract_test.py::TestCreateTask::test_default_priority FAILED                                                                                                           [ 56%]
tests/root/contract_test.py::TestCreateTask::test_validation_error_empty_title FAILED                                                                                               [ 57%]
tests/root/contract_test.py::TestListTasks::test_empty_list FAILED                                                                                                                  [ 58%]
tests/root/contract_test.py::TestListTasks::test_returns_created_tasks FAILED                                                                                                       [ 60%]
tests/root/contract_test.py::TestGetTask::test_happy_path FAILED                                                                                                                    [ 61%]
tests/root/contract_test.py::TestGetTask::test_not_found FAILED                                                                                                                     [ 62%]
tests/root/contract_test.py::TestUpdateTask::test_happy_path_partial_update FAILED                                                                                                  [ 63%]
tests/root/contract_test.py::TestUpdateTask::test_clear_due_date FAILED                                                                                                             [ 64%]
tests/root/contract_test.py::TestUpdateTask::test_toggle_completed FAILED                                                                                                           [ 65%]
tests/root/contract_test.py::TestUpdateTask::test_not_found FAILED                                                                                                                  [ 66%]
tests/root/contract_test.py::TestUpdateTask::test_validation_error FAILED                                                                                                           [ 67%]
tests/root/contract_test.py::TestDeleteTask::test_happy_path FAILED                                                                                                                 [ 68%]
tests/root/contract_test.py::TestDeleteTask::test_not_found FAILED                                                                                                                  [ 70%]
tests/root/contract_test.py::TestDeleteTask::test_double_delete FAILED                                                                                                              [ 71%]
tests/root/contract_test.py::TestTaskToDict::test_happy_path PASSED                                                                                                                 [ 72%]
tests/root/contract_test.py::TestTaskToDict::test_null_due_date PASSED                                                                                                              [ 73%]
tests/root/contract_test.py::TestTaskToDict::test_with_due_date PASSED                                                                                                              [ 74%]
tests/root/contract_test.py::TestTaskToDict::test_snake_case_keys PASSED                                                                                                            [ 75%]
tests/root/contract_test.py::TestTaskFromDict::test_happy_path PASSED                                                                                                               [ 76%]
tests/root/contract_test.py::TestTaskFromDict::test_round_trip PASSED                                                                                                               [ 77%]
tests/root/contract_test.py::TestTaskFromDict::test_round_trip_null_due_date PASSED                                                                                                 [ 78%]
tests/root/contract_test.py::TestTaskFromDict::test_missing_required_field[id] PASSED                                                                                               [ 80%]
tests/root/contract_test.py::TestTaskFromDict::test_missing_required_field[title] PASSED                                                                                            [ 81%]
tests/root/contract_test.py::TestTaskFromDict::test_missing_required_field[created_at] PASSED                                                                                       [ 82%]
tests/root/contract_test.py::TestTaskFromDict::test_invalid_priority_zero PASSED                                                                                                    [ 83%]
tests/root/contract_test.py::TestTaskFromDict::test_invalid_priority_negative PASSED                                                                                                [ 84%]
tests/root/contract_test.py::TestTaskFromDict::test_invalid_empty_title PASSED                                                                                                      [ 85%]
tests/root/contract_test.py::TestGetEndpointContracts::test_returns_exactly_five PASSED                                                                                             [ 86%]
tests/root/contract_test.py::TestGetEndpointContracts::test_methods_and_paths PASSED                                                                                                [ 87%]
tests/root/contract_test.py::TestGetEndpointContracts::test_all_http_status_codes_used PASSED                                                                                       [ 88%]
tests/root/contract_test.py::TestGetEndpointContracts::test_valid_methods PASSED                                                                                                    [ 90%]
tests/root/contract_test.py::TestGetEndpointContracts::test_valid_paths PASSED                                                                                                      [ 91%]
tests/root/contract_test.py::TestGetEndpointContracts::test_post_uses_201 PASSED                                                                                                    [ 92%]
tests/root/contract_test.py::TestInvariants::test_task_is_immutable PASSED                                                                                                          [ 93%]
tests/root/contract_test.py::TestInvariants::test_sentinel_never_in_serialized_task PASSED                                                                                          [ 94%]
tests/root/contract_test.py::TestInvariants::test_uuid_lowercase_format PASSED                                                                                                      [ 95%]
tests/root/contract_test.py::TestInvariants::test_created_at_immutable_after_creation FAILED                                                                                        [ 96%]
tests/root/contract_test.py::TestInvariants::test_create_task_always_completed_false FAILED                                                                                         [ 97%]
tests/root/contract_test.py::TestInvariants::test_unique_ids FAILED                                                                                                                 [ 98%]
tests/root/contract_test.py::TestInvariants::test_http_status_code_enum_values PASSED                                                                                               [100%]

======================================================================================== FAILURES =========================================================================================
_____________________________________________________________________________ TestCreateTask.test_happy_path ______________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
__________________________________________________________________________ TestCreateTask.test_default_priority ___________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
____________________________________________________________________ TestCreateTask.test_validation_error_empty_title _____________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
______________________________________________________________________________ TestListTasks.test_empty_list ______________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
________________________________________________________________________ TestListTasks.test_returns_created_tasks _________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
_______________________________________________________________________________ TestGetTask.test_happy_path _______________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
_______________________________________________________________________________ TestGetTask.test_not_found ________________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
______________________________________________________________________ TestUpdateTask.test_happy_path_partial_update ______________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
___________________________________________________________________________ TestUpdateTask.test_clear_due_date ____________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
__________________________________________________________________________ TestUpdateTask.test_toggle_completed ___________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
______________________________________________________________________________ TestUpdateTask.test_not_found ______________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
__________________________________________________________________________ TestUpdateTask.test_validation_error ___________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
_____________________________________________________________________________ TestDeleteTask.test_happy_path ______________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
______________________________________________________________________________ TestDeleteTask.test_not_found ______________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
____________________________________________________________________________ TestDeleteTask.test_double_delete ____________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
_________________________________________________________________ TestInvariants.test_created_at_immutable_after_creation _________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
_________________________________________________________________ TestInvariants.test_create_task_always_completed_false __________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
_____________________________________________________________________________ TestInvariants.test_unique_ids ______________________________________________________________________________
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted
==================================================================================== warnings summary =====================================================================================
tests/root/contract_test.py:298
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/contract_test.py:298: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

tests/root/contract_test.py:335
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/contract_test.py:335: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

tests/root/contract_test.py:358
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/contract_test.py:358: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

tests/root/contract_test.py:383
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/contract_test.py:383: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

tests/root/contract_test.py:442
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/contract_test.py:442: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

tests/root/contract_test.py:653
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/contract_test.py:653: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

tests/root/contract_test.py:664
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/contract_test.py:664: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

tests/root/contract_test.py:671
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/tests/root/contract_test.py:671: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================================================================================= short test summary info =================================================================================
FAILED tests/root/contract_test.py::TestCreateTask::test_happy_path - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestCreateTask::test_default_priority - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestCreateTask::test_validation_error_empty_title - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestListTasks::test_empty_list - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestListTasks::test_returns_created_tasks - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestGetTask::test_happy_path - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestGetTask::test_not_found - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestUpdateTask::test_happy_path_partial_update - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestUpdateTask::test_clear_due_date - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestUpdateTask::test_toggle_completed - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestUpdateTask::test_not_found - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestUpdateTask::test_validation_error - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestDeleteTask::test_happy_path - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestDeleteTask::test_not_found - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestDeleteTask::test_double_delete - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestInvariants::test_created_at_immutable_after_creation - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestInvariants::test_create_task_always_completed_false - Failed: async def functions are not natively supported.
FAILED tests/root/contract_test.py::TestInvariants::test_unique_ids - Failed: async def functions are not natively supported.
======================================================================== 18 failed, 72 passed, 8 warnings in 0.08s ===================================================================
```