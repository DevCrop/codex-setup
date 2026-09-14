# Ownership and package deployment

The manifest owns global policy files, profiles, and every file in the reviewed
Archify/Ponytail distributions. Bundled originals are pinned with per-file SHA-256
in versions.lock.json. Keeping complete originals makes offline installation and
transactional removal reproducible; package contents are not automatically loaded
as prompt context.

The official skill installer bootstrapped upstream packages. Subsequent managed
updates use setup.py so removal and rollback have the same ownership contract.
The standalone install_skills helper remains an optional bootstrap/hash checker.

Two specifically fingerprinted historical config backup files were retired from
the active Codex directory. Their contents remain only in the local prior restore
point. Other app state/backups were not declared owned and were not broadly deleted.

Global configuration is not an app-version lock. CLI 0.147.0 was observed and not
silently upgraded. Remote model availability may differ from its bundled catalog.
User-selected base model and reasoning settings are preserved.
