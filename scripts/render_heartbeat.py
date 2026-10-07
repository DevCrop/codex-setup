"""Render the existing monitor prompt; does not create/update an automation."""
import argparse
import platform
from pathlib import Path
import re

from setup import ROOT, Deployment, read_json


def render(routine, checkout=ROOT, host_identity=None, automation_id='trace'):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', automation_id):
        raise ValueError('Automation ID must be 1-64 letters, digits, underscores or hyphens')
    authorization = routine.get('maintenance_authorization', {})
    if (authorization.get('mode') == 'compatible-global-stable-tools' and
            authorization.get('automation_id') == automation_id and
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
    return (template.replace('{{checkout}}', str(Path(checkout).absolute()))
            .replace('{{authorization}}', scope).replace('{{automation_id}}', automation_id))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path)
    parser.add_argument('--automation-id', default='trace',
                        help='ID of the existing host automation; must match local authorization')
    args = parser.parse_args()
    state = args.state or Deployment().state
    print(render(read_json(state / 'routine-review.json', {}), automation_id=args.automation_id))


if __name__ == '__main__':
    main()
