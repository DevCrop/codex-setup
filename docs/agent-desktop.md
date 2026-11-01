# Codex agent-desktop — native Windows UI integration

Optional Codex-only skill: `$codex-agent-desktop`. Ordinary coding uses no UI
session. For websites prefer the available browser tools; this component cannot
override their safety checks or recover a policy-stopped page by changing drivers.
Claude's shared skill, PATH installation, state and configuration are not modified.

## Use

Example request:

> $codex-agent-desktop 메모장의 지정 창을 확인하고, 에이전트 커서를 보여주면서
> 요청한 편집을 수행해줘. 결과를 확인하고 세션을 종료해줘.

The installed runner is `CODEX_HOME/skills/codex-agent-desktop/scripts/desktop.py`
(default home: `~/.codex`). Invoke with Python and an argument array, never shell
interpolation. Start `session start --cursor --no-trace`, use the returned ID as
`--session <id>` on each subsequent command, and finish `session end --session <id>`.
Read the binary's `skills get desktop` and `skills get platform` when using it.
The overlay is a presentation cursor, not permission to take physical mouse/focus
control. `rendered: true` is renderer acknowledgment; a human visual observation
is separate evidence. Do not use `--headed` without task-specific authorization.

No automatic trace/screenshots, API provider, JEV, new MCP server, hook, daemon or
model switch is added. Do not capture other apps or store their screen contents.
An action delivery acknowledgment does not prove that the requested edit persisted.

## Technical-failure routing

For Computer Use/browser bootstrap or tool-connection failures, the skill loads
its conditional [failure procedure](../components/agent-desktop/references/fallback.md).
Diagnose the actual failing stage and verify existing access and the same target.
Only a confirmed technical cause with confirmed non-delivery can select one switch
to this driver. Policy/human/runtime stops, unknown permissions or current URL,
website/app errors and uncertain action delivery block substitution. No permissions,
profiles or endpoints are repaired automatically. Current runtime instructions win.

The stdin-only `scripts/fallback.py` decision helper checks the diagnosed fields;
it cannot itself establish authority and does not execute UI commands. This is an
agent workflow activated by relevant failure triage, not a hook that catches every
Codex tool exception. The user's standing request permits an eligible switch
without a repetitive approval question. Freshly observe through the verified runner,
perform only the original task, verify the outcome and end the session. A second
driver failure ends this route rather than starting a switching/retry loop.
When the user is gaming/reserves input, neither driver observes or controls apps;
no capture, overlay, focus change or live UI test is started. The decision helper
also blocks this state. Continue non-UI work and wait for the user to release it;
headless mode alone does not establish that an accessibility provider cannot steal focus.

## Install and ownership

From this checkout, on Windows x64 with Python 3.11+:

```powershell
python -B scripts/agent_desktop.py plan
python -B scripts/agent_desktop.py install
python -B scripts/agent_desktop.py verify
```

`--home <path>` honors an explicit alternate Codex home; otherwise `CODEX_HOME`
or `~/.codex` is used. `--binary <path>` on install reuses an exact pinned native
binary instead of downloading. The installer checks both release archive and
native binary SHA-256. The downloaded archive is kept in memory, not left on disk.
Only Windows x64 installation is currently supported and tested here; upstream's
macOS/Linux support does not establish validation of this integration there.

Source and pin: `components/agent-desktop/manifest.json`. The independent component
receipt and one restore point live under private TRACE state
`components/agent-desktop/`. Its four installed files live only inside
`CODEX_HOME/skills/codex-agent-desktop/`; the verified runtime and isolated sessions
live under the private component state. The base global manifest intentionally
does not own this optional package. Its skill may appear in the base installer's
unmanaged inventory; use the component verifier for ownership. No second source
of global agent/model/configuration settings is created.

`rollback`, `recover` and `uninstall` reuse TRACE's conflict-checked text lifecycle.
An interrupted runtime write has its own exact-owner journal. `install` resumes
only a matching journal; `recover` can finish a verified binary's missing receipt.
If interrupted before the binary write, run `install` to complete the pinned copy.
An unowned binary without that journal is preserved and rejected, even if its hash
matches. No unconditional adoption or deletion is used to repair such a conflict.
Uninstall removes only owned skill files; it retains the pinned runtime, session
data and restore point for recovery. Their removal requires a separate ownership
and inactivity review. User-modified files and linked/junction paths are refused.
This task does not silently adopt or overwrite existing global drift.

Restart Codex or start a new chat if the new skill does not appear. Actual new-chat
discovery is separate from file installation and CLI checks. Use this unique skill
name to distinguish it from the existing shared `agent-desktop` skill; the latter
may carry another agent's permission assumptions and is left intact for Claude.

## Evidence and limits

Reviewed 2026-11-01: upstream stable v1.0.2, source commit recorded in the component
manifest. The earlier isolated native fixture passed six checks (Unicode input,
idempotent state setting, save outcome, snapshot, scoped image, stale-ref rejection).
That is one controlled native task, not a reliability benchmark or browser result.
The Codex runner then passed 10 disposable lifecycle/isolation tests, including
runtime-write interruption and Windows junction refusal. Its installed v1.0.2
hash and repeat/no-op installation matched. A separate native acceptance loop
through this runner confirmed input readback, exactly one save and fixture exit;
the cursor renderer acknowledged `rendered: true` and the session ended. Trace
recording stayed off; the component's two ended test sessions were reclaimed by
its own `session gc --ended`. No human visual capture or new-chat discovery test
was performed. Other operating systems and GitHub CI were not run for this change.
The prior official Windows browser attempt stopped because the URL could not be
established confidently enough for policy; it remains unresolved and was not
repeated through this driver. Existing experiment cleanup was policy-blocked and
its exact retained targets are not deleted by this integration.

The fallback integration is component v1.1.0; the native binary remains v1.0.2.
Its negative cases include policy and human stops even alongside a connection
failure, unknown access, missing current browser URL and possibly delivered actions.
Controlled fault injection and actual native UI execution are separate evidence
from reproducing the user's intermittent browser failure. No claim is made that
the original Codex initialization defect or browser policy stop has been repaired.
See the [dated error/source review](ui-error-routing.md) for observed failures,
official limitations, user reports and why this is not the default for every task.

Sources: [upstream README](https://github.com/vercel-labs/agent-desktop),
[v1.0.2](https://github.com/vercel-labs/agent-desktop/releases/tag/v1.0.2),
[installation](https://github.com/vercel-labs/agent-desktop/blob/main/docs/install.md),
[JSON/action outcomes](https://github.com/vercel-labs/agent-desktop/blob/main/docs/json-output.md),
[OpenAI skills](https://learn.chatgpt.com/docs/build-skills).
