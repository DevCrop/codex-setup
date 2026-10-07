# Computer and browser interaction

Read for a computer/browser task or its failure, not for ordinary coding. Follow
the currently installed tool skill and returned API documentation; this guide
does not replace them or grant app/site access.

## Route and readiness

Use a dedicated connector for supported structured operations, Browser Use for
websites (the user's selected browser/profile when specified), and Computer Use
for native apps. Select a returned unique target; do not infer it from a title or
guess handles. Do not operate the same app concurrently. Windows needs an
unlocked active desktop; macOS behavior and permissions differ.

Check only dependencies of the selected route. Shell execution, native helper
initialization, browser extension connection, target enumeration, observation and
input are separate capabilities. A shell/skill-read failure does not establish a
browser outage; a connected PC does not establish helper or action readiness.
Test a supported lightweight call on each relevant independent route before
declaring it unavailable. Do not require a successful shell probe for Browser Use.
Do not probe every route at every task start or repeat unchanged successful probes.
Accessibility reading, screenshot capture and native input are also independent.
Successful accessibility text does not prove capture or coordinate-input readiness;
keep browser input distinct from native input in verification records.

For Windows native control use the installed skill's node_repl + @oai/sky entry
point, not a helper executable or custom protocol. Initialize once per live
session; enumerate, uniquely select, observe, act, then observe the result.
Use accessibility text when sufficient, screenshot capture for a visual decision,
and both only when required. Use observed keyboard shortcuts when useful.
Discard stale coordinates, screenshot IDs, indexes and focus after any state
change or failed input. Read returned observations before selecting an action.

## Failure routing and recovery

| Failure | Evidence and next step |
|---|---|
| Execution/setup initialization | Record the sanitized error code and failing layer. Try the independent supported browser entry point if relevant and permitted. Do not attribute it to Chrome or the website without evidence. |
| Native helper timeout | Follow the installed skill's bounded lightweight retry/reset procedure. Current Windows skill: wait two seconds, retry once, reset/reinitialize once if supported, then report failure. Other versions may differ. |
| Browser extension connection | Follow official troubleshooting: blocked site, app update, browser restart, Manage/toggle, installed profile, new chat, app restart/reinstall, then /feedback. Restart/update/install actions require the applicable user authority and product confirmations. |
| Window/focus/modal mismatch | Enumerate again and select fresh returned objects. Observe the actual workspace/focus before one justified retry. |
| Input/refresh failure | Outcome is unknown. Reobserve and reconcile whether the action already happened before retrying; never blindly repeat a submission or mutation. |
| Policy, protocol or permission denial | Stop the denied action. Do not route through native control, raw CDP, shell navigation, a proxy or another browser to bypass it. Use a genuinely permitted alternative or report required user action. |
| Locked desktop or security/auth prompt | Stop as required by the installed skill and let the user handle it. Never change permissions or automate authentication as a recovery shortcut. |
| User interruption / Escape | Stop input. A later automation or checkpoint does not revoke the user's stop. Require fresh human authorization before resuming; never delete a tool interruption marker. |

`helper_unknown_error: setup refresh had errors` is an observed incident label,
not a documented root cause or universal repair. Distinguish error text, supported
inference and confirmed cause. Read only relevant diagnostic log entries if
authorized; redact secrets, account data, URLs and paths before durable storage.
Repeated unchanged failure triggers diagnosis, not repeated restart requests.
For Windows setup-refresh failures, inspect the relevant structured setup error and
matching sandbox log entries. Sharing violation (32), access denied (5), missing
path and long-path errors require different diagnoses. Do not reset ACLs or remove
runtime caches merely because the top-level label is the same. CLI sandbox health
and native screenshot readiness remain separate claims.

## Checkpoint and resume

For multi-step QA or an interrupted interaction, keep one compact task checkpoint
in the existing private routine-review.json through scripts/interaction_checkpoint.py
from the TRACE checkout (use its absolute script path from another project).
Use opaque task/step/target IDs, stage status and sanitized error codes. Never store
page contents, screenshots, credentials, URLs or raw commands in the checkpoint.
Actual project acceptance/results remain in that project's canonical QA record.

Record completed, pending, failed and unknown-outcome steps. On recovery verify
the same intended target and refresh the current state. Reconcile unknown outcomes
first; then resume remaining steps. A saved checkpoint is not a live window,
permission or runtime success. Only mark a step complete after observing its
acceptance result. Failed steps require a changed diagnosis; completed steps are
not repeated unless a changed dependency invalidates them.

Report configuration/integrity, initialization, enumeration, observation, action
and result verification separately. No setup can promise error-free apps or
faster interaction without measured task evidence. Preserve unknowns and report
the smallest concrete recovery action.

Sources: [Computer Use](https://learn.chatgpt.com/docs/computer-use),
[Browser troubleshooting](https://learn.chatgpt.com/docs/chrome-extension#troubleshooting),
[Computer use practices](https://learn.chatgpt.com/use-cases/use-your-computer-with-codex).
Retry counts, checkpoint format and independent-route checks are TRACE operating
choices informed by installed OpenAI skill guidance, not universal product settings.
