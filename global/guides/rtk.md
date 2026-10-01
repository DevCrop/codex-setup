# RTK shell output policy

Use RTK across projects when a supported CLI command would produce noisy output.
Examples: `rtk git status`, `rtk git diff`, `rtk rg "pattern" .`, and supported
test, build, and Docker log filters. Scope the command first; do not produce
unnecessary output just to compress it. Do not wrap an already wrapped command.

Use native tools for unsupported operations, PowerShell cmdlets and scripts,
machine-readable data, complete source/config inspection, or exact diagnostic
evidence. `rtk proxy <program> <args>` provides unfiltered output when appropriate.
Never treat a summary as proof that omitted lines contain no relevant evidence.
Do not repeat mutating commands to recover output. RTK does not grant authority
to install, build, publish, delete, or change permissions.

## Host installation

Reviewed release: RTK v0.50.0, 2026-10-01. Obtain the Windows binary from the
official release and verify its published SHA-256. The reviewed Windows ZIP hash
is `cb03399305135dd59ee23eb59a3260ccdeea5a8e08fbc7a271b115b85583a6c9`.
Install the executable in the user's `.local/bin` and add that folder to user PATH.
An already-running desktop app may need restarting to inherit PATH changes.

Upstream `rtk init -g --codex` writes hooks.json, RTK.md and an AGENTS.md reference.
TRACE owns AGENTS.md: do not let another installer overwrite that agreement.
Generate the upstream integration in a disposable CODEX_HOME, inspect hooks.json,
and merge its Bash PreToolUse entry into the real host's hooks.json, preserving
existing entries. Use the installed executable's absolute path when the running
app has an older PATH. This guide and the agreement provide explicit-call fallback;
the upstream awareness text is not required. Hook registration and the executable
are machine-local and are not installed or removed by setup.py.

Codex requires review and trust of new or changed non-managed hooks. Use `/hooks`
in Codex CLI to review the exact registration; do not edit trust records or bypass
trust. Restart the host after setup. Registration and a processor smoke test do
not prove end-to-end interception in an existing desktop chat. Until confirmed,
invoke RTK explicitly. Preserve sandbox, approval, model, MCP and login settings.

The native hook rewrites supported Bash/exec calls. Browser actions, hosted tools,
MCP outputs, prompts and reasoning are outside this RTK integration's scope.
RTK's required PreToolUse `allow` accompanies the replacement input; Codex retains
its execution checks, but classification of an RTK-wrapped command can differ.

## Verification and recovery

Check `rtk --version`, compare a read-only native/RTK command, and use `rtk gain`
for local command-output estimates. RTK estimates tokens from bytes; these are not
account usage, guaranteed savings, or subscription-limit measurements.
In v0.50.0, the generic "No hook installed" warning checks Claude's hook files;
it is not a Codex registration test. Inspect Codex's hooks.json and `/hooks`.
On Windows, verify RTK inside the actual Codex sandbox. If RTK reports that it
cannot determine the Claude config directory, use the documented Codex
`shell_environment_policy.set` table to set `CLAUDE_CONFIG_DIR` to the host's
existing Claude directory. This is a host-local path; do not deploy another
machine's absolute path. It does not install Claude hooks or change Claude files.
A native PowerShell session may report a generic failure code; compare child exit
codes through `$LASTEXITCODE` when checking exact error preservation.

A sandbox `setup refresh` failure occurs before RTK execution. Inspect the exact
runtime path and access error. Long-path support alone may not fix it. Back up
only a verified unused generated cache if it blocks validation; preserve active
runtimes, user history and sandbox protections. This is a local recovery finding,
not a mandatory cleanup step for other hosts.

When a filter fails, use raw evidence rather than guessing. To stop automatic
rewriting, disable/remove only the RTK hook via Codex's hook UI, leaving other
hooks intact. Removing the global preference is a separate TRACE source change.

Sources:
- [Official RTK repository](https://github.com/rtk-ai/rtk)
- [Reviewed release](https://github.com/rtk-ai/rtk/releases/tag/v0.50.0)
- [Codex adapter](https://github.com/rtk-ai/rtk/blob/v0.50.0/hooks/codex/README.md)
- [Codex hook and trust contract](https://learn.chatgpt.com/docs/hooks)
- [Codex shell environment configuration](https://learn.chatgpt.com/docs/config-file/config-reference)
