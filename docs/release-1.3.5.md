# TRACE v1.3.5 — local completion candidate

This checkout and local installation are the v1.3.5 candidate. It is not a
published GitHub release; v1.3.4 remains the last published version.

- The primary Codex dashboard reuses the requested monitor UI on a separate
  loopback listener. Claude files, server and disk map remain separate.
- Global guidance is concise, task-scoped and model-neutral in execution. The
  user's everyday preference is GPT-6.1 Sol; Astra is for demanding user-selected
  work. Existing model/effort and two-child settings are preserved.
- Conditional native delegation has bounded ownership, integration, validation
  and failure handling. There is no new agent daemon or model benchmark.
- Ponytail is pinned to v5.3.2 commit
  `16352ac229eb08a9598dcae48fe9f2b342567d86`. Its reviewed SKILL.md only adds `off`
  to the argument hint compared with the old payload. Explicit-only invocation
  and task scope remain. Claude session import, hooks and board tooling are absent.
- RTK 1.0.1 uses the Apache-2.0 OSS assets on all five supported platforms.
  The executable remains `rtk`; edition-specific archive selection preserves old
  standard-edition receipts and restore behavior. The runner keeps telemetry off,
  avoids native hook rewriting and retains one previous owned binary.
- RTK 1.0's schema changes are isolated in TRACE's private history.db through a
  process-local override. No shared history is copied, merged or deleted. The
  dashboard labels the boundary and does not add old shared totals to new totals.
- Stable standalone CLI 0.164.0 is reviewed. The observed Windows executable is
  app-managed preview 0.164.0-alpha.11.1. It is preserved, not overwritten or
  duplicated merely to match a release number. The app updater reported current.
- Repeated RTK routing/update prose is consolidated into its conditional guide.
  Historical release notes remain historical; current entry points use the new UI.

Owned install verification and runtime checks are distinct from new-session model
behavior, actual UI execution, cross-platform CI and publication. Actual results
are recorded in the private routine record; no future success is predeclared here.
Exact old report artifacts and historical diagram diagnostics remain retained
where execution policy blocked deletion. No retry through another tool is allowed.

The existing daily heartbeat now supports host-approved native refresh of enrolled
installed plugins, with matching 24-hour owner checks reused. App-owned runtimes
remain owner-managed. The Codex-only dashboard projects package/skill identities,
dated account quota percentages and approved MCP metadata observations; it excludes
credentials, account balances and raw sessions. See [update operations](software-updates.md).
The source collector's `--summary` bounds routine output while retaining full
private evidence and unresolved source candidates. No extra global rule, hook,
scheduler or automatic model switching is introduced.

Sources: [Ponytail v5.3.2](https://github.com/DietrichGebert/ponytail/releases/tag/v5.3.2),
[RTK 1.0.1](https://github.com/rtk-ai/rtk/releases/tag/v1.0.1),
[RTK edition build](https://github.com/rtk-ai/rtk/blob/v1.0.1/Cargo.toml),
[RTK schema](https://github.com/rtk-ai/rtk/blob/v1.0.1/src/core/tracking.rs),
[Codex 0.164.0](https://github.com/openai/codex/releases/tag/rust-v0.164.0).
