# Codex dashboard design QA

final result: passed

Scope: the opt-in Codex dashboard, not the original Claude dashboard or a new
global-policy deployment. Reviewed 2026-10-25, Asia/Seoul.

## Reference and fidelity

The reference is the existing local monitor. Its stylesheet is reused with the
same warm dark/light palette, typography, segmented navigation, KPI band, panel
grid and chart components. The checked stylesheet identity is recorded in
`templates/reports/codex-dashboard-source.json`. Labels, values and chart contents
intentionally represent Codex metadata. This is layout/style reuse, not a claim
that unlike datasets produce pixel-identical pages.

Claude settings, collectors, source files and listeners were not changed or
restarted. The Codex viewer runs on a separate loopback port. Its optional disk-map
link does not rescan or modify the existing map.

## Actual browser checks

- Compared reference and Codex screenshots at 1440 by 1000 and 390 by 844.
- Exercised Overview, Routine, Agents, RTK, Ponytail and Settings navigation.
- Verified dark/light theme changes and persistence in the Codex origin.
- Checked mobile Overview, Agents and Settings: no document horizontal overflow;
  wide tables use their own scrolling region.
- Observed ten-second refresh, saved daily 08:00 schedule and current metadata.
- Stopped only the owned Codex viewer: the page retained previous values and
  displayed a connection error; restarting the owned viewer restored collection.
- Checked the optional disk-map link target without changing the map.
- Final browser error/warning log was empty after recovery and reload.

Screenshots remain in private host reports. No personal reference statistics or
screenshots are included in this repository. The viewport override was reset and
the Codex dashboard was left open.

## Code and data checks

The existing suite passed 100 tests with four skips before the final optional-link
validation addition. All seven dashboard tests then passed with that addition.
Checks cover whitelisted metadata, absent secrets/history, ten-second caching,
unknown/stale handling, actual HTTP host/origin/path/method restrictions and
preservation of unrelated readiness files. The final repository checks and
JavaScript syntax check are separate from the browser evidence above.

The UI distinguishes configured model defaults from live session execution and
RTK estimates from actual OpenAI usage. Missing live counts, tokens, cache rates
and Ponytail savings remain unknown. Current file fingerprints are not a fresh
lifecycle test or proof of model compliance. Historical native-app interaction
failures are outside this browser validation and remain unresolved.

No unresolved P0/P1/P2 visual defects remain in the tested scope. Startup services,
remote hosting, automatic publication and other computers were not tested or added.

## v1.3.5 affected-scope follow-up

The current overview visibly shows v1.3.5, 17/17 fingerprints and the new private
RTK scope without adding old shared totals. Ponytail's tab visibly shows 5.3.2,
the pinned commit and explicit-only policy. The existing visual shell is retained.
The current screenshot replaces the private final screenshot. Broader earlier
viewport/theme checks retain their original dates and are not relabelled as new.

The current workspace suite passed 112 tests with four environment-dependent
skips, the dashboard-focused suite passed 18 cases, and eight changed-binary
runtime checks passed. The latter checks cover Git evidence, Unicode/space paths,
stderr, nonzero exits and argument preservation; they do not cover every filter.
An optional extra version-label/restart attempt was policy-blocked. That optional
source change was reverted; the already verified running viewer is retained.

## 2026-10-25 existing-component monitoring follow-up

The later, explicitly authorized dashboard update was restarted after fresh
readiness/health ownership checks. The running Codex page shows 29 installed
plugins, 121 discovered SKILL.md files, zero unavailable inventory entries,
dated quota percentages and the exact MCP probe limitations. These counts are
metadata checks, not execution of every installed skill or tool.

The affected final workspace suite ran 131 cases: 127 passed and four
environment-dependent cases were skipped. Managed installation and RTK native
verification passed. Desktop rendering and a 390px monitoring-card view were
inspected; the mobile document did not overflow its viewport. Browser error logs
were empty. The temporary viewport override was reset. Private current screenshots
replace the previous final image; they are not committed here.

Native Windows input failures, standalone MCP authentication/connectivity limits,
blocked historical artifact deletion and unpublished v1.3.5 remain separate dated
findings. This follow-up does not claim cross-platform CI or universal runtime
health. No Claude process or setup was modified.
