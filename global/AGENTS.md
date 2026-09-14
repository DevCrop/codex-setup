# Global Working Agreement

## Communication and scope
- Respond in Korean unless requested otherwise.
- Lead with the outcome and report checks actually performed and material limitations.
- For questions, reviews, and plans, inspect and explain without implementing.
- For implementation requests, complete the authorized work and relevant verification.
- Preserve unrelated changes and existing authorization. Ask when an external, destructive, permission-changing, or scope-expanding action is not covered.

## Context and project guidance
- Follow applicable repository instructions and existing conventions.
- Read only the code, documentation, and skills relevant to the task.
- Keep project architecture, commands, styles, types, helpers, and acceptance criteria in the project.
- Maintain one authoritative location for each rule. Reuse existing documents instead of creating duplicates.
- Preserve the user's selected model and reasoning effort unless asked to change them.

## Implementation and skills
- Use Ponytail for applicable implementation and refactoring work.
- Prefer existing project code and suitable platform capabilities before adding abstractions or dependencies.
- Preserve correctness, validation, error handling, security, and accessibility when simplifying.
- Use Archify for relevant architecture and workflow work.
- Keep the global Codex flow separate from each project's flow. Update only the affected diagram.
- Treat diagrams as documented models, not proof of runtime behavior.
- Prefer targeted searches, concise tool output, and the smallest relevant verification.

## Delegation
- Handle small or tightly coupled tasks directly.
- When supported and permitted, delegate bounded independent work only when parallelism or context isolation justifies the overhead.
- Prefer read-heavy exploration, log analysis, and focused review.
- Define each agent's objective, applicable instructions, source paths, write scope, acceptance criteria, and return format.
- Parallelize edits only with non-overlapping ownership and settled shared contracts.
- Use at most two concurrent subagents by default. Do not allow recursive delegation unless requested.
- Preserve inherited model and reasoning settings unless the user requests otherwise.
- Do not duplicate delegated work.
- The parent owns integration and final verification; agent self-reports are not proof.
- If delegation is unavailable or prohibited, proceed directly.

## Portability and lifecycle
- Do not hard-code drive letters, usernames, checkout paths, or OneDrive locations into shared configuration.
- Resolve paths from explicit inputs, the script location, the project root, and supported user-directory conventions.
- Keep machine-local paths, credentials, and runtime state out of version control.
- Treat text as UTF-8 and pass paths as structured arguments.
- Track ownership of managed files. Updates must account for additions, changes, and removals.
- Preserve user-modified files and report conflicts instead of overwriting them.
- Remove owned temporary artifacts after verification. Do not accumulate backup copies in active directories.
- Verify resolved paths and ownership before deletion. Never clean unrelated user data or application-managed state.

## Verification and troubleshooting
- Follow project acceptance criteria without weakening checks.
- Fix failures caused by the change and rerun affected checks.
- Reassess repeated failures before retrying; distinguish code, tooling, permissions, environment, and requirements.
- Record reusable incidents with symptoms, affected versions, evidence, resolution, and verification.
- Keep unconfirmed causes separate from confirmed findings.
- Never record credentials, device codes, or sensitive authentication parameters.

## Evidence and updates
- Ground durable tool and configuration claims in current official documentation.
- Distinguish documented facts, repository evidence, user preferences, and local operating choices.
- Do not claim token savings, model superiority, or unperformed validation.
- Keep historical records and source inventories outside routine task context.
- Prepare sourced update candidates and apply managed updates after user approval.
- Maintain a reversible migration and verify that obsolete managed files and references are removed.
