# Bounded delegation

Load when considering or performing delegation. The global agreement requests
conditional delegation; this guide supplies the decision and completion loop.
Use native Codex orchestration, not a second scheduler, agent daemon or API harness.

## Decide before spawning

- Handle a small SCSS edit, a local TS/JS fix or a tightly coupled change directly.
- Use one explorer for a bounded, noisy investigation when its summary keeps the
  parent focused. Use a second child only for genuinely independent useful work.
- Prefer read-heavy exploration, triage and focused review. Delegate implementation
  only with separate file ownership and settled shared interfaces. Otherwise settle
  the contract first or work sequentially.
- Do not always create planner, worker and reviewer agents. A test command alone
  rarely needs a separate agent. Use built-in roles and the existing explorer;
  do not create another role file for each task.

## Execute and finish

1. The parent resolves the active project, applicable rules, requested result and
   smallest relevant acceptance checks. Decide which bounded work can be delegated.
2. Spawn only the needed children, at most two concurrently by default. No recursive
   delegation unless explicitly requested. Include the handoff below and tell writers
   they share the checkout: preserve others' edits and respect ownership.
3. While children work, continue only independent parent work. Do not repeat their
   investigation or edit their files. Use supported waits/progress summaries instead
   of frequent unchanged polling. Reuse a suitable existing child for follow-up.
4. Integrate results against the current diff and source identity. Check findings
   and run affected acceptance checks; reuse matching trustworthy test evidence
   rather than blindly repeating every child command. A self-report is not proof.
5. On failure, classify code, tooling, permissions or requirements before retrying.
   Default to at most one corrective child pass, with the failed evidence and a
   changed plan. If the same failure persists, the parent takes over or reports
   the actual blocker; do not bounce work between agents, spawn replacements or
   increase model effort as an unchanged retry. The parent continues authorized
   repairs until acceptance or a genuine external blocker.
6. Stop when acceptance is met. End completed child activity using supported host
   controls and report the integrated result, actual checks and remaining limits.
   No background improvement loop or mandatory extra reviewer runs after completion.

The two-child and one-corrective-pass limits are local operating defaults, not
OpenAI-prescribed optimal values or a guarantee of faster or cheaper execution.

## Handoff

```text
Objective and completion condition:
Project root, applicable instructions and relevant source paths:
Allowed write scope, shared contracts and other writers (or read-only):
Acceptance checks and existing evidence that can be reused:
Budget: one initial pass; no further delegation; return blockers promptly.
Return: concise findings with file/line evidence, changed files, checks/results,
unresolved issues and the exact source identity tested. Do not return raw logs.
```

## Models, permissions and project use

Preserve the parent's selected model/effort. Existing TRACE child defaults are
GPT-6.1 Sol medium; the existing read-only explorer uses Sol high. Retain them
unless the user requests a change. A custom role can override resolved defaults;
do not assume every child inherits the parent's model, especially with Astra.
Keep uncertainty explicit if the host does not expose the actual child's identity.

Global enabled/default settings do not themselves request delegation. Current local
Codex follows direct requests or applicable AGENTS.md/skill delegation instructions;
the agreement's standing request is conditional and cannot override higher-priority
host restrictions. If unavailable or prohibited, proceed directly.

New local sessions load Codex-home guidance plus applicable project instructions;
no copy of the global agreement or agent files is needed in each project. Project
rules and custom agents may override defaults. On a mismatch, inspect applicable
overrides and the active CODEX_HOME, rather than reinstalling global files.

Children must follow the same applicable project rules and acceptance standard.
Read-only exploration is a behavioral instruction, not enforced write isolation:
custom-agent sandbox/approval settings cannot replace the parent's permissions.
Do not broaden tools, permissions, authentication or external-write authority.

Sources reviewed 2026-10-25: [OpenAI subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
Official guidance favors bounded independent work and concise summaries, warns
about parallel write conflicts and states that comparable subagent runs consume
more total tokens. These local limits aim for useful speed and accuracy, not a
measured token-saving claim.
