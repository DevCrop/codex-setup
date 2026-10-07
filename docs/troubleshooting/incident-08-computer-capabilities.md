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
