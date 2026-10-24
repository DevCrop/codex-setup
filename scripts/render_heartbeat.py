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
    approved = (authorization.get('mode') == 'compatible-global-stable-tools' and
            authorization.get('automation_id') == automation_id and
            authorization.get('host_identity') == (host_identity or platform.node()) and
            bool(authorization.get('approved_on')))
    if approved:
        scope = ('Human-approved on ' + authorization['approved_on'] +
                 ': compatible small global Markdown updates and stable Codex CLI/RTK '
                 'after review and verification, within operations scope. This does not '
                 'authorize future GitHub publication, new features or scope expansion.')
    else:
        scope = ('Review-only; collect, analyze and verify. Managed changes and upgrades '
                 'require explicit host authorization. No authority is inherited from this repository.')
    cleanup = authorization.get('dependency_cleanup', {})
    if (approved and cleanup.get('automation_id') == automation_id and
            cleanup.get('approved_on') and cleanup.get('policy') == 'registered-45d-7d'):
        cleanup_scope = ('Separately recorded approval for this existing automation permits only '
                         'operations Project dependency cleanup: registered auto_cleanup projects, '
                         '45 observed idle days, verified ignored/untracked direct-child locked '
                         'dependencies, certain process state, no links/special files and seven '
                         'days after ACTUAL candidate notification. Notify exact target, size, '
                         'evidence and reinstall command before reported; record grace once, never '
                         'acknowledge an unreported candidate or reset it for a heartbeat. Use '
                         'only revalidating prune for eligible rows; unknown/activity blocks deletion. '
                         'Preserve source, locks, stores, credentials and unregistered projects; '
                         'report retained/partial failures. Never delete through RTK or shell paths.')
    else:
        cleanup_scope = ('No drive discovery, registration or dependency deletion in this routine. '
                         'Preserve separately registered cleanup schedules and exact human-approved '
                         'policies; a repository default is not deletion authority.')
    health = authorization.get('setup_health', {})
    if (approved and automation_id == 'trace' and health.get('automation_id') == automation_id
            and health.get('host_identity') == (host_identity or platform.node())
            and health.get('approved_on') and health.get('policy') == 'paths-mcp-drift-monthly-recovery-v1'):
        health_scope = ('Separately human-approved setup health: run python -B scripts/maintenance_health.py collect '
                        'once per heartbeat. Supply session-model/effort/approval/sandbox flags only for explicitly '
                        'observed current execution values; unknown stays unknown. This reads saved settings and '
                        'checks only registered C-to-D link metadata daily; probe exact enrolled MCP configurations '
                        'on configuration change or seven days since last attempt. Record actual success separately; '
                        'OAuth unavailable, app closed, timeout and changed launch pending review are unresolved, '
                        'never proven healthy. Do not start application-bound GUI servers or auto-enroll changed '
                        'commands/endpoints. Use only approved server/discover or legacy initialize/list metadata. '
                        'No tools/call, model API calls, installers or configuration repairs. '
                        'Every 30 days since a successful drill, copy receipt-owned approved text plus a selected '
                        'nonsecret settings summary to the registered backup root; restore and hash-test only in '
                        'a disposable directory. Exclude raw config, credentials, chats, DB and work files. '
                        'Failed recovery remains due. Keep redacted daily snapshots/change events in private '
                        'health-logs and setup_health in routine-review.json; preserve existing schedules, model, '
                        'reasoning, permissions and unrelated data. Notify only material changes/failures requiring '
                        'attention; compare action_fingerprint with last_notified_fingerprint and update the latter '
                        'with last_notified_at only after actual notification. Do not repeat already reported unresolved states.')
    else:
        health_scope = 'No setup-health execution or recovery authority is inherited; exact host approval is required.'
    updates = authorization.get('software_updates', {})
    if (approved and updates.get('automation_id') == automation_id
            and updates.get('host_identity') == (host_identity or platform.node())
            and updates.get('approved_on') and updates.get('policy') == 'reviewed-existing-software-v1'):
        update_scope = ('Human-approved existing-component auto-updates: run python -B scripts/software_updates.py refresh-plugins '
                        'once per heartbeat; matching successful owner checks inside 24 hours are reused. Collect the installed personal/system/plugin skill '
                        'inventory and current owner catalogs; keep a compact version/hash baseline. Review changed originals '
                        'and release notes, then update existing TRACE-managed skills, global guidance and RTK through their '
                        'owned lifecycle, and installed plugins through supported native owner operations. Preserve enabled '
                        'state, model/effort, authentication, permissions, hooks and Claude. Never edit plugin/system caches '
                        'by hand or install duplicate app-owned CLI executors. Latest-version metadata is not compatibility '
                        'acceptance. New packages, new capabilities/permissions, conflicts, breaking/unknown migrations or '
                        'unavailable owner operations remain explicit candidates; do not silently omit them. After each '
                        'changed batch verify exact installed identities, relevant loading/runtime checks and repeat/no-op '
                        'behavior; on failure restore the owned prior state or preserve an owner-managed failure. Reuse '
                        'unchanged reviewed evidence and avoid daily full suites or repeated unchanged installs. Record '
                        'collection/review/application/verification separately in routine-review.json. GitHub publication '
                        'still needs separate authorization. If the native Codex usage-limit tool is available, refresh only '
                        'used percentage/window/reset timestamps into codex_monitoring.usage_limits, with the actual observation '
                        'time; never store account IDs, balances or raw responses. If unavailable, retain the dated/unknown state. '
                        'Follow docs/software-updates.md; update its owned dashboard projection after changed evidence.')
    else:
        update_scope = 'Existing skills/plugins are review-only on this host until exact local auto-update approval is recorded.'
    template = (ROOT / 'templates/maintenance-prompt.md').read_text(encoding='utf-8')
    return (template.replace('{{checkout}}', str(Path(checkout).absolute()))
            .replace('{{authorization}}', scope).replace('{{automation_id}}', automation_id)
            .replace('{{cleanup_scope}}', cleanup_scope)
            .replace('{{setup_health_scope}}', health_scope)
            .replace('{{software_update_scope}}', update_scope))


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
