"""Render the existing monitor prompt; does not create/update an automation."""
import argparse
import platform
from pathlib import Path

from setup import ROOT, Deployment, read_json


def render(routine, checkout=ROOT, host_identity=None):
    authorization = routine.get('maintenance_authorization', {})
    if (authorization.get('mode') == 'compatible-global-stable-tools' and
            authorization.get('automation_id') == 'trace' and
            authorization.get('host_identity') == (host_identity or platform.node()) and
            authorization.get('approved_on')):
        scope = ('Human-approved on ' + authorization['approved_on'] +
                 ': compatible small global Markdown updates and stable Codex CLI/RTK '
                 'after review and verification, within operations scope. This does not '
                 'authorize future GitHub publication, new features or scope expansion.')
    else:
        scope = ('Review-only; collect, analyze and verify. Managed changes and upgrades '
                 'require explicit host authorization. No authority is inherited from this repository.')
    template = (ROOT / 'templates/maintenance-prompt.md').read_text(encoding='utf-8')
    return template.replace('{{checkout}}', str(Path(checkout).absolute())).replace('{{authorization}}', scope)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path)
    args = parser.parse_args()
    state = args.state or Deployment().state
    print(render(read_json(state / 'routine-review.json', {})))


if __name__ == '__main__':
    main()
