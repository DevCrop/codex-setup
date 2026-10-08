"""Render one portable, sanitized RTK report from existing private evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import math
from pathlib import Path
import subprocess
import copy
import re

from presentation import font_css
from setup import ROOT, Deployment, atomic, deployment_lock, read_json, safe, save_json
from tools import verify


def number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0 else None


def model(routine, installed, runtime):
    feedback = routine.get('feedback_loop', {})
    aggregate = feedback.get('rtk_aggregate', {})
    summary = aggregate.get('summary', {})
    inp, out = number(summary.get('total_input')), number(summary.get('total_output'))
    difference = inp - out if inp is not None and out is not None else None
    saved = number(summary.get('total_saved'))
    evidence = feedback.get('rtk_validation', {})
    identity = evidence.get('identity', {})
    harness = ROOT / 'scripts/verify_rtk.py'
    runner = ROOT / 'global/runtime/rtk_runner.py'
    matches = (runtime.get('status') == 'pass' and evidence.get('status') == 'pass'
               and identity.get('binary_sha256') == installed.get('sha256')
               and identity.get('version') == runtime.get('version')
               and identity.get('scope') == 'Explicit project arguments plus disposable argv/exit/evidence fixtures.'
               and identity.get('runner_sha256') == hashlib.sha256(runner.read_bytes()).hexdigest()
               and harness.is_file() and identity.get('harness_sha256') == hashlib.sha256(harness.read_bytes()).hexdigest())
    daily = []
    import re
    for date, row in sorted(aggregate.get('daily_by_date', {}).items()):
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date) or not isinstance(row, dict):
            continue
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            continue
        daily.append({'date': date, **{k: number(row.get(k)) for k in
                      ('commands', 'input_tokens', 'output_tokens', 'saved_tokens', 'savings_pct')}})
    return {'input': inp, 'output': out, 'difference': difference, 'reported_saved': saved,
            'discrepancy': saved - difference if saved is not None and difference is not None else None,
            'commands': number(summary.get('total_commands')), 'daily': daily[-90:],
            'runtime_status': runtime.get('status', 'unknown'),
            'runtime_checks': number(evidence.get('check_count')) if matches else None,
            'runtime_evidence_reused': bool(matches),
            'runtime_checked_at': evidence.get('checked_at') if matches else None,
            'runtime_scope': identity.get('scope') if matches else None,
            'collected_at': aggregate.get('collected_at'),
            'binary_sha256': installed.get('sha256'),
            'actual_openai_token_savings': None, 'browser_review': 'not-verified'}


def payload(data):
    return {'collected_at': data['collected_at'], 'summary': {
        'total_commands': data['commands'], 'total_input': data['input'],
        'total_output': data['output'], 'total_saved': data['reported_saved'],
        'avg_savings_pct': 100 * data['reported_saved'] / data['input']
        if data['input'] and data['reported_saved'] is not None else None},
        'daily': data['daily'], 'probe': data.get('probe', {}),
        'arithmetic_difference': data['discrepancy'], 'openai_usage_measured': False,
        'live': {'enabled': False}}


def template_render(name, slot, data):
    source = (ROOT / 'templates/reports' / name).read_text(encoding='utf-8')
    source = source.replace('__TRACE_SHARED_STYLE__', '<style>' + (ROOT / 'templates/reports/shared.css').read_text(encoding='utf-8') + '</style>')
    if source.count(slot) != 1:
        raise ValueError('Report requires exactly one data slot')
    encoded = json.dumps(data, ensure_ascii=False, allow_nan=False).replace('<', r'\u003c').replace('>', r'\u003e')
    return source.replace(slot, encoded).replace('</head>', font_css() + '\n</head>').encode('utf-8')


def render(data, now):
    result = template_render('rtk-efficiency.template.html', '__RTK_REPORT_DATA__', payload(data))
    # Escaped metadata stays useful when scripts are unavailable.
    return result.replace(b'</head>', ('<meta name="collection" content="' +
        html.escape(str(data['collected_at'] or '미확인'), quote=True) + '">\n</head>').encode())


def overview(routine, installed_status, source_commit, now, *, source_clean=None, sources=None, flow=None):
    feedback = routine.get('feedback_loop', {})
    def rows(values, fields):
        if isinstance(values, dict):
            values = [{'id': k, **v} for k, v in values.items() if isinstance(v, dict)]
        return [{k: str(row[k])[:1500] for k in fields if k in row and isinstance(row[k], (str, int, float, bool))}
                for row in values if isinstance(row, dict)] if isinstance(values, list) else []
    finding_rows = rows(routine.get('unresolved_findings', {}),
        ('id', 'label', 'status', 'impact', 'action', 'proposed_action', 'validation'))
    publication = routine.get('current_checks', {}).get('git_publication', {})
    branch_published = (source_clean is True and publication.get('head') == source_commit
                        and publication.get('remote_head') == source_commit
                        and bool(publication.get('checked_at')))
    release_published = (branch_published and publication.get('release_commit') == source_commit
                         and publication.get('release_asset_install') == 'pass')
    # Never transfer another host's success; only this invocation verifies deployment.
    return {'reported_at': now, 'last_review_at': routine.get('last_substantive_review'),
        'last_apply_at': routine.get('last_policy_application'),
        'last_verify_at': now, 'preferences': rows(feedback.get('preferences', {}),
            ('id', 'label', 'value', 'scope', 'status', 'evidence', 'target')),
        'lessons': rows(feedback.get('lessons', {}),
            ('id', 'label', 'change', 'cause', 'status', 'evidence', 'acceptance')),
        'host_schedule': {'label': routine.get('automation', {}).get('schedule') or '미등록',
            'note': '현재 호스트의 저장된 일정. 미래 실행 완료를 의미하지 않음'},
        'timing_policy': {'rows': [
            {'activity': '공식·릴리스 검토', 'trigger': '현재 등록 일정', 'action': '관련 변경과 미해결만 검토', 'kind': '정기'},
            {'activity': '진행 중 오류', 'trigger': '승인된 작업에서 관찰', 'action': '원인 구분·수정·원래 경로 검증', 'kind': '조건부'},
            {'activity': 'RTK 재검증', 'trigger': '식별자 변경·관련 실패', 'action': '최소 영향 검사', 'kind': '조건부'}]},
        'checks': [{'label': '현재 설치 파일', 'status': installed_status,
                    'evidence': '이번 생성 시 manifest 대조'},
                   {'label': '소스 커밋', 'status': 'unknown', 'evidence': source_commit},
                   {'label': '화면·새 세션 동작', 'status': 'unknown', 'evidence': '파일 검사와 별도 검증 필요'}],
        'sources': sources or [], 'browser_workflow': {'routes': [
            {'name': name, 'status': 'unknown', 'when': trigger,
             'method': '현재 제공되는 공식 도구와 사용자가 선택한 대상 사용',
             'evidence': '이 통합본의 현재 세션 실행 근거 없음',
             'limit': '과거 호스트·다른 경로의 성공을 이전하지 않음', 'verified_at': None}
            for name, trigger in [('내장 브라우저', '로컬 웹 작업'),
                ('지정 브라우저', '사용자가 선택한 탭·프로필 작업'),
                ('Windows 앱', '네이티브 UI 작업')]]},
        'incident_summary': [{'label': x.get('label', x.get('id')), 'status': 'unresolved',
            'summary': x.get('impact', ''), 'validation': x.get('validation', ''),
            'recheck': x.get('action', x.get('proposed_action', ''))} for x in finding_rows],
        'flow_review': flow or {'status': 'unknown', 'findings': ['정본 FLOW에서 검증·복원·종료 분기를 확인'], 'reviewed_at': None},
        'publication': {'applied': installed_status == 'pass', 'verified': installed_status == 'pass',
                        'committed': source_clean is True, 'branch_published': branch_published,
                        'published': release_published}}


def reviewed_sources():
    """Registry claims are reviewed guidance, never current collection success."""
    registry = read_json(ROOT / 'references/registry.json', {})
    result = []
    for item in registry.get('sources', []):
        review = item.get('latest_relevant_review', {})
        if item.get('id') not in ('R01', 'R10', 'R24', 'R51', 'R56') or not review.get('claim'):
            continue
        result.append({'title': item['id'] + ' · ' + item['url'].rstrip('/').split('/')[-1],
            'url': item['url'], 'claim': review['claim'], 'reviewed_on': review.get('date'),
            'authority': '공식 문서의 기록된 검토 근거'})
    return result


def current_flow():
    """Bind static results to exact current bytes; rendering stays a separate gate."""
    receipt = read_json(ROOT / 'diagrams/global/codex-flow.receipt.json', {})
    paths = [('specification_sha256', 'codex-flow.json'), ('artifact_sha256', 'codex-flow.html')]
    matches = all(receipt.get(key) == hashlib.sha256((ROOT / 'diagrams/global' / name).read_bytes()).hexdigest()
                  for key, name in paths)
    passed = matches and all(receipt.get('gates', {}).get(k) == 'pass' for k in ('validate', 'deliver', 'check'))
    return {'status': 'pass' if passed else 'unknown', 'reviewed_at': None,
            'findings': ['현재 JSON·HTML과 정적 검증 영수증 일치' if passed else '현재 도식의 정적 검증 근거 미확인',
                         '브라우저 렌더링·시각 검증은 별도이며 미완료']}


def publish_reports(dep, artifacts):
    # Preflight every owned target before replacing any bytes.
    receipt_path = safe(dep.state, 'reports/report-artifacts.json')
    previous = read_json(receipt_path, {}).get('artifacts', {})
    old_rtk = read_json(safe(dep.state, 'reports/rtk-status.evidence.json'), {})
    paths = {}
    for name in artifacts:
        path = safe(dep.state, 'reports/' + name)
        expected = previous.get(name)
        if name == 'rtk-status.html' and not expected:
            expected = old_rtk.get('artifact_sha256')
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Report ownership conflict: ' + name)
        paths[name] = path
    before = {name: path.read_bytes() if path.exists() else None for name, path in paths.items()}
    written = []
    try:
        for name, data in artifacts.items():
            atomic(paths[name], data); written.append(name)
        save_json(receipt_path, {'schema_version': 1, 'artifacts': {
            name: hashlib.sha256(data).hexdigest() for name, data in artifacts.items()},
            'browser_review': 'not-verified'})
    except Exception:
        for name in reversed(written):
            if before[name] is None:
                paths[name].unlink()
            else:
                atomic(paths[name], before[name])
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path)
    args = parser.parse_args()
    dep = Deployment(state=args.state)
    with deployment_lock(dep.state):
        routine = read_json(safe(dep.state, 'routine-review.json'), None)
        if not isinstance(routine, dict):
            raise ValueError('Existing private routine state is required')
        try:
            runtime = verify(dep.state)
        except (OSError, ValueError, subprocess.SubprocessError):
            runtime = {'status': 'unknown'}
        installed = read_json(safe(dep.state, 'tools-installed.json'), {}).get('rtk', {})
        data = model(routine, installed, runtime)
        now = datetime.now(timezone.utc).isoformat()
        probe_record = read_json(safe(dep.state, 'rtk-runtime-check.json'), {})
        if data['runtime_evidence_reused'] and probe_record.get('identity') == routine.get('feedback_loop', {}).get('rtk_validation', {}).get('identity'):
            probe = next((x for x in probe_record.get('checks', []) if x.get('check') == 'project-1-git-status'), {})
            data['probe'] = {new: probe[old] for new, old in {'raw_bytes': 'raw_output_bytes', 'filtered_bytes': 'rtk_output_bytes', 'raw_exit': 'raw_exit', 'filtered_exit': 'rtk_exit'}.items() if old in probe}
            data['probe']['recorded_invocation_delta'] = routine.get('feedback_loop', {}).get('rtk_validation', {}).get('rtk_probe_invocations')
            data['probe'].update(checked_at=data['runtime_checked_at'],
                required_evidence_preserved=probe.get('status') == 'pass', identity_verified=True,
                identity=probe_record['identity'])
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        clean = not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()
        view = overview(routine, dep.verify()['status'], commit, now, source_clean=clean,
                        sources=reviewed_sources(), flow=current_flow())
        view['flow_link'] = (ROOT / 'diagrams/global/codex-flow.html').as_uri()
        encoded = render(data, now)
        rt = payload(data)
        live_template = (ROOT / 'templates/reports/rtk-efficiency.template.html').read_text(encoding='utf-8').replace('__TRACE_SHARED_STYLE__', '<style>' + (ROOT / 'templates/reports/shared.css').read_text(encoding='utf-8') + '</style>').replace('</head>', font_css() + '\n</head>')
        overview_html = template_render('adaptive-routine.template.html', '__ROUTINE_REPORT_DATA__', view)
        artifacts = {'rtk-status.html': encoded, 'overview.html': overview_html,
            'rtk-efficiency.template.html': live_template.encode(),
            'rtk-efficiency.json': json.dumps(rt, ensure_ascii=False, allow_nan=False).encode(),
            'overview.json': json.dumps(view, ensure_ascii=False, allow_nan=False).encode()}
        publish_reports(dep, artifacts)
        output = safe(dep.state, 'reports/rtk-status.html')
        save_json(safe(dep.state, 'reports/rtk-status.evidence.json'), {
            'schema_version': 3, 'generated_at': now, 'data': data,
            'artifact_sha256': hashlib.sha256(encoded).hexdigest(),
            'status': 'rendered-static-checks-only', 'browser_review': 'not-verified'})
    print(json.dumps({'status': 'rendered-static-checks-only', 'path': str(output),
                      'runtime_checks_reused': data['runtime_evidence_reused'], 'browser_review': 'not-verified'}))


if __name__ == '__main__':
    main()
