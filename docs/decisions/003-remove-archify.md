# Decision 003: Archify removed

Approved by the user on 2026-10-13 and explicitly reconfirmed on 2026-10-24: do not use Archify. TRACE sets up Ponytail and RTK only. Do not invoke, reinstall, monitor or propose upgrades for Archify unless the user later changes this preference. This supersedes the former requirement in Decision 001 and adoption deferral in Decision 002.

Removed: `vendor/archify`, its manifest, lock, registry and retirement entries, its invocation policy, the Archify-rendered `diagrams/global` flow and its receipt check in `validate_repo.py`, and Archify text in the global agreement, guides, templates and current docs. Release notes, verification records and handoffs stay as history.

The October 24 follow-up aligns the local checkout with the already merged removal,
retires the host's pending update candidate and owned temporary verification files,
and removes contradictory current documentation. Historical release evidence is not
an installation instruction. Existing user-created artifacts and unrelated projects
are outside automated cleanup; Git retains the removed tracked flow's history.

On a host that had Archify installed, `setup.py plan` removes the TRACE-owned copies that are unchanged. A modified owned copy is a conflict that blocks `apply` (existing plan behavior), and deleting it does not clear the conflict because the ownership record still holds its hash; such a host needs its record resolved before upgrading. Copies TRACE never owned (not in the record) are left alone and can be deleted by the user.
