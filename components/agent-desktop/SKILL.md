---
name: codex-agent-desktop
description: Use for native Windows UI work or diagnosing Computer Use/browser initialization and tool-connection failures before a possible switch to the isolated agent-desktop CLI. Never switch after a policy or human stop.
---

# Codex agent-desktop

Use the Python runner at `scripts/desktop.py` beside this skill, with structured
arguments. It verifies the pinned binary and isolates Codex state from Claude.
Do not use a PATH-resolved `agent-desktop`, shared skill wrapper or another driver.
Run `python -B <skill-directory>/scripts/desktop.py skills get desktop` and
`skills get platform` once per task; these are version-matched upstream procedures.
Consult `<command> --help` only for needed flags.

For an initialization or tool-connection failure, read
[fallback.md](references/fallback.md) before choosing a driver. The user's standing
authorization permits a switch for a confirmed technical failure within the same
task and access scope; it does not waive runtime policy or permission checks.
When the user is gaming or reserves foreground input, do not observe/control apps,
capture the screen, show a cursor, raise windows or launch UI tests. Continue only
non-UI work; resume UI only after the user releases that restriction. Headless
accessibility is not a guarantee against focus changes.

- For an authorized native UI task, start `session start --cursor --no-trace`. Retain the
  returned session ID and pass `--session <id>` to every task call. The visible
  overlay indicates the agent's targets; it is not the physical mouse and does
  not authorize `--headed`. Confirm `rendered` before claiming it is visible.
- Observe only the intended app/window. Prefer compact interactive snapshots,
  using skeleton/root narrowing for dense apps. Act on fresh snapshot-scoped refs
  and observe the result. Quote refs in PowerShell.
- Treat delivery acknowledgments separately from the requested outcome. On stale
  refs, refresh the snapshot. After an unknown action outcome, observe before any
  retry; never repeat a mutation just because a call timed out.
- Keep headless semantic delivery by default. Use `--headed` only when the user
  authorized physical input/focus for the task. Do not change permissions or
  switch to headed to repair a headless failure.
- End with `session end --session <id>` even when the task fails; this stops the
  overlay. Do not leave a background controller running between tasks. Session
  traces can contain private content; do not commit, upload or routinely collect
  snapshots/screenshots. The runner does not save command output.
- Browser tasks still follow applicable browser access and safety rules. A denied
  page, policy stop, uncertain URL or human stop is a stop, not permission to use
  this CLI instead. Do not repeat the unresolved browser comparison without a
  permitted, identified site/task. Do not invoke JEV or model-provider helpers.

`$codex-agent-desktop` explicitly selects this integration. Automatic discovery is
limited to native desktop work or the failure triage above; normal coding tasks
need no UI session. Existing shared `agent-desktop` belongs to a different setup and is not
this runner. If the binary/receipt is unavailable or changed, report that state;
do not silently install or use another copy.
