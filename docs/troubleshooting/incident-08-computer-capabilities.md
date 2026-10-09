# Computer accessibility works while capture/input fails

## Symptoms, environment and version

Observed on Windows in the designated host on 2026-10-07, CLI 0.160.0 and bundled
Computer Use skill 26.1002.52244. Native initialization and window enumeration
succeeded. Calculator capture reported FrameArrived timeout and then no screenshot
targets after fresh enumeration. A separate empty Notepad window returned its
accessibility tree; screenshot capture timed out and element click reported
coordinate input geometry unavailable. No text was typed or saved. IAB official
documentation reading and an accordion click/result observation succeeded.

## Confirmed findings and unresolved cause

Accessibility, screenshots and input are separate capabilities. This failure is
not proof of a browser outage. Native capture/input root cause is unresolved.
Do not treat this as a confirmed repair of historical setup-refresh errors.
CLI doctor returned overall fail because Windows sandbox provisioning recorded a
structured failure; authentication and app-server handshake passed. A scoped
review of the matching setup_error.json and sandbox log identified runtime
read/execute validation failing with Win32 sharing violation (32) on an existing
105-character runtime file. The generic setup-refresh label is confirmed in
that structured record. The holder/process and durable repair remain unknown;
this is not evidence of an access-denied (5) or long-path failure. The causal
relationship to native capture is unknown. Optional MCP/config warnings and
rollout-file/database parity warnings also remain independent observations.

## Non-destructive diagnosis and next action

Enumerate and select fresh returned targets. Observe accessibility without capture
to narrow the layer, and reconcile unknown input outcomes before retry. Repeated
unchanged failures stop native actions. Use the supported skill's bounded recovery
only; do not change sandbox permissions, endpoint protection or authentication as
a shortcut. Use /feedback with relevant redacted diagnostics if the current runtime
still reproduces the issue. Browser-specific troubleshooting does not prove a
native-helper repair.
Preserve relevant version/time/error evidence for support; do not infer that
0.160.1 repairs this issue. Its [reviewed release note](https://github.com/openai/codex/releases/tag/rust-v0.160.1) concerns remote stdio MCP
environment preservation, not this sharing violation. After a user Escape stop,
do not resume native or browser manipulation without fresh human authorization.

## Verification, effects and restoration

Browser success is limited to IAB public documentation, not Chrome extension or
product QA. Native screenshot and coordinate-input acceptance remain failed.
No permission/configuration recovery changes were made, so none need rollback.
The private checkpoint records accessibility/screenshot/native-input/browser-input
separately; completed actions are not replayed automatically. Global settings
verification cannot clear this runtime incident.

Evidence: direct supported-tool observations and redacted CLI doctor statuses,
last verified 2026-10-07. [Official Computer Use](https://learn.chatgpt.com/docs/computer-use)
and [browser recovery](https://learn.chatgpt.com/docs/chrome-extension#troubleshooting).

## Current CLI reproduction — 2026-10-08

The explicitly selected npm CLI is stable 0.161.0. The application-owned
`codex.exe` is separately 0.162.0-alpha.2; TRACE's stable CLI updater must not
replace that desktop bundle. Current stable-CLI doctor returned exit 1/overall
fail: authentication and desktop handshake passed, sandbox helpers failed.
This is separate from installed-file and RTK integrity, which passed.

The original sandbox path was exercised once with `codex sandbox -- cmd.exe /d /c ver`.
It exited 1 with `helper_unknown_error: setup refresh had errors`. The matching
fresh sandbox log identifies a sharing violation (Win32 32) while opening the
app-owned `cua_node` runtime's `node_repl.exe` for a root-only ACL update.
Two running instances used that exact runtime file. This establishes active use,
not the identity of the incompatible handle holder or a durable root cause.
The link to native capture/input remains unproven. Normal sandbox initialization
attempted provisioning; no manual ACL reset, process termination, permission-mode
change, runtime removal or endpoint-protection change was performed.

Save ongoing work before a user-controlled full app shutdown/reopen, then retry
the same affected sandbox path and doctor once with the changed runtime state.
Restart is a proposed bounded recovery, not a verified fix. If failure persists,
use official feedback with sanitized version/error evidence. Screen-control hold
still blocks browser/native acceptance; an app restart alone does not lift it.

Stable CLI also warned that `computer_use.windows.always_allowed_app_ids` was
ignored. The current [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
still documents it as saved Windows Computer Use app approvals, removed through
the desktop settings. Keep those user permissions: one client's ignored-key warning
does not establish global legacy. Three stale archived database rows were reported
separately; no database repair/deletion was performed.

## Post-restart contrast and upstream fix candidate — 2026-10-09

After the user reported restarting the app, stable CLI 0.161.0 still failed on
the original sandbox path. The already installed app-owned 0.162.0-alpha.2 also
failed; its fresh log again records a root-only ACL open failing with Win32 32
on an active runtime executable. Restart did not resolve this incident.

A non-mutating handle contrast on that runtime file opened successfully with
`READ_CONTROL` and `READ_CONTROL | WRITE_DAC`, but `MAXIMUM_ALLOWED` failed with
Win32 32. The probe opened/closed handles only; it did not update ACLs or terminate
processes. This narrows the failure to requested access/share compatibility;
it does not identify the incompatible holder or prove a native-capture cause.
Normal CLI sandbox initialization may provision ACLs independently of this probe.

OpenAI's [exact fix commit](https://github.com/openai/codex/commit/dd12f892f1b857e5161abd33a2967125b265d550)
restricts the broad open to directories and narrows file ACL-write access when an
update is required. Its regression test holds a runtime executable open while
repairing and revalidating permissions. The reviewed stable-tag source lacks
this change. Latest stable release collection still returned 0.161.0; the
app-owned version's observed failure is not proof of its source ancestry.

Keep this as a relevant vendor fix candidate, not a verified host repair.
At the existing maintenance cadence, review the next stable release for this
exact change and compatibility before any authorized update. Then recheck the
original sandbox path and doctor, preserving config, credentials and saved app
approvals. Do not install an alpha, rebuild a custom CLI, manually reset ACLs or
repeat unchanged restart attempts to bypass the release gate. Screen-control
acceptance remains separate and requires lifting the user's existing hold.
