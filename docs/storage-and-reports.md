# Codex home storage and local evidence reports

Run `python -B scripts/codex_storage.py scan` from TRACE. It honors CODEX_HOME
and replaces one metadata snapshot inside private routine-review.json. It reads
names/types/sizes only, skips links and reparse points, and does not delete or
infer inactivity. Missing paths and failed entries remain unknown. Logical bytes
deduplicate hardlinks within each top-level row, not across rows; these are not
physical disk allocation or guaranteed reclaimable bytes.

The designated host's inspected visualization work includes CUDA/Python libraries,
downloaded 3D models, application caches and user artifacts. A large visualization
directory is neither a single disposable cache nor permission to delete it.
Preserve sessions, attachments, databases/WAL, credentials, memories, active work
and application plugin state. Size, age or a cache-like name is insufficient.

TRACE retires its own obsolete managed files through setup.py plan/apply.
Other reclaim candidates require exact ownership, current activity/process state,
regeneration instructions and approved scope. Registered dependency cleanup keeps
its separate 45-observed-day / 7-day-after-actual-notice rules. Do not auto-register
visualization folders or scan drives. Application-owned data uses supported product
lifecycle controls after the user selects the target; `codex plugin remove` or
`codex delete` is not a blanket cleanup command.

## RTK verification note

Run `python -B scripts/rtk_status.py` to replace the same owned private
reports/rtk-status.html and its evidence receipt. The tracked template is
templates/rtk-status.html; data is a sanitized projection of routine-review.json,
not a separate source of truth. Another computer has its own unknown baseline.
Do not copy a private report, credentials, machine paths or historical command
records into Git. Conflicting report bytes are preserved.

The light document layout is inspired by Notion, not an integration or an exact
copy of a discovered historical design. Input-minus-output and the RTK reported
savings are displayed separately. Arithmetic discrepancies remain visible.
Missing days stay missing; unknown verification is not shown as zero or pass.
Runtime results are reused only with matching binary/version, harness and runner hashes.
The report never equates RTK estimates with actual OpenAI tokens or subscription
savings. No model calls or benchmarks are performed.

## Flow presentation

The canonical JSON/HTML/receipt stay under diagrams/global. Pretendard 1.3.9 is
bundled with its OFL license and hash receipt, embedded offline in generated HTML.
The presentation adapter operates on a temporary Archify package copy; original
vendor and installed skill bytes remain unchanged. It checks static delivery and
records any unperformed browser/visual gates honestly. Font declaration is not
proof that the browser rendered the font. Do not reuse old browser receipts for
changed output or bypass a denied local-file preview through another protocol.

Sources: [Codex home](https://learn.chatgpt.com/docs/config-file/config-advanced),
[supported diagnostic/lifecycle commands](https://learn.chatgpt.com/docs/developer-commands),
[Pretendard license](https://github.com/orioncactus/pretendard/blob/v1.3.9/LICENSE).
Storage classification and report layout are TRACE choices, not OpenAI defaults.

## Reviewed uv cache maintenance

For an explicitly reviewed uv cache, use the installed tool's supported
`uv cache prune --cache-dir <exact-cache> --offline --no-config` rather than direct
filesystem deletion. Verify the cache marker/layout, resolved scope and absence
of links first. Keep uv's in-use checks; do not use `--force` or workstation
cleanup's `--ci` shortcut. Bound the lock wait and record failures.

Compare surrounding source, outputs and installed-environment metadata before
and after. Hardlink sizes are not additive or a physical reclaim estimate.
No unused entries means no removals; do not repeat an unchanged prune or treat
it as proof that a person no longer needs the environment. This current-task
procedure does not expand the heartbeat's automatic deletion authority.

Source: [uv cache safety and pruning](https://docs.astral.sh/uv/concepts/cache/#clearing-the-cache).
