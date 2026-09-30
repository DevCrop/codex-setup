# TRACE v1.2 release verification

Reviewed 2026-10-01. Configuration and command checks only; no model benchmark or
API model calls. See [evidence boundaries](decisions/002-maintenance-and-rtk.md).

## Host and managed deployment

- Native Windows/Python local suite: 51 cases, 47 passed, four skipped (three
  symlink-creation permissions and one POSIX-only special-file case). Windows
  junction refusal passed. Tests exercise scoped cleanup, actual notification
  grace, activity/unknown-process cancellation, missing locks, tracked/nonignored
  content, interrupted intervals, package checksums, user edits and failed tool
  metadata writes, alongside existing install/remove/restore checks.
- Isolated actual v1.1.4 payload to v1.2.0: six changes, verify passed, repeat
  unchanged, rollback to v1.1.4 verified, then reapply verified. Disposable roots
  included spaces and Korean. No deletion tests ran on the real Codex home.
- Current host: six managed writes, 118 deployed files verified, repeat unchanged;
  no unmanaged user-skill findings. Base model, effort, service tier, credentials,
  MCP paths and permissions were preserved. The supplied task context refreshed
  with the RTK guide reference; a separately created desktop task was not tested.
- Optional `sol` profile now selects GPT-6.1 Sol Medium. This convenience preset
  is not a measured optimum or mandatory client default. CLI 0.159.2 and ChatGPT
  login status passed. CLI rollback is separate from policy rollback:
  `npm install -g @openai/codex@0.157.1` restores the prior host version.
- Always-loaded agreement: LF-normalized 1,507 to 1,560 bytes; whitespace-delimited
  words 204 to 210. Only a conditional RTK guide reference was added; these are
  text sizes, not actual tokens or subscription savings.

## RTK runtime checks

Upstream stable RTK 0.50.0 was checked against its official GitHub release. The
Windows release archive SHA-256 and extracted binary ownership were verified.
No automatic rewrite hook, injected RTK instructions, persistent PATH edit or
permission change was installed. Other platform asset digests are pinned, but
their native RTK execution has not been verified on this Windows host.

Eleven Windows checks passed in the setup repository, registered DevCrop repository
and disposable Unicode/space-path fixtures. Raw and RTK commands used the same
working directory and project tool environment. Assertions checked exit behavior;
diagnostic fixtures also required the same key error evidence.

| Observed command/fixture | Raw output bytes | RTK output bytes | Evidence |
|---|---:|---:|---|
| Setup Git status | 1,338 | 872 | Both exit 0; transient worktree snapshot |
| DevCrop Git status | 765 | 332 | Both exit 0; transient worktree snapshot |
| Git log in both repositories | 216 / 223 | 216 / 223 | No reduction |
| DevCrop TypeScript success | 0 | 28 | Both exit 0; summary adds bytes |
| Unicode/space Git status | 273 | 24 | Fixture filename retained |
| Unicode/space Git diff | 135 | 127 | Changed content retained |
| Intentional TypeScript error | 153 | 185 | Both nonzero, TS2322 retained |
| Explicit failure / stderr / space argument | 15 / 14 / 5 | 15 / 14 / 5 | Exits 7 / 3 / 0 retained |

Direct RTK `tsc` originally selected a different global compiler. TRACE now
prioritizes project `node_modules/.bin`, requires installed project TypeScript
and prevents implicit npm downloads. Both success and intentional-error cases
were rerun after that correction. The deployed global runner also passed DevCrop
`tsc --noEmit`. Final acceptance still uses project-native raw commands. No claim
is made that every filter preserves every diagnostic or reduces output.

## Maintenance and sources

- Existing `trace` heartbeat updated in place: Monday 10:00 host timezone; no new
  monitor. RTK releases and the host-local project registry now share that routine.
- Only DevCrop was registered. Observation started today with idle age zero;
  current ambiguous process state blocks deletion. Its tracked `vendor` is refused.
  No real project dependencies were removed. The minimum is 45 observed days plus
  seven days after actual notification; weekly cadence can extend it. This is a
  local policy authorized by the user, not an OpenAI inactivity standard.
- All 17 monitored endpoints collected successfully. Official model/profile and
  delegation guidance was reviewed; original Astra guidance was unchanged.
  Full release-feed/config-reference remainder and Archify upstream revisions
  remain pending rather than being marked reviewed from a truncated excerpt.
  Archify 3.0.1 stable reminder behavior was identified; 3.0.0 remains pinned
  pending a separate complete package review. Ponytail remains unchanged.
- Global flow updated for RTK/cleanup boundaries: showcase 9/9 and all four
  finalize gates passed, with four desktop viewport containment checks. No new
  perceptual screenshot review is claimed. Portable receipt binds JSON and HTML;
  generated intermediate files were removed after checking their exact paths.
- Repository validation covers 117 manifest assets plus managed config, 42 source
  records, two original skill packages, indexes/links and diagram hashes. Source
  collection, substantive review and policy application timestamps remain separate.

## Limits and restoration

CI results are recorded below only after execution. CI validates portable lifecycle
logic, not native RTK execution, account access or every product project. Cleanup
is deliberately manual-only for linked installs (common pnpm and POSIX layouts).
Human file reads may be invisible; `hold` and `touch` preserve active projects.
Unknown processes, missed observations and safety conflicts block automatic deletion.

The first macOS CI attempt exposed a test comparing `/var` with its canonical
`/private/var` spelling. The runner already canonicalizes the project path; the
test now requires that same canonical project-bin path. No path or ownership
protection was relaxed.

Policy rollback restores the previous managed payload; verify using that release
checkout. RTK has its own hash-checked rollback/uninstall. Dependency deletion
has no byte-for-byte rollback: retain source/locks and restore with the recorded
locked package-manager command during authorized work. Partial failures remain
unresolved. Whole-home Codex caches/session cleanup and the source of effective
session permission overrides remain outside this release's completion claim.

Sources: [OpenAI Astra guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra),
[Codex models](https://learn.chatgpt.com/docs/models),
[CLI changelog](https://learn.chatgpt.com/docs/changelog),
[RTK release](https://github.com/rtk-ai/rtk/releases/tag/v0.50.0),
[RTK TypeScript selection source](https://github.com/rtk-ai/rtk/blob/v0.50.0/src/cmds/js/tsc_cmd.rs).
