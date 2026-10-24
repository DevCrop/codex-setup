# RTK command output

Load for filtered diagnostics. RTK is third-party software, not an OpenAI feature
or evidence of subscription savings. TRACE pins RTK 1.0.1's Apache-2.0 OSS edition
and all five platform asset digests in versions.lock.json. Its CLI binary is still
named rtk. Pipeline engines, proxy daemons, native rewrite hooks and RTK.md injection
are not installed.

## Run only needed diagnostics

Use the verified CODEX_HOME/bin/trace_rtk.py runner for supported read-only
commands, including nested Python/PowerShell invocations. Honor CODEX_HOME and
retain the project working directory. From the setup checkout, tools.py run is
also supported; a custom deployment state must be passed to that tool explicitly.
The runner verifies binary ownership/hash on each invocation; do not double-wrap
or assume an existing native hook catches nested commands.

Keep exact source reads, structured JSON, mutations and final acceptance native.
Do not wrap deletion, installation, migration, publishing, authentication or
permission decisions. Never use bypass (formerly proxy) to claim an unsupported
command was compressed. If filtering hides needed evidence, use native output.
If the runner is unavailable, continue normally and report a material limitation.

Search narrowly and bound output. Do not add diagnostics or repeat checks merely
to increase gain. Preserve arguments, exits and required evidence. Use the project
compiler: the runner temporarily prioritizes node_modules/.bin, requires local
TypeScript for tsc, blocks implicit npm downloads and leaves persistent PATH alone.
Final acceptance still uses the project's native command.

## Keep this host's data separate

The managed runner and tools.py run use a private tools/rtk/history.db under the
resolved TRACE deployment state. Reject linked history paths. Do not migrate,
merge or modify Claude's RTK database, hooks, config or binary. The 1.0 schema
change is confined to this private database. Environment overrides exist only for
the invoked process; telemetry remains disabled. No service or watcher is added.

Earlier saved aggregates may contain shared Claude/Codex/fixture/version history.
Keep them labelled historical/shared and do not add them to the new private totals.
Private history can include explicit validation calls and is not pure task usage.
Missing dates are unknown, never invented zero rows. UI counters can restart at
this scope boundary; that is not deletion of the earlier history.

## Evidence and update lifecycle

Use gain --daily --format json through the owned runner for an authorized
aggregate. These are RTK token estimates and recorded invocations, not actual
OpenAI tokens, money or quota. Keep raw/filtered bytes, original probe time,
binary/runner identity, source timezone uncertainty and arithmetic discrepancies
separate. Version 1.0 changes the headline treatment of oversized outputs; compare
only matching scopes and definitions. Preserve stale snapshots as stale.

Collect releases and date-keyed snapshots on the existing cadence. Interpret on
request or a material anomaly. plan-rtk-update validates exact stable assets from
the current collection; it does not approve or install. Review changed features,
licence, platform assets and argument/JSON compatibility. Same-version drift,
missing assets or user edits block replacement; never reinstall an unchanged pin.
Use the owned installer, verify and one previous binary. After a changed tool/filter
or relevant failure, run only affected existing byte/exit/evidence checks; reuse
matching dated success. Count validation calls separately where observable.

Existing user-local RTK binaries and opt-in hooks have separate ownership. TRACE
neither upgrades nor removes them. The upstream Codex hook rewrites commands before
native approval classification, which does not unwrap RTK; keep hook trust and
permissions unchanged. CLI/app runtimes are also separately owned. Never replace
an application-managed executor to match a standalone CLI release number.

Sources reviewed 2026-10-25: [RTK 1.0.1](https://github.com/rtk-ai/rtk/releases/tag/v1.0.1),
[edition build](https://github.com/rtk-ai/rtk/blob/v1.0.1/Cargo.toml),
[tracking schema](https://github.com/rtk-ai/rtk/blob/v1.0.1/src/core/tracking.rs),
[Codex integration](https://github.com/rtk-ai/rtk/blob/v1.0.1/hooks/codex/README.md),
[OpenAI hooks](https://learn.chatgpt.com/docs/hooks).
