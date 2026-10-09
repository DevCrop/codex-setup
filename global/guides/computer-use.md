# Computer and browser interaction

Read for a computer/browser task or its failure, not for ordinary coding. Follow
the currently installed tool skill and returned API documentation; this guide
does not replace them or grant app/site access.

## Route, observation and recovery

The TRACE personal `computer-use-workflow` skill is the authoritative workflow
router; use its `references/recovery.md` only for the affected failure. Follow the
available official runtime skill/API for execution. No skill installs a plugin,
grants permission or makes browser and native health interchangeable.

Human interruption/Escape stops input until fresh human authorization. Never
remove an interruption marker. A denied protocol or permission is not bypassed
by a proxy, alternate browser, driver or shell.

CLI sandbox health remains separate from capture/input readiness. For setup
refresh failures distinguish sharing violation (32), access denied (5), missing
paths and long paths from actual evidence. Do not reset ACLs or delete runtime
assets from a top-level error label alone.

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
