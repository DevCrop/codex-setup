# TRACE v1.1 release verification

Date: 2026-09-21. This is configuration/lifecycle verification, not a model benchmark.

- Global agreement, normalized UTF-8/LF: 4,334 → 1,458 bytes; whitespace-delimited words: 599 → 193. These are text-size measurements, not measured tokens, subscription savings or performance.
- Windows local Python: 35 tests, 33 passed, two symlink-creation cases skipped because this host does not grant symlink creation. Junction refusal is tested separately. Tests include both-root migration, user-edit conflicts, interrupted recovery, rollback and the complete pinned release payload's install/uninstall/restore.
- Repository integrity: 224 manifest assets plus the existing managed config keys (225 deployed files), 38 references, two unchanged pinned upstream packages. TRACE owns two additional explicit-invocation YAML files separately from upstream hashes.
- Flow: 9/9 showcase checks; four browser viewport containment checks; 1440×900 dark and 2048×1320 light visual review passed. The receipt binds the JSON and HTML. Owned render sidecars were removed.
- SCSS, TS and document review routing examples were reviewed as template guidance. No product project was selected or altered; no actual model-task compliance claim is made.
- Native CI, current-host deployment and fresh-session loading results are recorded below when completed. A static YAML check alone does not establish actual model behavior.

The [Astra guide](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) supports narrower triggers and relevant context. [Build skills](https://learn.chatgpt.com/docs/build-skills) documents the explicit-only policy. Korean responses, model choice, two-child preference and approval-based weekly updates remain user operating choices, not a complete OpenAI preset.

Known limits: whole-home sessions/caches and large artifacts are not cleaned by this release; other personal skills are reported, not deleted. Real separate-drive Windows and a fresh desktop UI task require host validation. Credentials, MCP paths and app state remain local. CLI and upstream versions are not upgraded.

Rollback: run the v1.1 installer `rollback` before another changed deployment replaces its single restore point, then use the v1.0.1 checkout to verify the restored release. User edits after installation are conflicts, never overwritten to obtain a pass. See [operations](operations.md).
