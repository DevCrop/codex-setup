# RTK command output

Load when choosing output handling for noisy development commands. RTK is a third-party output filter, not an OpenAI feature or proof of subscription token savings. TRACE pins the reviewed release in versions.lock.json and installs one binary into private host state with scripts/tools.py install-rtk. No shared machine path, credentials, permission change, PATH edit, injected RTK.md or transparent rewrite hook is installed.

Use scripts/tools.py verify from the setup checkout to locate the owned binary, or scripts/tools.py run git status for explicit filtering. Prefer ordinary targeted rg and concise Git output when already sufficient. Use RTK only for supported, read-only diagnostic commands whose compression helps. Preserve arguments, exit codes and needed evidence. Read exact source code and authoritative acceptance-check output directly; rerun the original command when filtering obscures failures. Never interpret rtk gain estimates as actual OpenAI billed tokens or included allowance saved.

Outside the setup checkout, run the managed `bin/trace_rtk.py` in Codex home by absolute path with Python. Resolve Codex home from CODEX_HOME, otherwise the supported user home `.codex`; for example pass `git status` as arguments from the current project directory. The runner derives private tool state from that home, verifies the binary ownership/hash and preserves the caller's working directory. No project-local RTK files or extra project installation are needed. Custom deployment `--state` locations require tools.py --state STATE run instead; they are not guessed by the global runner.

For JavaScript/TypeScript tools, use the TRACE runner from the project working directory: it temporarily prioritizes that project's node_modules/.bin, blocks implicit npm downloads and disables RTK telemetry for the invocation. Direct rtk tsc can choose a global compiler; this was observed on Windows. Do not infer matching tool versions from two successful exits. Use the project-native acceptance command for final verification. The runner does not modify persistent PATH.

Do not transparently wrap deletes, installs, migrations, publishing, authentication or security decisions. Upstream's Codex hook rewrites commands before native approval checks, whose safety classifier does not unwrap RTK; this may obscure mutating-command signals. Hook setup is a separate opt-in review, with official /hooks trust, and is not included in this release. Do not bypass hook trust or add sandbox writable roots to make analytics work. Keep local analytics outside Git; analytics write failure does not establish filtering failure.

Sources: [RTK 0.51.0 release](https://github.com/rtk-ai/rtk/releases/tag/v0.51.0), [pinned Codex integration](https://github.com/rtk-ai/rtk/blob/v0.51.0/hooks/codex/README.md), [OpenAI hooks](https://learn.chatgpt.com/docs/hooks).

## Savings reporting

When reporting efficiency, use the verified runner's `gain --daily --format json`
aggregate snapshot; keep command text and project paths out of reports. Label
counts as local recorded invocations and values as RTK token estimates, never
OpenAI usage, money saved or subscription quota. Historical records may include
other RTK versions, repeated diagnostics and fixtures; do not attribute all savings
to the current runner. Compare arithmetic totals and disclose inconsistencies.
Pair estimates with a scoped raw/filtered byte comparison, exit/evidence checks
and recall/fallback limitations. Missing records mean unknown, not zero benefit.
On this user's authorized daily routine, collect daily aggregates and refresh one
current local chart, without duplicate daily totals or routine notifications.
Preserve recorded date/timezone limits and missing days as unknown. Compare one
permitted read-only raw/runner diagnostic and identify probe calls separately.
Other hosts need their own authorization. Do not run commands to increase gain.

## Existing host integrations

Earlier host guidance used a user-local PATH binary and an opt-in native hook.
The v1.2 installer neither removes nor upgrades that separately owned integration.
Prefer the verified TRACE runner to avoid silently selecting a second binary.
Inspect any existing hook with the supported Codex `/hooks` review and trust flow;
do not alter trust records or assume a processor smoke test proves desktop
interception. A CLI upgrade and a desktop app update are separate operations.
Do not copy host-local sandbox recovery paths or older 0.50.0 asset hashes into a
new computer. Preserve unrelated hooks, credentials, environment and permissions.
Sources: [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference),
[Hooks and trust](https://learn.chatgpt.com/docs/hooks).

## Use, release review and validation timing

Use the owned runner when a supported diagnostic is actually needed and its
output benefits from filtering; prefer already concise native output. Ownership
and SHA-256 verification already run per invocation in trace_rtk.py. This is a
local runtime check, not a network release lookup or universal hook interception.

Keep release discovery and daily gain collection in the authorized daily host
routine. One daily raw/filtered read-only probe checks the live path; count it as
a validation invocation. A changed RTK/CLI version, filter or relevant new failure
triggers only the affected existing checks during approved work, before relying
on the changed path. Do not reinstall an unchanged release or run probes at every
task start. Use native output immediately if compression hides needed evidence.
Confirm release compatibility before installation; stable releases may change
argument handling. Preserve existing hooks, trust, permissions and tool selection.
A task-observed failure is handled in that task, then summarized for daily review;
this does not install an event listener or authorize unrelated project commands.
