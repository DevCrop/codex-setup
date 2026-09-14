# Release verification

Date: 2026-09-14. This is configuration validation, not a model-efficiency benchmark.

- Windows/Python 3.14: 19 lifecycle tests, 18 passed and one symlink-creation test skipped because the host denied symlink creation. Windows junction refusal was exercised separately and passed.
- Covered: first install/adoption, idempotency, obsolete-file deletion, config preservation, modified-file conflicts, rollback, simulated write failure, interrupted recovery, path traversal, multiline TOML refusal, and removal of retired config keys.
- Repository validation: JSON/TOML/UTF-8, 222 manifest files and two pinned upstream packages passed. Config keys make 223 deployed managed files in total.
- Actual global application: 11 changes (including two fingerprint-matched old backup removals); subsequent verify passed and second apply was unchanged.
- Codex CLI 0.147.0 debug prompt rendering: global agreement, current project instructions, Archify and Ponytail all present. No model calls. This is not an app UI check or proof of model compliance.
- `--strict-config` cannot be combined with this CLI's debug command; that attempted check was unsupported, not passed. Ordinary debug prompt/catalog loading succeeded.
- Archify global diagram: schema/showcase validation 9/9; browser containment checked at four sizes. See the portable diagram receipt.
- Native macOS/Linux and real separate-drive Windows execution are not yet established by the local tests. GitHub CI runs lifecycle tests on Windows, macOS and Linux with Python 3.11 and 3.14.
- No actual product project selected: project-specific SCSS/TS behavior and project flow remain pending project onboarding.
- No login credentials copied, API model calls, model benchmark, or measured subscription saving claim.

Open the app's Personalization settings and compare with the deployed global AGENTS.md in a fresh task. The documented relationship is not a claim that the UI was inspected in this run.
