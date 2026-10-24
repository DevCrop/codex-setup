# Codex dashboard — existing monitor UI, separate Codex data

The user requested reuse of the existing local Claude monitor's HTML/CSS appearance.
The Codex viewer uses the same layout tokens, panels, tabs, typography and chart
components, with Codex-specific content. The reference stylesheet is copied without
private Claude statistics; its identity is in
`templates/reports/codex-dashboard-source.json`.

Claude settings, hooks, collectors, files and its port 47811 listener are not edited
or restarted. The existing disk map is an optional read-only link, not rescanned,
embedded or rewritten. Its machine-local URL is configured only in the private
routine record's `dashboard_links.disk_map`; it accepts an HTTP loopback root URL
and is not copied into shared configuration. The optional Codex listener has its
own default port 47812.

This is the current host's primary Codex UI. During migration, retire superseded
private `overview.html`, `overview.json`, `rtk-status.html`, its duplicate evidence
and copied display assets only after receipt/hash checks and an allowed deletion.
If execution policy blocks removal, retain and record the exact unresolved targets;
do not retry through a different tool or report them removed. Keep `rtk-efficiency.json`: both the RTK
collector and Codex viewer use it for original probe evidence and stale fallback.
Repository templates and their font remain source assets, not disposable copies.
Historical release documentation is evidence of those versions, not current setup
instructions. Do not regenerate retired host HTML during routine collection.

## Start and stop

From the checkout, or using the script's absolute path:

```text
python -B scripts/codex_dashboard.py --port 47812
```

Open `http://127.0.0.1:47812/` in the Codex desktop built-in browser. The process
must remain running. This command does not create a startup item, service, hook or
scheduled task. A foreground instance stops with Ctrl+C. For a deliberately started
background instance, identify it through the owned `codex-dashboard-ready.json` in
the private reports folder and matching `/api/health` instance ID before stopping
only that process. Never stop an unrelated listener or silently choose its port.

`--home`, `--state` and `--personal-skills` use the existing installer's supported
path conventions. Honor `CODEX_HOME`; do not copy machine-local state to another PC.
Do not copy the entire Codex home or credentials. New computers install their own
reviewed setup and tools before opting in to this viewer.

## What each tab reports

| Tab | Evidence |
|---|---|
| Overview | Installed/source versions, owned-file fingerprints, recorded routine and shared RTK estimates |
| Routine | Actual saved schedule/status and distinct collection/review/application/project-scan times |
| Agents | Selected configuration defaults and explorer settings, not live session execution |
| RTK | Existing verified runner's aggregate JSON, actual collection time and retained probe time |
| Ponytail | Installed skill hash versus lock and explicit-only policy; invocation counts remain unknown |
| Settings | Release receipt, dated CLI observation, outstanding findings and existing disk-map link |

The browser refreshes every ten seconds while visible, without overlapping requests.
The server caches the projection for ten seconds across clients. Only RTK's existing
read-only aggregate path executes; it does not call a model, run benchmarks, run full
setup verification, fetch Git, invoke Ponytail, spawn agents or crawl the disk.
The optional live view does not change the scheduled snapshot or routine timestamps.
Python/server code changes require restarting this owned viewer; refresh is not an
automatic pull or self-update mechanism.

Unavailable state is labelled unknown. RTK failure retains the last aggregate and
its original time, with a stale warning; missing dates are not fabricated as zeros.
Older saved records may mix Claude, Codex, fixture and other-version invocations. Estimates
are not actual OpenAI usage, subscription quota, money or Codex-only savings.
From v1.3.5 the owned runner uses isolated TRACE history. The viewer labels the
scope and does not add previous shared totals to private totals. Validation calls
remain included. Shared records are preserved; the 1.0 database schema is never
migrated into Claude's history by the managed runner.
Live agent counts, request-level models, real token totals, cache hit rate and local
Ponytail savings remain unmeasured. File fingerprints do not prove model compliance,
whole-home cleanliness or a fresh lifecycle/runtime test.

## Read-only boundary

The listener binds only to 127.0.0.1. Exact Host/Origin checks, an asset allowlist,
read-only methods and CSP prevent arbitrary file serving or cross-origin reads.
The known configuration TOML is parsed in memory; only allowlisted model/agent
metadata enters the response. MCP secret values are neither returned nor logged.
Authentication files, conversation/session contents and raw command history are
not read. The viewer cannot delete files, change policy or run arbitrary commands.

Source and rendered desktop/mobile comparisons, theme/navigation, actual data
and error retention are checked for the affected build. Screenshots stay private;
do not commit host statistics or visual evidence with personal data to this repo.
See [the dashboard design QA](../design-qa.md) for the tested scope and limitations.
