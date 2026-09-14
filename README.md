# TRACE Setup v1

Portable Codex personal instructions, optional profiles, pinned Archify/Ponytail,
and ownership-based deployment. Python 3.11+ and Git are required; Node.js is needed
to render Archify. Use ChatGPT subscription login on each host. No API key and no
50/200-run model benchmark are required.

## Install

Clone this repository anywhere, including paths with spaces and non-Latin names.
Run these commands from the checkout, or invoke the script by absolute path:

```text
python -B scripts/setup.py plan
python -B scripts/setup.py apply
python -B scripts/setup.py verify
```

For reviewed pre-existing personal instructions/profiles, inspect `plan --adopt-existing`
then use `apply --adopt-existing` once. This flag never overrides a modified file
already owned by TRACE. `--home` and `CODEX_HOME` select Codex home; `--state` selects
local deployment state. Defaults use supported per-user locations, not drive letters.
The complete reviewed upstream skill packages are bundled in `vendor/` and managed
by the same manifest for offline installation, removal, and rollback. They retain
upstream instructions unchanged; the global working agreement limits applicability.
`setup.py` is the sole install/update/verify/remove entry point, including skills.

## Lifecycle

```text
python -B scripts/setup.py rollback
python -B scripts/setup.py recover
python -B scripts/setup.py uninstall
python -B scripts/setup.py doctor --codex <executable-path>
python -B scripts/check_updates.py
```

`recover` handles a pending interrupted transaction. A single prior restore point
lives in private machine-local state, never in Git. Config restoration refuses
conflicting edits. Unmanaged files and credentials are not deleted. Close competing
setup/update processes before applying. A new session is needed to inspect effective
instructions; filesystem verification is not proof of app UI or model behavior.

Choose models in the app. Optional CLI commands: `codex --profile sol`,
`codex --profile astra`, `codex --profile astra-deep`. Profiles do not change
the persistent base model selection and do not implement automatic model switching.

## Project adoption

Start with [the project authoring contract](templates/project/README.md). Reuse
existing rule documents; do not blindly copy the template into an existing repo.
No actual project has been selected for this release. The global diagram lives in
[codex-flow.html](diagrams/global/codex-flow.html); each project's diagram must live
in that project's own repository and describe inspected source.

## Checks and maintenance

```text
python -B -m unittest discover -s scripts -p 'test_*.py' -v
python -B scripts/validate_repo.py
python -B scripts/index_docs.py
```

See [documentation index](docs/index.md), [operations](docs/operations.md), and
[release verification](docs/verification.md). Update detection produces review
candidates only. One designated desktop host runs weekly checks; inactive hosts
cannot guarantee scheduled execution. Review source changes and approve any policy
or upstream adoption before applying. No application-managed plugin cache is copied.
