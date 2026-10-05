# Operations

Start from the repository README and installer help for executable commands. Resolve paths from the script location, explicit root and supported user directories; never assume a drive letter or current shell directory. Honor CODEX_HOME. Authenticate separately on each host with the installed CLI's supported ChatGPT login flow; do not copy auth files into this repository.

## Managed lifecycle

Run plan before apply. Inspect additions, changes, removals and conflicts. Apply only approved owned files; preserve user edits, permissions, model selection, MCP secrets and unrelated settings. Verify after apply. Keep one previous managed state in the local state directory for rollback, not backup copies in active paths. On failure restore that state and report conflicts. Installer-owned temporary artifacts are cleaned after success; application caches, sessions and credentials are not general cleanup targets.

## Profiles and fresh sessions

The optional CLI profiles are `sol`, `astra` and `astra-deep`. They are separate `.config.toml` files selected with `--profile`. Check host model support; the app composer remains user-controlled. A parsed configuration is not proof of a fresh session's effective instruction or model behavior. Inspect new-session loading separately. Legacy overrides and project trust can affect effective configuration.

## Weekly maintenance

Use one operating host and the existing TRACE heartbeat, weekly on Monday at
10:00 in the configured host timezone. It covers source updates, global installation
health, RTK releases and explicitly registered projects; do not create a second project monitor.
Machine-specific checkout paths and project registrations belong in private
`cleanup-projects.json` beside deployment state, never in shared policy. A new computer
does not inherit monitoring ownership merely by installing this repository.

### Working routine

| Trigger | Scope | Completion |
|---|---|---|
| First project registration | Inspect applicable instructions, runtime, existing checks and project flow if present | Record findings and unknowns; do not invent missing configuration or diagrams |
| Normal implementation | Relevant project rules and affected code | Run task-appropriate acceptance checks; preserve unrelated edits |
| Weekly heartbeat | Source changes, managed installation and registered project deltas | Report only new actionable findings or material changes to unresolved findings |
| Architecture/dependency/rule change | Affected contracts, documentation and verification commands | Review semantic consistency and run relevant checks after an authorized change |
| Approved maintenance | Exact reviewed files and versions | Apply, verify, account for removals and preserve rollback |

### Weekly sequence and cost controls

1. Run `python -B scripts/check_updates.py`; inspect new and retained candidates.
2. Run `python -B scripts/setup.py verify`. Treat unmanaged skill findings separately
   from managed-file integrity; neither proves whole-home cleanliness or runtime loading.
3. For each registered project, check path availability, Git HEAD and working-tree
   changes, including relevant untracked instructions. Inspect only changed rules,
   configuration, package/runtime pins, scripts and affected source. Check the selected
   runtime against a project pin when present. An unchanged dirty filename list is
   not evidence of unchanged content: compare content/diff fingerprints too.
4. Only meaningful changes or failures trigger model review. Do not reread the
   entire reference inventory or project. Default to direct review; use bounded
   delegation only when independent work justifies it. Do not schedule model benchmarks.
5. Run `python -B scripts/tools.py verify` and `python -B scripts/project_cleanup.py scan`.
   Do not execute arbitrary repository scripts, installs, builds or browser tests
   during the heartbeat. The sole deletion exception is the pre-authorized dependency
   policy below, executed only by `project_cleanup.py prune`. Recommend the smallest checks for other candidates;
   execute them during approved implementation. Missing paths and failed collection
   stay unknown/failed, not healthy. An offline host cannot guarantee scheduled execution.
6. Run `python -B scripts/check_closure.py`. Compare checkout, installed policy,
   reviewed CLI/RTK and latest GitHub release versions. Inspect the existing PR's
   final-head checks and immutable tag/artifact identity when publication differs.
   A merged PR, prepared package and installed policy are separate from a published
   release. Missing GitHub access is unknown, never successful publication.
   For a registered project with no recorded substantive review, perform one scoped
   initial instruction/configuration/acceptance-contract review even when its
   content fingerprint is unchanged. Do not equate collection or a dirty file list
   with completed onboarding. Do not edit its source or manufacture a project flow.

### Completion audit and notification

At the end of each routine, reconcile unresolved stable findings with the collected
evidence. Each actionable candidate should name exact target files/versions, impact,
the smallest relevant checks and whether approval or session evidence is required.
Report new unfinished release/install/migration work proactively, without waiting
for the user to ask what remains. Keep previously reported pending work quiet unless
its evidence, impact, severity or resolution materially changes. Do not repeat a
notice merely because time passed. Collection never clears a finding automatically.

Before a managed update is approved, compare the assets TRACE actually installs,
not just an upstream tag or commit message. An identical managed skill hash can
justify keeping its pin despite unrelated plugin/hooks releases. A deliberate
deferral has a version/hash, reason and reconsideration trigger; it is not a claim
of runtime validation. Preserve unresolved candidates removed from the watch list
until an exact-content review resolves them. Use current [OpenAI plugin examples](https://github.com/openai/plugins)
and [plugin packaging guidance](https://developers.openai.com/plugins/build/plugins)
for future examples; the deprecated skills catalog remains historical evidence.

CLI `debug prompt-input` can confirm rendered global/project instructions without
a model call. Keep only hashes and presence checks in private evidence, never raw
prompt contents. It does not prove model obedience or desktop UI loading. Compare
the actual session permission context with defaults using the documented
[configuration precedence](https://learn.chatgpt.com/docs/config-file/config-basic)
and [developer settings](https://learn.chatgpt.com/docs/developer-settings).
Do not change permissions to make a check pass or label an override an installer fault.

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
The heartbeat never applies managed instructions, skills, configuration, project
source edits, upgrades or Git publication. Dependency removal is restricted to the
pre-authorized policy below; all other deletions require approval. Never overwrite project docs during
a global update. Update only affected Archify diagrams during approved work.

Source reports retain `pending` candidates across unchanged fetches. The success
marker records collection time; installed state `applied_at` records deployment,
not source acceptance. Older records without timestamps remain unknown. After
review, use `check_updates.py --resolve ID --expected-sha HASH --reason TEXT` to
record a decision about that exact candidate; this never applies policy. Typography,
GitHub statistics and example model names alone do not justify policy edits.
Quote styles are normalized; other relevance decisions require review. Report
known missed runs honestly; a timestamp alone cannot establish scheduler history.

## Project dependency cleanup

The user authorized idle dependency cleanup on 2026-10-01. This is TRACE operating
policy, not an OpenAI recommendation or proof a person has stopped using a project.
Only registered exact Git roots are examined; do not search every drive. Register
an approved project with `project_cleanup.py register --id NAME --path PATH --auto`.
Without `--auto`, it is held. Registrations and observations remain host-local.

- Begin observation at registration/first successful collection, never backdate
  inactivity from a last commit or old folder timestamp. Require 45 observed days
  without Git/content, install-root or manifest/lock changes. Missed/inaccessible
  intervals longer than 14 days, process-collection failure and possible runtime
  activity reset the observation period. Command lines are inspected transiently,
  never stored; a relative-path runtime can be ambiguous and blocks automatic deletion.
- Inspect only direct-child `node_modules`, Composer `vendor`, or uv `.venv` with
  an unambiguous manifest/lock pair, Git ignore coverage and no tracked contents.
  Before proposing/deleting, check the complete tree's write times and refuse all
  symlinks, junctions, special files and linked roots. Shared package stores,
  authentication, global installs, source, backups and other build outputs are excluded.
- Report an exact candidate, size and reinstall command. After actually notifying
  the user, run `reported --id NAME --artifact node_modules` once. Wait at least
  seven days from that notification before the fixed `prune` command can remove it.
  Unreported candidates never become eligible. Recheck identity, locks, contents and
  processes immediately before deletion. New activity cancels the grace period.
- `hold --id NAME` prevents automatic cleanup; `touch --id NAME` records active
  read-only/manual work and resets the idle clock. Users can resume work at any time.
  File reads outside observed tools may be invisible; no perfect inactivity detector
  is claimed. Linked installs are deliberately manual-only, including common
  POSIX virtualenv/bin or pnpm layouts. The tool never follows links into shared stores.
- Record verified removals and failures in one `cleanup-result.json`. Permission
  failure can leave a partial dependency directory; report it and reinstall using
  the pinned package manager/lock during authorized work. Source and lock files
  remain. Dependencies have no byte-for-byte managed-policy rollback. Do not hide
  unresolved errors or repeatedly force deletion. Logical size is not physical
  space reclaimed, especially with hard links.

The same registry supplies weekly project health scope; do not maintain a second
path inventory in policy. `cleanup-observations.json` holds one current observation
per project, separate from semantic-review evidence in `routine-review.json`.

## RTK lifecycle

`versions.lock.json` pins release assets for supported Windows, macOS and Linux
architectures. `tools.py install-rtk` verifies the release SHA-256, extracts only the
binary and checks its version before replacing an owned installation. One previous
binary is retained outside active paths; user-modified copies conflict. `tools.py
verify`, `tools.py rollback-rtk` and `tools.py uninstall-rtk` check ownership.
Runtime tools are separately owned in `tools-installed.json`, not copied into
Codex home, Git or a project. No PATH or shell profile is edited. Use `tools.py run`
or the verified absolute binary path. A new computer explicitly installs its own
platform asset; installing TRACE instructions alone does not install this binary.

Release changes are candidates, not automatic binary updates. Standard RTK gain
counts are estimates, not OpenAI usage. Run `verify_rtk.py --project PATH` during
approved maintenance for Git, TypeScript when installed, Unicode/space paths,
arguments, stderr and nonzero exit checks. It does not test every filter or imply
transparent hook loading. RTK's native auto-rewrite is not installed because of
its documented approval-classifier limitation; do not run `rtk init -g` as a
shortcut. See [conditional RTK guidance](../global/guides/rtk.md).

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
