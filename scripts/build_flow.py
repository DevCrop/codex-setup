"""Static Archify delivery with a TRACE font adapter; no browser bypass."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from presentation import font_css
from setup import ROOT, atomic, read_json, safe, save_json


def main():
    canonical = ROOT / 'diagrams/global'
    spec = canonical / 'codex-flow.json'
    if b'\r\n' in spec.read_bytes():
        raise ValueError('Canonical flow JSON must use LF, matching Git checkout bytes')
    artifact = canonical / 'codex-flow.html'
    receipt_path = canonical / 'codex-flow.receipt.json'
    old = read_json(receipt_path)
    if hashlib.sha256(artifact.read_bytes()).hexdigest() != old['artifact_sha256']:
        raise ValueError('Modified canonical HTML; preserve conflict')
    skill = next(s for s in read_json(ROOT / 'versions.lock.json')['skills'] if s['name'] == 'archify')
    with tempfile.TemporaryDirectory(prefix='trace-flow-') as directory:
        root = Path(directory)
        package = root / 'archify'
        for relative, digest in skill['files'].items():
            data = safe(ROOT / 'vendor/archify', relative).read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError('Upstream Archify bytes changed')
            target = safe(package, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        template = package / 'assets/template.html'
        text = template.read_text(encoding='utf-8')
        if text.count('</head>') != 1:
            raise ValueError('Unsupported Archify template')
        template.write_text(text.replace('</head>', font_css() + '\n</head>'), encoding='utf-8')
        out = root / 'codex-flow.html'
        command = ['node', str(package / 'bin/archify.mjs')]
        stages = {}
        raw = {}
        for stage, args in [
            ('validate', ['validate', 'workflow', str(spec), '--repo-root', str(ROOT), '--quality', 'showcase', '--json']),
            ('deliver', ['deliver', 'workflow', str(spec), str(out), '--repo-root', str(ROOT), '--quality', 'showcase', '--json']),
            ('check', ['check', str(out), '--require-provenance', '--json'])]:
            result = subprocess.run(command + args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=120)
            if result.returncode:
                print(result.stdout[:6000])
                print(result.stderr[:1500])
                raise ValueError('Archify ' + stage + ' failed; canonical output preserved')
            raw[stage] = json.loads(result.stdout)
            stages[stage] = 'pass'
        # Bind the receipt to portable Git bytes, not platform newline translation.
        data = out.read_bytes().replace(b'\r\n', b'\n')
        value = {'schema_version': 2, 'diagram_type': 'workflow',
                 'specification_sha256': hashlib.sha256(spec.read_bytes()).hexdigest(),
                 'artifact_sha256': hashlib.sha256(data).hexdigest(),
                 'specification_bytes': spec.stat().st_size, 'artifact_bytes': len(data),
                 'gates': {**stages, 'browser-check': 'not-performed'},
                 'repository_evidence': {'verified': True, **read_json(spec)['meta']['repository']},
                 'browser_evidence': 'not-performed', 'visual_review': 'not-performed',
                 'renderer_version': '3.0.0', 'presentation': 'TRACE temporary-template adapter / Pretendard 1.3.9 embedded',
                 'adapted_template_sha256': hashlib.sha256(template.read_bytes()).hexdigest(),
                 'limit': 'Static gates only. A denied file-preview protocol is not bypassed by a headless browser or alternate protocol; changed font/layout/browser behavior remain unverified.'}
        # Retain compact actual checks, not former browser receipts for changed bytes.
        checks = raw['validate'].get('checks', [])
        value['static_validation'] = {
            'checks_passed': sum(row.get('ok') is True for row in checks),
            'checks_total': len(checks), 'profile': 'showcase',
            'composition': raw['validate'].get('composition', {}).get('summary', {}),
            'checks': [{'name': row['name'], 'ok': row['ok']} for row in checks]}
        atomic(artifact, data)
        save_json(receipt_path, value)
    print(json.dumps({'status': 'static-gates-pass', 'gates': value['gates'],
                      'artifact_bytes': len(data), 'browser_review': 'not-performed'}))


if __name__ == '__main__':
    main()
