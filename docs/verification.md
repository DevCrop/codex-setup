# Release verification

Date: 2026-09-14. This is configuration validation, not a model-efficiency benchmark.

- Windows/Python 3.14 local: 20 lifecycle tests, 19 passed and one symlink-creation test skipped because the host denied symlink creation. Windows junction refusal was exercised separately and passed.
- Covered: first install/adoption, idempotency, obsolete-file deletion, config preservation, modified-file conflicts, rollback, simulated write failure, interrupted recovery, path traversal, multiline TOML refusal, and removal of retired config keys.
- Repository validation: JSON/TOML/UTF-8, 222 manifest files, 38 reference records and two pinned upstream packages passed. Config keys make 223 deployed managed files in total.
- Actual global application: 11 changes (including two fingerprint-matched old backup removals); subsequent verify passed and second apply was unchanged.
- Codex CLI 0.147.0 debug prompt rendering: global agreement, current project instructions, Archify and Ponytail all present. No model calls. This is not an app UI check or proof of model compliance.
- `--strict-config` cannot be combined with this CLI's debug command; that attempted check was unsupported, not passed. Ordinary debug prompt/catalog loading succeeded.
- Archify global diagram: schema/showcase validation 9/9; browser containment checked at four sizes. See the portable diagram receipt.
- GitHub CI [run 34855404249](https://github.com/DevCrop/codex-setup/actions/runs/34855404249), code commit 9b23ebe: all six native Windows/macOS/Linux × Python 3.11/3.14 jobs passed. Each runs 20 lifecycle cases with platform-specific skips and repository integrity checks. This does not establish a real product workflow or an actual separate-drive Windows installation.
- The first macOS run revealed system /var symlink rejection; only verified macOS system aliases were permitted, then all six jobs passed. Arbitrary symlinks and Windows junctions remain refused.
- No actual product project selected: project-specific SCSS/TS behavior and project flow remain pending project onboarding.
- No login credentials copied, API model calls, model benchmark, or measured subscription saving claim.
- Source monitoring: initial 12 endpoints fetched successfully; blog discovery subsequently added. Weekly automation `trace` registered for Monday 10:00 local time on this host only, with candidate approval required.
- Active AGENTS.md is 4,334 bytes. No instruction-token or subscription saving has been established; the release adds portability and ownership requirements while avoiding routine full-source loading.

Open the app's Personalization settings and compare with the deployed global AGENTS.md in a fresh task. The documented relationship is not a claim that the UI was inspected in this run.
