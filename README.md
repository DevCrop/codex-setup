# TRACE Setup v1.1

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
`--personal-skills` selects the separate personal skill root (default
`~/.agents/skills`); CODEX_HOME does not relocate it. For isolated checks, set
`--home`, `--personal-skills`, and `--state` to disposable locations together.
Keep the same roots for plan/apply/verify/rollback. Overlapping roots are refused.
The complete reviewed upstream skill packages are bundled in `vendor/` and managed
by the same manifest for offline installation, removal, and rollback. They retain
upstream instructions unchanged; the global working agreement limits applicability.
TRACE adds only `agents/openai.yaml` with implicit invocation disabled for these
two skills. Invoke `$ponytail` or `$archify` explicitly (or select the skill in the
app). This retains their full upstream procedures; it does not shorten the skills.
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
[release verification](docs/verification-v1.1.md). Update detection produces review
candidates only. One designated desktop host runs weekly checks; inactive hosts
cannot guarantee scheduled execution. Review source changes and approve any policy
or upstream adoption before applying. No application-managed plugin cache is copied.

## Migrating v1.0.1 and other computers

Use tag `v1.1.0` for a reproducible release checkout. On an existing TRACE host,
review `plan` before `apply`. Do not copy an entire Codex home between computers;
authenticate independently and preserve local model, MCP, permissions and app state.

The installer accepts previous ownership records and retires exactly reviewed
`encoding-safety/SKILL.md` and `official-source-workflow/SKILL.md` under the personal
skill root. Modified copies conflict even with `--adopt-existing`. The UTF-8 policy
is in the agreement, source procedure in its conditional guide, and database notes
in the optional project reference. Only empty parents of removed files are pruned.
One local restore point contains their prior bytes; credentials and raw backups
must never be committed. `doctor` reports additional personal skills, which can
make another computer's effective context differ. Whole-home cleanup remains separate.
