# TRACE v1.2.5 interaction and presentation verification

Working branch evidence, not a completed release. Performed on 2026-10-07,
Windows / Python 3.13. The existing v1.2.4 evidence remains historical.

## Completed checks

| Requirement | Observed result |
|---|---|
| Lifecycle, updates, checkpoint, storage and report tests | 88 cases: 83 passed, five platform/symlink skips, zero failures or errors |
| Installed managed policy | Exact-file verification passed; plan retained all 119 targets, including the existing configuration |
| Model/MCP/permission preservation | Installed configuration SHA-256 unchanged from the pre-change record |
| Ponytail and Archify | Pinned upstream package hashes and explicit-only invocation policies verified; upstream files not edited |
| RTK | Owned 0.51.0 binary verified; eight actual invocation/argument/exit/required-output checks passed using TRACE and disposable fixtures |
| Verification reuse | Binary/version, harness and execution-runner identities must all match; changed runner invalidates previous success |
| User interruption | Checkpoint returns user-resume-required; saved browser passes cannot override a recorded stop |
| Existing routine | Saved prompt matches its rendered source; weekly Monday 10:00 Asia/Seoul cadence, host, ID and chat retained |
| Flow and report | Tracked generators embed pinned Pretendard with its OFL license; upstream Archify is adapted in a temporary copy only |
| Archify static delivery | Validate, deliver and provenance check passed; nine static checks, no composition errors or warnings |
| Clean Git checkout | Independent local clone in a Unicode/space path passed repository validation; canonical JSON/HTML bytes match the working checkout exactly |
| Scoped uv cache check | Official uv 0.11.16 prune returned no unused entries; zero files removed, surrounding 25,375 regular-file metadata records unchanged |

The five local skips are four unavailable symlink-creation cases and one
POSIX-only special-file case. Windows junction checks are covered separately.
Final-head Windows/macOS/Linux CI must be inspected independently; a prior
release's checks do not validate this branch.

The generator normalizes generated HTML to LF and requires LF source JSON,
matching the repository's Git attributes. Receipts bind exact bytes rather than
ignoring line-ending differences during verification.

## Independent runtime findings

Native initialization and window enumeration passed; empty Notepad accessibility
reading passed. Native screenshot capture timed out, and coordinate input lacked
geometry. IAB public-document reading and an observed accordion action passed.
This is not Chrome-extension verification or product QA. See the
[incident record](troubleshooting/incident-08-computer-capabilities.md).

CLI 0.160.0 doctor independently reported Windows sandbox provisioning failure.
Matching scoped log evidence showed a Win32 sharing violation (32) on an existing
runtime file, not a confirmed long-path or access-denied error. Its relationship
to native capture and the durable repair remain unknown. No ACL, sandbox,
authentication or endpoint-protection changes were made. The reviewed
[0.160.1 release](https://github.com/openai/codex/releases/tag/rust-v0.160.1)
addresses remote stdio MCP environment preservation, not this observed failure.

The user stopped interaction with Escape and explicitly kept it stopped.
No subsequent UI capture or input is authorized. Do not bypass a denied local-file
preview with another protocol or headless rendering. Changed HTML's browser
behavior, rendered fonts and perceptual quality remain unverified; old browser
receipts must not be reused for new bytes.

## Remaining acceptance and boundaries

The Codex home scan is metadata-only: no cache, session, database, visualization
or plugin data was deleted. Large mixed artifact/dependency directories are not
proven unused or reclaimable; exact ownership/activity/regeneration and scope
remain required. This is not completed whole-home storage optimization.
The inspected uv cache contains about 5.28 GB of logical data, about 5.23 GB in
multi-link files. Clearing that directory does not establish the same physical
space saving; usage of its associated 3D environment remains a user decision.

The report keeps RTK estimates separate from actual OpenAI usage; mixed historical
measurements and their arithmetic discrepancy do not establish subscription
savings or faster tasks. No model benchmark or API model call was run.

Fresh-session skill invocation, native capture/input recovery, final browser
review and unused-data retirement remain outstanding. A draft PR can preserve
reviewable work while these gates remain open; do not call it a verified release.
