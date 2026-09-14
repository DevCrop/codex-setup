# Optional model profiles

The user chooses the parent model and effort. TRACE does not auto-switch models or claim a measured model ranking. The optional CLI presets are `sol` (Sol medium), `astra` (Astra medium), and `astra-deep` (Astra high). Select with `codex --profile astra`; profiles do not select the app composer model.

Check host model availability before using a preset; report unsupported choices rather than silently substituting. Subagents inherit resolved parent settings unless an explicit spawn value, agents default, or custom-agent configuration overrides them. Inspect existing overrides during migration.

Sources: [Profiles](https://learn.chatgpt.com/docs/config-file/config-advanced), [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). Preset choices are user convenience policy, not official optimal-effort recommendations.
