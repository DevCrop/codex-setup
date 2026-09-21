# Operations

Start from the repository README and installer help for executable commands. Resolve paths from the script location, explicit root and supported user directories; never assume a drive letter or current shell directory. Honor CODEX_HOME. Authenticate separately on each host with the installed CLI's supported ChatGPT login flow; do not copy auth files into this repository.

## Managed lifecycle

Run plan before apply. Inspect additions, changes, removals and conflicts. Apply only approved owned files; preserve user edits, permissions, model selection, MCP secrets and unrelated settings. Verify after apply. Keep one previous managed state in the local state directory for rollback, not backup copies in active paths. On failure restore that state and report conflicts. Installer-owned temporary artifacts are cleaned after success; application caches, sessions and credentials are not general cleanup targets.

## Profiles and fresh sessions

The optional CLI profiles are `sol`, `astra` and `astra-deep`. They are separate `.config.toml` files selected with `--profile`. Check host model support; the app composer remains user-controlled. A parsed configuration is not proof of a fresh session's effective instruction or model behavior. Inspect new-session loading separately. Legacy overrides and project trust can affect effective configuration.

## Weekly maintenance

Use one operating host. Check official source bodies and pinned upstream versions; process meaningful changes only. Network failures remain failures, not unchanged results. Record last successful check. Prepare the exact candidate, evidence and tests, then apply after approval. Never overwrite project docs during a global update. Update only affected Archify diagrams and remove owned intermediate render artifacts.

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
