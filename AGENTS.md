# AGENTS.md

## Project layout

Two independent packages, no workspace tooling:

| Package | Dir | Package manager | Entry |
|---|---|---|---|
| Backend | `backend/` | `uv` (pyproject.toml) | `backend/main.py` → `uvicorn backend.main:app` |
| Frontend | `frontend/` | `npm` (package.json) | `frontend/src/main.ts` → `npm run dev` |

All commands below run from repo root unless `frontend/` is specified.

## Essential commands

```bash
# ── Install ──
uv sync                        # backend deps (uv.lock is gitignored — generated locally)
cd frontend && npm install     # frontend deps

# ── Dev servers ──
uv run uvicorn backend.main:app --reload   # backend (port 8000)
cd frontend && npm run dev                 # frontend (port 5173)

# ── Lint / format ──
uv run ruff check backend/                 # backend lint
uv run ruff format --check backend/        # backend format check
uv run ruff format backend/                # backend format (apply)
uv run python scripts/lint_rules.py --fail backend/   # custom lint (no lambda, no nested comprehensions)
cd frontend && npm run lint                # frontend lint
cd frontend && npm run format              # frontend format (prettier)

# ── Type-check ──
cd frontend && npm run type-check          # vue-tsc --noEmit
# (pyright runs via IDE; no standalone backend typecheck script)

# ── Build ──
cd frontend && npm run build               # typecheck + vite build → frontend/dist/

# ── Tests ──
uv run pytest                              # all backend tests (cov gate: 40%)
uv run pytest --no-cov -ra --tb=short      # quick run, no coverage
uv run pytest -m "not integration"         # unit only
uv run pytest backend/tests/unit/ -v       # unit dir only
uv run pytest backend/tests/integration/ -v   # integration dir
uv run pytest -k "auth" -v                 # keyword match
uv run pytest backend/tests/unit/test_auth.py -v   # single file
# Frontend: no test runner configured yet (test dirs exist but are empty)
```

## Architecture: microkernel + plugins

`backend/core/` is the "never-changing" kernel. All features live under `backend/plugins/`.

Boot sequence in `backend/core/__init__.py` `create_app()`:
1. Logging → 2. DB init → 3. ServiceContainer → 4. Plugin activation (DAG-sorted by `requires`/`optional`) → 5. Plugin services registered → 6. Middleware → 7. Startup hooks (Alembic migrations auto-run, schema validation, config seeding) → 8. Mount `frontend/dist/` as static files if it exists

Plugins auto-discovered from `backend/plugins/` (no manual registration). Each is self-contained with its own `__init__.py` (plugin class + self-registration), `routes.py`, `services.py`, `models.py`.

## Key quirks

- **Alembic migrations run automatically at startup** — no separate CLI step. Runs in the `on_event("startup")` hook.
- **uv.lock is in .gitignore** — it's regenerated locally, not committed. CI uses `uv sync --frozen` which requires the lockfile; make sure to generate it once before CI-relevant changes.
- **Custom lint rules** (`scripts/lint_rules.py`): no `lambda` (3 whitelisted patterns: SQLAlchemy defaults, `iter()` sentinel, DI container factories) and no nested comprehensions deeper than 1 level.
- **No lambda, use named functions** — enforced by the custom lint. Plan for this when writing callbacks.
- **Database**: SQLite + aiosqlite for dev, PostgreSQL + asyncpg for production. In-memory SQLite tests use `StaticPool` to share the connection across sessions.
- **Config layering**: `.env` file < environment variables < database (with TTL cache). Dynamic config via `config_mgmt` plugin.
- **Chinese comments/docs**: all code comments and documentation are in Chinese. Commit messages follow Conventional Commits (`feat:`, `fix:`, etc.).
- **Frontend code splitting by role**: `blog/` (public), `platform/` (authenticated), `admin/` (admin). Vite dynamic imports per role; unauthenticated users never load admin chunks.
- **Backend serves frontend**: if `frontend/dist/` exists, FastAPI mounts `StaticFiles` at `/`. Production uses Nginx reverse proxy instead.
- **Alibaba Cloud ecosystem**: Docker images pushed to Aliyun Container Registry (Shanghai). PyPI uses Aliyun mirror.

## CI (`.github/workflows/ci.yml`)

Pipeline stages: `backend-lint` → `backend-test` → `frontend-check` → `frontend-test` → `security-scan` → `gate` → (`build` → `deploy`)

- Tags `v*` trigger build+deploy
- PR merges to `master` auto-increment patch version, then build+deploy
- Plain pushes to `master` (no tag) run lint/test only, no build

## References

- `backend/tests/TEST_STRATEGY.md` — full test documentation and fixture inventory
- `frontend/docs/api-call-policy.md` — frontend API error handling conventions
- `frontend/src/README.md` — frontend module structure rules
- `docs/` — Chinese architecture/design documents
- `README.md` — project overview, plugin table, quick start
- `CONTRIBUTING.md` — commit conventions, PR flow
