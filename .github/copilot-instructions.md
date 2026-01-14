**Purpose**

This file gives focused, actionable guidance for AI coding agents working on the Phone-Book-Management-System repository. It documents the runtime entry points, data layout, common patterns, and safe editing practices discovered from the codebase.

**Big picture**

- **Runtime:** The app is a small Flask server. The primary entry point is [System/app.py](System/app.py). Run locally with `python System/app.py` (starts on 127.0.0.1:5501, debug=True).
- **Templates & front-end:** HTML templates live under the app root `System/templates/` (examples: [System/templates/user/contact_list_dashboard_1/code.html](System/templates/user/contact_list_dashboard_1/code.html)). The server renders templates via `render_template()`.
- **Data flow:** Contacts are stored as JSON/CSV under [System/test_user_data/contacts.json](System/test_user_data/contacts.json). Server routes read/write this file directly. Search/load utilities under [System/function/](System/function/) provide programmatic access.

**Key components**

- `System/app.py` — Flask routes and small API endpoints (load all, search, sort_apply, delete). Prefer changing behaviour here only when adjusting API semantics.
- `System/function/search.py` — `ContactSearcher` class and legacy wrappers (`search_by_name`, `load_all`). Use the OOP class for new logic; maintain legacy wrappers for compatibility.
- `System/function/sorter.py` — `ContactsSorter` handles JSON/CSV load, sort, and save logic. Note: phone sorting extracts digits and converts to int.
- `System/function/delete.py` — `ContactDeleter` class and legacy `delete_item` wrapper.

**Project-specific conventions & patterns**

- Backward-compatibility wrappers: many modules expose both an OOP class (preferred) and top-level legacy functions (used by `app.py`). When refactoring, update both where appropriate.
- Data files are treated as canonical: editing contact persistence must preserve UTF-8 (`ensure_ascii=False`) and indentation (indent=2) to keep human-editable formatting.
- Routes and responses sometimes include messages in Vietnamese. Preserve existing message shapes when modifying APIs (JSON keys like `success`, `message`, or error objects).
- Optional dependency pattern: `app.py` tries `from function.sorter import ContactsSorter` inside a try/except — code should support absence of the sorter gracefully.

**Integration points & checks**

- File reads/writes: most critical paths read `System/test_user_data/contacts.json`. Any change that mutates this file should be robust to missing files and use atomic writes where possible.
- Static/test files: `app.py` exposes `/test_user_data/<path:filename>` using `send_from_directory` rooted at the app root. Use this when adding test fixtures.
- Templates: front-end expects certain JSON shapes from `/api/contacts` and `/api/search`. Confirm shape compatibility when changing endpoints.

**Developer workflows**

- Run locally: `python System/app.py` from repository root. The server binds to port `5501` by default.
- There is no test harness present; changes should be verified by running the server and exercising endpoints manually or with small scripts that read/write `System/test_user_data/contacts.json`.

**Recommended editing guidelines for AI agents**

- Small, targeted patches: prefer modifying `System/function/*` classes to implement logic, then update `System/app.py` to call the refined APIs.
- Preserve legacy wrappers and API response shapes to avoid breaking the minimal front-end.
- When adding imports or heavy new packages, update the repository with a `requirements.txt` and note run instructions in PR description.
- Avoid changing hard-coded server config (host/port/debug) unless accompanied by a clear migration path or configuration variable.

**Concrete examples**

- To add a new search field, update `ContactSearcher.DEFAULT_FIELDS` in [System/function/search.py](System/function/search.py) and ensure `search()` behavior remains backward-compatible with `search_by_name`.
- To change on-disk contact ordering, update `ContactsSorter.sort_by` in [System/function/sorter.py](System/function/sorter.py) and leave the `sort_apply` route behavior unchanged unless intentionally changing API semantics.

**When in doubt**

- Run the app and verify UI flows in `user/contact_list_dashboard_*` templates before merging changes that affect endpoints.
- Ask the human developer to confirm any change that mutates `contacts.json` in CI or production-like environments.

---
If any section is unclear or you want more examples (API response shapes, typical contact.json sample, or quick verification scripts), tell me which part to expand.
