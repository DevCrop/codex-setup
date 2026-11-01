# Diagnosed technical failure: one bounded driver switch

Load only after an actual tool initialization/connection failure. This is the
user's local operating choice, not a vendor recommendation or a universal hook.
Normal tasks keep their current tool. The model diagnoses the failure and calls
the decision helper; it does not intercept all Codex tool calls in the background.
If the user says they are gaming or reserves interactive input, set
`user_input_reserved: true` and do not start either UI driver, cursor overlay or
screen observation. Do not poll the desktop to guess when gaming ends. Continue
file/documentation work and resume UI only after the user releases the restriction.

1. Inspect the actual failing stage and current tool result. Resolve the runtime's
   allowed recovery/stop instructions first. A policy stop, user stop, disabled
   surface, missing access, uncertain current URL or instruction to end the turn
   prohibits substitution even if a connection/timeout error is also present.
2. Establish a technical cause using relevant non-mutating evidence: an absent
   documented bootstrap dependency, a runtime initialization failure, or an
   unavailable/closed tool transport. A missing tool alone or a generic timeout
   does not prove the cause. A website/server error, target-app failure, stale ref
   or login problem is not a tool transport failure. Do not reset permissions,
   install drivers, change endpoints or break a working connection to diagnose it.
3. Establish existing authority for the same app/window/browser/profile and task.
   A website switch requires the current target origin to be verified through an
   available permitted observation and the original browser policy/access checks
   to remain applicable. An expected URL or prior screenshot is insufficient.
   If policy checks are unavailable, policy state is unknown: stop. Do not use this
   driver to establish access after the official runtime has denied it.
4. Determine whether any mutation was delivered. Unknown, interrupted or possibly
   delivered actions require fresh observation and reconciliation, not automatic
   replay. This route accepts only confirmed `not_delivered` at initialization or
   connection. No same-task driver ping-pong: at most one switch attempt.
5. Send a minimal evidence object to `scripts/fallback.py` via stdin. Derive values
   from the current result, allowed diagnostics and access evidence. Do not change
   them merely to get a switch decision. No raw tool response, URLs, prompts,
   credentials or screen contents are needed or saved. Unknown stays unknown.
6. Only on `decision: switch`, explain the diagnosed technical cause briefly and
   continue within existing authority without another routine approval question.
   Use the verified `scripts/desktop.py` runner, read its version-matched docs,
   start a cursor/no-trace session, and freshly observe the exact target. Do not
   reuse refs/coordinates from the previous driver. Verify the requested outcome
   independently, then end the session. On another failure, preserve the evidence
   and report the blocker; do not switch back or retry an unchanged mutation.

The helper is a conservative consistency check on the model's diagnosis, not an
independent security boundary or proof of authorization. Runtime rules still win.
Its `stop` does not forbid permitted read-only diagnosis; it forbids this switch.

## Evidence schema

All fields below are required. Use native JSON booleans, not strings. The example
describes an already authorized native task with confirmed pre-action connection
refusal; it is not evidence that any actual user's session has failed.

```json
{
  "stage": "connection",
  "failure_origin": "tool_runtime",
  "technical_cause": "tool_transport_refused",
  "cause_confirmed": true,
  "policy_state": "allowed",
  "permission_state": "granted",
  "human_stop": false,
  "runtime_stop": false,
  "user_input_reserved": false,
  "target_kind": "native",
  "same_target_verified": true,
  "browser_url_verified": false,
  "action_delivery": "not_delivered",
  "switch_already_attempted": false
}
```

`stage`: `initialization` or `connection`. `failure_origin`: only `tool_runtime`.
`technical_cause`: `bootstrap_dependency_missing`, `runtime_initialization_failed`,
`tool_transport_refused` or `tool_transport_closed`, after confirmation.
`policy_state`: `allowed`, `denied` or `unknown`; `permission_state`: `granted`,
`denied` or `unknown`. Unrecognized values stop. For browser tasks,
`browser_url_verified` must be true. Set stop flags from the full original result,
not a selectively extracted transport error. Exit code 0 means switch candidate;
2 means stop/invalid input. No desktop command is executed by this helper.
`user_input_reserved` reflects the user's current interaction constraint; it blocks
headless use too because individual accessibility providers may change focus.

Sources reviewed 2026-11-01: [OpenAI Computer Use](https://learn.chatgpt.com/docs/computer-use),
[browser access](https://learn.chatgpt.com/docs/browser),
[upstream delivery semantics](https://github.com/vercel-labs/agent-desktop/blob/v1.0.2/docs/json-output.md).
