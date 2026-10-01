# Optional model profiles

The user chooses the parent model and effort. TRACE does not auto-switch models or claim a measured model ranking. The optional CLI presets are `sol` (GPT-6.1 Sol medium), `astra` (Astra medium), and `astra-deep` (Astra high). Select with `codex --profile astra`; profiles do not select the app composer model.

Check host model availability before using a preset; report unsupported choices rather than silently substituting. Subagents inherit resolved parent settings unless an explicit spawn value, agents default, or custom-agent configuration overrides them. Inspect existing overrides during migration.

Sources: [Profiles](https://learn.chatgpt.com/docs/config-file/config-advanced), [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). Preset choices are user convenience policy, not official optimal-effort recommendations.

## Recommended everyday model

For new work, prefer GPT-6.1 Sol when available to the account and client.
Keep Astra presets for tasks where the user explicitly selects Astra. Preserve
the chosen reasoning effort; medium in the Sol preset is a local convenience
policy, not a measured optimum. An existing base `model` setting overrides the
client recommendation. To choose this as a host default, review and set
`model = "gpt-6.1-sol"` in that host's config.toml. TRACE does not force this
choice on other hosts or change an existing conversation's selected model.

Source: [Current model recommendations](https://learn.chatgpt.com/docs/models),
reviewed 2026-10-01.
