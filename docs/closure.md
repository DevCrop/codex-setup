# v1.0.1 closure audit

## Corrected behavior

- Uninstall restores only currently owned config keys. A key released by an earlier update belongs to the user and is no longer overwritten.
- Repeated uninstall is a no-op and preserves the usable restore point.
- Uninstall checks for concurrent edits and verifies the resulting files before declaring success.
- Verify checks the installed version and ownership hashes as well as file contents.
- Source monitoring exits nonzero on fetch failure, keeps the last success marker, and removes discontinued source entries from its current local index.
- HTML monitoring prefers the main/article body to reduce navigation noise. A text hash remains a review candidate, not proof of a meaningful policy change.
- One manifest lifecycle owns bundled skills; the duplicate bootstrap script was removed.
- Source hashes, diagram hashes, config values, document links, and the generated documentation index are now release checks.

## Flow and rule mapping

| Behavior | Authoritative location | Verification |
|---|---|---|
| Global work and delegation policy | [Global agreement](../global/AGENTS.md) | Fresh CLI prompt rendering; model compliance remains separate |
| Installed files and retired targets | [Manifest](../manifest.json) | setup.py verify and lifecycle tests |
| Upstream package versions | [Version lock](../versions.lock.json) | Exact vendored file hashes |
| Official source decisions | [Source registry](../references/registry.json) | Snapshot hashes and review statuses |
| Failure/rollback branch | [Global flow](../diagrams/global/codex-flow.html) | Archify showcase plus browser containment |
| Project adoption | [Project template](../templates/project/README.md) | Requires selected project's actual source and commands |

## Active installation audit

The v1.0.1 local installation contains 223 owned files and passes manifest
verification. No pending transaction remains; one restore point exists. The
global instruction entry is AGENTS.md with no AGENTS override sibling. The
managed guides/profiles directories contain no unaccounted files. Six generated
visual-check sidecars were removed after the compact diagram receipt was updated.
These checks do not classify unrelated Codex home contents as legacy.

## Boundaries

Archived lab records remain outside the active setup repository. Unmanaged app
state and user-modified conflicts are not broad deletion targets. A successful
manifest check does not mean every file under the user's Codex home is owned.
Abrupt process termination may leave OS temp artifacts without a journal; their
ownership cannot be inferred from a filename prefix, so they are not swept blindly.
Existing product projects and the app settings UI have not been directly verified.
No model benchmark or quantified token saving claim is part of this release.
