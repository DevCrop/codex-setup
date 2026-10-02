# Operations

Start from the repository README and installer help for executable commands. Resolve paths from the script location, explicit root and supported user directories; never assume a drive letter or current shell directory. Honor CODEX_HOME. Authenticate separately on each host with the installed CLI's supported ChatGPT login flow; do not copy auth files into this repository.

## Managed lifecycle

Run plan before apply. Inspect additions, changes, removals and conflicts. Apply only approved owned files; preserve user edits, permissions, model selection, MCP secrets and unrelated settings. Verify after apply. Keep one previous managed state in the local state directory for rollback, not backup copies in active paths. On failure restore that state and report conflicts. Installer-owned temporary artifacts are cleaned after success; application caches, sessions and credentials are not general cleanup targets.

## Profiles and fresh sessions

The optional CLI profiles are `sol`, `astra` and `astra-deep`. They are separate `.config.toml` files selected with `--profile`. Check host model support; the app composer remains user-controlled. A parsed configuration is not proof of a fresh session's effective instruction or model behavior. Inspect new-session loading separately. Legacy overrides and project trust can affect effective configuration.

## Daily global maintenance

Use one operating host and its existing global setup heartbeat, daily at 10:00
in the configured host timezone. On the designated host, the user has approved
daily checks and stable Codex CLI/RTK updates. This is local operating policy,
not an OpenAI default or authorization for every computer. It covers official
release comparison, global installation health and repository deployment status.
Keep separately authorized project cleanup schedules separate; do not create a
duplicate monitor or expand cleanup scope through this global routine.
Machine-specific checkout paths and project registrations belong in the host's
automation settings or private local state, never in shared policy. A new computer
does not inherit monitoring ownership merely by installing this repository.

### Working routine

| Trigger | Scope | Completion |
|---|---|---|
| First project registration | Inspect applicable instructions, runtime, existing checks and project flow if present | Record findings and unknowns; do not invent missing configuration or diagrams |
| Normal implementation | Relevant project rules and affected code | Run task-appropriate acceptance checks; preserve unrelated edits |
| Daily global heartbeat | Official releases, managed installation and repository deployment | Apply already authorized stable CLI/RTK updates; report only meaningful changes, failures or required user action |
| Registered project review | Relevant project deltas when project review is authorized | Inspect changed content and preserve project-specific rules |
| Architecture/dependency/rule change | Affected contracts, documentation and verification commands | Review semantic consistency and run relevant checks after an authorized change |
| Approved maintenance | Exact reviewed files and versions | Apply, verify, account for removals and preserve rollback |

### Daily sequence and cost controls

1. Run `python -B scripts/check_updates.py`; inspect new and retained candidates.
2. Run `python -B scripts/setup.py verify`. Treat unmanaged skill findings separately
   from managed-file integrity; neither proves whole-home cleanliness or runtime loading.
3. Compare installed Codex CLI and RTK versions with their official stable releases.
   Update only tools covered by the host's existing authorization, using official
   installation procedures and available integrity checks. Preserve hooks, selected
   model/reasoning effort, authentication and user changes. Use the desktop app's
   update check to report restart/Store actions; a CLI update is separate.
   Verify resulting versions and a relevant RTK invocation.
4. When project review is separately authorized, check path availability, Git HEAD and working-tree
   changes, including relevant untracked instructions. Inspect only changed rules,
   configuration, package/runtime pins, scripts and affected source. Check the selected
   runtime against a project pin when present. An unchanged dirty filename list is
   not evidence of unchanged content: compare content/diff fingerprints too.
5. Only meaningful changes or failures trigger deeper review. Do not reread the
   entire reference inventory or project. Default to direct review; use bounded
   delegation only when independent work justifies it. Do not schedule model benchmarks.
6. Do not execute arbitrary project scripts, installs, builds, browser tests or
   cleanup during the global heartbeat. Run task-appropriate checks for authorized
   maintenance; recommend the smallest checks for other candidates. Missing paths and failed collection
   stay unknown/failed, not healthy. An offline host cannot guarantee scheduled execution.

Keep one current local routine record beside source-monitor state (not in project
files). Track last attempt, last successful collection, last substantive review,
last policy application, per-project inspected commit/content fingerprint and
unresolved findings. Each finding has a stable identity, evidence, impact, proposed
action, validation and last-notified fingerprint. Retain unresolved findings across
unchanged checks; do not equate a new collection timestamp with resolution. Keep
history in Git where appropriate, not dated operational copies. Never store source
diff bodies, credentials or authentication parameters in the routine record.

Stay quiet when unchanged, non-actionable or already reported without material new
information. Notify on new actionable findings, changed severity/impact, confirmed
resolution or a failure requiring action. Record known missed runs honestly; do not
infer missed executions from timestamp gaps alone. A file hash change is a trigger
for review, not proof of a policy change or a fault.

Prepare exact candidate edits, evidence and validation before requesting approval.
The existing authorization covers stable CLI/RTK upgrades and narrowly scoped
compatibility repairs, with backup, minimal changes and verification. Publish a
verified repository PR only when Git publication is also authorized on that host.
New optional features, skills, plugins, permission expansion and major structural
changes require separate approval. Never overwrite project docs or perform project
cleanup during a global update. Update only affected Archify diagrams during
explicitly approved work. Execution-policy restrictions and user edits remain binding.

Source reports retain `pending` candidates across unchanged fetches. The success
marker records collection time; installed state `applied_at` records deployment,
not source acceptance. Older records without timestamps remain unknown. After
review, use `check_updates.py --resolve ID --expected-sha HASH --reason TEXT` to
record a decision about that exact candidate; this never applies policy. Typography,
GitHub statistics and example model names alone do not justify policy edits.
Quote styles are normalized; other relevance decisions require review. Report
known missed runs honestly; a timestamp alone cannot establish scheduler history.

## Manifest migration

Manifest schema 2 adds optional `root: personal_skills` to file/retirement entries;
absent `root` means Codex home. Local keys use `@personal/` for the former and retain
v1 keys for Codex home. Records/journals bind both roots. V1 records remain readable.
After rollback to v1.0.1, use its checkout to verify that version. A blocked deletion
remains unresolved; do not bypass the restriction.

## Troubleshooting and portability

Record reusable failures in the existing troubleshooting index: symptoms, affected
environment/version, confirmed cause versus hypothesis, non-destructive diagnosis,
resolution, verification, side effects/restore, evidence and last verified date.
Do not universalize historical workarounds or record authentication parameters.
Only project-specific incidents belong in the project.

Check C-only Windows, different checkout/home drives, Unicode and spaces, OneDrive paths, execution outside checkout, custom CODEX_HOME, missing/read-only paths and links/junctions. Also verify native macOS/Linux install, repeat install, conflict and rollback behavior before declaring those platforms tested. Simulated paths do not establish native OS support.

Sources: [Configuration and paths](https://learn.chatgpt.com/docs/config-file/config-advanced), [Authentication](https://learn.chatgpt.com/docs/auth), [App settings](https://learn.chatgpt.com/docs/app/settings).
