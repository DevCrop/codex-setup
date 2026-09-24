# TRACE v1.1 release verification

Date: 2026-09-21. This is configuration/lifecycle verification, not a model benchmark.

## v1.1.2 maintenance — 2026-09-24

- Approved `sol` preset now selects `gpt-6-sol` with `medium`. Base user model and both Astra presets are unchanged.
- Restored the installed agreement's missing final newline only, after confirming all other bytes match. No instruction policy was added.
- npm stable dist-tag and [official changelog](https://learn.chatgpt.com/docs/changelog) both identified CLI 0.156.1. Updated the existing npm CLI from 0.147.0 to that exact version; `codex --version` and ChatGPT `login status` succeeded. This is a host CLI update, not a desktop app upgrade or a mandatory automatic update on other machines. Roll back the CLI separately with `npm install -g @openai/codex@0.147.0` if necessary.
- Repository integrity, 225-file deployment verification and unchanged repeat application passed. No installer logic changed, model calls or benchmarks were run. Help output is not proof of model execution.
- Source refresh succeeded for all 13 endpoints. Reviewed exact-hash typography, example, repository-statistics and unrelated blog candidates were resolved locally. GPT-6 selection guidance was reviewed; inheritance remains unchanged. Release-feed remainder (R27) and Archify upstream adoption remain pending: the latest commit title does not establish the safety of all intervening revisions. Neither upstream skill was upgraded.
- One managed restore point now restores the v1.1.1 profile state; it does not roll back npm. Authentication, project files and caches were not migrated or removed.

Sources: [model selection](https://learn.chatgpt.com/docs/models#pick-a-reasoning-effort), [CLI installation](https://learn.chatgpt.com/docs/codex/cli). Sol Medium is the documented starting point, not a measured optimum for every task.

## v1.1.1 documentation follow-up

Added a human-facing skill selection guide and refined one agreement bullet to
use task-appropriate checks with a clear stopping condition. Installer code and
upstream packages are unchanged. Repository integrity and current-host verification
passed; exactly one managed file changed and repeated apply was unchanged. The
user explicitly selected Ponytail in the desktop conversation and its full skill
attachment was received, establishing explicit loading on this host. Archify
invocation and task performance were not exercised by this documentation change.
The previous restore point now targets v1.1.0; use that checkout after rollback.

## v1.1.0 evidence

- Global agreement, normalized UTF-8/LF: 4,334 → 1,458 bytes; whitespace-delimited words: 599 → 193. These are text-size measurements, not measured tokens, subscription savings or performance.
- Windows local Python: 35 tests, 33 passed, two symlink-creation cases skipped because this host does not grant symlink creation. Junction refusal is tested separately. Tests include both-root migration, user-edit conflicts, interrupted recovery, rollback and the complete pinned release payload's install/uninstall/restore.
- Repository integrity: 224 manifest assets plus the existing managed config keys (225 deployed files), 38 references, two unchanged pinned upstream packages. TRACE owns two additional explicit-invocation YAML files separately from upstream hashes.
- Flow: 9/9 showcase checks; four browser viewport containment checks; 1440×900 dark and 2048×1320 light visual review passed. The receipt binds the JSON and HTML. Owned render sidecars were removed.
- SCSS, TS and document review routing examples were reviewed as template guidance. No product project was selected or altered; no actual model-task compliance claim is made.
- Native [CI run 35612633308](https://github.com/DevCrop/codex-setup/actions/runs/35612633308) at code commit 596d10f passed all six Windows/macOS/Linux × Python 3.11/3.14 jobs, including 35 cases with platform-specific skips and repository integrity. Subsequent documentation changes record results only.
- Current-host v1.0.1 → v1.1.0 application at 2026-09-21T14:31:40Z: three instruction/guide writes, two invocation-policy additions and two fingerprint-matched personal-skill removals. No conflicts; 225 managed files verified; repeated apply unchanged. One private restore point exists; no pending transaction. `doctor` found no additional unmanaged skills in the two inspected user skill roots; plugin/system catalogs are outside that inventory.
- Two fresh CLI 0.147.0 `debug prompt-input` processes exited successfully and rendered the new agreement. Ordinary prompt catalogs omitted both explicit-only skills and both retired skills. A textual `$ponytail` request also did not inject its body through this debug command. Explicit runtime invocation therefore remains unverified; this debug renderer is not a model execution or the desktop skill picker. No model calls were made. The app also refreshed this task's supplied global agreement after installation; a newly created desktop task was not tested.
- Source collection: 13/13 endpoints succeeded before deployment; nine unresolved candidates were retained, including the prior Archify revision candidate. None were adopted as part of the monitor run. Last collection success and installed `applied_at` are separate; absent historical application timestamps remain unknown. Candidate relevance review and approval remain required, and unseen/missed historical schedule runs are not asserted successful.

The [Astra guide](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) supports narrower triggers and relevant context. [Build skills](https://learn.chatgpt.com/docs/build-skills) documents the explicit-only policy. Korean responses, model choice, two-child preference and approval-based weekly updates remain user operating choices, not a complete OpenAI preset.

Known limits: whole-home sessions/caches and large artifacts are not cleaned by this release; other personal skills are reported, not deleted. Real separate-drive Windows and a fresh desktop UI task require host validation. Credentials, MCP paths and app state remain local. CLI and upstream versions are not upgraded.

Rollback: run the v1.1 installer `rollback` before another changed deployment replaces its single restore point, then use the v1.0.1 checkout to verify the restored release. User edits after installation are conflicts, never overwritten to obtain a pass. See [operations](operations.md).
