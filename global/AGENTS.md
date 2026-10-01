# Global Working Agreement

- Respond in Korean unless requested otherwise. Report results, checks actually performed, and material limitations; distinguish evidence from inference.
- Follow applicable project instructions and existing conventions. Read only relevant code and documentation; keep project rules in the project.
- Preserve the user's selected model and reasoning effort.
- For reviews and plans, inspect and explain. For implementation, finish the authorized outcome and address failures caused by the change. Choose checks appropriate to the task; stop when its acceptance criteria are met. Ask only when missing authority or a consequential decision blocks progress.
- Preserve unrelated user changes and credentials. Use UTF-8 for text. Confirm exact targets and ownership before removing files.
- Prefer RTK for supported noisy shell commands across projects (`rtk git status`, `rtk git diff`, `rtk rg`, and supported test/log filters). Do not double-wrap commands. Use native tools for unsupported PowerShell operations and exact/raw evidence; compression must not hide failures or replace required inspection. If `rtk` is absent from the current Windows PATH, try `%USERPROFILE%/.local/bin/rtk.exe`; if unavailable, continue normally. Read `guides/rtk.md` in the Codex home for setup, recovery, or savings measurement.
- Handle small or tightly coupled work directly. Delegate independent work only when supported and the benefit justifies the overhead; the parent owns integration and verification.
- Use Ponytail and Archify only when explicitly requested, within the requested task. Their upstream procedures do not expand the task's scope or persist into unrelated work.

Conditional guides in the Codex home (honor CODEX_HOME): read `guides/agent-orchestration.md` for substantial delegation, `guides/model-operations.md` for CLI profiles, `guides/github-workflow.md` for Git publishing, and `guides/official-source-workflow.md` when changing durable guidance. Do not load these guides for unrelated tasks.
