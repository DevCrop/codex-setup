# Adaptive routine branch verification

Scope: the current guidance and portable maintenance prompt on
`codex/portable-adaptive-routine`, based on v1.2.3 main commit
`f8b972ebc867a4cbf096252d912ca1374809335a`.
This is branch/PR evidence, not a new tagged release or a transfer of monitoring authority.

## Acceptance

- The existing automation ID is explicit; authority requires the matching recorded
  host, ID, mode and approval date. A new or mismatched host stays review-only.
- Daily collection, local per-invocation integrity checks and observed in-task
  responses are distinct. No new event service or transparent rewrite hook.
- Global maintenance does not delete dependencies or replace separate cleanup policies.
- Private feedback and aggregate records remain local. Reporting does not imply
  actual OpenAI usage, model retraining or universal desktop interception.
- The actual payload supports isolated installation, repeat application, rollback,
  user-change conflicts and preservation of user-selected settings/authentication.

## Results

Performed on 2026-10-07, Windows / Python 3.13. All lifecycle experiments used
disposable homes, personal-skill roots and state directories; no real-home deletion.

| Check | Observed result |
|---|---|
| Full existing suite plus four added cases | 69 tests: 65 passed, 4 skipped, 0 failures |
| Offline repository validator | Pass; 117 manifest targets, 50 source references, two intact upstream skill packages |
| Actual payload CLI outside checkout | Pass; CODEX_HOME, Unicode/space paths, separate skill/state roots, plan/apply/verify/repeat/rollback |
| Existing main -> branch migration | Pass; only agreement, official-source guide and RTK guide changed in the managed payload |
| Repeated application | Unchanged; previous restore point bytes preserved |
| Restore to the main source | Pass against the previous source's owned-file verifier |
| User-owned managed-file edit | Rejected even with adoption; edited bytes preserved |
| Configuration/authentication fixtures | Model, effort, permissions, MCP, authentication/history fixtures and private state preserved |
| Current installed deployment | Owned-file verification passed; no unmanaged-skill findings |
| Current installed RTK | Ownership/hash/version verification passed, 0.51.0; no hook change |
| Existing codex authorization rendering | Matching local host/ID approved; no unresolved placeholders |
| Different host/ID and prompt injection | Review-only or invalid ID rejected, respectively |

The four local skips cover three unavailable symlink-creation cases and one
POSIX-only special-file case. Windows junction tests ran and passed. Native OS
coverage and any differing skips appear in the PR's final-commit GitHub checks.
No other physical user computer or fresh desktop model/skill session was run here.

The existing GitHub workflow runs the same lifecycle suite and offline validator on
native Windows, macOS and Linux with Python 3.11 and 3.14. Its status must be checked
for the final branch commit; a previous commit's green checks are insufficient.
Use its live results rather than treating this document as proof of a future run.

## Boundaries

No model/API calls, model benchmarks, new plugin/hook, scheduler creation, credential
copy, dependency deletion, merge, tag or release publication are required for this PR.
Local saved schedules do not prove future execution. The repository renderer does
not update the actual scheduler. The preserved designated-host automation and the
new computer's review-only default remain separate.

Historical [v1.2 verification](verification-v1.2.md) remains an observation of that
earlier release. Current instructions and the fresh-host checklist are in
[the portable routine guide](portable-routine.md).
