# Experience Log

Lessons learned during Arche development — non-obvious pitfalls, design rationale, and reusable insights.

## How to Contribute

Log an entry immediately when you encounter something worth remembering.

### Entry Criteria

All four must apply:

- **Actual pain** — a bug we fixed, a mistake we made, an ambiguity that caused rework
- **Actionable** — the reader knows exactly what to do differently
- **Non-obvious** — common sense doesn't belong here
- **Reusable** — the same situation could plausibly recur

### Format

Keep it tight — one or two sentences per field:

```
### YYYY-MM-DD: Short imperative title

**What:** What to do (or what went wrong).

**When:** Context — module, trigger, preconditions.

**Why:** Root cause or rationale — the insight behind the fix.

**Lesson:** How to avoid this in the future.
```

---

## Entries

### 2026-06-12: Use `--body-file` in PowerShell for `gh issue create`

**What:** Pass issue body via a temp file (`--body-file`) instead of inline `--body`.

**When:** Creating GitHub Issues from Windows PowerShell with multi-line bodies containing backticks, quotes, or other special characters.

**Why:** PowerShell parses CLI arguments differently from bash — backticks and nested quotes in `--body` trigger syntax errors. `--body-file` bypasses argument parsing entirely.

**Lesson:** On Windows, always use `--body-file <tempfile>` for `gh issue create` with non-trivial bodies. Clean up the temp file afterward.

---

### 2026-06-12: Verify parent status before adding a GitHub Sub-issue

**What:** Check that an issue has no existing parent before adding it as a sub-issue.

**When:** Restructuring issues with GitHub Sub-issues — especially when migrating from an old parent to a new one.

**Why:** GitHub enforces one parent per sub-issue. Adding an issue that already has a parent returns `"Sub issue may only have one parent"`. Closing the old parent does NOT release the relationship.

**Lesson:** Before `addSubIssue`, run `removeSubIssue` from the old parent first. Design the issue hierarchy upfront to avoid mass migration.

---

### 2026-06-10: Never manually delete Alembic migration files

**What:** Don't delete `.sql` migration files under `backend/plugins/*/alembic/`.

**When:** Cleaning up files — migration directories can look like "old" or "generated" files that seem safe to remove.

**Why:** Alembic relies on a complete migration chain to reach the current database version. Missing any file breaks the version chain and prevents startup.

**Lesson:** Migration files are infrastructure, not cache. Use Alembic's own squashing/merging commands if cleanup is needed.

---

### 2026-06-10: CI can't run `generate:api` without a live backend

**What:** In CI, verify `generated.d.ts` exists instead of re-running `npm run generate:api`.

**When:** Frontend CI pipeline — the step that ensures API types are in sync.

**Why:** `npm run generate:api` requires a running backend on port 8000 to fetch the OpenAPI schema. CI doesn't run the backend, so the command would fail. The committed file is the source of truth.

**Lesson:** Build-time code generation that depends on external services needs a CI fallback strategy. File-existence checks are simple and effective.

---

### 2026-06-05: Replace naive-ui components with self-built Ar components

**What:** Build custom Ar* components (ArButton, ArCard, etc.) instead of wrapping or patching naive-ui components.

**When:** A third-party library's rendering behavior (slot wrappers, opinionated CSS, undocumented DOM structure) conflicts with the project's design system.

**Why:** naive-ui's extra wrapper elements cause hard-to-fix layout bugs (e.g., `<span>` wrappers breaking flex alignment). Self-built components give full control over rendering and design language.

**Lesson:** For UI-consistent projects, a self-built component library pays off in the long run. Migrate incrementally — one component at a time, not a big bang.

---

### 2026-06-12: Prefer self-built ArPopconfirm over NPopconfirm workarounds

**What:** Build `ArPopconfirm` as a `src/components/ui/` component to replace `NPopconfirm`.

**When:** A third-party component has a structural rendering issue that can't be cleanly fixed with CSS.

**Why:** CSS hacks for naive-ui's DOM structure are fragile and don't fix the root cause. A self-built component (`position: absolute` + `transform` + Vue `Transition`) is fully controllable and matches the glassmorphism design system.

**Lesson:** When a library component fights your layout, replace it rather than patch around it. Positioning and transition utilities are worthwhile shared infrastructure.
