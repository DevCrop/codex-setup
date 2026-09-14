"""Offline release integrity checks; does not call any model."""
import hashlib
import json
from pathlib import Path
import re
import tomllib

from setup import ROOT, read_json, safe
from index_docs import render


def main():
    for p in ROOT.rglob("*.json"):
        if ".git" not in p.parts:
            json.loads(p.read_text(encoding="utf-8"))
    for p in (ROOT / "global").rglob("*.toml"):
        tomllib.loads(p.read_text(encoding="utf-8"))
    manifest = read_json(ROOT / "manifest.json")
    if tomllib.loads((ROOT / 'global/config.base.toml').read_text(encoding='utf-8'))['agents'] != manifest['agent_settings']:
        raise ValueError('Config documentation differs from deployed manifest values')
    targets = set()
    for f in manifest["files"]:
        if f["target"] in targets:
            raise ValueError("Duplicate manifest target")
        targets.add(f["target"])
        assert safe(ROOT, f["source"]).is_file()
    for skill in read_json(ROOT / "versions.lock.json")["skills"]:
        folder = ROOT / "vendor" / skill["name"]
        actual = {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in folder.rglob("*") if p.is_file()}
        assert actual == skill["files"], f'Upstream integrity mismatch: {skill["name"]}'
    sources = read_json(ROOT / "references/registry.json")["sources"]
    assert len({s["id"] for s in sources}) == len(sources)
    for source in sources:
        if source.get('snapshot'):
            snapshot = source['snapshot']
            path = safe(ROOT / 'references', snapshot['path'])
            if hashlib.sha256(path.read_bytes()).hexdigest() != snapshot['sha256']:
                raise ValueError('Source snapshot hash mismatch: ' + source['id'])
    if (ROOT / 'docs/index.md').read_bytes().replace(b'\r\n', b'\n') != render():
        raise ValueError('Documentation index is stale; run scripts/index_docs.py')
    receipt = read_json(ROOT / 'diagrams/global/codex-flow.receipt.json')
    for suffix, field in [('json', 'specification_sha256'), ('html', 'artifact_sha256')]:
        if hashlib.sha256((ROOT / f'diagrams/global/codex-flow.{suffix}').read_bytes()).hexdigest() != receipt[field]:
            raise ValueError('Flow receipt is stale: ' + suffix)
    for folder in ("global", "docs", "templates"):
        for p in (ROOT / folder).rglob("*.md"):
            text = p.read_text(encoding="utf-8")
            assert "\ufffd" not in text, f"Encoding replacement character: {p}"
            assert not re.search(r"[A-Za-z]:[\\/]Users[\\/]", text), f"Machine path: {p}"
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if '://' in target or target.startswith('#'):
                    continue
                if not (p.parent / target.split('#')[0]).exists():
                    raise ValueError(f'Broken documentation link: {p.relative_to(ROOT)} -> {target}')
    print(json.dumps({"status": "pass", "managed_files": len(targets), "references": len(sources), "skills": 2}))


if __name__ == "__main__":
    main()
