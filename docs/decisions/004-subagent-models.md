# Decision 004: subagent model defaults

Approved by the user on 2026-10-12. The parent model stays the user's choice (decision 001); TRACE now also sets the default for spawned agents.

- `[agents] default_subagent_model = "gpt-6.1-sol"`, `default_subagent_reasoning_effort = "medium"`: code-changing children run on Sol, which the Models page describes as near-Astra performance at lower cost for repeated, long-running work.
- `agents/explorer.toml`: the October 24 reconciliation preserves the deployed `gpt-6.1-sol` at `high`; the earlier Luna example is no longer the deployed choice. This preserves the installed model rather than inferring a new selection from a benchmark. The custom agent replaces the same-name built-in agent.
- Read-only search is an instruction, not enforced write isolation. Custom-agent `sandbox_mode` does not override parent permissions; the ineffective field is removed. No parent permissions or available tools are broadened.
- These are local operating choices, not a measured model ranking or a policy for another product. No benchmark was run (repository rule).
- Undo: remove the two keys from `global/config.base.toml` and `manifest.json` `agent_settings`, remove the `explorer` entry and file, then `setup.py apply`. TRACE restores the user's original `[agents]` values it recorded.

Sources: [Models](https://learn.chatgpt.com/docs/models), [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), both read 2026-10-12.
