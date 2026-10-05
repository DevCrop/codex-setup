# TRACE v1.2.1 release verification

Reviewed 2026-10-05 for the completion maintenance patch. The dated October 1
observations below remain historical evidence, not checks repeated today.

## October 5 maintenance acceptance

- Windows local suite: 56 cases, 52 passed and four platform/permission skips.
  New checks cover unpublished-version detection, unavailable GitHub/install state,
  initial-review gaps for registered projects, and preservation of retired-watch
  pending candidates. Resolving a hash-bound source also updates its report.
- CLI 0.160.0 installed from the exact official npm version; ChatGPT login status
  passed. Existing model, effort, MCP and permission defaults were preserved.
  No model calls, quota benchmark or permission changes were made.
- RTK 0.51.0 release digests pinned for the five supported platform assets;
  owned Windows binary installed and verified. Twelve native Windows checks passed:
  same-workdir Git, local TypeScript success/real errors, Unicode/space paths,
  nonzero exits/stderr and direct `test` argv containing literal shell characters.
  Other native RTK platforms are unverified. A single prior binary remains available
  through `tools.py rollback-rtk`; it is outside active setup paths.
- Isolated actual v1.2.0 to v1.2.1 migration: one guide changed, verify/repeat/rollback
  using previous source and reapply passed in disposable Unicode/space roots.
- The completion patch originally changed one guide. Merging previously approved
  main changes also reconciles RTK agreement and host-default guidance. Final
  deployment changed three owned files and verified 118 entries; repeat apply was
  unchanged, config bytes were preserved and the prior 1.2.0 restore point retained.
  The agreement is 1,855 LF bytes / 250 whitespace words
  (before this merge: 1,560 bytes / 210 words).
  Skill originals and explicit invocation policies remain unchanged. These text
  sizes are not a token-savings measurement.
- `check_closure.py` adds read-only release/deployment/tool alignment and first
  registered-project review checks. The existing Monday 10:00 designated-host
  heartbeat is extended in place. Candidate approvals and cleanup safeguards stay
  in effect; no new monitor or automatic publisher/upgrader is introduced.
- R31's deprecated examples catalog is historical; current official plugin examples
  and packaging are R43/R44. Ponytail's single deployed upstream asset matches
  v4.11.0 and current exact upstream HEAD, so no replacement is needed. Archify
  remains 3.0.0: the 3.0.1 stable reminder change is deliberately deferred for this
  quiet, centrally monitored setup. Reconsider on meaningful functional/security
  changes or an explicit request; unrelated main changes are not adopted.
- DevCrop initial review now records root/scripts/style instructions, relevant
  skill contracts, runtime pins and the existing executable contract source.
  Product source and its nine existing dirty status entries were preserved.
  No global template or flow was copied into the project. Its contract forbids
  Host `docs/`, so no project document tree was manufactured.
- Zero-model-call CLI `debug prompt-input` probes from the project and styles
  directories include the global agreement, project root and nested style rules.
  This does not prove model obedience or desktop session UI behavior. The explicit
  skill text is not expanded by the inspected debug renderer; filesystem policy
  verification does not establish an actual composer-selected skill invocation.
- Global flow topology is unchanged and its existing JSON/HTML receipt is validated.
  No new visual/perceptual or browser gate execution is claimed for this patch.

## Main reconciliation (October 5)

Merged PR #8's GPT-6.1 Sol preset and cross-project RTK preference are preserved
with a portable verified runner, replacing its unmanaged PATH fallback. Existing
host-local hooks are preserved, not installed or trusted by TRACE. PR #9's daily
authorization is retained as host-specific; only one weekly TRACE automation is
actually registered on this host. No cadence change or duplicate monitor occurred.
Registry IDs that collided across branches are deduplicated by canonical source;
R45 retains the historical 0.50.0 hook provenance. Current deployment uses the
reviewed 0.51.0 explicit runner, not older host-local install instructions.

## Prior v1.2 implementation evidence (October 1)

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

Native [CI run 36742103889](https://github.com/DevCrop/codex-setup/actions/runs/36742103889)
at code commit `c2413a9` passed all six Windows/macOS/Linux × Python 3.11/3.14
jobs, each running the 51-case suite with platform-specific skips and repository
integrity checks. The following commit records this evidence only.

CI validates portable lifecycle
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
